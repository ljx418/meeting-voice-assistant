import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.language_provider_v2 import language_provider_status_path, reference_facts_path, symbol_facts_path
from data_service.code_assets.architecture.service import ArchitectureService
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
        "backend/app.py": """import os
from backend.services.user_service import UserService


class App:
    def __init__(self):
        self.service = UserService()


def create_app():
    return App()
""",
        "backend/services/user_service.py": """from pathlib import Path


class UserService:
    def list_users(self):
        return []


async def load_user(user_id: str):
    return {"id": user_id}
""",
        "backend/bad_syntax.py": "def broken(:\n    pass\n",
        "frontend/src/api/client.ts": """import axios from 'axios'

export function loadUsers() {
  return axios.get('/api/users')
}

export const clientName = 'fixture'
""",
        "frontend/src/main.js": """const api = require('./api/client')

export function boot() {
  return api.loadUsers()
}
""",
        "README.md": "# Fixture\n",
        "pyproject.toml": "[project]\nname = 'fixture'\n",
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
    workspace_id = _create_workspace(client, "V40 Language Providers")
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


def _assert_line_ranges_exist(repo: Path, facts: list[dict], *, sample_limit: int = 12) -> None:
    assert facts
    for fact in facts[:sample_limit]:
        rel = fact["path"]
        start, end = fact["line_range"]
        lines = (repo / rel).read_text(encoding="utf-8", errors="replace").splitlines()
        assert 1 <= start <= end <= max(1, len(lines))
        assert "\n".join(lines[start - 1 : end]).strip()


def _statuses(payload: dict) -> dict[tuple[str, str], dict]:
    return {(item["language"], item["provider"]): item for item in payload["provider_status"]}


def _assert_language_provider_payload(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.40_language_provider"
    assert payload["workspace_id"] == workspace_id
    assert payload["codebase_id"] == codebase_id
    assert payload["snapshot_id"] == snapshot_id
    statuses = _statuses(payload)
    assert statuses[("python", "ast")]["status"] == "accepted"
    assert statuses[("typescript/javascript", "baseline_lexical")]["status"] == "accepted"
    assert statuses[("multi", "tree_sitter")]["status"] == "provider_unavailable"
    assert statuses[("multi", "lsp")]["status"] == "provider_unavailable"
    assert any(warning["code"] == "PYTHON_SYNTAX_ERROR" and warning["path"] == "backend/bad_syntax.py" for warning in statuses[("python", "ast")]["warnings"])
    assert payload["summary"]["accepted_provider_count"] >= 2
    assert payload["summary"]["symbol_fact_count"] >= 4
    assert payload["summary"]["reference_fact_count"] >= 3
    assert any(fact["qualified_name"].endswith("create_app") and fact["provider"] == "ast" for fact in payload["symbol_facts"])
    assert any(fact["path"] == "frontend/src/api/client.ts" and fact["provider"] == "baseline_lexical" and fact["needs_review"] for fact in payload["symbol_facts"])
    assert any(fact["target"] == "axios" and fact["provider"] == "baseline_lexical" and fact["needs_review"] for fact in payload["reference_facts"])
    assert all(not Path(fact["path"]).is_absolute() for fact in payload["symbol_facts"] + payload["reference_facts"])
    assert all(fact["evidence_refs"] for fact in payload["symbol_facts"] + payload["reference_facts"])
    _assert_line_ranges_exist(repo, payload["symbol_facts"])
    _assert_line_ranges_exist(repo, payload["reference_facts"])
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v40_language_provider_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)

    payload = service.build_language_provider_facts(codebase_id, snapshot_id=snapshot_id)
    _assert_language_provider_payload(payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)
    assert language_provider_status_path(workspace, codebase_id).exists()
    assert symbol_facts_path(workspace, codebase_id).exists()
    assert reference_facts_path(workspace, codebase_id).exists()

    read_payload = service.read_language_provider_facts(codebase_id)
    _assert_language_provider_payload(read_payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-providers/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    build_data = _v2(http_build.json())["data"]["language_providers"]
    assert build_data["summary"]["symbol_fact_count"] == len(payload["symbol_facts"])
    assert build_data["symbol_facts"]["total"] == len(payload["symbol_facts"])
    _assert_no_absolute_path(build_data, repo, workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-providers")
    assert http_read.status_code == 200
    read_data = _v2(http_read.json())["data"]["language_providers"]
    assert read_data["summary"]["reference_fact_count"] == len(payload["reference_facts"])
    assert read_data["reference_facts"]["total"] == len(payload["reference_facts"])
    assert read_data["artifact_refs"]
    _assert_no_absolute_path(read_data, repo, workspace_root)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_language_providers_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id}))
    assert _v2(mcp_build)["data"]["language_providers"]["summary"]["symbol_fact_count"] == len(payload["symbol_facts"])
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_language_providers", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["language_providers"]["summary"]["reference_fact_count"] == len(payload["reference_facts"])

    assert knowledge_main(["code", "architecture", "language-providers", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["language_providers"]["summary"]["symbol_fact_count"] == len(payload["symbol_facts"])
    assert knowledge_main(["code", "architecture", "language-providers-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--snapshot-id", snapshot_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    assert _v2(cli_build)["data"]["language_providers"]["summary"]["reference_fact_count"] == len(payload["reference_facts"])


def test_v40_language_provider_missing_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V40 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/language-providers")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_LANGUAGE_PROVIDERS_NOT_BUILT"
