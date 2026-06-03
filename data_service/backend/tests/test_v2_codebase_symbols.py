import asyncio
import json
from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.artifacts import imports_path, read_json, read_jsonl, symbol_summary_path, symbols_path
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService


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


def _write_symbol_fixture(repo: Path) -> None:
    repo.mkdir(parents=True)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "pkg" / "module.py").write_text(
        "\n".join(
            [
                "import json as json_lib",
                "from .helper import value",
                "",
                "class Alpha:",
                "    def run(self, item: str) -> str:",
                "        def nested(value):",
                "            return value",
                "        return nested(item)",
                "",
                "class Beta:",
                "    def run(self):",
                "        return value",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "pkg" / "helper.py").write_text("value = 'ok'\n", encoding="utf-8")
    (repo / "pkg" / "bad.py").write_text("def broken(:\n", encoding="utf-8")


def test_v2_codebase_symbols_service_real_repo_artifacts_and_golden_symbols(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    registry = CodebaseRegistry(workspace, workspace_id="phase4")
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot = CodebaseSnapshotService(workspace, workspace_id="phase4").create_snapshot(asset.codebase_id)["snapshot"]
    snapshot_id = snapshot["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id="phase4").build_inventory(asset.codebase_id, snapshot_id=snapshot_id)

    sources_manifest = workspace / "lifecycle" / "sources.json"
    before_sources = sources_manifest.read_text(encoding="utf-8") if sources_manifest.exists() else None
    result = CodebaseSymbolIndexService(workspace, workspace_id="phase4").build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    after_sources = sources_manifest.read_text(encoding="utf-8") if sources_manifest.exists() else None
    assert after_sources == before_sources

    assert symbols_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert imports_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert symbol_summary_path(workspace, asset.codebase_id, snapshot_id).exists()
    symbols = read_jsonl(symbols_path(workspace, asset.codebase_id, snapshot_id))
    imports = read_jsonl(imports_path(workspace, asset.codebase_id, snapshot_id))
    summary = read_json(symbol_summary_path(workspace, asset.codebase_id, snapshot_id), {})

    assert result["summary"]["symbol_count"] == len(symbols) == summary["symbol_count"]
    assert result["summary"]["import_count"] == len(imports) == summary["import_count"]
    assert summary["schema_version"] == "v2.0"
    assert summary["symbol_count"] > 100
    assert summary["import_count"] > 20
    assert summary["symbols_by_kind"]["module"] > 0
    assert summary["symbols_by_kind"]["class"] > 0
    assert summary["symbols_by_kind"]["function"] > 0
    assert summary["symbols_by_kind"]["method"] > 0
    assert all(check["passed"] for check in summary["golden_checks"].values()), summary["golden_checks"]

    by_name = {item["qualified_name"]: item for item in symbols}
    expected_symbol = by_name["backend.data_service.code_assets.inventory.CodebaseInventoryService"]
    assert expected_symbol["kind"] == "class"
    assert expected_symbol["line_range"][0] >= 1
    source_lines = (repo_root / expected_symbol["path"]).read_text(encoding="utf-8").splitlines()
    assert source_lines[expected_symbol["line_range"][0] - 1].strip().startswith("class CodebaseInventoryService")

    function_symbol = by_name["backend.data_service.cli_code.run_code_command"]
    assert function_symbol["signature"].startswith("run_code_command(")
    assert function_symbol["symbol_id"] == "py:function:backend.data_service.cli_code.run_code_command"

    assert any(
        item["from_module"] == "backend.data_service.mcp_code_tools"
        and item["to_module"] == "backend.data_service.code_assets.inventory"
        for item in imports
    )

    second = CodebaseSymbolIndexService(workspace, workspace_id="phase4").build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    assert {item["symbol_id"] for item in second["symbols"]} == {item["symbol_id"] for item in symbols}


def test_v2_codebase_symbols_syntax_error_isolated_and_duplicate_methods_do_not_collide(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    _write_symbol_fixture(repo)
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    registry = CodebaseRegistry(workspace, workspace_id="phase4")
    asset = registry.import_codebase(path=str(repo), codebase_id="fixture")["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id="phase4").create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    result = CodebaseSymbolIndexService(workspace, workspace_id="phase4").build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    symbols = result["symbols"]
    summary = result["summary"]

    assert summary["syntax_error_count"] == 1
    assert any(warning["path"] == "pkg/bad.py" and warning["code"] == "SYNTAX_ERROR" for warning in summary["warnings"])
    ids = {item["symbol_id"] for item in symbols}
    assert "py:method:pkg.module.Alpha.run" in ids
    assert "py:method:pkg.module.Beta.run" in ids
    assert "py:function:pkg.module.Alpha.run.<locals>.nested" in ids


def test_v2_codebase_symbols_http_mcp_cli_real_repo(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase4 Symbols")
    imported = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo_root)})
    assert imported.status_code == 200
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]
    snapshot = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots", json={})
    assert snapshot.status_code == 200
    snapshot_id = snapshot.json()["data"]["snapshot"]["snapshot_id"]
    assert client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory", json={}).status_code == 200

    missing = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols", params={"query": "CodebaseInventoryService"})
    assert missing.status_code == 404
    assert "Symbol index not found" in missing.json()["detail"]

    built = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols", json={})
    assert built.status_code == 200
    built_payload = built.json()
    assert built_payload["status"] == "ok"
    assert built_payload["data"]["symbol_index"]["snapshot_id"] == snapshot_id
    assert all(check["passed"] for check in built_payload["data"]["symbol_index"]["summary"]["golden_checks"].values())
    _assert_no_internal_paths(built_payload)
    _assert_no_path_values(built_payload, repo_root, workspace_root)

    searched = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols",
        params={"query": "CodebaseInventoryService", "limit": 5},
    )
    assert searched.status_code == 200
    items = searched.json()["data"]["items"]
    assert items[0]["qualified_name"] == "backend.data_service.code_assets.inventory.CodebaseInventoryService"
    assert "source_file" in items[0]
    assert "path" not in items[0]
    symbol_id = items[0]["symbol_id"]

    described = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols/{quote(symbol_id, safe='')}")
    assert described.status_code == 200
    assert described.json()["data"]["symbol"]["symbol_id"] == symbol_id

    imports = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/imports")
    assert imports.status_code == 200
    assert any(item["from_module"] == "backend.data_service.mcp_code_tools" for item in imports.json()["data"]["items"])

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
    assert mcp_payload["status"] == "ok"
    assert mcp_payload["data"]["symbol_index"]["symbols"][0]["qualified_name"] == "backend.data_service.code_assets.inventory.CodebaseInventoryService"
    _assert_no_path_values(mcp_payload, repo_root, workspace_root)

    assert (
        knowledge_main(
            [
                "code",
                "symbols",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
                "--snapshot-id",
                snapshot_id,
                "--query",
                "CodebaseInventoryService",
            ]
        )
        == 0
    )
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["data"]["symbol_index"]["symbols"][0]["qualified_name"] == "backend.data_service.code_assets.inventory.CodebaseInventoryService"
    _assert_no_path_values(cli_payload, repo_root, workspace_root)
