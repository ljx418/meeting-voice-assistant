from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService
from data_service.code_assets.coding_agent_v2_16.persistence import (
    workbench_v2_html_path,
    workbench_v2_mermaid_path,
    workbench_v2_payload_path,
)
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _workbench_v2(payload: dict) -> dict:
    if "data" in payload and "workbench_v2" in payload["data"]:
        return payload["data"]["workbench_v2"]
    return payload


def _view(payload: dict) -> dict:
    if "data" in payload and "workbench_v2_view" in payload["data"]:
        return payload["data"]["workbench_v2_view"]
    return payload


def _assert_workbench_v2(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: str, workspace_path: str) -> dict:
    workbench = _workbench_v2(payload)
    serialized = json.dumps(workbench, ensure_ascii=False)
    assert workbench["schema_version"] == "v2.16"
    assert workbench["workspace_id"] == workspace_id
    assert workbench["codebase_id"] == codebase_id
    assert workbench["snapshot_id"] == snapshot_id
    assert workbench["summary"]["provider_count"] >= 1
    assert workbench["summary"]["semantic_fact_count"] > 0
    assert workbench["summary"]["runtime_profile_count"] >= 1
    assert workbench["summary"]["blocker_count"] >= 1
    assert {section["section_id"] for section in workbench["sections"]} >= {"provider_matrix", "semantic_coverage", "runtime_profiles", "risk_lanes", "blocker_board"}
    assert workbench["graph"]["nodes"]
    node_ids = {node["node_id"] for node in workbench["graph"]["nodes"]}
    for edge in workbench["graph"]["edges"]:
        assert edge["from"] in node_ids
        assert edge["to"] in node_ids
    assert str(repo) not in serialized
    assert str(workspace_path) not in serialized
    return workbench


def test_v216_workbench_v2_service_views(tmp_path, monkeypatch):
    for env_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)

    workbench = _assert_workbench_v2(service.build_workbench_v2(codebase_id, snapshot_id=snapshot_id), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))
    assert workbench_v2_payload_path(workspace, codebase_id).exists()
    assert workbench_v2_html_path(workspace, codebase_id).exists()
    assert workbench_v2_mermaid_path(workspace, codebase_id).exists()
    html = service.read_workbench_v2_view(codebase_id, "html")
    mermaid = service.read_workbench_v2_view(codebase_id, "mermaid")
    assert "<script" not in html["content"].lower()
    assert "Provider Matrix" in html["content"]
    assert "flowchart TD" in mermaid["content"]
    for node in workbench["graph"]["nodes"]:
        assert node["node_id"] in mermaid["content"]


def test_v216_workbench_v2_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    for env_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench-v2/build",
        json={"snapshot_id": snapshot_id},
    )
    assert http_build.status_code == 200
    http_workbench = _assert_workbench_v2(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench-v2/views/html")
    assert http_view.status_code == 200
    assert "<script" not in _view(_v2(http_view.json()))["content"].lower()

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_workbench_v2_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id},
        )
    )
    mcp_workbench = _assert_workbench_v2(_v2(mcp_build), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert knowledge_main(["code", "coding-agent", "workbench-v2-read", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_workbench = _assert_workbench_v2(_v2(json.loads(capsys.readouterr().out)), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert http_workbench["summary"] == mcp_workbench["summary"] == cli_workbench["summary"]
    assert [section["section_id"] for section in http_workbench["sections"]] == [section["section_id"] for section in cli_workbench["sections"]]
