import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import architecture_config_inventory_path, architecture_deployment_inventory_path, architecture_language_facts_path, architecture_review_queue_path, architecture_scale_profile_path, architecture_schema_inventory_path, architecture_taxonomy_override_path, architecture_taxonomy_path, architecture_view_path
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.context.service import CodebaseAgentContextService
from data_service.code_assets.trace import CodebaseTraceService
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
        "backend/app/api/v1/code_assets_architecture.py": """from fastapi import APIRouter
router = APIRouter()
@router.post('/architecture/scale/build')
def build_scale():
    return {'ok': True}
""",
        "backend/data_service/mcp_code_architecture_tools.py": """ARCHITECTURE_TOOL_SPECS = [{'name': 'knowledge_code_architecture_scale_build'}]
def handle_architecture_tool(name, arguments):
    return {'ok': True}
""",
        "backend/data_service/cli_code_architecture.py": """def add_architecture_parser(subparsers):
    return subparsers
""",
        "backend/data_service/code_assets/architecture/service.py": "class ArchitectureService:\n    pass\n",
        "backend/data_service/code_assets/context/service.py": "class AgentContextPackService:\n    pass\n",
        "frontend/src/pages/KnowledgePage.vue": "<template><main>Project Intelligence</main></template>\n",
        "frontend/src/api/client.ts": "import axios from 'axios'\nexport const load = () => axios.get('/api/workspaces')\n",
        "frontend/src/router/index.ts": "export const routes = [{ path: '/knowledge', component: 'KnowledgePage' }]\n",
        "package.json": json.dumps({"name": "fixture-ui", "scripts": {"dev": "vite --host 0.0.0.0", "build": "vite build"}, "dependencies": {"vue": "^3.0.0"}, "devDependencies": {"vite": "^5.0.0"}, "MINIMAX_API_KEY": "abc123"}),
        "Dockerfile": "FROM python:3.11-slim\nEXPOSE 8000\nCMD [\"python\", \"app.py\"]\n",
        "docker-compose.yml": "services:\n  api:\n    build: .\n    ports:\n      - \"8000:8000\"\n",
        ".github/workflows/test.yml": "name: test\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n",
        ".env.example": "MINIMAX_API_KEY=abc123\nPUBLIC_FLAG=true\n",
        "openapi.yaml": "openapi: 3.0.0\ninfo:\n  title: Fixture\n  version: '1.0'\n",
        "schema.sql": "CREATE TABLE users (id INTEGER PRIMARY KEY);\n",
        "docs/architecture.md": "# Architecture\n\nProject intelligence architecture.\n",
        "tests/test_architecture.py": "def test_architecture():\n    assert True\n",
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
    workspace_id = _create_workspace(client, "V26 Phase44")
    workspace = workspace_root / workspace_id
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_code_architecture(asset.codebase_id, snapshot_id=snapshot_id)
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, snapshot_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_scale_profile(profile: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path) -> None:
    assert profile["schema_version"] == "v2.39_scale"
    assert profile["workspace_id"] == workspace_id
    assert profile["codebase_id"] == codebase_id
    assert profile["snapshot_id"] == snapshot_id
    assert profile["profile_id"] == f"scale:{workspace_id}:{codebase_id}:{snapshot_id}"
    assert profile["file_count"] > 0
    assert profile["loc_total"] > 0
    assert "python" in profile["language_distribution"]
    assert profile["artifact_sizes"]
    assert "snapshot" in profile["artifact_sizes"]
    assert set(profile["confidence_distribution"]) == {"high", "medium", "low", "needs_review"}
    assert "summary_mode_required" in profile
    assert profile["source_artifact_refs"]
    assert profile["artifact_refs"]
    assert profile["status"] in {"ready", "partial"}
    assert "budget" in profile
    assert "scale_artifacts" in profile
    serialized = json.dumps(profile, ensure_ascii=False)
    assert str(repo) not in serialized


