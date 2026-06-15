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


def _assert_impact_payload(payload: dict) -> str:
    impact = payload["data"]["impact_analysis"]
    selection = payload["data"]["test_selection"]
    assert impact["impact_id"]
    assert impact["task_id"]
    assert (
        impact["summary"]["impacted_file_count"]
        + impact["summary"]["impacted_symbol_count"]
        + impact["summary"]["impacted_surface_count"]
        + impact["summary"]["impacted_test_count"]
        + impact["summary"]["impacted_doc_count"]
        > 0
    )
    assert selection["summary"]["suggested_test_count"] > 0
    for item in selection["suggested_tests"]:
        assert item["reason"]
        assert item.get("evidence_refs") or item.get("needs_review")
    assert all(item.get("code") != "runtime_call_accepted" for item in impact.get("risk_items", []))
    return str(impact["task_id"])


def test_v2_33_change_impact_and_test_selection_http_mcp_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    workspace_root = tmp_path / "managed"
    _make_repo(repo)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    tool_names = {spec["name"] for spec in all_tool_specs()}
    assert "knowledge_code_task_impact_analyze" in tool_names
    assert "knowledge_code_task_impact_read" in tool_names

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase99 Impact")
    codebase_id, snapshot_id = _bootstrap_codebase(client, repo, workspace_id)

    built = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2",
        json={"snapshot_id": snapshot_id, "task": "新增 HTTP API 并补测试", "max_items": 50},
    )
    assert built.status_code == 200, built.text
    task_id = _assert_impact_payload(built.json())
    _assert_no_abs_path(built.json(), repo, workspace_root)

    read_back = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2/{task_id}")
    assert read_back.status_code == 200, read_back.text
    assert read_back.json()["data"]["impact_analysis"]["task_id"] == task_id

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_task_impact_read",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "task_id": task_id},
        )
    )
    assert mcp_payload["status"] == "ok"
    assert mcp_payload["data"]["impact_analysis"]["task_id"] == task_id
    _assert_no_abs_path(mcp_payload, repo, workspace_root)

    exit_code = knowledge_main(
        [
            "code",
            "coding-agent",
            "impact-v2-read",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            workspace_id,
            "--codebase-id",
            codebase_id,
            "--task-id",
            task_id,
        ]
    )
    assert exit_code == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["data"]["impact_analysis"]["task_id"] == task_id
    _assert_no_abs_path(cli_payload, repo, workspace_root)
