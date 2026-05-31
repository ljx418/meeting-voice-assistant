import asyncio
import json
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.artifacts import (
    read_jsonl,
    snapshot_files_path,
    snapshot_json_path,
    snapshot_stats_path,
    snapshot_warnings_path,
)
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService


FORBIDDEN_PUBLIC_KEYS = {"root_path", "path", "paths", "workspace_path", "debug_paths"}


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


def _write_minimal_repo(root: Path) -> None:
    root.mkdir(parents=True)
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")
    (root / "src" / "token_service.py").write_text("def issue_token():\n    return 'opaque'\n", encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_app.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")


def test_v2_codebase_snapshot_service_real_repo_artifacts_and_no_source_registry(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    registry = CodebaseRegistry(workspace, workspace_id="phase2")
    asset = registry.import_codebase(path=str(repo_root))["asset"]

    service = CodebaseSnapshotService(workspace, workspace_id="phase2")
    result = service.create_snapshot(asset.codebase_id)
    snapshot = result["snapshot"]

    assert snapshot["schema_version"] == "v2.0"
    assert snapshot["workspace_id"] == "phase2"
    assert snapshot["codebase_id"] == "codebase_data_service"
    assert snapshot["snapshot_id"].startswith("snap_")
    assert snapshot["stats"]["file_count"] > 0
    assert snapshot["stats"]["languages"]["python"]["files"] > 0
    assert snapshot["stats"]["languages"]["markdown"]["files"] > 0
    assert "README.md" in snapshot["important_paths"]["readme"]
    assert any(path.endswith("__main__.py") for path in snapshot["important_paths"]["entrypoints"])
    assert (workspace / "lifecycle" / "sources.json").exists() is False

    snapshot_id = snapshot["snapshot_id"]
    assert snapshot_json_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert snapshot_files_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert snapshot_stats_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert snapshot_warnings_path(workspace, asset.codebase_id, snapshot_id).exists()
    files = read_jsonl(snapshot_files_path(workspace, asset.codebase_id, snapshot_id))
    assert any(row["path"] == "backend/data_service/code_assets/registry.py" and row["included"] for row in files)
    assert not any(row["path"].startswith(".git/") for row in files)
    assert not any(row["path"].startswith("workspace/assets/codebase/") for row in files)

    duplicate = service.create_snapshot(asset.codebase_id)
    assert duplicate["snapshot"]["snapshot_id"] == snapshot_id


def test_v2_codebase_snapshot_changes_with_content_and_skips_sensitive_self_artifacts(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    _write_minimal_repo(repo)
    (repo / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
    (repo / "workspace" / "assets" / "codebase" / "generated").mkdir(parents=True)
    (repo / "workspace" / "assets" / "codebase" / "generated" / "snapshot.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    workspace = tmp_path / "managed" / "phase2"
    registry = CodebaseRegistry(workspace, workspace_id="phase2")
    asset = registry.import_codebase(path=str(repo), codebase_id="demo")["asset"]
    service = CodebaseSnapshotService(workspace, workspace_id="phase2")

    first = service.create_snapshot(asset.codebase_id)
    first_id = first["snapshot"]["snapshot_id"]
    files = read_jsonl(snapshot_files_path(workspace, asset.codebase_id, first_id))
    warnings = read_jsonl(snapshot_warnings_path(workspace, asset.codebase_id, first_id))

    assert any(row["path"] == ".env" and row["skip_reason"] == "SENSITIVE_SKIPPED" for row in files)
    assert any(row["code"] == "SENSITIVE_SKIPPED" and row["path"] == ".env" for row in warnings)
    assert not any(row["path"].startswith("workspace/assets/codebase/") for row in files)

    (repo / "src" / "app.py").write_text("def hello():\n    return 'changed'\n", encoding="utf-8")
    second = service.create_snapshot(asset.codebase_id)
    assert second["snapshot"]["snapshot_id"] != first_id
    second_files = read_jsonl(snapshot_files_path(workspace, asset.codebase_id, second["snapshot"]["snapshot_id"]))
    changed_record = next(row for row in second_files if row["path"] == "src/app.py")
    assert changed_record["sha256"] != next(row for row in files if row["path"] == "src/app.py")["sha256"]


def test_v2_codebase_snapshot_stays_stable_with_repo_local_workspace_artifacts(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    _write_minimal_repo(repo)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    workspace = repo / "workspace" / "phase2"
    registry = CodebaseRegistry(workspace, workspace_id="phase2")
    asset = registry.import_codebase(path=str(repo), codebase_id="demo")["asset"]
    service = CodebaseSnapshotService(workspace, workspace_id="phase2")

    first = service.create_snapshot(asset.codebase_id)
    second = service.create_snapshot(asset.codebase_id)
    assert second["snapshot"]["snapshot_id"] == first["snapshot"]["snapshot_id"]

    files = read_jsonl(snapshot_files_path(workspace, asset.codebase_id, first["snapshot"]["snapshot_id"]))
    assert any(row["path"] == "src/token_service.py" and row["included"] for row in files)
    assert not any(row["path"].startswith("workspace/phase2/assets/codebase/") for row in files)


def test_v2_codebase_snapshot_list_is_latest_first_and_unknown_codebase_is_controlled(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    _write_minimal_repo(repo)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    workspace = tmp_path / "workspace"
    registry = CodebaseRegistry(workspace, workspace_id="phase2")
    asset = registry.import_codebase(path=str(repo), codebase_id="demo")["asset"]
    service = CodebaseSnapshotService(workspace, workspace_id="phase2")

    first = service.create_snapshot(asset.codebase_id)
    (repo / "src" / "app.py").write_text("def hello():\n    return 'latest'\n", encoding="utf-8")
    second = service.create_snapshot(asset.codebase_id)

    snapshots = service.list_snapshots(asset.codebase_id)
    assert [item["snapshot_id"] for item in snapshots[:2]] == [second["snapshot"]["snapshot_id"], first["snapshot"]["snapshot_id"]]
    try:
        service.list_snapshots("missing")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Unknown codebase should not return an empty snapshot list")


def test_v2_codebase_snapshot_rejects_invalid_scan_policy_and_unknown_http_codebase(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase2 Failure Paths")

    unknown = client.post(f"/api/workspaces/{workspace_id}/codebases/missing/snapshots", json={})
    assert unknown.status_code == 404
    assert "Unknown codebase_id" in unknown.json()["detail"]

    imported = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo_root)})
    assert imported.status_code == 200
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]

    invalid = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots",
        json={"scan_policy": {"include": "*.py"}},
    )
    assert invalid.status_code == 200
    assert invalid.json()["status"] == "blocked"
    assert invalid.json()["data"]["error"]["code"] == "invalid_scan_policy"


def test_v2_codebase_snapshot_http_mcp_cli_real_repo(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase2 Snapshot")
    imported = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo_root)})
    assert imported.status_code == 200
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]

    created = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots", json={})
    assert created.status_code == 200
    payload = created.json()
    assert payload["status"] == "ok"
    snapshot_id = payload["data"]["snapshot"]["snapshot_id"]
    assert payload["data"]["snapshot"]["stats"]["file_count"] > 0
    assert payload["artifact_refs"][0]["artifact_ref"] == f"snapshot://{codebase_id}/{snapshot_id}"
    _assert_no_internal_paths(payload)
    _assert_no_path_values(payload, repo_root, workspace_root)

    listed = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots")
    assert listed.status_code == 200
    assert [item["snapshot_id"] for item in listed.json()["data"]["items"]] == [snapshot_id]
    described = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots/{snapshot_id}")
    assert described.status_code == 200
    assert described.json()["data"]["snapshot"]["snapshot_id"] == snapshot_id

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
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_codebase_snapshot", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert mcp_payload["data"]["snapshot"]["snapshot_id"] == snapshot_id

    assert (
        knowledge_main(
            [
                "code",
                "snapshot",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
            ]
        )
        == 0
    )
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["data"]["snapshot"]["snapshot_id"] == snapshot_id
    _assert_no_internal_paths(cli_payload)
    _assert_no_path_values(cli_payload, repo_root, workspace_root)
