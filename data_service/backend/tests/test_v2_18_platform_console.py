from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.platform.console import PlatformConsoleService
from data_service.code_assets.platform.persistence import console_html_path, console_payload_path
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _console(payload: dict) -> dict:
    if "data" in payload and "platform_console" in payload["data"]:
        return payload["data"]["platform_console"]
    return payload


def _view(payload: dict) -> dict:
    if "data" in payload and "platform_console_view" in payload["data"]:
        return payload["data"]["platform_console_view"]
    return payload


def _assert_console(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: str, workspace_path: str) -> dict:
    console = _console(payload)
    serialized = json.dumps(console, ensure_ascii=False)
    assert console["schema_version"] == "v2.18"
    assert console["artifact_type"] == "platform_console"
    assert console["workspace_id"] == workspace_id
    assert console["codebase_id"] == codebase_id
    assert console["snapshot_id"] == snapshot_id
    assert console["source_policy"]["fact_source"] == "persisted_artifacts_only"
    assert console["summary"]["panel_count"] == 7
    assert {panel["panel_id"] for panel in console["panels"]} >= {"overview", "evidence", "architecture", "agent", "runtime", "patch", "next_actions"}
    assert console["artifact_refs"]
    assert console["next_actions"]
    statuses = {panel["status"] for panel in console["panels"]}
    assert "needs_build" in statuses or "partial" in statuses
    assert repo not in serialized
    assert workspace_path not in serialized
    return console


def test_v218_platform_console_service_view(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = PlatformConsoleService(workspace, workspace_id=workspace_id)

    console = _assert_console(
        service.build_console(codebase_id, snapshot_id=snapshot_id),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )
    assert console_payload_path(workspace, codebase_id).exists()
    assert console_html_path(workspace, codebase_id).exists()
    html = service.read_console_view(codebase_id, "html")
    assert html["content_type"] == "text/html"
    assert "<script" not in html["content"].lower()
    assert "Project Intelligence Console" in html["content"]
    assert "下一步动作" in html["content"]
    assert str(repo) not in html["content"]
    assert str(workspace) not in html["content"]
    assert console["summary"]["ready_panel_count"] >= 0


def test_v218_platform_console_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/console/build",
        json={"snapshot_id": snapshot_id},
    )
    assert http_build.status_code == 200
    http_console = _assert_console(
        _v2(http_build.json()),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/console/views/html")
    assert http_view.status_code == 200
    assert "<script" not in _view(_v2(http_view.json()))["content"].lower()

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_platform_console_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id},
        )
    )
    mcp_console = _assert_console(
        _v2(mcp_build),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert knowledge_main(["code", "platform", "console", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_console = _assert_console(
        _v2(json.loads(capsys.readouterr().out)),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert http_console["summary"] == mcp_console["summary"] == cli_console["summary"]
    assert [panel["panel_id"] for panel in http_console["panels"]] == [panel["panel_id"] for panel in cli_console["panels"]]
    assert http_console["next_actions"] == cli_console["next_actions"]
