from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.doc_quality import build_document_quality
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import architecture_doc_quality_findings_path, architecture_doc_quality_summary_path
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _doc(
    doc_id: str,
    *,
    title: str = "Doc",
    doc_type: str = "target_architecture",
    authority_level: str = "primary",
    authority_role: str = "target",
    stale_hint: bool = False,
    phase_hint: str = "V2.7",
) -> dict:
    return {
        "schema_version": "v2.7",
        "workspace_id": "ws",
        "codebase_id": "cb",
        "snapshot_id": "snap",
        "doc_id": doc_id,
        "doc_type": doc_type,
        "path": f"docs/{doc_id}.md",
        "repo_path": f"docs/{doc_id}.md",
        "title": title,
        "phase_hint": phase_hint,
        "scope_hint": "scope-a",
        "authority_role": authority_role,
        "authority_level": authority_level,
        "stale_hint": stale_hint,
        "evidence": [{"type": "source_file", "repo_path": f"docs/{doc_id}.md", "line_range": [1, 1]}],
    }


def _claim(
    claim_id: str,
    doc_id: str,
    label: str,
    *,
    claim_type: str = "component",
    confidence: float = 0.9,
    evidence: list[dict] | None = None,
    needs_review: list[dict] | None = None,
    source_block_type: str = "bullet",
    scope_hint: str = "scope-a",
) -> dict:
    return {
        "schema_version": "v2.7",
        "workspace_id": "ws",
        "codebase_id": "cb",
        "snapshot_id": "snap",
        "claim_id": claim_id,
        "doc_id": doc_id,
        "claim_type": claim_type,
        "label": label,
        "scope_hint": scope_hint,
        "source_block_type": source_block_type,
        "source_path": f"docs/{doc_id}.md",
        "repo_path": f"docs/{doc_id}.md",
        "line_range": [1, 1],
        "confidence": confidence,
        "needs_review": needs_review or [],
        "evidence": evidence if evidence is not None else [{"type": "source_file", "repo_path": f"docs/{doc_id}.md", "line_range": [1, 1]}],
    }


def test_v27_phase51_quality_rule_spec_fixtures():
    docs = [
        _doc("doc_target_current", title="Target Current Architecture"),
        _doc("doc_stale", title="Historical Target", stale_hint=True),
        _doc("doc_plan", title="Implementation Plan", doc_type="development_plan", authority_role="implementation_plan", authority_level="supporting"),
        _doc("doc_owner", title="Owner Notes", doc_type="development_plan", authority_role="implementation_plan", authority_level="supporting", phase_hint=""),
    ]
    claims = [
        _claim("accepted_no_evidence", "doc_target_current", "Phase 51 accepted implementation evidence passed", evidence=[]),
        _claim("planned_and_accepted", "doc_target_current", "Phase 52 planned and accepted", claim_type="milestone"),
        _claim("scope_missing", "doc_target_current", "Runtime Component", scope_hint=""),
        _claim("drawio_ready", "doc_target_current", "Target architecture ready", confidence=0.6, source_block_type="diagram_node", needs_review=[{"code": "DIAGRAM_REVIEW"}]),
        _claim("overbroad", "doc_target_current", "Complete architecture fully implemented", claim_type="system"),
        _claim("plan_without_gate", "doc_plan", "Phase 51 implementation plan", claim_type="milestone"),
        _claim("owner_missing", "doc_owner", "Owner must approve architecture work", scope_hint=""),
    ]
    relations = [
        {
            "schema_version": "v2.7",
            "workspace_id": "ws",
            "codebase_id": "cb",
            "snapshot_id": "snap",
            "relation_id": "broken",
            "source_doc_id": "doc_target_current",
            "from_claim_id": "missing_from",
            "to_claim_id": "accepted_no_evidence",
        }
    ]

    payload = build_document_quality(workspace_id="ws", codebase_id="cb", snapshot_id="snap", documents=docs, claims=claims, relations=relations)
    finding_types = {item["finding_type"] for item in payload["findings"]}

    assert {
        "missing_evidence",
        "missing_acceptance_gate",
        "stale_document",
        "status_conflict",
        "scope_conflict",
        "unsupported_claim",
        "ambiguous_ownership",
        "missing_current_target_split",
        "doc_code_mismatch",
        "overbroad_architecture_claim",
        "low_confidence_claim",
        "broken_document_relation",
    }.issubset(finding_types)
    assert payload["summary"]["severity_counts"]["major"] >= 1
    assert payload["summary"]["overall_status"] == "needs_review"
    assert all(item["target_id"] for item in payload["findings"])
    assert all(item.get("evidence") or item.get("needs_review") for item in payload["findings"])


def _assert_quality(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo_path: str) -> None:
    quality = payload["data"]["document_quality"] if "data" in payload else payload
    assert quality["schema_version"] == "v2.7"
    assert quality["workspace_id"] == workspace_id
    assert quality["codebase_id"] == codebase_id
    assert quality["snapshot_id"] == snapshot_id
    assert quality["artifact_refs"]
    assert quality["summary"]["document_count"] >= 1
    assert quality["summary"]["claim_count"] >= 1
    assert quality["summary"]["finding_count"] == len(quality["findings"])
    assert quality["summary"]["overall_status"] != "high_quality" or not quality["summary"].get("severity_counts", {}).get("major")
    assert all(item["target_id"] for item in quality["findings"])
    assert all(item.get("evidence") or item.get("needs_review") for item in quality["findings"])
    assert repo_path not in json.dumps(quality, ensure_ascii=False)


def test_v27_phase51_document_quality_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_document_registry(codebase_id, snapshot_id=snapshot_id)
    service.build_document_claims(codebase_id)

    direct = service.build_document_quality(codebase_id)
    assert architecture_doc_quality_findings_path(workspace, codebase_id).exists()
    assert architecture_doc_quality_summary_path(workspace, codebase_id).exists()
    assert architecture_doc_quality_findings_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_doc_quality_summary_path(workspace, codebase_id).stat().st_size > 0
    _assert_quality(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality/build")
    assert http_build.status_code == 200
    _assert_quality(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality")
    assert http_read.status_code == 200
    _assert_quality(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_doc_quality", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_quality(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "docs-quality", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_quality(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))


def test_v27_phase51_document_quality_missing_claims_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    ArchitectureService(workspace, workspace_id=workspace_id).build_document_registry(codebase_id, snapshot_id=snapshot_id)

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality/build")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT"
