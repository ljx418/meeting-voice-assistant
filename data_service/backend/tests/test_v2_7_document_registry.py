import asyncio
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.reconstruction import render_reconstructed_architecture_html
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import architecture_doc_claims_path, architecture_doc_code_alignment_path, architecture_doc_code_drift_v2_path, architecture_doc_quality_findings_path, architecture_doc_quality_summary_path, architecture_doc_relations_path, architecture_doc_sources_path, architecture_doc_view_path, architecture_docs_path, architecture_reconstructed_model_path
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.quality.service import CodeQualityService
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
        "README.md": "# Fixture Project\n\nProject readme.\n",
        "docs/V2.x/V2_7_TARGET_PRD.md": """# V2.7 Target PRD

Target documentation-code governance.

## Functional Scope

- Document Asset Registry registers project architecture documents.
- Architecture Claim Extractor extracts claims from Markdown and drawio.
- Acceptance: every accepted claim has document evidence.
- GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment is the Doc-Code Alignment v2 read API.
- ArchitectureService.build_document_quality is the document quality implementation symbol.
- knowledge_code_architecture_doc_code_alignment is the MCP read tool for doc-code alignment.
- Out of scope: complete recovery of human design intent from code alone.
- Unsafe example must be escaped: <script>alert('x')</script>.

| Capability | Artifact |
| --- | --- |
| Document Quality Evaluator | architecture_doc_quality_summary.json |
| Doc-Code Alignment v2 | architecture_doc_code_alignment.jsonl |

GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims
""",
        "docs/V2.x/V2_7_TARGET_ARCHITECTURE.md": """# V2.7 Target Architecture

Architecture target.

## Components

- Document Asset Registry
- Architecture Claim Extractor
- Document Quality Evaluator
- Doc-Code Alignment v2
- Reconstructed Architecture Model
- Governance Overlay
""",
        "backend/app/api/v1/code_assets_architecture.py": """from fastapi import APIRouter

router = APIRouter(prefix="/workspaces")

@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment")
async def read_architecture_document_code_alignment(workspace_id: str, codebase_id: str):
    return {"ok": True}
""",
        "backend/data_service/code_assets/architecture/service.py": """class ArchitectureService:
    def build_document_quality(self, codebase_id: str) -> dict:
        return {"codebase_id": codebase_id}
""",
        "backend/data_service/mcp_code_architecture_tools.py": """ARCHITECTURE_TOOL_SPECS = [
    {"name": "knowledge_code_architecture_doc_code_alignment", "description": "Read V2.7 doc-code alignment"}
]
""",
        "backend/data_service/__main__.py": """import argparse


def build_parser():
    parser = argparse.ArgumentParser(prog="knowledge")
    subparsers = parser.add_subparsers(dest="command")
    code = subparsers.add_parser("code")
    code_subparsers = code.add_subparsers(dest="code_command")
    architecture = code_subparsers.add_parser("architecture")
    architecture_subparsers = architecture.add_subparsers(dest="architecture_command")
    architecture_subparsers.add_parser("docs-alignment")
    return parser
""",
        "docs/V2.x/V2_7_DOCUMENT_AUDIT_REPORT.md": "# V2.7 Document Audit Report\n\nAudit status.\n",
        "docs/V2.x/V2_7_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md": "# V2.7 Development and Acceptance Plan\n\nPlan.\n",
        "docs/V2.x/V2_7_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md": "# V2.7 Real Repo E2E Acceptance Matrix\n\nAcceptance.\n",
        "docs/V2.x/V2_6_TARGET_PRD.md": "# V2.6 Target PRD\n\nPrior phase target.\n",
        "docs/V2.x/V2_5_FULL_PRD_COVERAGE_MATRIX.md": "# V2.5 Full PRD Coverage Matrix\n\nPrior phase matrix.\n",
        "docs/design/V6.x/v6_target_architecture.md": "# HarnessOS V6 Target Architecture\n\nTarget planes.\n",
        "docs/design/V4.x/v4_headless_current_gap_analysis.drawio": """<mxfile>
  <diagram name="V4">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="a" value="Headless Workflow Plane" vertex="1" parent="1" />
        <mxCell id="b" value="External App Adapter" vertex="1" parent="1" />
        <mxCell id="e1" value="depends_on" edge="1" source="a" target="b" parent="1" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
""",
        "backend/app/main.py": "print('not a document candidate')\n",
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
    workspace_id = _create_workspace(client, "V27 Phase49")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, snapshot_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _by_path(documents: list[dict]) -> dict[str, dict]:
    return {str(item.get("path") or item["repo_path"]): item for item in documents}


