import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.overview import CodebaseOverviewService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.code_assets.trace import CodebaseTraceService


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _prepare_real_repo(workspace: Path, workspace_id: str, repo_root: Path):
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseTraceService(workspace, workspace_id=workspace_id).build_trace(asset.codebase_id, snapshot_id=snapshot_id)
    return asset.codebase_id, snapshot_id


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_path_values(payloads: list[dict], *paths: Path):
    raw = json.dumps(payloads, ensure_ascii=False)
    for path in paths:
        assert str(path) not in raw


def test_v2_project_overview_http_mcp_cli_converge_real_repo(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase7 Overview")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id = _prepare_real_repo(workspace, workspace_id, repo_root)

    overview = CodebaseOverviewService(workspace, workspace_id=workspace_id).build_overview(codebase_id, snapshot_id=snapshot_id)
    overview_path = workspace / "assets" / "codebase" / codebase_id / "overview.json"
    assert overview_path.exists()
    assert not (workspace / "lifecycle" / "sources.json").exists()
    assert overview["project_one_liner"]
    assert overview["entrypoints"]
    assert overview["public_surface_summary"]["surface_count"] > 0
    assert overview["language_stats"]["languages"]["python"]["files"] > 0
    assert overview["core_modules"]
    assert overview["storage_summary"]
    assert overview["evidence"]

    from data_service.__main__ import knowledge_main
    from data_service.mcp_build_runtime import BuildRuntime
    from data_service.mcp_dispatcher import MCPToolDispatcher
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )

    http_payload = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/overview",
        params={"snapshot_id": snapshot_id},
    ).json()
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_project_overview",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id},
        )
    )
    assert (
        knowledge_main(
            [
                "code",
                "overview",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
                "--snapshot-id",
                snapshot_id,
            ]
        )
        == 0
    )
    cli_payload = json.loads(capsys.readouterr().out)

    http_v2 = _v2(http_payload)
    mcp_v2 = _v2(mcp_payload)
    cli_v2 = _v2(cli_payload)
    assert {http_v2["ok"], mcp_v2["ok"], cli_v2["ok"]} == {True}
    assert {http_v2["snapshot_id"], mcp_v2["snapshot_id"], cli_v2["snapshot_id"]} == {snapshot_id}
    assert (
        http_v2["data"]["overview"]["public_surface_summary"]["surface_count"]
        == mcp_v2["data"]["overview"]["public_surface_summary"]["surface_count"]
        == cli_v2["data"]["overview"]["public_surface_summary"]["surface_count"]
    )
    assert http_v2["data"]["overview"]["evidence"]
    _assert_no_path_values([http_payload, mcp_payload, cli_payload], repo_root, workspace_root)
