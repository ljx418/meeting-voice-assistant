from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.doc_code_alignment import build_document_code_alignment
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.artifacts import architecture_doc_code_alignment_path, architecture_doc_code_drift_v2_path
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _claim(claim_id: str, label: str, *, claim_type: str = "component", evidence: list[dict] | None = None, needs_review: list[dict] | None = None, doc_id: str = "doc_a") -> dict:
    return {
        "schema_version": "v2.7",
        "workspace_id": "ws",
        "codebase_id": "cb",
        "snapshot_id": "snap",
        "claim_id": claim_id,
        "doc_id": doc_id,
        "claim_type": claim_type,
        "label": label,
        "scope_hint": "scope-a",
        "source_block_type": "bullet",
        "confidence": 0.9,
        "needs_review": needs_review or [],
        "evidence": evidence if evidence is not None else [{"type": "source_file", "repo_path": "docs/arch.md", "line_range": [1, 1]}],
    }


def test_v27_phase52_alignment_strategy_rules():
    claims = [
        _claim("surface_exact", "http:POST:/api/workspaces/{workspace_id}/query", claim_type="public_interface"),
        _claim("symbol_exact", "py:function:pkg.module.run", claim_type="component"),
        _claim("capability_exact", "agent_context_pack", claim_type="public_interface"),
        _claim("role_match", "api_router component", claim_type="component"),
        _claim("taxonomy_match", "interface layer", claim_type="layer"),
        _claim("token_only", "Inventory Service", claim_type="component"),
        _claim("missing_doc_evidence", "Missing evidence claim", evidence=[]),
        _claim("missing_code", "Future Runtime Plane", claim_type="component"),
        _claim("stale_claim", "Stale target claim", claim_type="component", doc_id="doc_stale"),
    ]
    quality = {
        "findings": [
            {
                "finding_id": "stale_finding",
                "finding_type": "stale_document",
                "severity": "major",
                "doc_id": "doc_stale",
                "claim_id": "stale_claim",
            }
        ]
    }
    code_facts = {
        "surfaces": [
            {"surface_id": "http:POST:/api/workspaces/{workspace_id}/query", "surface_type": "http_api", "capability_id": "query", "source_file": "backend/app/api.py", "line_range": [10, 12]},
            {"surface_id": "mcp:knowledge_agent_context_pack", "surface_type": "mcp_tool", "capability_id": "agent_context_pack", "source_file": "backend/mcp.py", "line_range": [3, 3]},
        ],
        "symbols": [
            {"symbol_id": "py:function:pkg.module.run", "qualified_name": "pkg.module.run", "name": "run", "kind": "function", "path": "pkg/module.py", "line_range": [1, 2]},
            {"symbol_id": "py:class:pkg.inventory.InventoryService", "qualified_name": "pkg.inventory.InventoryService", "name": "InventoryService", "kind": "class", "path": "pkg/inventory.py", "line_range": [1, 10]},
            {"symbol_id": "py:function:pkg.undocumented.helper", "qualified_name": "pkg.undocumented.helper", "name": "helper", "kind": "function", "path": "pkg/undocumented.py", "line_range": [1, 2]},
        ],
        "roles": [{"role_id": "role_api", "role_type": "api_router", "name": "api router", "evidence": [{"repo_path": "backend/api.py", "line_range": [1, 1]}]}],
        "boundaries": [],
        "taxonomy": {"layer_types": [{"id": "interface", "name": "interface layer", "description": "Interface layer"}]},
    }

    payload = build_document_code_alignment(workspace_id="ws", codebase_id="cb", snapshot_id="snap", claims=claims, quality=quality, code_facts=code_facts)
    by_claim = {item["claim_id"]: item for item in payload["alignments"] if item["claim_id"]}

    assert by_claim["surface_exact"]["status"] == "matched"
    assert by_claim["surface_exact"]["match_strategy"] == "exact_surface_id"
    assert by_claim["symbol_exact"]["status"] == "matched"
    assert by_claim["symbol_exact"]["match_strategy"] == "exact_symbol_id"
    assert by_claim["capability_exact"]["status"] == "matched"
    assert by_claim["capability_exact"]["match_strategy"] == "capability_id_match"
    assert by_claim["role_match"]["match_strategy"] == "v24_role_boundary_match"
    assert by_claim["taxonomy_match"]["match_strategy"] == "v26_taxonomy_match"
    assert by_claim["token_only"]["status"] == "weak_match"
    assert by_claim["token_only"]["match_strategy"] == "token_overlap_only"
    assert by_claim["missing_doc_evidence"]["status"] == "doc_claim_without_evidence"
    assert by_claim["missing_code"]["status"] == "designed_not_found_in_code"
    assert by_claim["stale_claim"]["status"] == "stale_doc_claim"
    assert all(item["document_evidence"] and item["code_evidence"] and item["match_strategy"] != "token_overlap_only" for item in payload["alignments"] if item["status"] == "matched")
    assert any(item["status"] == "code_not_documented" for item in payload["alignments"])
    assert payload["summary"]["token_overlap_only_accepted"] is False if "token_overlap_only_accepted" in payload["summary"] else True


def _assert_alignment(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo_path: str) -> None:
    alignment = payload["data"]["document_code_alignment"] if "data" in payload else payload
    assert alignment["schema_version"] == "v2.7"
    assert alignment["workspace_id"] == workspace_id
    assert alignment["codebase_id"] == codebase_id
    assert alignment["snapshot_id"] == snapshot_id
    assert alignment["artifact_refs"]
    assert alignment["summary"]["alignment_count"] == len(alignment["alignments"])
    assert alignment["summary"]["drift_count"] == len(alignment["drift"])
    assert alignment["alignments"]
    assert alignment["drift"]
    assert all(item["document_evidence"] and item["code_evidence"] and item["match_strategy"] != "token_overlap_only" for item in alignment["alignments"] if item["status"] == "matched")
    assert any(item["status"] == "code_not_documented" for item in alignment["alignments"])
    assert repo_path not in json.dumps(alignment, ensure_ascii=False)


def test_v27_phase52_document_code_alignment_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_document_registry(codebase_id, snapshot_id=snapshot_id)
    service.build_document_claims(codebase_id)
    service.build_document_quality(codebase_id)

    direct = service.build_document_code_alignment(codebase_id)
    assert architecture_doc_code_alignment_path(workspace, codebase_id).exists()
    assert architecture_doc_code_drift_v2_path(workspace, codebase_id).exists()
    assert architecture_doc_code_alignment_path(workspace, codebase_id).stat().st_size > 0
    assert architecture_doc_code_drift_v2_path(workspace, codebase_id).stat().st_size > 0
    _assert_alignment(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment/build")
    assert http_build.status_code == 200
    _assert_alignment(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment")
    assert http_read.status_code == 200
    _assert_alignment(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_doc_code_alignment", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_alignment(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "docs-alignment", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_alignment(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))


def test_v27_phase52_alignment_requires_quality_artifacts(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)
    service.build_document_registry(codebase_id, snapshot_id=snapshot_id)
    service.build_document_claims(codebase_id)

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment/build")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOC_QUALITY_NOT_BUILT"
