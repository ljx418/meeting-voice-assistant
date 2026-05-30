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


@pytest.mark.asyncio
async def test_v2_codebase_mcp_tool_registered():
    pytest.importorskip("mcp")
    from data_service import mcp_stdio
    from data_service.mcp_tool_registry import all_tool_specs

    specs = all_tool_specs()
    assert "knowledge_codebase_import" in {spec["name"] for spec in specs}
    tools = await mcp_stdio.list_tools()
    assert "knowledge_codebase_import" in {tool.name for tool in tools}

