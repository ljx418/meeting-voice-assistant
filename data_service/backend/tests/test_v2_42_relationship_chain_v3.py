import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import (
    architecture_forbidden_edge_scan_v242_path,
    architecture_relationship_chain_summary_v242_path,
    architecture_relationship_chains_v242_path,
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
        "backend/cli.py": """import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-users', action='store_true')
    return parser.parse_args()
""",
        "backend/console_app.py": """from rich.console import Console

console = Console()
""",
        "frontend/src/api/client.ts": """import axios from 'axios'

export function listUsers() {
  return axios.get('/api/users')
}
""",
        "tests/test_user_service.py": """from backend.services.user_service import UserService


def test_list_users():
    assert UserService().list_users() == []
""",
        "docs/architecture.md": """# Architecture

- user management capability is exposed through the users API.
- UserService implements user management.
""",
        "README.md": "# Relationship Chain Fixture\n",
        "pyproject.toml": "[project]\nname = 'relationship-fixture'\n",
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
    workspace_id = _create_workspace(client, "V42 Relationship Chains")
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
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, snapshot_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_line_refs(repo: Path, chains: list[dict]) -> None:
    assert chains
    checked = 0
    for chain in chains:
        for edge in chain.get("edges", []):
            assert edge["edge_type"] not in {"runtime_call", "data_flow", "control_flow", "production_topology", "type_inferred_dependency"}
            if edge["determinism"] == "heuristic":
                assert edge["needs_review"]
            for ref in edge.get("evidence_refs", []):
                path = ref.get("path")
                line_range = ref.get("line_range")
                if not path or not line_range:
                    continue
                assert not Path(path).is_absolute()
                lines = (repo / path).read_text(encoding="utf-8", errors="replace").splitlines()
                start, end = line_range
                assert 1 <= start <= end <= max(1, len(lines))
                assert "\n".join(lines[start - 1 : end]).strip()
                checked += 1
    assert checked >= 3


def _assert_relationship_chain_payload(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.42_relationship_chain"
    assert payload["workspace_id"] == workspace_id
    assert payload["codebase_id"] == codebase_id
    assert payload["snapshot_id"] == snapshot_id
    summary = payload["summary"]
    assert summary["chain_count"] >= 1
    assert summary["accepted_chain_count"] >= 1
    assert summary["forbidden_edge_count"] == 0
    assert summary["unsupported_edge_count"] == 0
    assert summary["heuristic_without_review"] == 0
    assert payload["forbidden_edge_scan"]["forbidden_edge_count"] == 0
    assert payload["forbidden_edge_scan"]["unsupported_edge_count"] == 0
    assert "runtime_call" in payload["forbidden_edge_scan"]["forbidden_edge_types"]
    assert any(chain["chain_type"] == "capability_chain" for chain in payload["chains"])
    _assert_line_refs(repo, payload["chains"])
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v42_relationship_chains_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)

    payload = service.build_relationship_chains_v3(codebase_id, snapshot_id=snapshot_id)
    _assert_relationship_chain_payload(payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)
    assert architecture_relationship_chains_v242_path(workspace, codebase_id).exists()
    assert architecture_relationship_chain_summary_v242_path(workspace, codebase_id).exists()
    assert architecture_forbidden_edge_scan_v242_path(workspace, codebase_id).exists()

    read_payload = service.read_relationship_chains_v3(codebase_id)
    _assert_relationship_chain_payload(read_payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    build_data = _v2(http_build.json())["data"]["relationship_chains_v3"]
    assert build_data["summary"]["chain_count"] == payload["summary"]["chain_count"]
    assert build_data["chains"]["total"] == len(payload["chains"])
    _assert_no_absolute_path(build_data, repo, workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains")
    assert http_read.status_code == 200
    read_data = _v2(http_read.json())["data"]["relationship_chains_v3"]
    assert read_data["summary"]["accepted_chain_count"] == payload["summary"]["accepted_chain_count"]
    assert read_data["artifact_refs"]
    _assert_no_absolute_path(read_data, repo, workspace_root)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_relationship_chains_v3_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id}))
    assert _v2(mcp_build)["data"]["relationship_chains_v3"]["summary"]["chain_count"] == payload["summary"]["chain_count"]
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_relationship_chains_v3", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["relationship_chains_v3"]["summary"]["forbidden_edge_count"] == 0

    assert knowledge_main(["code", "architecture", "relationship-chains-v3", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["relationship_chains_v3"]["summary"]["accepted_chain_count"] == payload["summary"]["accepted_chain_count"]
    assert knowledge_main(["code", "architecture", "relationship-chains-v3-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--snapshot-id", snapshot_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    assert _v2(cli_build)["data"]["relationship_chains_v3"]["summary"]["unsupported_edge_count"] == 0


def test_v42_relationship_chains_missing_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V42 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/v2_42/relationship-chains")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT"
