from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_v2_codebase_mcp_import_real_repo(tmp_path, monkeypatch):
    from data_service.mcp_build_runtime import BuildRuntime
    from data_service.mcp_dispatcher import MCPToolDispatcher
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )

    payload = await dispatcher.call_tool(
        "knowledge_codebase_import",
        {"workspace_id": "phase1", "path": str(repo_root), "metadata": {"caller": "mcp"}},
    )
    assert payload["status"] == "ok"
    assert payload["workspace_id"] == "phase1"
    assert payload["data"]["codebase"]["codebase_id"] == "codebase_data_service"
    assert payload["data"]["codebase"]["metadata"] == {"caller": "mcp"}
    assert payload["artifact_refs"][0]["artifact_ref"] == "codebase://codebase_data_service"
    assert "root_path" not in str(payload)

    duplicate = await dispatcher.call_tool("knowledge_codebase_import", {"workspace_id": "phase1", "path": str(repo_root)})
    assert duplicate["data"]["created"] is False

    listed = await dispatcher.call_tool("knowledge_codebase_list", {"workspace_id": "phase1"})
    assert [item["codebase_id"] for item in listed["data"]["items"]] == ["codebase_data_service"]

    described = await dispatcher.call_tool(
        "knowledge_codebase_describe",
        {"workspace_id": "phase1", "codebase_id": "codebase_data_service"},
    )
    assert described["data"]["codebase"]["codebase_id"] == "codebase_data_service"

    archived = await dispatcher.call_tool(
        "knowledge_codebase_archive",
        {"workspace_id": "phase1", "codebase_id": "codebase_data_service", "reason": "done"},
    )
    assert archived["data"]["codebase"]["status"] == "archived"
    assert archived["data"]["codebase"]["archive_reason"] == "done"

    active_only = await dispatcher.call_tool("knowledge_codebase_list", {"workspace_id": "phase1"})
    assert active_only["data"]["items"] == []

    include_archived = await dispatcher.call_tool(
        "knowledge_codebase_list",
        {"workspace_id": "phase1", "include_archived": True},
    )
    assert [item["codebase_id"] for item in include_archived["data"]["items"]] == ["codebase_data_service"]


@pytest.mark.asyncio
async def test_v2_codebase_mcp_blocks_bad_path_without_leaking_paths(tmp_path, monkeypatch):
    from data_service.mcp_build_runtime import BuildRuntime
    from data_service.mcp_dispatcher import MCPToolDispatcher
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    repo_root = Path(__file__).resolve().parents[2]
    outside = tmp_path / "outside"
    outside.mkdir()
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )

    payload = await dispatcher.call_tool("knowledge_codebase_import", {"workspace_id": "phase1", "path": str(outside)})
    assert payload["status"] == "blocked"
    assert payload["data"]["error"]["code"] == "path_not_allowed"
    raw = str(payload)
    assert str(outside) not in raw
    assert str(repo_root) not in raw


@pytest.mark.asyncio
async def test_v2_codebase_mcp_tool_registered():
    pytest.importorskip("mcp")
    from data_service import mcp_stdio
    from data_service.mcp_tool_registry import all_tool_specs

    specs = all_tool_specs()
    assert {
        "knowledge_codebase_import",
        "knowledge_codebase_list",
        "knowledge_codebase_snapshot",
        "knowledge_codebase_describe",
        "knowledge_codebase_archive",
        "knowledge_project_overview",
        "knowledge_agent_context_pack",
    } <= {spec["name"] for spec in specs}
    tools = await mcp_stdio.list_tools()
    assert {
        "knowledge_codebase_import",
        "knowledge_codebase_list",
        "knowledge_codebase_snapshot",
        "knowledge_codebase_describe",
        "knowledge_codebase_archive",
        "knowledge_project_overview",
        "knowledge_agent_context_pack",
    } <= {tool.name for tool in tools}
