import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import (
    architecture_context_cache_index_v244_path,
    architecture_context_pack_optimized_markdown_v244_path,
    architecture_context_pack_optimized_v244_path,
    architecture_token_budget_ledger_v244_path,
)
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_repo(repo: Path) -> None:
    files = {
        "backend/api.py": """from fastapi import FastAPI
from backend.services.user_service import UserService

app = FastAPI()


@app.get('/api/users')
def list_users():
    return UserService().list_users()
""",
        "backend/services/user_service.py": """from backend.storage.user_repo import UserRepository


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def list_users(self):
        return self.repo.list_users()
""",
        "backend/storage/user_repo.py": """class UserRepository:
    def list_users(self):
        return []
""",
        "tests/test_user_service.py": """from backend.services.user_service import UserService


def test_list_users():
    assert UserService().list_users() == []
""",
        "docs/architecture.md": """# Target Architecture

- Acceptance gate: every recommendation must retain evidence or needs_review.
- Non-goal: do not claim runtime call graph.
- The users API is the public entrypoint for user management.
- UserService is the implementation module for user management.
- Token budget should omit low-priority items with reasons.
""",
        "README.md": "# Token Cache Fixture\n",
        "pyproject.toml": "[project]\nname = 'token-cache-fixture'\n",
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
    workspace_id = _create_workspace(client, "V44 Token Cache")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_language_provider_facts(asset.codebase_id, snapshot_id=snapshot_id)
    service.build_workflow_runtime_candidates(asset.codebase_id, snapshot_id=snapshot_id)
    service.build_document_registry(asset.codebase_id, snapshot_id=snapshot_id)
    service.build_document_claims(asset.codebase_id)
    service.build_relationship_chains_v3(asset.codebase_id, snapshot_id=snapshot_id)
    service.build_document_semantics_v3(asset.codebase_id, snapshot_id=snapshot_id)
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, snapshot_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_pack(pack: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path, workspace_root: Path) -> None:
    assert pack["schema_version"] == "v2.44_token_context_cache"
    assert pack["workspace_id"] == workspace_id
    assert pack["codebase_id"] == codebase_id
    assert pack["snapshot_id"] == snapshot_id
    assert pack["token_estimate"] > 0
    assert pack["token_estimate"] <= pack["max_tokens"]
    assert pack["source_artifact_hash"]
    assert pack["reading_order"]
    assert pack["recommendations"]
    assert all(item.get("evidence_refs") or item.get("needs_review") for item in pack["recommendations"])
    assert all(item.get("reason") for item in pack.get("omitted_items", []))
    assert "## Recommendations" in pack["markdown"]
    _assert_no_absolute_path(pack, repo, workspace_root)


def test_v44_token_budget_cache_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)

    pack = service.create_optimized_context_pack_v244(codebase_id, mode="task_context", role="coding_agent", task="change users API", max_tokens=650)
    _assert_pack(pack, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)
    assert pack["omitted_items"]
    assert architecture_token_budget_ledger_v244_path(workspace, codebase_id).exists()
    assert architecture_context_cache_index_v244_path(workspace, codebase_id).exists()
    assert architecture_context_pack_optimized_v244_path(workspace, codebase_id, pack["pack_id"]).exists()
    assert architecture_context_pack_optimized_markdown_v244_path(workspace, codebase_id, pack["pack_id"]).exists()

    second = service.create_optimized_context_pack_v244(codebase_id, mode="task_context", role="coding_agent", task="change users API", max_tokens=650)
    assert second["pack_id"] == pack["pack_id"]
    assert second["cache_hit"] is True
    assert second["ledger"]["cache_hit"] is True

    read_pack = service.read_optimized_context_pack_v244(codebase_id, pack["pack_id"])
    _assert_pack(read_pack, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized", json={"mode": "task_context", "role": "coding_agent", "task": "change users API", "max_tokens": 650})
    assert http_build.status_code == 200
    build_pack = _v2(http_build.json())["data"]["architecture_context_pack_optimized"]["architecture_context_pack_optimized"]
    assert build_pack["pack_id"] == pack["pack_id"]
    assert build_pack["cache_hit"] is True

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized/{pack['pack_id']}")
    assert http_read.status_code == 200
    read_data = _v2(http_read.json())["data"]["architecture_context_pack_optimized"]["architecture_context_pack_optimized"]
    assert read_data["pack_id"] == pack["pack_id"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_context_pack_optimized", {"workspace_id": workspace_id, "codebase_id": codebase_id, "mode": "task_context", "role": "coding_agent", "task": "change users API", "max_tokens": 650}))
    assert _v2(mcp_build)["data"]["architecture_context_pack_optimized"]["architecture_context_pack_optimized"]["pack_id"] == pack["pack_id"]
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_context_pack_optimized_read", {"workspace_id": workspace_id, "codebase_id": codebase_id, "pack_id": pack["pack_id"]}))
    assert _v2(mcp_read)["data"]["architecture_context_pack_optimized"]["architecture_context_pack_optimized"]["cache_key"] == pack["cache_key"]

    assert knowledge_main(["code", "architecture", "context-pack-optimized", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--mode", "task_context", "--role", "coding_agent", "--task", "change users API", "--max-tokens", "650"]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    assert _v2(cli_build)["data"]["architecture_context_pack_optimized"]["architecture_context_pack_optimized"]["pack_id"] == pack["pack_id"]
    assert knowledge_main(["code", "architecture", "context-pack-optimized-read", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--pack-id", pack["pack_id"]]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["architecture_context_pack_optimized"]["architecture_context_pack_optimized"]["pack_id"] == pack["pack_id"]


def test_v44_token_budget_missing_prerequisite_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Missing prereq\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V44 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/v2_44/context-pack-optimized", json={"max_tokens": 650})
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] in {"ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT", "ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT"}