def _assert_registry(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path) -> None:
    registry = payload["data"]["document_registry"] if "data" in payload else payload
    assert registry["schema_version"] == "v2.7"
    assert registry["workspace_id"] == workspace_id
    assert registry["codebase_id"] == codebase_id
    assert registry["snapshot_id"] == snapshot_id
    assert registry["summary"]["document_count"] >= 9
    assert registry["artifact_refs"]
    assert registry["documents"]
    assert registry["sources"]

    serialized = json.dumps(registry, ensure_ascii=False)
    assert str(repo) not in serialized

    docs = _by_path(registry["documents"])
    prd = docs["docs/V2.x/V2_7_TARGET_PRD.md"]
    assert prd["doc_type"] == "prd"
    assert prd["authority_role"] == "target"
    assert prd["authority_level"] == "primary"
    assert prd["stale_hint"] is False
    assert (prd["evidence"][0].get("path") or prd["evidence"][0]["repo_path"]) == "docs/V2.x/V2_7_TARGET_PRD.md"
    assert prd["repo_path"] == "docs/V2.x/V2_7_TARGET_PRD.md"
    assert prd["evidence"][0]["repo_path"] == "docs/V2.x/V2_7_TARGET_PRD.md"
    assert prd["evidence"][0]["line_range"] == [1, 1]

    target = docs["docs/V2.x/V2_7_TARGET_ARCHITECTURE.md"]
    assert target["doc_type"] == "target_architecture"
    assert target["authority_role"] == "target"
    assert target["authority_level"] == "primary"

    audit = docs["docs/V2.x/V2_7_DOCUMENT_AUDIT_REPORT.md"]
    assert audit["doc_type"] == "audit_report"
    assert audit["authority_role"] == "audit_status"
    assert audit["authority_level"] == "supporting"

    old_prd = docs["docs/V2.x/V2_6_TARGET_PRD.md"]
    assert old_prd["authority_role"] == "historical_reference"
    assert old_prd["authority_level"] == "historical"
    assert old_prd["stale_hint"] is True

    drawio = docs["docs/design/V4.x/v4_headless_current_gap_analysis.drawio"]
    assert drawio["doc_type"] == "drawio"
    assert drawio["authority_role"] == "historical_reference"
    assert drawio["authority_level"] == "historical"
    assert any(source["doc_id"] == drawio["doc_id"] and source["source_type"] == "drawio" for source in registry["sources"])


