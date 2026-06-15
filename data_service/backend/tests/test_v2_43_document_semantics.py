import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import (
    architecture_document_semantic_claims_v243_path,
    architecture_document_semantic_relations_v243_path,
    architecture_document_semantic_summary_v243_path,
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
        "docs/architecture.md": """# Target Architecture

- Acceptance gate: report must include evidence.
- Non-goal: not a full runtime topology.
- Stop condition: reject raw Mermaid injection.
- Real repo path: `/Users/Zhuanz/Desktop/workspace/data_service` must be redacted in public claims.

| Area | Claim |
| --- | --- |
| MCP | Tool catalog must stay aligned |
""",
        "docs/current.drawio": """<mxfile host="test">
  <diagram id="page-1" name="Target View">
    <mxGraphModel><root>
      <mxCell id="0"/><mxCell id="1" parent="0"/>
      <mxCell id="lane1" value="Workflow Lane" style="swimlane" vertex="1" parent="1"/>
      <mxCell id="group1" value="Agent Group" style="group" vertex="1" parent="lane1"/>
      <mxCell id="gate1" value="验收门槛 &lt;script&gt;bad&lt;/script&gt;" vertex="1" parent="group1"/>
      <mxCell id="edge1" value="depends" edge="1" source="lane1" target="gate1" parent="1"/>
    </root></mxGraphModel>
  </diagram>
</mxfile>""",
        "README.md": "# Fixture\n",
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
    workspace_id = _create_workspace(client, "V43 Document Semantics")
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


def _assert_semantics_payload(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.43_document_semantics"
    assert payload["workspace_id"] == workspace_id
    assert payload["codebase_id"] == codebase_id
    assert payload["snapshot_id"] == snapshot_id
    summary = payload["summary"]
    assert summary["claim_count"] >= 8
    assert summary["relation_count"] >= 2
    assert summary["code_fact_count"] == 0
    assert summary["drawio_claim_count"] >= 3
    assert summary["markdown_claim_count"] >= 4
    block_types = {item["source_block_type"] for item in payload["claims"]}
    assert {"heading", "acceptance_gate", "non_goal", "stop_condition", "table_row", "drawio_page", "drawio_lane", "drawio_group"} <= block_types
    assert any(item["source_block_type"] == "drawio_edge" or item.get("drawio_cell_id") == "edge1" for item in payload["claims"] + payload["relations"])
    assert all(item["is_code_fact"] is False for item in payload["claims"])
    assert all("<script>" not in item["label"].lower() for item in payload["claims"])
    assert all("/Users/Zhuanz/Desktop/workspace" not in item["label"] for item in payload["claims"])
    assert all(item["evidence_refs"] for item in payload["claims"])
    assert all(not Path(item["path"]).is_absolute() for item in payload["claims"])
    assert all(item["needs_review"] for item in payload["claims"] if item["source_type"] == "drawio")
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v43_document_semantics_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)

    payload = service.build_document_semantics_v3(codebase_id, snapshot_id=snapshot_id)
    _assert_semantics_payload(payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)
    assert architecture_document_semantic_claims_v243_path(workspace, codebase_id).exists()
    assert architecture_document_semantic_relations_v243_path(workspace, codebase_id).exists()
    assert architecture_document_semantic_summary_v243_path(workspace, codebase_id).exists()

    read_payload = service.read_document_semantics_v3(codebase_id)
    _assert_semantics_payload(read_payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    build_data = _v2(http_build.json())["data"]["document_semantics_v3"]
    assert build_data["summary"]["claim_count"] == payload["summary"]["claim_count"]
    assert build_data["claims"]["total"] == len(payload["claims"])
    _assert_no_absolute_path(build_data, repo, workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics")
    assert http_read.status_code == 200
    read_data = _v2(http_read.json())["data"]["document_semantics_v3"]
    assert read_data["summary"]["relation_count"] == payload["summary"]["relation_count"]
    assert read_data["artifact_refs"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_document_semantics_v3_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id}))
    assert _v2(mcp_build)["data"]["document_semantics_v3"]["summary"]["claim_count"] == payload["summary"]["claim_count"]
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_document_semantics_v3", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["document_semantics_v3"]["summary"]["code_fact_count"] == 0

    assert knowledge_main(["code", "architecture", "document-semantics-v3", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["document_semantics_v3"]["summary"]["drawio_claim_count"] >= 3
    assert knowledge_main(["code", "architecture", "document-semantics-v3-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--snapshot-id", snapshot_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    assert _v2(cli_build)["data"]["document_semantics_v3"]["summary"]["markdown_claim_count"] >= 4


def test_v43_document_semantics_missing_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V43 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/v2_43/document-semantics")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT"
