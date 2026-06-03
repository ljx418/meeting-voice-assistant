import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import architecture_code_boundaries_path, architecture_code_derived_model_path, architecture_code_layers_path, architecture_code_roles_path, architecture_design_code_drift_path, architecture_pattern_candidates_path
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
        "backend/app/api/v1/code_assets_architecture.py": """from fastapi import APIRouter
router = APIRouter()
@router.post('/architecture/code/build')
def build_code_architecture():
    return {'ok': True}
""",
        "backend/data_service/mcp_code_architecture_tools.py": """ARCHITECTURE_TOOL_SPECS = [{'name': 'knowledge_code_architecture_build'}]
def handle_architecture_tool(name, arguments):
    return {'ok': True}
""",
        "backend/data_service/cli_code_architecture.py": """def add_architecture_parser(subparsers):
    return subparsers
""",
        "backend/data_service/code_assets/artifacts.py": """def architecture_code_roles_path(workspace, codebase_id):
    return workspace / codebase_id / 'architecture' / 'code_roles.jsonl'
""",
        "backend/data_service/code_assets/quality/service.py": """class CodeQualityService:
    pass
""",
        "backend/data_service/code_assets/devwiki/service.py": """class DevWikiService:
    pass
""",
        "backend/data_service/code_assets/graph/service.py": """class CodeGraphService:
    pass
""",
        "backend/data_service/code_assets/context/service.py": """class AgentContextPackService:
    pass
""",
        "frontend/src/pages/KnowledgePage.vue": "<template><main>Project Intelligence</main></template>\n",
        "backend/tests/test_architecture.py": "def test_architecture():\n    assert True\n",
        "docs/architecture.md": "# Architecture\n\nProject intelligence architecture.\n",
        "docs/design/current.drawio": """<mxfile host="test"><diagram id="d1" name="Architecture"><mxGraphModel><root>
<mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="api" value="FastAPI Router" vertex="1" parent="1"/>
<mxCell id="mcp" value="MCP Registry" vertex="1" parent="1"/>
<mxCell id="missing" value="Unimplemented Runtime Plane" vertex="1" parent="1"/>
</root></mxGraphModel></diagram></mxfile>""",
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
    workspace_id = _create_workspace(client, "V24 Phase19")
    workspace = workspace_root / workspace_id
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, snapshot_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_phase19_payload(payload: dict, repo: Path) -> None:
    role_types = {role["role_type"] for role in payload["roles"] if role["confidence"] >= 0.8}
    layer_types = {layer["layer_type"] for layer in payload["layers"]}
    assert {"api_router", "mcp_tooling", "cli_tooling", "frontend", "artifact_store", "governance", "test", "docs"} <= role_types
    assert {"interface", "application", "artifact", "governance", "test", "docs"} <= layer_types
    assert payload["summary"]["high_confidence_without_evidence"] == 0
    for role in payload["roles"]:
        if role["confidence"] >= 0.8:
            assert role["evidence"]
        if role["role_type"] == "unknown":
            assert role["needs_review"]
    serialized = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in serialized


def _assert_phase20_payload(payload: dict, repo: Path) -> None:
    boundary_types = {boundary["boundary_type"] for boundary in payload["boundaries"] if boundary["confidence"] >= 0.8}
    pattern_types = {pattern["pattern_type"] for pattern in payload["patterns"] if pattern["confidence"] >= 0.8}
    assert {"package", "public_surface_boundary", "governance_boundary", "storage_boundary"} <= boundary_types
    assert {"fastapi_router", "mcp_registry", "cli_command_group", "artifact_store", "quality_gate", "context_pack", "devwiki", "code_graph", "architecture_alignment"} <= pattern_types
    for boundary in payload["boundaries"]:
        if boundary["confidence"] >= 0.8:
            assert boundary["evidence"]
    for pattern in payload["patterns"]:
        if pattern["confidence"] >= 0.8:
            assert pattern["evidence"]
    serialized = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in serialized


