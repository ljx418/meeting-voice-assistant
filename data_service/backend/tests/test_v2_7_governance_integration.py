from __future__ import annotations

import hashlib
import json
from pathlib import Path

from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import (
    architecture_doc_claims_path,
    architecture_doc_code_alignment_path,
    architecture_doc_quality_findings_path,
    architecture_reconstructed_model_path,
)

from test_v2_7_document_registry import _prepare, _prepare_alignment_artifacts, _v2


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record_feedback(client, workspace_id: str, codebase_id: str, *, target_type: str, target_id: str, rule_type: str, action: str = "needs_review"):
    return client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback",
        json={
            "target_type": target_type,
            "target_id": target_id,
            "action": action,
            "rule_type": rule_type,
            "severity": "medium",
            "reason": "V2.7 governance overlay test",
            "suggested_value": "review_required",
        },
    )


def test_v27_phase54_governance_read_time_overlay_and_hash_gate(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_document_code_alignment(codebase_id)
    service.build_reconstructed_architecture(codebase_id)

    claims = service.read_document_claims(codebase_id)["claims"]
    quality = service.read_document_quality(codebase_id)["findings"]
    alignment = service.read_document_code_alignment(codebase_id)["alignments"]
    reconstructed = service.read_reconstructed_architecture(codebase_id)
    claim_id = claims[0]["claim_id"]
    finding_id = quality[0]["finding_id"]
    alignment_id = next(item["alignment_id"] for item in alignment if item.get("status") != "matched")
    node_id = reconstructed["diff_nodes"][0]["node_id"]

    source_paths = [
        architecture_doc_claims_path(workspace, codebase_id),
        architecture_doc_quality_findings_path(workspace, codebase_id),
        architecture_doc_code_alignment_path(workspace, codebase_id),
        architecture_reconstructed_model_path(workspace, codebase_id),
    ]
    before_hashes = {path.name: _hash(path) for path in source_paths}

    missing = _record_feedback(client, workspace_id, codebase_id, target_type="architecture_doc_claim", target_id="missing_claim", rule_type="missing_evidence")
    assert missing.status_code == 404
    assert missing.json()["v2"]["error"]["code"] == "QUALITY_TARGET_NOT_FOUND"

    for target_type, target_id, rule_type in [
        ("architecture_doc_claim", claim_id, "missing_evidence"),
        ("architecture_doc_quality_finding", finding_id, "stale_document"),
        ("architecture_doc_code_alignment", alignment_id, "doc_code_mismatch"),
        ("architecture_reconstructed_node", node_id, "wrong_target_current_split"),
    ]:
        response = _record_feedback(client, workspace_id, codebase_id, target_type=target_type, target_id=target_id, rule_type=rule_type)
        assert response.status_code == 200
        payload = _v2(response.json())["data"]
        assert payload["feedback"]["target_type"] == target_type
        assert payload["feedback"]["target_id"] == target_id
        assert str(repo) not in json.dumps(payload, ensure_ascii=False)

    build_rules = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/build")
    assert build_rules.status_code == 200
    rules = _v2(build_rules.json())["data"]["rules"]
    assert len(rules) >= 4

    approved_ids = []
    for rule in rules:
        if rule["target_id"] in {claim_id, finding_id, alignment_id, node_id}:
            review = client.post(
                f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rule['rule_id']}/review",
                json={"status": "approved", "reviewer": "phase54-test", "note": "approve overlay"},
            )
            assert review.status_code == 200
            approved_ids.append(rule["rule_id"])
    assert approved_ids

    plan_response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/plan")
    assert plan_response.status_code == 200
    plan = _v2(plan_response.json())["data"]["plan"]
    assert set(approved_ids).issubset(set(plan["approved_rule_ids"]))
    assert all(item["target_id"] in {claim_id, finding_id, alignment_id, node_id} for item in plan["impacted_targets"])

    claims_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims")
    quality_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality")
    alignment_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment")
    reconstructed_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed")
    for response in (claims_read, quality_read, alignment_read, reconstructed_read):
        assert response.status_code == 200

    governed_claim = next(item for item in _v2(claims_read.json())["data"]["document_claims"]["claims"] if item["claim_id"] == claim_id)
    governed_finding = next(item for item in _v2(quality_read.json())["data"]["document_quality"]["findings"] if item["finding_id"] == finding_id)
    governed_alignment = next(item for item in _v2(alignment_read.json())["data"]["document_code_alignment"]["alignments"] if item["alignment_id"] == alignment_id)
    governed_node = next(item for item in _v2(reconstructed_read.json())["data"]["reconstructed_architecture"]["diff_nodes"] if item["node_id"] == node_id)
    for item in (governed_claim, governed_finding, governed_alignment, governed_node):
        assert item["applied_rules"]
        assert item["governance_status"] == "governed"
        assert "governed_by_rule" in item["needs_review"]

    revoked = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{approved_ids[0]}/review",
        json={"status": "revoked", "reviewer": "phase54-test", "note": "revoke overlay"},
    )
    assert revoked.status_code == 200
    rebuilt_plan = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/plan")
    assert rebuilt_plan.status_code == 200
    assert approved_ids[0] not in _v2(rebuilt_plan.json())["data"]["plan"]["approved_rule_ids"]

    after_hashes = {path.name: _hash(path) for path in source_paths}
    assert before_hashes == after_hashes
