import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.doc_grounded_architecture.paths import (
    current_model_path,
    doc_authority_registry_path,
    doc_claims_path,
    reconstruction_report_path,
    report_html_path,
    verification_matrix_path,
)
from data_service.code_assets.doc_grounded_architecture.service import DocGroundedArchitectureService
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
        "README.md": "# Fixture Project\n\nA project used for V2.37 document-grounded architecture tests.\n",
        "docs/V2.x/V2_37_DOC_GROUNDED_ARCHITECTURE_PRD.md": """# V2.37 PRD

## Target Experience

- DocGroundedArchitectureService builds the document-grounded architecture pipeline.
- backend/data_service/code_assets/doc_grounded_architecture/service.py stores the focused implementation.
- GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/report exposes the human report.
- Acceptance: supported claims require document evidence and code evidence.
- Out of scope: complete recovery of human design intent from code alone.
""",
        "docs/V2.x/V2_37_DOC_GROUNDED_ARCHITECTURE_TARGET_ARCHITECTURE.md": """# V2.37 Target Architecture

- Document Authority Registry v2
- Architecture Claim Graph v2
- Current Implementation Model
- Claim-to-Code Verification
- Reconstruction Report and Agent Brief
""",
        "docs/V2.x/V2_36_TASK_NAVIGATION_PRD.md": "# V2.36 Prior PRD\n\nHistorical plan.\n",
        "docs/design/current_target.drawio": """<mxfile>
  <diagram name="Target">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="a" value="Document Authority Registry v2" vertex="1" parent="1" />
        <mxCell id="b" value="Claim-to-Code Verification" vertex="1" parent="1" />
        <mxCell id="e1" value="feeds" edge="1" source="a" target="b" parent="1" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
""",
        "backend/app/api/v1/code_assets_doc_grounded_architecture.py": """from fastapi import APIRouter

router = APIRouter(prefix="/workspaces")

@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/report")
async def read_doc_grounded_report(workspace_id: str, codebase_id: str):
    return {"ok": True}
""",
        "backend/data_service/code_assets/doc_grounded_architecture/service.py": """class DocGroundedArchitectureService:
    def build_pipeline(self, codebase_id: str) -> dict:
        return {"codebase_id": codebase_id}
""",
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
    workspace_id = _create_workspace(client, "V237")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, snapshot_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def test_v237_doc_grounded_architecture_direct_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = DocGroundedArchitectureService(workspace, workspace_id=workspace_id)

    direct = service.build_pipeline(codebase_id, snapshot_id=snapshot_id)
    assert direct["schema_version"] == "v2.37"
    assert doc_authority_registry_path(workspace, codebase_id).exists()
    assert doc_claims_path(workspace, codebase_id).exists()
    assert current_model_path(workspace, codebase_id).exists()
    assert verification_matrix_path(workspace, codebase_id).exists()
    assert reconstruction_report_path(workspace, codebase_id).exists()
    assert report_html_path(workspace, codebase_id).exists()

    registry = service.read_document_authority_registry(codebase_id)
    docs = {item["repo_path"]: item for item in registry["documents"]}
    assert docs["docs/V2.x/V2_37_DOC_GROUNDED_ARCHITECTURE_PRD.md"]["authority_role"] == "target"
    assert docs["docs/V2.x/V2_37_DOC_GROUNDED_ARCHITECTURE_PRD.md"]["authority_level"] == "primary"
    assert docs["docs/V2.x/V2_36_TASK_NAVIGATION_PRD.md"]["authority_role"] == "historical_reference"
    assert docs["docs/V2.x/V2_36_TASK_NAVIGATION_PRD.md"]["stale"] is True

    claims = service.read_claim_graph(codebase_id)["claims"]
    drawio_claims = [item for item in claims if item["source_block_type"] == "diagram_node"]
    assert drawio_claims
    assert all(item["is_code_fact"] is False for item in drawio_claims)
    assert all(item["confidence"] <= 0.7 for item in drawio_claims)

    verification = service.read_verification(codebase_id)
    supported = [row for row in verification["verification_rows"] if row["verification_status"] == "supported"]
    assert supported
    assert all(row["document_evidence"] and row["code_evidence"] for row in supported)
    assert all(row["match_strategy"] != "token_overlap_only" for row in supported)
    assert all(row["verification_status"] != "supported" for row in verification["verification_rows"] if row["match_strategy"] == "token_overlap_only")

    html = report_html_path(workspace, codebase_id).read_text(encoding="utf-8")
    assert "<svg" in html
    assert "flowchart LR" not in html

    serialized = json.dumps(direct, ensure_ascii=False)
    assert str(repo) not in serialized

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    assert _v2(http_build.json())["data"]["doc_grounded_architecture"]["schema_version"] == "v2.37"

    http_report = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/report")
    assert http_report.status_code == 200
    assert _v2(http_report.json())["data"]["doc_grounded_architecture_report"]["summary"]["supported_count"] >= 1

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_doc_grounded_verification", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_payload)["data"]["doc_grounded_verification"]["summary"]["supported_count"] >= 1

    assert knowledge_main(["code", "architecture", "doc-grounded", "report", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert _v2(cli_payload)["data"]["doc_grounded_architecture_report"]["summary"]["supported_count"] >= 1
