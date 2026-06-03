import asyncio
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.devwiki.service import CodebaseDevWikiService
from data_service.code_assets.graph.model import UNSUPPORTED_RELATIONS
from data_service.code_assets.graph.renderer_mermaid import safe_id
from data_service.code_assets.graph.service import CodeGraphService
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.overview import CodebaseOverviewService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.code_assets.trace import CodebaseTraceService


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _prepare_real_repo(workspace: Path, workspace_id: str, repo_root: Path):
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseTraceService(workspace, workspace_id=workspace_id).build_trace(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseOverviewService(workspace, workspace_id=workspace_id).build_overview(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseDevWikiService(workspace, workspace_id=workspace_id).build_devwiki(asset.codebase_id, snapshot_id=snapshot_id)
    return asset.codebase_id, snapshot_id


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def _source_artifact_paths(workspace: Path, codebase_id: str, snapshot_id: str) -> list[Path]:
    base = workspace / "assets" / "codebase" / codebase_id
    snap = base / "snapshots" / snapshot_id
    return [
        snap / "snapshot.json",
        snap / "files.jsonl",
        snap / "inventory_summary.json",
        snap / "surfaces.jsonl",
        snap / "capabilities.jsonl",
        snap / "symbol_summary.json",
        snap / "symbols.jsonl",
        snap / "imports.jsonl",
        snap / "mapping_summary.json",
        snap / "evidence.jsonl",
        base / "overview.json",
        base / "devwiki" / "index.json",
    ] + sorted((base / "devwiki" / "pages").glob("*.json"))


def _assert_no_path_values(payloads: list[dict | str], *paths: Path):
    raw = json.dumps(payloads, ensure_ascii=False)
    for path in paths:
        assert str(path) not in raw


def _node_of_type(graph: dict, node_type: str) -> dict:
    return next(item for item in graph["nodes"] if item["node_type"] == node_type)


def test_v2_code_graph_build_read_neighbors_mermaid_http_mcp_cli_real_repo(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase9 Graph")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id = _prepare_real_repo(workspace, workspace_id, repo_root)
    before_hashes = _hashes(_source_artifact_paths(workspace, codebase_id, snapshot_id))

    service = CodeGraphService(workspace, workspace_id=workspace_id)
    graph = service.build_graph(codebase_id, snapshot_id=snapshot_id)
    after_hashes = _hashes(_source_artifact_paths(workspace, codebase_id, snapshot_id))
    assert before_hashes == after_hashes
    assert not (workspace / "lifecycle" / "sources.json").exists()

    graph_root = workspace / "assets" / "codebase" / codebase_id / "graph"
    for rel in ["graph.json", "nodes.jsonl", "edges.jsonl", "summary.json", "mermaid/project.mmd"]:
        assert (graph_root / rel).exists()
        assert (graph_root / rel).stat().st_size > 0

    node_types = {item["node_type"] for item in graph["nodes"]}
    assert {"Codebase", "Snapshot", "File", "Module", "Function", "HTTPRoute", "MCPTool", "CLICommand", "Capability", "DevWikiPage", "EvidenceSpan"} <= node_types
    relations = {item["relation"] for item in graph["edges"]}
    assert relations.isdisjoint(UNSUPPORTED_RELATIONS)
    assert graph["summary"]["unsupported_edge_count"] == 0
    for relation in ["CONTAINS", "DEFINES", "IMPORTS", "EXPOSES_ROUTE", "REGISTERS_MCP_TOOL", "EXPOSES_CLI_COMMAND", "IMPLEMENTS_CAPABILITY", "DOCUMENTED_BY", "EVIDENCED_BY"]:
        assert graph["summary"]["edge_coverage_by_type"].get(relation, 0) > 0
    for edge in graph["edges"]:
        assert edge["edge_id"]
        assert edge["from_id"]
        assert edge["to_id"]
        assert edge["extractor"]
        assert "confidence" in edge
        assert edge["evidence"] or edge["needs_review"]

    mermaid = (graph_root / "mermaid/project.mmd").read_text(encoding="utf-8")
    node_ids = {item["node_id"] for item in graph["nodes"]}
    assert "flowchart TD" in mermaid
    assert str(repo_root) not in mermaid
    for node_id in list(node_ids)[:20]:
        if safe_id(node_id) in mermaid:
            assert node_id in node_ids

    center = _node_of_type(graph, "HTTPRoute")
    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/build", json={"snapshot_id": snapshot_id}).json()
    http_neighbors = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/neighbors",
        params={"node_id": center["node_id"]},
    ).json()
    http_mermaid = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid").json()

    from data_service.__main__ import knowledge_main
    from data_service.mcp_build_runtime import BuildRuntime
    from data_service.mcp_dispatcher import MCPToolDispatcher
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_neighbors = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_graph_neighbors",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "node_id": center["node_id"]},
        )
    )
    assert (
        knowledge_main(
            [
                "code",
                "graph",
                "neighbors",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
                "--node-id",
                center["node_id"],
            ]
        )
        == 0
    )
    cli_neighbors = json.loads(capsys.readouterr().out)

    assert _v2(http_build)["ok"] is True
    assert { _v2(http_neighbors)["snapshot_id"], _v2(mcp_neighbors)["snapshot_id"], _v2(cli_neighbors)["snapshot_id"] } == {snapshot_id}
    assert _v2(http_neighbors)["data"]["neighbors"]["center"]["node_id"] == center["node_id"]
    assert _v2(mcp_neighbors)["data"]["neighbors"]["center"]["node_id"] == center["node_id"]
    assert _v2(cli_neighbors)["data"]["neighbors"]["center"]["node_id"] == center["node_id"]
    assert _v2(http_mermaid)["data"]["mermaid"]["content"]
    _assert_no_path_values([http_build, http_neighbors, http_mermaid, mcp_neighbors, cli_neighbors], repo_root, workspace_root)


def test_v2_code_graph_missing_devwiki_returns_structured_error(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase9 Missing DevWiki")
    workspace = workspace_root / workspace_id
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/graph/build", json={"snapshot_id": snapshot_id})
    assert response.status_code == 404
    payload = response.json()
    assert payload["v2"]["ok"] is False
    assert payload["v2"]["error"]["code"] in {"V20_ARTIFACT_MISSING", "DEVWIKI_NOT_FOUND"}
