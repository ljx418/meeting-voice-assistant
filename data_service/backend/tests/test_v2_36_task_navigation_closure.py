from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_tool_registry import all_tool_specs
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from backend.tests.test_v2_32_lightweight_relationship_graph import _bootstrap_codebase, _create_workspace, _make_repo


def _assert_no_abs_path(payload: object, *paths: Path) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    assert "/Users/" not in text
    assert "/private/var" not in text
    assert "/var/folders" not in text
    for path in paths:
        assert str(path) not in text


def _assert_closure_payload(payload: dict) -> None:
    report = payload["data"]["closure_report"]
    html = payload["data"]["html"]
    mermaid = payload["data"]["mermaid"]
    coverage = payload["data"]["coverage_matrix"]
    governance = payload["data"]["governance_targets"]
    audit = payload["data"]["closure_audit"]
    assert report["schema_version"] == "v2.36"
    assert report["summary"]["relationship_count"] > 0
    assert report["summary"]["forbidden_relationship_count"] == 0
    assert report["nodes"]
    assert "<script" not in html.lower()
    assert "Task Navigation Closure Report" in html
    assert mermaid.startswith("flowchart LR")
    node_ids = {node["node_id"] for node in report["nodes"]}
    for node_id in node_ids:
        assert node_id in mermaid
    assert coverage["rows"]
    assert governance["targets"]
    assert audit["checks"]
    for target in governance["targets"]:
        assert target["target_id"]


def test_v2_36_task_navigation_closure_http_mcp_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    workspace_root = tmp_path / "managed"
    _make_repo(repo)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    tool_names = {spec["name"] for spec in all_tool_specs()}
    assert "knowledge_code_task_navigation_closure_build" in tool_names
    assert "knowledge_code_task_navigation_closure_read" in tool_names
    assert "knowledge_code_task_navigation_closure_view" in tool_names

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase102 Closure")
    codebase_id, snapshot_id = _bootstrap_codebase(client, repo, workspace_id)

    handoff = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff",
        json={"snapshot_id": snapshot_id, "task": "新增 HTTP API 并补测试", "target_agent": "codex", "max_tokens": 900},
    )
    assert handoff.status_code == 200, handoff.text
    handoff_id = handoff.json()["data"]["agent_handoff"]["handoff_id"]

    built = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/build",
        json={"snapshot_id": snapshot_id, "handoff_id": handoff_id},
    )
    assert built.status_code == 200, built.text
    _assert_closure_payload(built.json())
    _assert_no_abs_path(built.json(), repo, workspace_root)

    read_back = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure")
    assert read_back.status_code == 200, read_back.text
    _assert_closure_payload(read_back.json())

    view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/views/mermaid")
    assert view.status_code == 200, view.text
    assert view.json()["data"]["closure_view"]["content"].startswith("flowchart LR")

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_task_navigation_closure_read",
            {"workspace_id": workspace_id, "codebase_id": codebase_id},
        )
    )
    assert mcp_payload["status"] == "ok"
    assert mcp_payload["data"]["closure_report"]["schema_version"] == "v2.36"
    _assert_no_abs_path(mcp_payload, repo, workspace_root)

    exit_code = knowledge_main(
        [
            "code",
            "coding-agent",
            "closure",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            workspace_id,
            "--codebase-id",
            codebase_id,
        ]
    )
    assert exit_code == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["data"]["closure_report"]["schema_version"] == "v2.36"
    _assert_no_abs_path(cli_payload, repo, workspace_root)
