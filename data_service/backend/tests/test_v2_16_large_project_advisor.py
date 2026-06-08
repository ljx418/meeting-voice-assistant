from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService
from data_service.code_assets.coding_agent_v2_16.persistence import (
    large_project_advisor_path,
    large_project_blockers_path,
    large_project_pattern_adapters_path,
)
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _advisor(payload: dict) -> dict:
    if "data" in payload and "large_project_advisor" in payload["data"]:
        return payload["data"]["large_project_advisor"]
    return payload


def _assert_advisor(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: str, workspace_path: str) -> dict:
    advisor = _advisor(payload)
    serialized = json.dumps(advisor, ensure_ascii=False).lower()
    assert advisor["schema_version"] == "v2.16"
    assert advisor["workspace_id"] == workspace_id
    assert advisor["codebase_id"] == codebase_id
    assert advisor["snapshot_id"] == snapshot_id
    assert advisor["summary"]["generic_adapter_count"] > 0
    assert advisor["generic_pattern_adapters"]
    assert advisor["accepted_patterns"] or advisor["blockers"]
    for pattern in advisor["accepted_patterns"]:
        assert pattern["confidence"] >= 0.8
        assert pattern["evidence_refs"]
        assert not any(ref.endswith((".md", ".drawio")) for ref in pattern["evidence_refs"])
        assert not any(path.endswith((".md", ".drawio")) for path in pattern["matched_paths"])
    for blocker in advisor["blockers"]:
        assert blocker["reason"]
        assert blocker["missing_evidence"]
        assert blocker["next_actions"]
    assert "harnessos-only" not in serialized
    assert "project_specific_override" not in serialized
    assert str(repo).lower() not in serialized
    assert str(workspace_path).lower() not in serialized
    return advisor


def test_v216_large_project_advisor_service_artifacts(tmp_path, monkeypatch):
    for env_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)

    advisor = _assert_advisor(service.build_large_project_advisor(codebase_id, snapshot_id=snapshot_id), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))
    assert large_project_advisor_path(workspace, codebase_id).exists()
    assert large_project_pattern_adapters_path(workspace, codebase_id).exists()
    assert large_project_blockers_path(workspace, codebase_id).exists()
    assert service.read_large_project_advisor(codebase_id)["summary"] == advisor["summary"]


def test_v216_large_project_advisor_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    for env_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/large-project-advisor/build",
        json={"snapshot_id": snapshot_id},
    )
    assert http_build.status_code == 200
    http_advisor = _assert_advisor(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_large_project_advisor_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id},
        )
    )
    mcp_advisor = _assert_advisor(_v2(mcp_build), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert knowledge_main(["code", "coding-agent", "large-project-advisor", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_advisor = _assert_advisor(_v2(json.loads(capsys.readouterr().out)), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert http_advisor["summary"] == mcp_advisor["summary"] == cli_advisor["summary"]
    assert [item["adapter_id"] for item in http_advisor["generic_pattern_adapters"]] == [item["adapter_id"] for item in cli_advisor["generic_pattern_adapters"]]