def test_v27_phase49_document_registry_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)

    direct = service.build_document_registry(codebase_id, snapshot_id=snapshot_id)
    assert architecture_docs_path(workspace, codebase_id).exists()
    assert architecture_doc_sources_path(workspace, codebase_id).exists()
    assert architecture_docs_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_doc_sources_path(workspace, codebase_id).stat().st_size > 0
    _assert_registry({"data": {"document_registry": service.read_document_registry(codebase_id)}}, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    repeat = service.build_document_registry(codebase_id, snapshot_id=snapshot_id)
    assert [item["doc_id"] for item in direct["documents"]] == [item["doc_id"] for item in repeat["documents"]]

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    _assert_registry(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs")
    assert http_read.status_code == 200
    _assert_registry(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_docs_list", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_registry(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    assert knowledge_main(["code", "architecture", "docs", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_registry(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)


def test_v27_phase49_document_registry_missing_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, _snapshot_id, _repo = _prepare(tmp_path, monkeypatch)

    service = ArchitectureService(workspace, workspace_id=workspace_id)
    missing = service.read_document_registry
    try:
        missing(codebase_id)
    except FileNotFoundError as exc:
        assert "ARCHITECTURE_DOCS_NOT_BUILT" in str(exc)
    else:
        raise AssertionError("read_document_registry should fail before docs-build")

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOCS_NOT_BUILT"


def _assert_claims(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path) -> None:
    claims_payload = payload["data"]["document_claims"] if "data" in payload else payload
    assert claims_payload["schema_version"] == "v2.7"
    assert claims_payload["workspace_id"] == workspace_id
    assert claims_payload["codebase_id"] == codebase_id
    assert claims_payload["snapshot_id"] == snapshot_id
    assert claims_payload["summary"]["claim_count"] >= 10
    assert claims_payload["summary"]["relation_count"] >= 1
    assert claims_payload["artifact_refs"]

    serialized = json.dumps(claims_payload, ensure_ascii=False)
    assert str(repo) not in serialized

    claims = claims_payload["claims"]
    relations = claims_payload["relations"]
    assert all(item["doc_id"] for item in claims)
    assert all(item["source_path"] == item["repo_path"] for item in claims)
    assert all(item["evidence"] for item in claims)
    assert all(item["confidence"] <= 0.9 for item in claims)

    labels = {item["label"] for item in claims}
    assert "V2.7 Target PRD" in labels
    assert "Document Asset Registry registers project architecture documents." in labels
    assert "Acceptance: every accepted claim has document evidence." in labels
    assert "Out of scope: complete recovery of human design intent from code alone." in labels
    assert any(item["source_block_type"] == "table_row" and "Document Quality Evaluator" in item["label"] for item in claims)
    assert any(item["source_block_type"] == "interface_list" and item["claim_type"] == "public_interface" for item in claims)
    assert any(item["source_block_type"] == "non_goal" and item["claim_type"] == "non_goal" for item in claims)
    assert any(item["source_block_type"] == "acceptance_gate" and item["claim_type"] == "acceptance_gate" for item in claims)

    drawio_claims = [item for item in claims if item["source_path"].endswith(".drawio")]
    assert any(item["label"] == "Headless Workflow Plane" for item in drawio_claims)
    assert all(item["confidence"] <= 0.7 for item in drawio_claims)
    assert all(item["needs_review"] for item in drawio_claims)
    assert any(item["relation_type"] == "depends_on" for item in relations)
    claim_ids = {item["claim_id"] for item in claims}
    assert all(item["from_claim_id"] in claim_ids and item["to_claim_id"] in claim_ids for item in relations)


def test_v27_phase50_document_claims_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_document_registry(codebase_id, snapshot_id=snapshot_id)

    direct = service.build_document_claims(codebase_id)
    assert architecture_doc_claims_path(workspace, codebase_id).exists()
    assert architecture_doc_relations_path(workspace, codebase_id).exists()
    assert architecture_doc_claims_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_doc_relations_path(workspace, codebase_id).stat().st_size > 0
    _assert_claims(service.read_document_claims(codebase_id), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    repeat = service.build_document_claims(codebase_id)
    assert [item["claim_id"] for item in direct["claims"]] == [item["claim_id"] for item in repeat["claims"]]

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims/build")
    assert http_build.status_code == 200
    _assert_claims(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims")
    assert http_read.status_code == 200
    _assert_claims(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_doc_claims", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_claims(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    assert knowledge_main(["code", "architecture", "docs-claims", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_claims(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)


def test_v27_phase50_claims_missing_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    ArchitectureService(workspace, workspace_id=workspace_id).build_document_registry(codebase_id, snapshot_id=snapshot_id)

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT"


def _assert_quality(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path) -> None:
    quality = payload["data"]["document_quality"] if "data" in payload else payload
    assert quality["schema_version"] == "v2.7"
    assert quality["workspace_id"] == workspace_id
    assert quality["codebase_id"] == codebase_id
    assert quality["snapshot_id"] == snapshot_id
    assert quality["artifact_refs"]
    summary = quality["summary"]
    findings = quality["findings"]
    assert summary["document_count"] >= 9
    assert summary["claim_count"] >= 10
    assert summary["finding_count"] == len(findings)
    assert summary["severity_counts"]
    assert summary["finding_type_counts"]
    assert summary["overall_status"] != "high_quality"
    if summary["severity_counts"].get("major", 0) or summary["severity_counts"].get("fatal", 0):
        assert summary["overall_status"] in {"needs_review", "blocked"}
    assert any(item["finding_type"] == "low_confidence_claim" for item in findings)
    assert any(item["finding_type"] in {"missing_acceptance_gate", "status_conflict", "overbroad_architecture_claim"} for item in findings)
    assert all(item["target_id"] for item in findings)
    assert all(item["evidence"] or item["needs_review"] for item in findings)
    serialized = json.dumps(quality, ensure_ascii=False)
    assert str(repo) not in serialized


def test_v27_phase51_document_quality_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_document_registry(codebase_id, snapshot_id=snapshot_id)
    service.build_document_claims(codebase_id)

    direct = service.build_document_quality(codebase_id)
    assert architecture_doc_quality_findings_path(workspace, codebase_id).exists()
    assert architecture_doc_quality_summary_path(workspace, codebase_id).exists()
    assert architecture_doc_quality_findings_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_doc_quality_summary_path(workspace, codebase_id).stat().st_size > 0
    _assert_quality(service.read_document_quality(codebase_id), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    repeat = service.build_document_quality(codebase_id)
    assert direct["summary"]["finding_count"] == repeat["summary"]["finding_count"]

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality/build")
    assert http_build.status_code == 200
    _assert_quality(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality")
    assert http_read.status_code == 200
    _assert_quality(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_doc_quality", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_quality(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    assert knowledge_main(["code", "architecture", "docs-quality", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_quality(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)


def test_v27_phase51_quality_missing_claims_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    ArchitectureService(workspace, workspace_id=workspace_id).build_document_registry(codebase_id, snapshot_id=snapshot_id)

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality/build")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT"

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOC_QUALITY_NOT_BUILT"


def _prepare_alignment_artifacts(workspace: Path, workspace_id: str, codebase_id: str, snapshot_id: str) -> ArchitectureService:
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(codebase_id, snapshot_id=snapshot_id)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_document_registry(codebase_id, snapshot_id=snapshot_id)
    service.build_document_claims(codebase_id)
    service.build_document_quality(codebase_id)
    return service


def _assert_alignment(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path) -> None:
    alignment = payload["data"]["document_code_alignment"] if "data" in payload else payload
    assert alignment["schema_version"] == "v2.7"
    assert alignment["workspace_id"] == workspace_id
    assert alignment["codebase_id"] == codebase_id
    assert alignment["snapshot_id"] == snapshot_id
    assert alignment["artifact_refs"]
    assert alignment["alignments"]
    assert alignment["drift"]
    summary = alignment["summary"]
    assert summary["alignment_count"] == len(alignment["alignments"])
    assert summary["drift_count"] == len(alignment["drift"])
    assert summary["token_overlap_only_accepted"] is False
    assert summary["status_counts"]
    assert summary["drift_type_counts"].get("code_not_documented", 0) >= 1
    assert any(item["status"] == "matched" and item["match_strategy"] in {"exact_surface_id", "exact_symbol_id", "capability_id_match"} for item in alignment["alignments"])
    assert any(item["status"] in {"weak_match", "designed_not_found_in_code"} for item in alignment["alignments"])
    for item in alignment["alignments"]:
        if item["status"] == "matched":
            assert item["confidence"] >= 0.8
            assert item["match_strategy"] != "token_overlap_only"
            assert item["document_evidence"]
            assert item["code_evidence"]
            assert not item["needs_review"]
        if item["match_strategy"] == "token_overlap_only":
            assert item["status"] != "matched"
            assert item["confidence"] < 0.8
    assert all(item["code_evidence"] or item["document_evidence"] or item["needs_review"] for item in alignment["drift"])
    assert str(repo) not in json.dumps(alignment, ensure_ascii=False)


def test_v27_phase52_document_code_alignment_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    direct = service.build_document_code_alignment(codebase_id)
    assert architecture_doc_code_alignment_path(workspace, codebase_id).exists()
    assert architecture_doc_code_drift_v2_path(workspace, codebase_id).exists()
    assert architecture_doc_code_alignment_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_doc_code_drift_v2_path(workspace, codebase_id).stat().st_size > 0
    _assert_alignment(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment/build")
    assert http_build.status_code == 200
    _assert_alignment(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment")
    assert http_read.status_code == 200
    _assert_alignment(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_doc_code_alignment", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_alignment(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    assert knowledge_main(["code", "architecture", "docs-alignment", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_alignment(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)


def test_v27_phase52_alignment_missing_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT"


def _prepare_reconstruction_artifacts(workspace: Path, workspace_id: str, codebase_id: str, snapshot_id: str) -> ArchitectureService:
    service = _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_document_code_alignment(codebase_id)
    return service


def _assert_reconstruction(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path) -> None:
    reconstructed = payload["data"]["reconstructed_architecture"] if "data" in payload else payload
    assert reconstructed["schema_version"] == "v2.7"
    assert reconstructed["workspace_id"] == workspace_id
    assert reconstructed["codebase_id"] == codebase_id
    assert reconstructed["snapshot_id"] == snapshot_id
    assert reconstructed["artifact_refs"]
    summary = reconstructed["summary"]
    assert summary["target_node_count"] >= 1
    assert summary["current_node_count"] >= 1
    assert summary["diff_node_count"] >= 1
    assert summary["edge_count"] >= 1
    assert set(reconstructed["sections"]) == {"target_from_documents", "current_from_code", "gap_and_drift"}
    assert reconstructed["target_nodes"]
    assert reconstructed["current_nodes"]
    assert reconstructed["diff_nodes"]
    assert any(item["source_kind"] == "document_claim" for item in reconstructed["target_nodes"])
    assert any(item["source_kind"] == "code_fact" for item in reconstructed["current_nodes"])
    assert any(item["source_kind"] in {"alignment", "quality_finding"} for item in reconstructed["diff_nodes"])
    assert not any(item["source_kind"] == "code_fact" and item["label"] == "Headless Workflow Plane" for item in reconstructed["current_nodes"])
    rendered_ids = set(summary["rendered_node_ids"])
    for collection in (reconstructed["target_nodes"], reconstructed["current_nodes"], reconstructed["diff_nodes"]):
        assert all(item["node_id"] in rendered_ids for item in collection)
        assert all(item["source_refs"] for item in collection)
    edge_nodes = {edge["from_node_id"] for edge in reconstructed["edges"]} | {edge["to_node_id"] for edge in reconstructed["edges"]}
    assert edge_nodes <= rendered_ids
    assert str(repo) not in json.dumps(reconstructed, ensure_ascii=False)


def test_v27_phase53_reconstructed_architecture_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_reconstruction_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    direct = service.build_reconstructed_architecture(codebase_id)
    assert architecture_reconstructed_model_path(workspace, codebase_id).exists()
    html_path = architecture_doc_view_path(workspace, codebase_id, "document_code_architecture_report.html")
    mermaid_path = architecture_doc_view_path(workspace, codebase_id, "document_code_architecture_diff.mmd")
    assert html_path.exists()
    assert mermaid_path.exists()
    assert html_path.stat().st_size > 0
    assert mermaid_path.stat().st_size > 0
    _assert_reconstruction(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    html = html_path.read_text(encoding="utf-8")
    mermaid = mermaid_path.read_text(encoding="utf-8")
    assert "Architecture Relationship Overview" in html
    assert 'role="img" aria-label="Architecture relationship overview"' in html
    assert "Target Architecture from Documents" in html
    assert "Current Architecture from Code" in html
    assert "Gaps and Drift" in html
    assert "<script>alert" not in html
    escaped_smoke = render_reconstructed_architecture_html(
        {
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "summary": {},
            "target_nodes": [{"node_id": "target:unsafe", "node_type": "component", "label": "<script>alert('x')</script>", "source_kind": "document_claim", "confidence": 0.5, "needs_review": []}],
            "current_nodes": [],
            "diff_nodes": [],
        }
    )
    assert "<script>alert" not in escaped_smoke
    assert "&lt;script&gt;alert" in escaped_smoke
    assert str(repo) not in html
    assert str(repo) not in mermaid
    assert "flowchart LR" in mermaid
    assert "%% n0=" in mermaid
    assert "Headless Workflow Plane" in json.dumps(direct, ensure_ascii=False)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed/build")
    assert http_build.status_code == 200
    _assert_reconstruction(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed")
    assert http_read.status_code == 200
    _assert_reconstruction(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/views/document_code_architecture_report.html")
    assert http_view.status_code == 200
    view = _v2(http_view.json())["data"]["view"]
    assert view["content_type"] == "text/html"
    assert "Target Architecture from Documents" in view["content"]
    assert "<script>alert" not in view["content"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_reconstructed", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_reconstruction(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)
    mcp_view = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_doc_view", {"workspace_id": workspace_id, "codebase_id": codebase_id, "view_id": "document_code_architecture_diff.mmd"}))
    assert _v2(mcp_view)["data"]["view"]["content_type"] == "text/mermaid"

    assert knowledge_main(["code", "architecture", "docs-reconstructed", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_reconstruction(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo)

    assert knowledge_main(["code", "architecture", "docs-view", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--view-id", "document_code_architecture_diff.mmd"]) == 0
    cli_view = json.loads(capsys.readouterr().out)
    assert _v2(cli_view)["data"]["view"]["content_type"] == "text/mermaid"


def test_v27_phase53_reconstruction_missing_alignment_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    try:
        service.build_reconstructed_architecture(codebase_id)
    except FileNotFoundError as exc:
        assert "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT" in str(exc)
    else:
        raise AssertionError("build_reconstructed_architecture should fail before alignment is built")

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed/build")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT"

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v27_phase54_governance_overlay_for_document_code_targets(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_reconstruction_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_document_code_alignment(codebase_id)
    model = service.build_reconstructed_architecture(codebase_id)
    claim_id = service.read_document_claims(codebase_id)["claims"][0]["claim_id"]
    alignment = next(item for item in service.read_document_code_alignment(codebase_id)["alignments"] if item["status"] in {"matched", "weak_match", "designed_not_found_in_code"})
    node_id = model["target_nodes"][0]["node_id"]

    guarded_paths = [
        architecture_doc_claims_path(workspace, codebase_id),
        architecture_doc_code_alignment_path(workspace, codebase_id),
        architecture_reconstructed_model_path(workspace, codebase_id),
    ]
    before_hashes = {str(path): _sha256(path) for path in guarded_paths}

    quality = CodeQualityService(workspace, workspace_id=workspace_id)
    feedback_claim = quality.record_feedback(
        codebase_id,
        target_type="architecture_doc_claim",
        target_id=claim_id,
        action="needs_review",
        rule_type="overbroad_architecture_claim",
        severity="major",
        reason="Claim needs tighter evidence.",
    )["feedback"]
    assert feedback_claim["resolved_target"]["claim_id"] == claim_id
    feedback_alignment = quality.record_feedback(
        codebase_id,
        target_type="architecture_doc_code_alignment",
        target_id=alignment["alignment_id"],
        action="needs_review",
        rule_type="doc_code_mismatch",
        severity="major",
        reason="Alignment should be reviewed.",
    )["feedback"]
    assert feedback_alignment["resolved_target"]["alignment_id"] == alignment["alignment_id"]
    feedback_node = quality.record_feedback(
        codebase_id,
        target_type="architecture_reconstructed_node",
        target_id=node_id,
        action="needs_review",
        rule_type="wrong_target_current_split",
        severity="medium",
        reason="Node split should be governed in read output.",
    )["feedback"]
    assert feedback_node["resolved_target"]["node_type"]

    public_claim_id = service.read_document_claims(codebase_id)["claims"][1]["claim_id"]
    http_feedback = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback",
        json={
            "target_type": "architecture_doc_claim",
            "target_id": public_claim_id,
            "action": "needs_review",
            "rule_type": "missing_evidence",
            "severity": "minor",
            "reason": "Public HTTP governance smoke for V2.7 target.",
        },
    )
    assert http_feedback.status_code == 200
    assert _v2(http_feedback.json())["data"]["feedback"]["resolved_target"]["claim_id"] == public_claim_id

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_summary = asyncio.run(dispatcher.call_tool("knowledge_code_quality_summary", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_summary)["data"]["summary"]["feedback_count"] >= 4

    assert knowledge_main(["code", "quality", "summary", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_summary = json.loads(capsys.readouterr().out)
    assert _v2(cli_summary)["data"]["summary"]["feedback_count"] >= 4

    try:
        quality.record_feedback(codebase_id, target_type="architecture_doc_claim", target_id="missing-claim", action="needs_review", rule_type="missing_evidence")
    except FileNotFoundError as exc:
        assert "QUALITY_TARGET_NOT_FOUND" in str(exc)
    else:
        raise AssertionError("missing V2.7 governance target should be rejected")

    rules = quality.build_rules(codebase_id)["rules"]
    claim_rule = next(rule for rule in rules if rule["target_id"] == claim_id)
    alignment_rule = next(rule for rule in rules if rule["target_id"] == alignment["alignment_id"])
    node_rule = next(rule for rule in rules if rule["target_id"] == node_id)
    quality.review_rule(codebase_id, claim_rule["rule_id"], status="approved", reviewer="phase54")
    quality.review_rule(codebase_id, alignment_rule["rule_id"], status="approved", reviewer="phase54")
    quality.review_rule(codebase_id, node_rule["rule_id"], status="approved", reviewer="phase54")
    plan = quality.build_plan(codebase_id)["plan"]
    assert {claim_rule["rule_id"], alignment_rule["rule_id"], node_rule["rule_id"]} <= set(plan["approved_rule_ids"])
    assert all(item["target_id"] for item in plan["impacted_targets"])

    governed_claims = service.read_document_claims(codebase_id)
    governed_alignment = service.read_document_code_alignment(codebase_id)
    governed_model = service.read_reconstructed_architecture(codebase_id)
    governed_view = service.read_document_architecture_view(codebase_id, "document_code_architecture_report.html")
    governed_claim = next(item for item in governed_claims["claims"] if item["claim_id"] == claim_id)
    governed_alignment_row = next(item for item in governed_alignment["alignments"] if item["alignment_id"] == alignment["alignment_id"])
    governed_node = next(item for item in governed_model["target_nodes"] if item["node_id"] == node_id)
    assert claim_rule["rule_id"] in governed_claim["applied_rules"]
    assert alignment_rule["rule_id"] in governed_alignment_row["applied_rules"]
    assert node_rule["rule_id"] in governed_node["applied_rules"]
    assert node_rule["rule_id"] in governed_view["applied_rules"]
    assert governed_model["governance_status"] == "governed"

    for path in guarded_paths:
        assert _sha256(path) == before_hashes[str(path)]

    quality.review_rule(codebase_id, claim_rule["rule_id"], status="revoked", reviewer="phase54")
    quality.review_rule(codebase_id, alignment_rule["rule_id"], status="revoked", reviewer="phase54")
    quality.review_rule(codebase_id, node_rule["rule_id"], status="revoked", reviewer="phase54")
    revoked_plan = quality.build_plan(codebase_id)["plan"]
    assert claim_rule["rule_id"] not in revoked_plan["approved_rule_ids"]
    assert not service.read_reconstructed_architecture(codebase_id)["applied_rules"]
    for path in guarded_paths:
        assert _sha256(path) == before_hashes[str(path)]