def test_v26_phase44_scale_profile_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    profile = service.build_scale_profile(codebase_id, snapshot_id=snapshot_id)
    _assert_scale_profile(profile, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)
    assert architecture_scale_profile_path(workspace, codebase_id).exists()
    assert architecture_scale_profile_path(workspace, codebase_id).stat().st_size > 0

    partial_profile = service.build_scale_profile(codebase_id, snapshot_id=snapshot_id, budget={"max_files": 1, "max_loc": 1, "shard_size": 2})
    assert partial_profile["status"] == "partial"
    assert partial_profile["partial"] is True
    assert any(blocker["code"] == "SCAN_BUDGET_EXCEEDED" for blocker in partial_profile["blockers"])
    readback = service.read_scale_shard(codebase_id, shard="files", page=1, page_size=2)
    assert readback["schema_version"] == "v2.39_scale"
    assert readback["snapshot_id"] == snapshot_id
    assert readback["page"] == 1
    assert readback["page_size"] == 2
    assert readback["total"] >= len(readback["items"]) >= 1
    assert str(repo) not in json.dumps(readback, ensure_ascii=False)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/build", json={"snapshot_id": snapshot_id, "max_files": 1, "max_loc": 1, "shard_size": 2})
    assert http_build.status_code == 200
    build_v2 = _v2(http_build.json())
    assert build_v2["ok"] is True
    _assert_scale_profile(build_v2["data"]["scale_profile"], workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)
    assert build_v2["data"]["scale_profile"]["status"] == "partial"

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/profile")
    assert http_read.status_code == 200
    read_profile = _v2(http_read.json())["data"]["scale_profile"]
    _assert_scale_profile(read_profile, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)
    assert read_profile["status"] == "partial"

    http_readback = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/readback", params={"shard": "files", "page": 1, "page_size": 2})
    assert http_readback.status_code == 200
    http_readback_payload = _v2(http_readback.json())["data"]["scale_readback"]
    assert http_readback_payload["snapshot_id"] == snapshot_id
    assert http_readback_payload["page_size"] == 2
    assert http_readback_payload["items"]
    assert str(repo) not in json.dumps(http_readback_payload, ensure_ascii=False)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_profile = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_scale_profile", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_scale_profile(_v2(mcp_profile)["data"]["scale_profile"], workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)
    mcp_readback = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_scale_readback", {"workspace_id": workspace_id, "codebase_id": codebase_id, "shard": "files", "page": 1, "page_size": 2}))
    assert _v2(mcp_readback)["data"]["scale_readback"]["snapshot_id"] == snapshot_id

    assert knowledge_main(["code", "architecture", "scale-profile", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_scale_profile(_v2(cli_payload)["data"]["scale_profile"], workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)
    assert knowledge_main(["code", "architecture", "scale-readback", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--shard", "files", "--page", "1", "--page-size", "2"]) == 0
    cli_readback = json.loads(capsys.readouterr().out)
    assert _v2(cli_readback)["data"]["scale_readback"]["snapshot_id"] == snapshot_id


def test_v26_phase44_scale_profile_missing_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('hello')\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V26 Phase44 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/scale/profile")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_SCALE_PROFILE_NOT_BUILT"


def test_v26_phase45_architecture_inventory_http_mcp_cli_and_redaction(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    payload = service.build_inventory(codebase_id, snapshot_id=snapshot_id)

    assert payload["schema_version"] == "v2.6"
    assert payload["language_facts"]
    assert payload["config_inventory"]
    assert payload["deployment_inventory"]
    assert payload["schema_inventory"]
    assert architecture_language_facts_path(workspace, codebase_id).exists()
    assert architecture_config_inventory_path(workspace, codebase_id).exists()
    assert architecture_deployment_inventory_path(workspace, codebase_id).exists()
    assert architecture_schema_inventory_path(workspace, codebase_id).exists()

    serialized = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in serialized
    assert "abc123" not in serialized
    assert "MINIMAX_API_KEY=abc123" not in serialized
    assert "[redacted" in serialized
    assert any(item["fact_type"] == "api_client_hint" for item in payload["language_facts"])
    assert any(item["item_type"] == "package_manifest" for item in payload["config_inventory"])
    assert any(item["deployment_type"] == "dockerfile" for item in payload["deployment_inventory"])
    assert any(item["schema_type"] == "openapi_like_schema" for item in payload["schema_inventory"])
    assert all(item.get("evidence") for item in payload["language_facts"][:5])

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/inventory/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    build_v2 = _v2(http_build.json())
    assert build_v2["ok"] is True
    assert build_v2["data"]["architecture_inventory"]["config_inventory"]["total"] >= 1

    for endpoint, key in {
        "language-facts": "language_facts",
        "config": "config_inventory",
        "deployment": "deployment_inventory",
        "schema": "schema_inventory",
    }.items():
        response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/{endpoint}")
        assert response.status_code == 200
        data = _v2(response.json())["data"]
        assert data[key]["total"] >= 1
        assert str(repo) not in json.dumps(data, ensure_ascii=False)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_config = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_config_inventory", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_config)["data"]["config_inventory"]["total"] >= 1

    assert knowledge_main(["code", "architecture", "config", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert _v2(cli_payload)["data"]["config_inventory"]["total"] >= 1


def test_v26_phase45_architecture_inventory_missing_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text('{"name":"missing-inventory"}\n', encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V26 Phase45 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/config")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_CONFIG_INVENTORY_NOT_BUILT"


def test_v26_phase46_taxonomy_review_queue_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_scale_profile(codebase_id, snapshot_id=snapshot_id)
    service.build_inventory(codebase_id, snapshot_id=snapshot_id)

    override_path = architecture_taxonomy_override_path(workspace, codebase_id)
    override_path.parent.mkdir(parents=True, exist_ok=True)
    override_path.write_text(json.dumps({"role_types": ["product"], "confidence_thresholds": {"accepted_min": 0.85}}), encoding="utf-8")
    taxonomy = service.build_taxonomy(codebase_id)
    assert architecture_taxonomy_path(workspace, codebase_id).exists()
    for role_type in ["interface", "application", "domain", "infrastructure", "governance", "runtime", "artifact", "test", "docs", "product"]:
        assert role_type in taxonomy["role_types"]
    assert taxonomy["confidence_thresholds"]["accepted_min"] == 0.85
    assert taxonomy["override_source"] == "architecture_taxonomy_override.json"

    queue_payload = service.build_review_queue(codebase_id)
    assert architecture_review_queue_path(workspace, codebase_id).exists()
    assert queue_payload["review_queue"]
    first = queue_payload["review_queue"][0]
    for key in ["review_id", "target_type", "target_id", "reason", "severity", "confidence", "signals", "evidence", "recommended_action"]:
        assert key in first
    ids_once = [item["review_id"] for item in queue_payload["review_queue"]]
    ids_twice = [item["review_id"] for item in service.build_review_queue(codebase_id)["review_queue"]]
    assert ids_once == ids_twice
    serialized = json.dumps(queue_payload, ensure_ascii=False)
    assert str(repo) not in serialized

    http_taxonomy = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/taxonomy/build")
    assert http_taxonomy.status_code == 200
    assert "product" in _v2(http_taxonomy.json())["data"]["taxonomy"]["role_types"]
    http_queue_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/review-queue/build")
    assert http_queue_build.status_code == 200
    queue_data = _v2(http_queue_build.json())["data"]["review_queue"]["review_queue"]
    assert queue_data["total"] >= 1
    http_queue = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/review-queue")
    assert http_queue.status_code == 200
    assert _v2(http_queue.json())["data"]["review_queue"]["review_queue"]["total"] == queue_data["total"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_queue = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_review_queue", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_queue)["data"]["review_queue"]["review_queue"]["total"] == queue_data["total"]

    assert knowledge_main(["code", "architecture", "review-queue", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert _v2(cli_payload)["data"]["review_queue"]["review_queue"]["total"] == queue_data["total"]


def test_v26_phase46_review_queue_missing_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text('{"name":"missing-review"}\n', encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V26 Phase46 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/review-queue")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_REVIEW_QUEUE_NOT_BUILT"


def test_v26_phase47_large_project_views_and_context_summary_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_scale_profile(codebase_id, snapshot_id=snapshot_id)
    service.build_inventory(codebase_id, snapshot_id=snapshot_id)
    service.build_taxonomy(codebase_id)
    service.build_review_queue(codebase_id)

    payload = service.build_large_project_views(codebase_id)
    assert payload["schema_version"] == "v2.6"
    assert payload["view_ids"] == ["architecture_large_project_overview.html", "architecture_key_boundaries.mmd"]
    assert payload["mermaid_persisted_ids"]
    assert architecture_view_path(workspace, codebase_id, "architecture_large_project_overview.html").exists()
    assert architecture_view_path(workspace, codebase_id, "architecture_key_boundaries.mmd").exists()

    html = service.read_large_project_view(codebase_id, "architecture_large_project_overview.html")
    mermaid = service.read_large_project_view(codebase_id, "architecture_key_boundaries.mmd")
    assert html["content_type"] == "text/html"
    assert mermaid["content_type"] == "text/mermaid"
    assert "V2.6 Large Project Architecture Overview" in html["content"]
    assert "flowchart TD" in mermaid["content"]
    assert "architecture_scale_profile.json" in html["content"]
    assert str(repo) not in json.dumps([payload, html, mermaid], ensure_ascii=False)
    for persisted_id in payload["mermaid_persisted_ids"][:10]:
        assert persisted_id

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/build")
    assert http_build.status_code == 200
    assert _v2(http_build.json())["data"]["views"]["view_ids"] == payload["view_ids"]
    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/architecture_large_project_overview.html")
    assert http_view.status_code == 200
    assert "V2.6 Large Project Architecture Overview" in _v2(http_view.json())["data"]["view"]["content"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_view = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_large_project_view", {"workspace_id": workspace_id, "codebase_id": codebase_id, "view_id": "architecture_key_boundaries.mmd"}))
    assert "flowchart TD" in _v2(mcp_view)["data"]["view"]["content"]

    assert knowledge_main(["code", "architecture", "large-view", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--view-id", "architecture_key_boundaries.mmd"]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert "flowchart TD" in _v2(cli_payload)["data"]["view"]["content"]

    CodebaseTraceService(workspace, workspace_id=workspace_id).build_trace(codebase_id, snapshot_id=snapshot_id)
    pack = CodebaseAgentContextService(workspace, workspace_id=workspace_id).create_pack(
        codebase_id,
        snapshot_id=snapshot_id,
        mode="task_context",
        task="Review architecture risks before editing the project.",
        output_format="markdown",
        max_tokens=16000,
    )
    assert pack["architecture_summary"]["summary"]["file_count"] > 0
    assert pack["architecture_summary"]["artifact_refs"]
    assert "Architecture Summary" in pack["content"]

    small_pack = CodebaseAgentContextService(workspace, workspace_id=workspace_id).create_pack(
        codebase_id,
        snapshot_id=snapshot_id,
        mode="task_context",
        task="Review architecture risks before editing the project.",
        output_format="json",
        max_tokens=64,
    )
    omitted = [item for item in small_pack["omitted_items"] if item.get("item_ref") == "architecture_summary"]
    if "architecture_summary" in small_pack:
        assert small_pack["architecture_summary"]["artifact_refs"]
    else:
        assert omitted
        assert omitted[0]["evidence"]
