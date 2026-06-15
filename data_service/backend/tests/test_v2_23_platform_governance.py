from __future__ import annotations

import asyncio
import hashlib
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.platform.console import PlatformConsoleService
from data_service.code_assets.platform.governance import PlatformGovernanceService
from data_service.code_assets.platform.persistence import console_payload_path, governance_feedback_path, governance_overlay_report_path, governance_rules_path
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _governance(payload: dict) -> dict:
    if "data" in payload and "platform_governance" in payload["data"]:
        return payload["data"]["platform_governance"]
    if "overlay_report" in payload:
        return {
            "schema_version": "v2.23",
            "artifact_type": "platform_governance_bundle",
            "feedback": payload.get("feedback"),
            "rules": payload.get("rules"),
            "rule": payload.get("rule"),
            "overlay_report": payload["overlay_report"],
            "artifact_refs": payload.get("artifact_refs", []),
        }
    return payload


def _hash(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_overlay(payload: dict, *, applied_count: int, source_hash: str, repo: str, workspace_path: str) -> dict:
    bundle = _governance(payload)
    serialized = json.dumps(bundle, ensure_ascii=False)
    assert bundle["schema_version"] == "v2.23"
    assert bundle["artifact_type"] == "platform_governance_bundle"
    report = bundle["overlay_report"]
    assert report["schema_version"] == "v2.23"
    assert report["artifact_type"] == "platform_governance_overlay_report"
    assert report["summary"]["applied_rule_count"] == applied_count
    assert report["summary"]["source_artifact_hash_unchanged"] is True
    assert report["source_artifact_hash_before"]["platform_console"] == source_hash
    assert report["source_artifact_hash_after"]["platform_console"] == source_hash
    assert repo not in serialized
    assert workspace_path not in serialized
    return bundle


def test_v223_platform_governance_service_approve_revoke_and_missing_target(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    PlatformConsoleService(workspace, workspace_id=workspace_id).build_console(codebase_id, snapshot_id=snapshot_id)
    source_hash = _hash(console_payload_path(workspace, codebase_id))
    service = PlatformGovernanceService(workspace, workspace_id=workspace_id)

    feedback = service.record_feedback(
        codebase_id,
        target_type="platform_panel",
        target_id="overview",
        action="needs_review",
        rule_type="read_time_overlay",
        reason="overview panel needs reviewer note",
        suggested_value="show reviewer note",
    )["feedback"]
    assert governance_feedback_path(workspace, codebase_id).exists()
    rules = service.build_rules(codebase_id)["rules"]
    assert governance_rules_path(workspace, codebase_id).exists()
    rule_id = rules[0]["rule_id"]
    assert feedback["target_id"] == "overview"

    approved = service.review_rule(codebase_id, rule_id, status="approved", reviewer="unit-test")
    _assert_overlay(approved, applied_count=1, source_hash=source_hash, repo=str(repo), workspace_path=str(workspace))
    assert _hash(console_payload_path(workspace, codebase_id)) == source_hash

    revoked = service.review_rule(codebase_id, rule_id, status="revoked", reviewer="unit-test")
    _assert_overlay(revoked, applied_count=0, source_hash=source_hash, repo=str(repo), workspace_path=str(workspace))
    assert governance_overlay_report_path(workspace, codebase_id).exists()

    try:
        service.record_feedback(codebase_id, target_type="platform_panel", target_id="missing-panel", action="needs_review", rule_type="read_time_overlay")
    except FileNotFoundError as exc:
        assert str(exc) == "PLATFORM_GOVERNANCE_TARGET_NOT_FOUND"
    else:
        raise AssertionError("missing target feedback must be rejected")


def test_v223_platform_governance_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    PlatformConsoleService(workspace, workspace_id=workspace_id).build_console(codebase_id, snapshot_id=snapshot_id)
    source_hash = _hash(console_payload_path(workspace, codebase_id))

    feedback = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/feedback",
        json={"target_type": "platform_panel", "target_id": "overview", "action": "needs_review", "reason": "needs reviewer note", "suggested_value": "show reviewer note"},
    )
    assert feedback.status_code == 200
    rules = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/build")
    assert rules.status_code == 200
    rule_id = _v2(rules.json())["data"]["platform_governance"]["rules"][0]["rule_id"]
    approved = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/{rule_id}/review",
        json={"status": "approved", "reviewer": "http-test"},
    )
    assert approved.status_code == 200
    http_overlay = _assert_overlay(_v2(approved.json()), applied_count=1, source_hash=source_hash, repo=str(repo), workspace_path=str(workspace))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_overlay = asyncio.run(dispatcher.call_tool("knowledge_code_platform_governance_overlay", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_bundle = _assert_overlay(_v2(mcp_overlay), applied_count=1, source_hash=source_hash, repo=str(repo), workspace_path=str(workspace))

    assert knowledge_main(["code", "platform", "governance-overlay", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_bundle = _assert_overlay(_v2(json.loads(capsys.readouterr().out)), applied_count=1, source_hash=source_hash, repo=str(repo), workspace_path=str(workspace))

    assert http_overlay["overlay_report"]["summary"] == mcp_bundle["overlay_report"]["summary"]
    assert http_overlay["overlay_report"]["summary"] == cli_bundle["overlay_report"]["summary"]

    revoked = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/{rule_id}/review",
        json={"status": "revoked", "reviewer": "http-test"},
    )
    assert revoked.status_code == 200
    _assert_overlay(_v2(revoked.json()), applied_count=0, source_hash=source_hash, repo=str(repo), workspace_path=str(workspace))
