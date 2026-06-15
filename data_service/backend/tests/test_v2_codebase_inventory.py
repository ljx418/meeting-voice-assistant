import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.artifacts import (
    inventory_alignment_path,
    inventory_capabilities_path,
    inventory_summary_path,
    inventory_surfaces_path,
    read_json,
    read_jsonl,
)
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.mcp_tool_registry import all_tool_specs


FORBIDDEN_PUBLIC_KEYS = {"root_path", "workspace_path", "debug_paths"}


def _assert_no_internal_paths(payload):
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                assert key not in FORBIDDEN_PUBLIC_KEYS
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)


def _assert_no_path_values(payload, *paths: Path):
    raw = json.dumps(payload, ensure_ascii=False)
    for path in paths:
        assert str(path) not in raw


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _surface_ids(surfaces: list[dict]) -> set[str]:
    return {str(item.get("surface_id")) for item in surfaces}


def _capabilities_by_id(capabilities: list[dict]) -> dict[str, dict]:
    return {str(item.get("capability_id")): item for item in capabilities}


def test_v2_codebase_inventory_service_real_repo_artifacts_and_golden_alignment(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    registry = CodebaseRegistry(workspace, workspace_id="phase3")
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot = CodebaseSnapshotService(workspace, workspace_id="phase3").create_snapshot(asset.codebase_id)["snapshot"]
    snapshot_id = snapshot["snapshot_id"]

    sources_manifest = workspace / "lifecycle" / "sources.json"
    before_sources = sources_manifest.read_text(encoding="utf-8") if sources_manifest.exists() else None
    result = CodebaseInventoryService(workspace, workspace_id="phase3").build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    after_sources = sources_manifest.read_text(encoding="utf-8") if sources_manifest.exists() else None
    assert after_sources == before_sources

    assert inventory_surfaces_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert inventory_capabilities_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert inventory_alignment_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert inventory_summary_path(workspace, asset.codebase_id, snapshot_id).exists()

    surfaces = read_jsonl(inventory_surfaces_path(workspace, asset.codebase_id, snapshot_id))
    capabilities = read_jsonl(inventory_capabilities_path(workspace, asset.codebase_id, snapshot_id))
    alignment = read_json(inventory_alignment_path(workspace, asset.codebase_id, snapshot_id), {})
    summary = read_json(inventory_summary_path(workspace, asset.codebase_id, snapshot_id), {})

    assert result["summary"]["surface_count"] == len(surfaces) == summary["surface_count"]
    assert result["summary"]["capability_count"] == len(capabilities) == summary["capability_count"]
    assert summary["schema_version"] == "v2.0"
    assert summary["workspace_id"] == "phase3"
    assert summary["codebase_id"] == asset.codebase_id
    assert summary["snapshot_id"] == snapshot_id
    assert summary["surface_counts"]["mcp_tool"] == len(all_tool_specs())
    assert summary["surface_counts"]["http_api"] >= 7
    assert summary["surface_counts"]["cli_command"] >= 7
    assert summary["unresolved_ratio"] < 0.5
    assert all(check["passed"] for check in summary["golden_checks"].values()), summary["golden_checks"]

    ids = _surface_ids(surfaces)
    assert "http:POST:/api/workspaces/{workspace_id}/codebases" in ids
    assert "http:GET:/api/workspaces/{workspace_id}/codebases/{codebase_id}/overview" in ids
    assert "http:POST:/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack" in ids
    assert "http:POST:/api/workspaces/{workspace_id}/query" in ids
    assert "http:GET:/api/workspaces/{workspace_id}/graph/neighbors" in ids
    assert "http:POST:/api/v1/knowledge/query" in ids
    assert "mcp:knowledge_project_overview" in ids
    assert "mcp:knowledge_agent_context_pack" in ids
    assert "mcp:knowledge_project_inventory" in ids
    assert "mcp:knowledge_source_import" in ids
    assert "cli:knowledge code overview" in ids
    assert "cli:knowledge code context-pack" in ids
    assert "cli:knowledge code inventory" in ids
    assert "cli:knowledge source import" in ids

    by_capability = _capabilities_by_id(capabilities)
    for capability_id in [
        "agent_context_pack",
        "codebase_import",
        "codebase_snapshot",
        "project_overview",
        "source_import",
        "query",
        "build",
        "quality",
        "graph",
    ]:
        assert capability_id in by_capability
        assert by_capability[capability_id]["capability_id"] in alignment["capabilities"]
    assert {"http", "mcp", "cli"} <= set(alignment["capabilities"]["agent_context_pack"])
    assert {"http", "mcp", "cli"} <= set(alignment["capabilities"]["project_overview"])
    assert {"http", "mcp", "cli"} <= set(alignment["capabilities"]["query"])
    assert alignment["capabilities"]["query"]["http"]
    assert alignment["capabilities"]["query"]["mcp"]
    assert alignment["capabilities"]["query"]["cli"]

    sampled = [
        item
        for item in surfaces
        if item["surface_id"]
        in {
            "http:POST:/api/workspaces/{workspace_id}/codebases",
            "http:POST:/api/workspaces/{workspace_id}/query",
            "mcp:knowledge_project_inventory",
            "mcp:knowledge_source_import",
            "cli:knowledge code inventory",
            "cli:knowledge source import",
        }
    ]
    assert len(sampled) == 6
    for item in sampled:
        assert item["source_file"]
        assert item["line_range"] and item["line_range"][0] >= 1
        assert item["confidence"] >= 0.7

    _assert_no_internal_paths(result)
    _assert_no_path_values(result, repo_root, workspace)


def test_v2_codebase_inventory_does_not_inject_current_mcp_registry_for_external_repo(tmp_path, monkeypatch):
    repo_root = tmp_path / "external_repo"
    repo_root.mkdir()
    (repo_root / "README.md").write_text("# External Repo\n", encoding="utf-8")
    (repo_root / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    registry = CodebaseRegistry(workspace, workspace_id="external")
    asset = registry.import_codebase(path=str(repo_root), codebase_id="external_repo")["asset"]
    snapshot = CodebaseSnapshotService(workspace, workspace_id="external").create_snapshot(asset.codebase_id)["snapshot"]
    snapshot_id = snapshot["snapshot_id"]

    result = CodebaseInventoryService(workspace, workspace_id="external").build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    surfaces = read_jsonl(inventory_surfaces_path(workspace, asset.codebase_id, snapshot_id))
    assert result["summary"]["surface_counts"].get("mcp_tool", 0) == 0
    assert not any(str(item.get("surface_id", "")).startswith("mcp:knowledge_") for item in surfaces)
    _assert_no_internal_paths(result)
    _assert_no_path_values(result, repo_root, workspace)


def test_v2_codebase_inventory_http_mcp_cli_real_repo_and_failure_paths(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase3 Inventory")
    imported = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo_root)})
    assert imported.status_code == 200
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]

    before_snapshot = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory")
    assert before_snapshot.status_code == 404
    assert "snapshot" in before_snapshot.json()["detail"].lower()

    snapshot = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots", json={})
    assert snapshot.status_code == 200
    snapshot_id = snapshot.json()["data"]["snapshot"]["snapshot_id"]

    missing_inventory = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory")
    assert missing_inventory.status_code == 404
    assert "Inventory not found" in missing_inventory.json()["detail"]

    built = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory", json={})
    assert built.status_code == 200
    built_payload = built.json()
    assert built_payload["status"] == "ok"
    assert built_payload["data"]["inventory"]["snapshot_id"] == snapshot_id
    assert all(check["passed"] for check in built_payload["data"]["inventory"]["summary"]["golden_checks"].values())
    _assert_no_internal_paths(built_payload)
    _assert_no_path_values(built_payload, repo_root, workspace_root)

    read_back = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory")
    assert read_back.status_code == 200
    assert read_back.json()["data"]["inventory"]["summary"]["surface_count"] == built_payload["data"]["inventory"]["summary"]["surface_count"]

    mcp_surfaces = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces", params={"surface_type": "mcp_tool"})
    assert mcp_surfaces.status_code == 200
    assert mcp_surfaces.json()["data"]["count"] == len(all_tool_specs())
    assert "mcp:knowledge_project_inventory" in {item["surface_id"] for item in mcp_surfaces.json()["data"]["items"]}

    invalid_type = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces", params={"surface_type": "not_real"})
    assert invalid_type.status_code == 200
    assert invalid_type.json()["status"] == "blocked"
    assert invalid_type.json()["data"]["error"]["code"] == "invalid_surface_type"

    capabilities = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/capabilities")
    assert capabilities.status_code == 200
    assert "query" in {item["capability_id"] for item in capabilities.json()["data"]["items"]}

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
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_project_inventory",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id, "build": False},
        )
    )
    assert mcp_payload["status"] == "ok"
    assert mcp_payload["data"]["inventory"]["snapshot_id"] == snapshot_id
    assert mcp_payload["data"]["inventory"]["summary"]["surface_count"] == built_payload["data"]["inventory"]["summary"]["surface_count"]
    _assert_no_internal_paths(mcp_payload)
    _assert_no_path_values(mcp_payload, repo_root, workspace_root)

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
    assert cli_payload["data"]["inventory"]["snapshot_id"] == snapshot_id
    assert cli_payload["data"]["inventory"]["summary"]["surface_count"] == built_payload["data"]["inventory"]["summary"]["surface_count"]
    _assert_no_internal_paths(cli_payload)
    _assert_no_path_values(cli_payload, repo_root, workspace_root)