def test_v24_phase19_builds_code_roles_layers_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_architecture(codebase_id, snapshot_id=snapshot_id)
    payload = service.build_code_architecture(codebase_id, snapshot_id=snapshot_id)
    _assert_phase19_payload(payload, repo)

    assert architecture_code_roles_path(workspace, codebase_id).exists()
    assert architecture_code_layers_path(workspace, codebase_id).exists()
    assert architecture_code_boundaries_path(workspace, codebase_id).exists()
    assert architecture_pattern_candidates_path(workspace, codebase_id).exists()
    assert architecture_code_derived_model_path(workspace, codebase_id).exists()
    assert architecture_design_code_drift_path(workspace, codebase_id).exists()
    code_view_html = workspace / "assets" / "codebase" / codebase_id / "architecture" / "views" / "code_derived_architecture.html"
    code_view_mmd = workspace / "assets" / "codebase" / codebase_id / "architecture" / "views" / "code_derived_architecture.mmd"
    assert code_view_html.exists()
    assert code_view_mmd.exists()
    assert architecture_code_roles_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_code_layers_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_code_boundaries_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_pattern_candidates_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_code_derived_model_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_design_code_drift_path(workspace, codebase_id).stat().st_size >= 0
    assert code_view_html.stat().st_size > 0
    assert code_view_mmd.stat().st_size > 0
    assert str(repo) not in code_view_html.read_text(encoding="utf-8")
    assert str(repo) not in code_view_mmd.read_text(encoding="utf-8")

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    assert _v2(http_build.json())["ok"] is True
    http_roles = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/roles")
    assert http_roles.status_code == 200
    _assert_phase19_payload(_v2(http_roles.json())["data"]["code_architecture"], repo)
    _assert_phase20_payload(_v2(http_roles.json())["data"]["code_architecture"], repo)
    code_architecture = _v2(http_roles.json())["data"]["code_architecture"]
    assert code_architecture["code_model"]["model_id"].startswith("code_derived_architecture:")
    assert "drift_count" in code_architecture["summary"]
    assert code_architecture["summary"]["drift_count"] > 0
    http_patterns = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/patterns")
    assert http_patterns.status_code == 200
    pattern_data = _v2(http_patterns.json())["data"]
    _assert_phase20_payload({"boundaries": pattern_data["boundaries"], "patterns": pattern_data["patterns"]}, repo)
    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/views/code_derived_architecture.html")
    assert http_view.status_code == 200
    assert "V2.4 Code-Derived Architecture" in _v2(http_view.json())["data"]["view"]["content"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_roles = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_roles", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_phase19_payload(_v2(mcp_roles)["data"]["code_architecture"], repo)
    mcp_patterns = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_patterns", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_phase20_payload(_v2(mcp_patterns)["data"], repo)
    mcp_view = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_view", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert "V2.4 Code-Derived Architecture" in _v2(mcp_view)["data"]["view"]["content"]

    assert knowledge_main(["code", "architecture", "roles", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_phase19_payload(_v2(cli_payload)["data"]["code_architecture"], repo)
    assert knowledge_main(["code", "architecture", "patterns", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_pattern_payload = json.loads(capsys.readouterr().out)
    _assert_phase20_payload(_v2(cli_pattern_payload)["data"], repo)
    assert knowledge_main(["code", "architecture", "code-view", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_view_payload = json.loads(capsys.readouterr().out)
    assert "V2.4 Code-Derived Architecture" in _v2(cli_view_payload)["data"]["view"]["content"]


def test_v24_phase19_missing_inventory_returns_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "backend/data_service/example.py").parent.mkdir(parents=True)
    (repo / "backend/data_service/example.py").write_text("def example():\n    return True\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V24 Phase19 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/code/build", json={"snapshot_id": snapshot_id})
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "INVENTORY_NOT_FOUND"
