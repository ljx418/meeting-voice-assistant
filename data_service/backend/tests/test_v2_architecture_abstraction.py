import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import code_graph_json_path
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_fixture_repo(repo: Path) -> None:
    (repo / "docs/design/V4.x").mkdir(parents=True)
    (repo / "core").mkdir()
    (repo / "README.md").write_text("# Harness Fixture\n\n## Architecture\n\nThin Web Console adapts to Harness Core.\n", encoding="utf-8")
    (repo / "core/thin_web_console.py").write_text("class ThinWebConsole:\n    pass\n\nclass HarnessCore:\n    pass\n", encoding="utf-8")
    (repo / "docs/design/V4.x/current.drawio").write_text(
        """<mxfile host="test"><diagram id="d1" name="Seven Plane Architecture"><mxGraphModel><root>
<mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="plane0" value="Plane-0&lt;br&gt;Product UI / Heads" vertex="1" parent="1" style="rounded=1;fillColor=#DCFCE7"/>
<mxCell id="thin" value="Thin Web Console&lt;br&gt;BFF-only observation" vertex="1" parent="1" style="rounded=1;fillColor=#FFFBEB"/>
<mxCell id="core" value="Harness Core&lt;br&gt;Job / Artifact / Approval / Trace" vertex="1" parent="1" style="rounded=1;fillColor=#DCFCE7"/>
<mxCell id="forbidden" value="Agent executor&lt;br&gt;禁止误报" vertex="1" parent="1" style="rounded=1;fillColor=#FEF2F2"/>
<mxCell id="e1" edge="1" parent="1" source="plane0" target="thin"/>
<mxCell id="e2" edge="1" parent="1" source="thin" target="core"/>
</root></mxGraphModel></diagram></mxfile>""",
        encoding="utf-8",
    )


def _write_fake_graph(workspace: Path, codebase_id: str, snapshot_id: str) -> None:
    path = code_graph_json_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    graph = {
        "schema_version": "v2.1",
        "workspace_id": workspace.name,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "nodes": [
            {"node_id": "node_thin", "node_type": "Class", "natural_id": "py:class:core.thin_web_console.ThinWebConsole", "label": "ThinWebConsole", "data": {"path": "core/thin_web_console.py"}},
            {"node_id": "node_core", "node_type": "Class", "natural_id": "py:class:core.thin_web_console.HarnessCore", "label": "HarnessCore", "data": {"path": "core/thin_web_console.py"}},
            {"node_id": "node_api", "node_type": "Capability", "natural_id": "thin_web_console", "label": "Thin Web Console", "data": {}},
        ],
        "edges": [],
        "summary": {"node_count": 3, "edge_count": 0},
    }
    path.write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")


def _prepare(workspace: Path, workspace_id: str, repo: Path) -> tuple[str, str]:
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    _write_fake_graph(workspace, asset.codebase_id, snapshot_id)
    return asset.codebase_id, snapshot_id


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def test_v23_architecture_model_builds_from_drawio_and_aligns_http_mcp_cli(tmp_path, monkeypatch, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_fixture_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "V23 Architecture")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id = _prepare(workspace, workspace_id, repo)

    service = ArchitectureService(workspace, workspace_id=workspace_id)
    bundle = service.build_architecture(codebase_id, snapshot_id=snapshot_id)
    labels = {node["label"] for node in bundle["design_nodes"]}
    node_types = {node["node_type"] for node in bundle["design_nodes"]}
    assert "Plane-0 | Product UI / Heads" in labels
    assert "Thin Web Console | BFF-only observation" in labels
    assert {"Plane", "Component", "ForbiddenClaim"} <= node_types
    assert bundle["alignment"]["summary"]["match_count"] >= 1
    assert any(finding["finding_type"] == "UNSUPPORTED_CLAIM" for finding in bundle["findings"])

    root = workspace / "assets" / "codebase" / codebase_id / "architecture"
    for rel in ["sources.jsonl", "design_nodes.jsonl", "design_edges.jsonl", "model.json", "alignment.json", "findings.jsonl", "summary.json", "views/architecture.mmd", "views/architecture.html"]:
        assert (root / rel).exists()
        assert (root / rel).stat().st_size > 0

    http_model = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/model").json()
    http_findings = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/findings").json()
    assert _v2(http_model)["ok"] is True
    assert _v2(http_findings)["data"]["summary"]["finding_count"] >= 1

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_alignment = asyncio.run(dispatcher.call_tool("knowledge_architecture_alignment", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_alignment)["data"]["alignment"]["summary"]["match_count"] >= 1

    assert knowledge_main(["code", "architecture", "findings", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert _v2(cli_payload)["data"]["summary"]["finding_count"] >= 1
    assert str(repo) not in json.dumps([http_model, http_findings, mcp_alignment, cli_payload], ensure_ascii=False)


def test_v23_architecture_missing_sources_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('no architecture docs')\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "V23 Missing Sources")
    workspace = workspace_root / workspace_id
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/build", json={"snapshot_id": snapshot_id})
    assert response.status_code == 404
    payload = response.json()
    assert payload["v2"]["ok"] is False
    assert payload["v2"]["error"]["code"] == "ARCHITECTURE_SOURCE_NOT_FOUND"
