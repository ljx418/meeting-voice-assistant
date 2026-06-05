from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.artifacts import architecture_context_pack_v29_path, architecture_human_review_report_v29_path, architecture_public_surface_evidence_v29_path
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _prepare_alignment_artifacts, _v2


def _prepare_v29(workspace, workspace_id: str, codebase_id: str, snapshot_id: str) -> ArchitectureService:
    service = _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_document_code_alignment(codebase_id)
    service.build_reconstructed_architecture(codebase_id)
    try:
        service.build_code_fact_chains(codebase_id)
    except FileNotFoundError:
        pass
    return service


def _assert_evidence(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo_path: str) -> None:
    evidence = payload["data"]["public_surface_evidence_v2"] if "data" in payload else payload
    assert evidence["schema_version"] == "v2.9"
    summary = evidence["summary"]
    assert summary["workspace_id"] == workspace_id
    assert summary["codebase_id"] == codebase_id
    assert summary["snapshot_id"] == snapshot_id
    assert summary["evidence_row_count"] >= 1
    assert summary["accepted_count"] >= 1
    accepted = [item for item in evidence["evidence"] if item["status"] == "accepted"]
    assert accepted
    for item in accepted[:20]:
        assert item["confidence"] >= 0.85
        assert item["truth_check"] == "passed"
        assert item["source_path"]
        assert len(item["line_range"]) == 2
        assert item["line_range"][0] > 0
        assert item["evidence_refs"]
    assert str(repo_path) not in json.dumps(evidence, ensure_ascii=False)


def _assert_relationships(payload: dict) -> None:
    relationships = payload["data"]["code_relationships_v2"] if "data" in payload else payload
    assert relationships["schema_version"] == "v2.9"
    summary = relationships["summary"]
    assert summary["relationship_count"] >= 1
    assert summary["unsupported_relationship_count"] == 0
    assert summary["forbidden_relationship_count"] == 0
    forbidden = {"runtime_calls", "data_flow", "control_flow", "type_inferred_dependency", "production_runtime_topology"}
    assert not {item["relation_type"] for item in relationships["relationships"]} & forbidden
    assert all(item["semantic_claim"] for item in relationships["relationships"])
    assert any(item["relation_type"] == "surface_handled_by" for item in relationships["relationships"])


def _assert_ranking(payload: dict) -> None:
    ranking_payload = payload["data"]["ranking_calibration_v2"] if "data" in payload else payload
    ranking = ranking_payload["ranking"]
    assert ranking["schema_version"] == "v2.9"
    assert ranking["items"]
    assert ranking["summary"]["hidden_major_count"] == 0
    assert ranking["summary"]["hidden_fatal_count"] == 0
    assert ranking["summary"]["weak_evidence_promoted"] is False
    for item in ranking["items"][:50]:
        assert item["reason_codes"]
        if item["severity"] in {"fatal", "major"}:
            assert item["pinned"] is True
            assert item["blocked_by_major_findings"] is True


def _assert_report(payload: dict, *, repo_path: str) -> None:
    report_payload = payload["data"]["human_review_report_v2"] if "data" in payload else payload
    report = report_payload["report"]
    assert report["schema_version"] == "v2.9"
    assert set(report["sections"]) == {"executive_summary", "capability_to_entrypoint_map", "module_cluster_map", "evidence_coverage_heatmap", "target_current_drift_board", "ranking_priority_lanes", "unresolved_needs_review_table"}
    assert report["summary"]["view_ids"] == ["architecture_capability_entrypoint_map.mmd", "architecture_evidence_heatmap.mmd", "architecture_human_review_report_v2.html"]
    assert report["renderer_consistency"]["html_introduces_unpersisted_facts"] is False
    assert report["renderer_consistency"]["mermaid_introduces_unpersisted_nodes"] is False
    assert str(repo_path) not in json.dumps(report_payload, ensure_ascii=False)


def _assert_view(payload: dict, *, repo_path: str) -> None:
    view = payload["data"]["view"] if "data" in payload else payload
    assert view["schema_version"] == "v2.9"
    assert view["content_type"] in {"text/html", "text/mermaid"}
    assert view["content"]
    assert "<script>" not in view["content"]
    assert str(repo_path) not in view["content"]


def _assert_context_pack(payload: dict, *, mode: str) -> None:
    pack_payload = payload["data"]["architecture_context_pack_v3"] if "data" in payload else payload
    pack = pack_payload["architecture_context_pack_v3"] if "architecture_context_pack_v3" in pack_payload else pack_payload
    assert pack["schema_version"] == "v2.9"
    assert pack["mode"] == mode
    assert pack["source_phase_refs"] == [63, 64, 65, 66]
    assert pack["recommendations"]
    assert all(item.get("evidence_refs") or item.get("needs_review") for item in pack["recommendations"])
    assert "Architecture Context Pack v3" in pack["content"]
    return pack


def test_v29_phase63_67_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_v29(workspace, workspace_id, codebase_id, snapshot_id)

    evidence = service.build_public_surface_evidence_v2(codebase_id, snapshot_id=snapshot_id)
    assert architecture_public_surface_evidence_v29_path(workspace, codebase_id).exists()
    _assert_evidence(evidence, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    relationships = service.build_code_relationships_v2(codebase_id)
    _assert_relationships(relationships)

    ranking = service.build_ranking_calibration_v2(codebase_id)
    _assert_ranking(ranking)

    report = service.build_human_review_report_v2(codebase_id)
    assert architecture_human_review_report_v29_path(workspace, codebase_id).exists()
    _assert_report(report, repo_path=str(repo))
    _assert_view(service.read_human_review_report_view_v2(codebase_id, "architecture_human_review_report_v2.html"), repo_path=str(repo))

    pack = service.create_architecture_context_pack_v3(codebase_id, mode="architecture_review", role="architecture_reviewer", task="review architecture evidence", max_tokens=800)
    assert architecture_context_pack_v29_path(workspace, codebase_id, pack["pack_id"]).exists()
    assert pack["omitted_items"]
    _assert_context_pack(pack, mode="architecture_review")

    http_evidence = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence")
    assert http_evidence.status_code == 200
    _assert_evidence(_v2(http_evidence.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_relationships = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships")
    assert http_relationships.status_code == 200
    _assert_relationships(_v2(http_relationships.json()))

    http_ranking = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking")
    assert http_ranking.status_code == 200
    _assert_ranking(_v2(http_ranking.json()))

    http_report = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report")
    assert http_report.status_code == 200
    _assert_report(_v2(http_report.json()), repo_path=str(repo))

    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report/views/architecture_capability_entrypoint_map.mmd")
    assert http_view.status_code == 200
    _assert_view(_v2(http_view.json()), repo_path=str(repo))

    http_pack = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack",
        json={"mode": "project_brief", "role": "maintainer", "max_tokens": 1200},
    )
    assert http_pack.status_code == 200
    pack_from_http = _assert_context_pack(_v2(http_pack.json()), mode="project_brief")

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_evidence_v2", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_evidence(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))
    mcp_pack = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_context_pack_v3_read", {"workspace_id": workspace_id, "codebase_id": codebase_id, "pack_id": pack_from_http["pack_id"]}))
    _assert_context_pack(_v2(mcp_pack), mode="project_brief")

    assert knowledge_main(["code", "architecture", "evidence-v2", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_evidence = json.loads(capsys.readouterr().out)
    _assert_evidence(_v2(cli_evidence), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "context-pack-v3-read", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--pack-id", pack_from_http["pack_id"]]) == 0
    cli_pack = json.loads(capsys.readouterr().out)
    _assert_context_pack(_v2(cli_pack), mode="project_brief")
