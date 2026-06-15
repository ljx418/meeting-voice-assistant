from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.platform.persistence import mcp_tool_catalog_path, workflow_guides_path
from data_service.code_assets.platform.tool_catalog import ToolCatalogService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_tool_registry import all_tool_specs
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _catalog(payload: dict) -> dict:
    if "data" in payload and "tool_catalog" in payload["data"]:
        return payload["data"]["tool_catalog"]
    if "catalog" in payload and "workflow_guides" in payload:
        return {
            "schema_version": "v2.20",
            "artifact_type": "mcp_tool_catalog_bundle",
            "catalog": payload["catalog"],
            "workflow_guides": payload["workflow_guides"],
            "artifact_refs": payload.get("artifact_refs", []),
        }
    return payload


def _assert_catalog(payload: dict, *, workspace_id: str, codebase_id: str, repo: str, workspace_path: str) -> dict:
    catalog_bundle = _catalog(payload)
    serialized = json.dumps(catalog_bundle, ensure_ascii=False)
    assert catalog_bundle["schema_version"] == "v2.20"
    assert catalog_bundle["artifact_type"] == "mcp_tool_catalog_bundle"
    assert catalog_bundle["artifact_refs"]

    catalog = catalog_bundle["catalog"]
    guides = catalog_bundle["workflow_guides"]
    assert catalog["schema_version"] == "v2.20"
    assert catalog["artifact_type"] == "mcp_tool_catalog"
    assert catalog["workspace_id"] == workspace_id
    assert catalog["codebase_id"] == codebase_id
    assert catalog["tool_count"] == len(all_tool_specs())
    assert catalog["validation_summary"]["registry_count"] == len(all_tool_specs())
    assert catalog["validation_summary"]["catalog_count"] == catalog["tool_count"]
    assert {tool["tool_name"] for tool in catalog["tools"]} == {str(spec["name"]) for spec in all_tool_specs()}
    assert any(group["group_id"] == "platform" for group in catalog["groups"])

    assert guides["schema_version"] == "v2.20"
    assert guides["artifact_type"] == "workflow_guides"
    assert guides["validation_summary"]["guide_count"] >= 3
    assert guides["validation_summary"]["missing_tool_refs"] == []
    assert {guide["goal_id"] for guide in guides["guides"]} >= {"project_reading", "coding_task_preparation", "architecture_review"}

    project_steps = next(guide["steps"] for guide in guides["guides"] if guide["goal_id"] == "project_reading")
    assert [step["tool_name"] for step in project_steps][:3] == [
        "knowledge_codebase_snapshot",
        "knowledge_project_inventory",
        "knowledge_project_overview",
    ]
    assert all(step["status"] == "available" for step in project_steps)

    assert repo not in serialized
    assert workspace_path not in serialized
    return catalog_bundle


def test_v220_tool_catalog_service(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, _snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ToolCatalogService(workspace, workspace_id=workspace_id)

    payload = _assert_catalog(
        service.build_tool_catalog(codebase_id, all_tool_specs()),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )
    assert mcp_tool_catalog_path(workspace, codebase_id).exists()
    assert workflow_guides_path(workspace, codebase_id).exists()
    readback = _assert_catalog(
        service.read_tool_catalog(codebase_id),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )
    assert payload["catalog"]["tool_count"] == readback["catalog"]["tool_count"]


def test_v220_tool_catalog_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, _snapshot_id, repo = _prepare(tmp_path, monkeypatch)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog/build")
    assert http_build.status_code == 200
    http_catalog = _assert_catalog(
        _v2(http_build.json()),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog")
    assert http_read.status_code == 200
    _assert_catalog(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, repo=str(repo), workspace_path=str(workspace))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_platform_tool_catalog_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id},
        )
    )
    mcp_catalog = _assert_catalog(
        _v2(mcp_build),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert knowledge_main(["code", "platform", "tool-catalog", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_catalog = _assert_catalog(
        _v2(json.loads(capsys.readouterr().out)),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert http_catalog["catalog"]["validation_summary"] == mcp_catalog["catalog"]["validation_summary"]
    assert http_catalog["catalog"]["validation_summary"] == cli_catalog["catalog"]["validation_summary"]
    assert http_catalog["workflow_guides"]["validation_summary"] == cli_catalog["workflow_guides"]["validation_summary"]
