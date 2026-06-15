from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.platform.ci import PlatformCIReadinessService
from data_service.code_assets.platform.console import PlatformConsoleService
from data_service.code_assets.platform.contracts import ArtifactContractService
from data_service.code_assets.platform.governance import PlatformGovernanceService
from data_service.code_assets.platform.incremental import PlatformIncrementalService
from data_service.code_assets.platform.persistence import ci_readiness_report_path, console_payload_path, release_readiness_report_path
from data_service.code_assets.platform.providers import PlatformProviderService
from data_service.code_assets.platform.tool_catalog import ToolCatalogService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_tool_registry import all_tool_specs
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _command_evidence(*, warnings: int = 12) -> dict:
    return {
        "unit": {"status": "passed", "command": "PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_24_ci_readiness.py -q", "exit_code": 0, "warning_count": 0},
        "contract": {"status": "passed", "command": "PYTHONPATH=backend python3 -m pytest backend/tests/test_public_surface_guard.py -q", "exit_code": 0, "warning_count": 0},
        "artifact": {"status": "passed", "command": "python validate_platform_artifacts.py", "exit_code": 0, "warning_count": 0},
        "frontend": {"status": "passed", "command": "npm run build", "exit_code": 0, "warning_count": 0},
        "real_repo_e2e": {"status": "passed", "command": "python phase90_real_repo_e2e.py", "exit_code": 0, "warning_count": warnings},
        "slow_nightly": {"status": "skipped", "reason": "not part of Phase 90 mandatory gate"},
    }


def _build_prerequisites(workspace, workspace_id: str, codebase_id: str, snapshot_id: str) -> None:
    PlatformConsoleService(workspace, workspace_id=workspace_id).build_console(codebase_id, snapshot_id=snapshot_id)
    ArtifactContractService(workspace, workspace_id=workspace_id).build_contracts(codebase_id)
    ToolCatalogService(workspace, workspace_id=workspace_id).build_tool_catalog(codebase_id, all_tool_specs())
    PlatformIncrementalService(workspace, workspace_id=workspace_id).build_incremental_plan(codebase_id, from_snapshot_id=snapshot_id, to_snapshot_id=snapshot_id)
    PlatformProviderService(workspace, workspace_id=workspace_id).build_provider_artifacts(codebase_id, snapshot_id=snapshot_id)
    governance = PlatformGovernanceService(workspace, workspace_id=workspace_id)
    governance.record_feedback(codebase_id, target_type="platform_panel", target_id="overview", action="needs_review", rule_type="read_time_overlay")


def _readiness(payload: dict) -> dict:
    if "data" in payload and "ci_readiness" in payload["data"]:
        return payload["data"]["ci_readiness"]
    if "ci_readiness" in payload:
        return payload["ci_readiness"]
    return payload


def test_v224_ci_readiness_service_ready_skipped_and_redaction_gates(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    _build_prerequisites(workspace, workspace_id, codebase_id, snapshot_id)
    service = PlatformCIReadinessService(workspace, workspace_id=workspace_id)

    ready = service.build_readiness(codebase_id, snapshot_id=snapshot_id, command_evidence=_command_evidence(), warning_budget=700)
    assert ready["overall_status"] == "ready"
    assert ready["release_gate"]["ready"] is True
    assert ready["test_layers"]["slow_nightly"]["status"] == "skipped"
    assert ci_readiness_report_path(workspace, codebase_id).exists()
    assert release_readiness_report_path(workspace, codebase_id).exists()

    skipped = _command_evidence()
    skipped["unit"] = {"status": "skipped", "command": "not run", "reason": "intentional test fixture"}
    blocked = service.build_readiness(codebase_id, snapshot_id=snapshot_id, command_evidence=skipped, warning_budget=700)
    assert blocked["overall_status"] == "blocked"
    assert any(item["layer"] == "unit" and item["status"] == "skipped" for item in blocked["release_gate"]["blockers"])

    console_path = console_payload_path(workspace, codebase_id)
    payload = json.loads(console_path.read_text(encoding="utf-8"))
    payload["test_leak"] = str(repo)
    console_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    leaked = service.build_readiness(codebase_id, snapshot_id=snapshot_id, command_evidence=_command_evidence(), warning_budget=700)
    assert leaked["security_gate"]["redaction"] == "failed"
    assert leaked["overall_status"] == "blocked"
    assert any(item["code"] == "PUBLIC_PAYLOAD_REDACTION_FAILED" for item in leaked["release_gate"]["blockers"])


def test_v224_ci_readiness_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    _build_prerequisites(workspace, workspace_id, codebase_id, snapshot_id)
    service = PlatformCIReadinessService(workspace, workspace_id=workspace_id)
    service.build_readiness(codebase_id, snapshot_id=snapshot_id, command_evidence=_command_evidence(), warning_budget=700)

    http_response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/ci/readiness")
    assert http_response.status_code == 200
    http_payload = _readiness(_v2(http_response.json()))
    assert http_payload["overall_status"] == "ready"

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_response = asyncio.run(dispatcher.call_tool("knowledge_code_platform_ci_readiness_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_payload = _readiness(_v2(mcp_response))

    assert knowledge_main(["code", "platform", "ci-readiness", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = _readiness(_v2(json.loads(capsys.readouterr().out)))

    for payload in [mcp_payload, cli_payload]:
        assert payload["schema_version"] == http_payload["schema_version"]
        assert payload["codebase_id"] == http_payload["codebase_id"]
        assert payload["overall_status"] == http_payload["overall_status"]
        assert payload["release_gate"]["ready"] == http_payload["release_gate"]["ready"]
        assert len(payload["artifact_refs"]) == len(http_payload["artifact_refs"])

    report_response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/ci/release-report")
    assert report_response.status_code == 200
    report = _v2(report_response.json())["data"]["ci_release_report"]
    assert "Release Readiness Report" in report["content"]
    assert "npm run build" in report["content"]
