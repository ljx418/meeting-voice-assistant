import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import (
    architecture_closure_audit_report_v245_path,
    architecture_no_hardcode_audit_v245_path,
    architecture_real_repo_regression_matrix_v245_path,
    architecture_taxonomy_registry_v245_path,
)
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_repo(repo: Path) -> None:
    files = {
        "README.md": "# Generic Architecture Project\n",
        "docs/architecture.md": "# Target Architecture\n\n- Profile terms stay in profile artifacts.\n",
        "src/main.py": "def main():\n    return True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V45 Profile Regression")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, snapshot_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_payload(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.45_profile_taxonomy_regression"
    assert payload["workspace_id"] == workspace_id
    assert payload["codebase_id"] == codebase_id
    assert payload["snapshot_id"] == snapshot_id
    assert payload["profile"]["profile_id"]
    assert payload["taxonomy_registry"]["architecture_terms"]
    assert payload["real_repo_regression_matrix"]["projects"]
    assert payload["no_hardcode_audit"]["status"] == "passed"
    assert payload["no_hardcode_audit"]["findings"] == []
    assert payload["closure_audit_report"]["content"]
    assert payload["artifact_refs"]
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v45_profile_taxonomy_regression_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    projects = [
        {"name": "data_service", "exists": True, "artifact_refs": [{"type": "test", "artifact_ref": "artifact://data_service"}], "test_commands": ["pytest focused"]},
        {"name": "harness_fixture", "exists": True, "artifact_refs": [{"type": "test", "artifact_ref": "artifact://harness"}], "test_commands": ["pytest harness"]},
        {"name": "codex_fixture", "exists": False, "path": str(tmp_path / "missing-codex"), "artifact_refs": [], "test_commands": []},
    ]

    payload = service.build_profile_taxonomy_regression_v245(codebase_id, snapshot_id=snapshot_id, regression_projects=projects)
    _assert_payload(payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)
    assert payload["real_repo_regression_matrix"]["summary"]["structured_unavailable_count"] == 1
    assert architecture_taxonomy_registry_v245_path(workspace, codebase_id).exists()
    assert architecture_real_repo_regression_matrix_v245_path(workspace, codebase_id).exists()
    assert architecture_no_hardcode_audit_v245_path(workspace, codebase_id).exists()
    assert architecture_closure_audit_report_v245_path(workspace, codebase_id).exists()

    read_payload = service.read_profile_taxonomy_regression_v245(codebase_id)
    _assert_payload(read_payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    build_data = _v2(http_build.json())["data"]["profile_taxonomy_regression"]
    assert build_data["profile"]["profile_id"]

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression")
    assert http_read.status_code == 200
    read_data = _v2(http_read.json())["data"]["profile_taxonomy_regression"]
    assert read_data["no_hardcode_audit"]["status"] == "passed"

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_profile_regression_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id}))
    assert _v2(mcp_build)["data"]["profile_taxonomy_regression"]["no_hardcode_audit"]["status"] == "passed"
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_profile_regression", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["profile_taxonomy_regression"]["profile"]["profile_id"]

    assert knowledge_main(["code", "architecture", "profile-regression-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--snapshot-id", snapshot_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    assert _v2(cli_build)["data"]["profile_taxonomy_regression"]["taxonomy_registry"]["risk_labels"]
    assert knowledge_main(["code", "architecture", "profile-regression", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["profile_taxonomy_regression"]["no_hardcode_audit"]["findings"] == []


def test_v45_profile_regression_missing_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Missing build\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V45 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/v2_45/profile-regression")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_PROFILE_TAXONOMY_REGRESSION_NOT_BUILT"
