import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.code_assets.trace import CodebaseTraceService


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _assert_no_path_values(payloads: list[dict], *paths: Path):
    raw = json.dumps(payloads, ensure_ascii=False)
    for path in paths:
        assert str(path) not in raw


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _prepare_real_repo(workspace: Path, workspace_id: str, repo_root: Path):
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseTraceService(workspace, workspace_id=workspace_id).build_trace(asset.codebase_id, snapshot_id=snapshot_id)
    return asset.codebase_id, snapshot_id


def test_v2_codebase_http_mcp_cli_read_envelopes_converge_real_repo(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase6 Convergence")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id = _prepare_real_repo(workspace, workspace_id, repo_root)

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

    http_inventory = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory",
        params={"snapshot_id": snapshot_id},
    ).json()
    mcp_inventory = asyncio.run(
        dispatcher.call_tool(
            "knowledge_project_inventory",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id, "build": False},
        )
    )
    assert (
        knowledge_main(
            [
                "code",
                "inventory",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
                "--snapshot-id",
                snapshot_id,
                "--read-only",
            ]
        )
        == 0
    )
    cli_inventory = json.loads(capsys.readouterr().out)

    http_v2 = _v2(http_inventory)
    mcp_v2 = _v2(mcp_inventory)
    cli_v2 = _v2(cli_inventory)
    assert http_v2["ok"] is True
    assert mcp_v2["ok"] is True
    assert cli_v2["ok"] is True
    assert {http_v2["schema_version"], mcp_v2["schema_version"], cli_v2["schema_version"]} == {"v2.0"}
    assert {http_v2["workspace_id"], mcp_v2["workspace_id"], cli_v2["workspace_id"]} == {workspace_id}
    assert {http_v2["codebase_id"], mcp_v2["codebase_id"], cli_v2["codebase_id"]} == {codebase_id}
    assert {http_v2["snapshot_id"], mcp_v2["snapshot_id"], cli_v2["snapshot_id"]} == {snapshot_id}
    assert (
        http_v2["data"]["inventory"]["summary"]["surface_count"]
        == mcp_v2["data"]["inventory"]["summary"]["surface_count"]
        == cli_v2["data"]["inventory"]["summary"]["surface_count"]
    )
    assert http_v2["artifact_refs"] == mcp_v2["artifact_refs"] == cli_v2["artifact_refs"]

    http_symbols = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols",
        params={"snapshot_id": snapshot_id, "query": "CodebaseInventoryService", "limit": 5},
    ).json()
    mcp_symbols = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_symbol_search",
            {
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "query": "CodebaseInventoryService",
                "build": False,
            },
        )
    )
    assert _v2(http_symbols)["data"]["items"][0]["symbol_id"] == _v2(mcp_symbols)["data"]["symbol_index"]["symbols"][0]["symbol_id"]

    http_trace = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/codebase_import",
        params={"snapshot_id": snapshot_id},
    ).json()
    mcp_trace = asyncio.run(
        dispatcher.call_tool(
            "knowledge_public_surface_trace",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id, "capability": "codebase_import"},
        )
    )
    assert _v2(http_trace)["snapshot_id"] == snapshot_id
    assert _v2(mcp_trace)["snapshot_id"] == snapshot_id
    assert {item["surface_id"] for item in _v2(http_trace)["data"]["trace"]["surfaces"]} == {
        item["surface_id"] for item in _v2(mcp_trace)["data"]["trace"]["surfaces"]
    }
    _assert_no_path_values([http_inventory, mcp_inventory, cli_inventory, http_symbols, mcp_symbols, http_trace, mcp_trace], repo_root, workspace_root)


def test_v2_codebase_error_envelopes_converge_for_missing_inventory(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase6 Errors")
    imported = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo_root)})
    assert imported.status_code == 200
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]
    snapshot = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots", json={})
    assert snapshot.status_code == 200
    snapshot_id = snapshot.json()["data"]["snapshot"]["snapshot_id"]

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
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory",
        params={"snapshot_id": snapshot_id},
    ).json()
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_project_inventory",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id, "build": False},
        )
    )
    assert (
        knowledge_main(
            [
                "code",
                "inventory",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
                "--snapshot-id",
                snapshot_id,
                "--read-only",
            ]
        )
        == 0
    )
    cli_payload = json.loads(capsys.readouterr().out)

    http_v2 = _v2(http_payload)
    mcp_v2 = _v2(mcp_payload)
    cli_v2 = _v2(cli_payload)
    assert http_v2["ok"] is False
    assert mcp_v2["ok"] is False
    assert cli_v2["ok"] is False
    assert {http_v2["error"]["code"], mcp_v2["error"]["code"], cli_v2["error"]["code"]} == {"INVENTORY_NOT_FOUND"}
    assert {http_v2["workspace_id"], mcp_v2["workspace_id"], cli_v2["workspace_id"]} == {workspace_id}
    assert {http_v2["codebase_id"], mcp_v2["codebase_id"], cli_v2["codebase_id"]} == {codebase_id}
    assert {http_v2["snapshot_id"], mcp_v2["snapshot_id"], cli_v2["snapshot_id"]} == {snapshot_id}
    assert http_v2["next_actions"]
    assert mcp_v2["next_actions"]
    assert cli_v2["next_actions"]
    _assert_no_path_values([http_payload, mcp_payload, cli_payload], repo_root, workspace_root)
