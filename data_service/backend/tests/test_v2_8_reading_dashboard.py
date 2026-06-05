from __future__ import annotations

import asyncio
import json
import re

from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.reading_dashboard import render_architecture_reading_dashboard_html
from data_service.code_assets.artifacts import architecture_code_fact_chains_v28_path, architecture_context_pack_v28_path, architecture_graph_clusters_v28_path, architecture_graph_summary_v28_path, architecture_graph_view_v28_path, architecture_intent_evidence_v28_path, architecture_reading_dashboard_path, architecture_review_queue_v2_v28_path, architecture_runtime_boundaries_v28_path, architecture_signal_ranking_v28_path, architecture_v28_view_path
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _prepare_alignment_artifacts, _v2


REQUIRED_CHART_IDS = {
    "architecture_overview",
    "capability_map",
    "doc_code_drift_map",
    "quality_severity",
    "evidence_coverage",
    "hotspot_table",
}


def _prepare_v28_artifacts(workspace, workspace_id: str, codebase_id: str, snapshot_id: str):
    service = _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_document_code_alignment(codebase_id)
    service.build_reconstructed_architecture(codebase_id)
    return service


def _assert_dashboard(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo_path: str) -> None:
    dashboard = payload["data"]["reading_dashboard"] if "data" in payload else payload
    assert dashboard["schema_version"] == "v2.8"
    assert dashboard["workspace_id"] == workspace_id
    assert dashboard["codebase_id"] == codebase_id
    assert dashboard["snapshot_id"] == snapshot_id
    assert dashboard["dashboard_id"].startswith("v28_")
    assert dashboard["summary"]["chart_count"] >= 6
    assert dashboard["summary"]["target_node_count"] >= 1
    assert dashboard["summary"]["current_node_count"] >= 1
    assert dashboard["summary"]["diff_node_count"] >= 1
    assert dashboard["summary"]["view_ids"] == ["architecture_reading_dashboard.html", "architecture_relationship_summary.mmd"]
    assert REQUIRED_CHART_IDS <= {item["chart_id"] for item in dashboard["charts"]}
    assert dashboard["first_screen"]["one_liner"]
    assert dashboard["artifact_refs"]
    assert str(repo_path) not in json.dumps(dashboard, ensure_ascii=False)


def _assert_html(payload: dict, *, repo_path: str) -> None:
    view = payload["data"]["view"] if "data" in payload else payload
    html = view["content"]
    assert view["schema_version"] == "v2.8"
    assert view["content_type"] == "text/html"
    assert "Architecture Reading Dashboard" in html
    for chart_id in REQUIRED_CHART_IDS:
        assert f'id="{chart_id}"' in html
    assert "<script>" not in html
    assert "<script>alert" not in html
    assert str(repo_path) not in html


def _assert_mermaid(payload: dict, *, repo_path: str) -> None:
    view = payload["data"]["view"] if "data" in payload else payload
    mermaid = view["content"]
    assert view["schema_version"] == "v2.8"
    assert view["content_type"] == "text/mermaid"
    assert mermaid.startswith("flowchart LR")
    assert "%% persisted_dashboard_id" in mermaid
    assert "<script>" not in mermaid
    assert str(repo_path) not in mermaid


def _assert_graph_summary(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str) -> None:
    graph = payload["data"]["graph_summary"] if "data" in payload else payload
    summary = graph["summary"]
    assert summary["schema_version"] == "v2.8"
    assert summary["workspace_id"] == workspace_id
    assert summary["codebase_id"] == codebase_id
    assert summary["snapshot_id"] == snapshot_id
    assert summary["node_count"] >= 1
    assert summary["cluster_count"] >= 1
    assert summary["unsupported_edge_count"] == 0
    assert {"system_overview", "layer_view", "capability_view", "public_surface_view", "doc_code_drift_view", "evidence_view"} <= set(summary["view_ids"])
    clusters = graph["clusters"]["clusters"] if isinstance(graph.get("clusters"), dict) else graph["clusters"]
    assert clusters
    for cluster in clusters:
        assert cluster["cluster_id"]
        assert cluster["member_node_ids"]
        assert cluster["source_artifact_refs"] or cluster["needs_review"] is not None


def _assert_graph_view(payload: dict, *, view_id: str, snapshot_id: str) -> None:
    view = payload["data"]["graph_view"] if "data" in payload else payload
    assert view["schema_version"] == "v2.8"
    assert view["snapshot_id"] == snapshot_id
    assert view["view_id"] == view_id
    assert view["nodes"]
    assert view["clusters"]
    for node in view["nodes"]:
        assert node["primary_cluster_id"]
        assert node["cluster_memberships"]
        assert "source_artifact_refs" in node
        assert "evidence_refs" in node


def _assert_code_fact_chains(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str) -> None:
    chains_payload = payload["data"]["code_fact_chains"] if "data" in payload else payload
    summary = chains_payload["summary"]
    assert summary["schema_version"] == "v2.8"
    assert summary["workspace_id"] == workspace_id
    assert summary["codebase_id"] == codebase_id
    assert summary["snapshot_id"] == snapshot_id
    assert summary["chain_count"] >= 1
    assert summary["accepted_chain_count"] >= 1
    assert summary["runtime_boundary_count"] >= 1
    chains = chains_payload["chains"]
    assert any(item["chain_type"] == "http_route_chain" for item in chains)
    assert any(item["chain_type"] == "mcp_tool_chain" for item in chains)
    assert any(item["chain_type"] == "cli_command_chain" for item in chains)
    for chain in chains:
        assert chain["chain_type"] in {"http_route_chain", "mcp_tool_chain", "cli_command_chain", "config_runtime_boundary", "import_dependency_cluster", "test_reference_chain"}
        assert chain["status"] in {"accepted", "inferred", "needs_review", "unresolved"}
        for step in chain["steps"]:
            assert step["relation_type"] != "imports_module" or chain["status"] != "accepted"
        if chain["status"] == "accepted":
            assert chain["source_files"]
            assert chain["line_ranges"]
            assert chain["evidence_refs"]
            assert not chain["needs_review"]
    for boundary in chains_payload["runtime_boundaries"]:
        assert boundary["boundary_type"] in {"http_server", "mcp_stdio", "cli", "frontend_static", "local_file_storage", "external_provider", "database", "test_runtime", "unknown"}
        assert boundary["status"] in {"deterministic", "inferred", "needs_review"}
        if boundary["status"] == "deterministic":
            assert boundary["evidence_refs"]


def _assert_signal_ranking(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str) -> None:
    ranking_payload = payload["data"]["signal_ranking"] if "data" in payload else payload
    ranking = ranking_payload["ranking"]
    queue = ranking_payload["review_queue_v2"]
    assert ranking["schema_version"] == "v2.8"
    assert ranking["workspace_id"] == workspace_id
    assert ranking["codebase_id"] == codebase_id
    assert ranking["snapshot_id"] == snapshot_id
    assert ranking["items"]
    assert queue["items"]
    scores = [item["score"] for item in ranking["items"]]
    assert scores == sorted(scores, reverse=True) or any(item.get("pinned") for item in ranking["items"][:3])
    assert ranking["summary"]["weak_evidence_promoted"] is False
    for item in ranking["items"][:20]:
        assert item["ranking_id"]
        assert item["score_components"]
        assert item["reason_codes"]
        if item["severity"] in {"fatal", "major"}:
            assert item["pinned"] is True
            assert item["blocked_by_major_findings"] is True
    assert all(item["reason_codes"] for item in queue["items"][:20])


def _assert_intent_evidence(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str) -> None:
    intent_payload = payload["data"]["intent_evidence"] if "data" in payload else payload
    summary = intent_payload["summary"]
    assert summary["schema_version"] == "v2.8"
    assert summary["workspace_id"] == workspace_id
    assert summary["codebase_id"] == codebase_id
    assert summary["snapshot_id"] == snapshot_id
    assert summary["intent_count"] >= 1
    assert summary["pure_code_human_intent_claimed"] is False
    assert {"documented_intent", "code_observed"} & set(summary["intent_type_counts"])
    for item in intent_payload["intents"][:80]:
        assert item["intent_id"]
        assert item["intent_type"] in {"documented_intent", "code_observed", "audit_accepted", "mismatch", "needs_review"}
        assert item["evidence_refs"] or item["claim_refs"] or item["code_refs"] or item["audit_refs"] or item["needs_review"]
    drawio_intents = [
        item
        for item in intent_payload["intents"]
        if any(review.get("code") == "DRAWIO_ONLY_INTENT" for review in item.get("needs_review", []))
    ]
    if drawio_intents:
        assert all(item["intent_type"] == "documented_intent" for item in drawio_intents)


def _assert_context_pack(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, mode: str) -> None:
    pack = payload["data"]["architecture_context_pack"] if "data" in payload else payload
    assert pack["schema_version"] == "v2.8"
    assert pack["workspace_id"] == workspace_id
    assert pack["codebase_id"] == codebase_id
    assert pack["snapshot_id"] == snapshot_id
    assert pack["mode"] == mode
    assert pack["pack_id"]
    assert pack["sections"]
    assert pack["items"]
    assert pack["source_artifact_refs"]
    assert pack["artifact_refs"]
    assert "Architecture Context Pack" in pack["content"]
    assert pack["token_estimate"] <= pack["max_tokens"] or pack["max_tokens"] < 12000
    required_types = {"project_brief", "ranked_signal", "code_fact_chain", "intent_evidence"}
    assert required_types & {item["item_type"] for item in pack["items"]}
    for item in pack["items"]:
        if item.get("recommendation"):
            assert item.get("evidence_refs") or item.get("needs_review")


def test_v28_phase56_renderer_escapes_untrusted_content():
    dashboard = {
        "schema_version": "v2.8",
        "workspace_id": "ws",
        "codebase_id": "cb",
        "snapshot_id": "snap",
        "first_screen": {"one_liner": "<script>alert('x')</script>"},
        "summary": {"target_node_count": 1, "current_node_count": 1, "diff_node_count": 1, "edge_count": 0, "quality_finding_count": 0, "alignment_count": 0, "drift_count": 0, "hotspot_count": 0},
        "charts": [
            {"chart_id": "architecture_overview", "values": {"target_nodes": 1, "current_nodes": 1, "diff_nodes": 1, "edges": 0, "quality_findings": 0}},
            {"chart_id": "capability_map", "values": {"<b>bad</b>": 1}},
            {"chart_id": "doc_code_drift_map", "values": {}},
            {"chart_id": "quality_severity", "values": {}},
            {"chart_id": "evidence_coverage", "values": {"with_source_refs": 1, "without_source_refs": 0}},
        ],
        "hotspots": [{"kind": "<img src=x>", "severity": "major", "label": "<script>alert(1)</script>", "source_refs": [], "needs_review": []}],
        "warnings": [],
        "unresolved": [],
    }
    html = render_architecture_reading_dashboard_html(dashboard)
    assert "&lt;script&gt;alert" in html
    assert "<script>alert" not in html
    assert "&lt;b&gt;bad&lt;/b&gt;" in html
    assert "<img src=x>" not in html


def test_v28_phase56_reading_dashboard_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_v28_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    direct = service.build_architecture_reading_dashboard(codebase_id)
    assert architecture_reading_dashboard_path(workspace, codebase_id).exists()
    assert architecture_v28_view_path(workspace, codebase_id, "architecture_reading_dashboard.html").exists()
    assert architecture_v28_view_path(workspace, codebase_id, "architecture_relationship_summary.mmd").exists()
    _assert_dashboard(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))
    _assert_html({"data": {"view": service.read_architecture_reading_view(codebase_id, "architecture_reading_dashboard.html")}}, repo_path=str(repo))
    _assert_mermaid({"data": {"view": service.read_architecture_reading_view(codebase_id, "architecture_relationship_summary.mmd")}}, repo_path=str(repo))

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views/build")
    assert http_build.status_code == 200
    _assert_dashboard(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views")
    assert http_read.status_code == 200
    _assert_dashboard(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_html = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views/architecture_reading_dashboard.html")
    assert http_html.status_code == 200
    _assert_html(_v2(http_html.json()), repo_path=str(repo))

    http_mermaid = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views/architecture_relationship_summary.mmd")
    assert http_mermaid.status_code == 200
    _assert_mermaid(_v2(http_mermaid.json()), repo_path=str(repo))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_views_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_dashboard(_v2(mcp_build), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))
    mcp_view = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_view_v2_8", {"workspace_id": workspace_id, "codebase_id": codebase_id, "view_id": "architecture_reading_dashboard.html"}))
    _assert_html(_v2(mcp_view), repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "views", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_dashboard(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "view-v2-8", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--view-id", "architecture_relationship_summary.mmd"]) == 0
    cli_view = json.loads(capsys.readouterr().out)
    _assert_mermaid(_v2(cli_view), repo_path=str(repo))


def test_v28_phase56_requires_reconstructed_model(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views/build")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT"


def test_v28_phase57_graph_aggregation_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_v28_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    direct = service.build_architecture_graph_summary(codebase_id)
    assert architecture_graph_summary_v28_path(workspace, codebase_id).exists()
    assert architecture_graph_clusters_v28_path(workspace, codebase_id).exists()
    assert architecture_graph_view_v28_path(workspace, codebase_id, "system_overview").exists()
    _assert_graph_summary(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)
    _assert_graph_view(service.read_architecture_graph_view(codebase_id, "system_overview"), view_id="system_overview", snapshot_id=snapshot_id)
    _assert_graph_view(service.read_architecture_graph_view(codebase_id, "doc_code_drift_view"), view_id="doc_code_drift_view", snapshot_id=snapshot_id)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/build")
    assert http_build.status_code == 200
    _assert_graph_summary(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph")
    assert http_read.status_code == 200
    _assert_graph_summary(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/views/evidence_view")
    assert http_view.status_code == 200
    _assert_graph_view(_v2(http_view.json()), view_id="evidence_view", snapshot_id=snapshot_id)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_summary = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_graph_summary", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_graph_summary(_v2(mcp_summary), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)
    mcp_view = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_graph_view", {"workspace_id": workspace_id, "codebase_id": codebase_id, "view_id": "system_overview"}))
    _assert_graph_view(_v2(mcp_view), view_id="system_overview", snapshot_id=snapshot_id)

    assert knowledge_main(["code", "architecture", "graph-v2-8", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_graph_summary(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    assert knowledge_main(["code", "architecture", "graph-view-v2-8", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--view-id", "doc_code_drift_view"]) == 0
    cli_view = json.loads(capsys.readouterr().out)
    _assert_graph_view(_v2(cli_view), view_id="doc_code_drift_view", snapshot_id=snapshot_id)


def test_v28_phase57_unsupported_graph_view_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_v28_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_architecture_graph_summary(codebase_id)

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/views/not_a_view")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_GRAPH_VIEW_NOT_FOUND"


def test_v28_phase58_code_fact_chains_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_v28_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    direct = service.build_code_fact_chains(codebase_id)
    assert architecture_code_fact_chains_v28_path(workspace, codebase_id).exists()
    assert architecture_runtime_boundaries_v28_path(workspace, codebase_id).exists()
    _assert_code_fact_chains(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains/build")
    assert http_build.status_code == 200
    _assert_code_fact_chains(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains")
    assert http_read.status_code == 200
    _assert_code_fact_chains(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_code_fact_chains", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_code_fact_chains(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    assert knowledge_main(["code", "architecture", "chains", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_code_fact_chains(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)


def test_v28_phase58_requires_inventory(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_document_code_alignment(codebase_id)
    service.build_reconstructed_architecture(codebase_id)
    # Remove only surfaces to preserve the reconstruction precondition while simulating missing chain input.
    from data_service.code_assets.artifacts import inventory_surfaces_path

    inventory_surfaces_path(workspace, codebase_id, snapshot_id).unlink()

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains/build")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "INVENTORY_NOT_FOUND"


def test_v28_phase59_60_ranking_and_intent_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_v28_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_architecture_reading_dashboard(codebase_id)
    service.build_architecture_graph_summary(codebase_id)
    service.build_code_fact_chains(codebase_id)

    direct_ranking = service.build_signal_ranking(codebase_id)
    assert architecture_signal_ranking_v28_path(workspace, codebase_id).exists()
    assert architecture_review_queue_v2_v28_path(workspace, codebase_id).exists()
    _assert_signal_ranking(direct_ranking, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    direct_intent = service.build_intent_evidence(codebase_id)
    assert architecture_intent_evidence_v28_path(workspace, codebase_id).exists()
    _assert_intent_evidence(direct_intent, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    http_ranking = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking/build")
    assert http_ranking.status_code == 200
    _assert_signal_ranking(_v2(http_ranking.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)
    http_ranking_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking")
    assert http_ranking_read.status_code == 200
    _assert_signal_ranking(_v2(http_ranking_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    http_intent = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/intent/build")
    assert http_intent.status_code == 200
    _assert_intent_evidence(_v2(http_intent.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)
    http_intent_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/intent")
    assert http_intent_read.status_code == 200
    _assert_intent_evidence(_v2(http_intent_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_ranking = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_ranking", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_signal_ranking(_v2(mcp_ranking), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)
    mcp_intent = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_intent_evidence", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_intent_evidence(_v2(mcp_intent), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    assert knowledge_main(["code", "architecture", "ranking", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_ranking = json.loads(capsys.readouterr().out)
    _assert_signal_ranking(_v2(cli_ranking), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)

    assert knowledge_main(["code", "architecture", "intent", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_intent = json.loads(capsys.readouterr().out)
    _assert_intent_evidence(_v2(cli_intent), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id)


def test_v28_phase59_ranking_requires_reconstructed_model(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking/build")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT"


def test_v28_phase61_context_pack_v2_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_v28_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_architecture_reading_dashboard(codebase_id)
    service.build_architecture_graph_summary(codebase_id)
    service.build_code_fact_chains(codebase_id)
    service.build_signal_ranking(codebase_id)
    service.build_intent_evidence(codebase_id)

    direct = service.create_architecture_context_pack_v2(codebase_id, mode="project_brief", max_tokens=12000)
    assert architecture_context_pack_v28_path(workspace, codebase_id, direct["pack_id"]).exists()
    _assert_context_pack(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, mode="project_brief")

    small = service.create_architecture_context_pack_v2(codebase_id, mode="task_context", task="update architecture ranking", max_tokens=700)
    _assert_context_pack(small, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, mode="task_context")
    assert small["omitted_items"]
    for item in small["items"]:
        if item.get("recommendation"):
            assert item.get("evidence_refs") or item.get("needs_review")

    http_create = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/context-pack",
        json={"mode": "task_context", "task": "inspect context pack", "max_tokens": 12000},
    )
    assert http_create.status_code == 200
    http_pack = _v2(http_create.json())["data"]["architecture_context_pack"]
    _assert_context_pack(http_pack, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, mode="task_context")

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/context-pack/{http_pack['pack_id']}")
    assert http_read.status_code == 200
    _assert_context_pack(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, mode="task_context")

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_pack = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_context_pack_v2", {"workspace_id": workspace_id, "codebase_id": codebase_id, "mode": "project_brief", "max_tokens": 12000}))
    _assert_context_pack(_v2(mcp_pack), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, mode="project_brief")
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_context_pack_read", {"workspace_id": workspace_id, "codebase_id": codebase_id, "pack_id": _v2(mcp_pack)["data"]["architecture_context_pack"]["pack_id"]}))
    _assert_context_pack(_v2(mcp_read), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, mode="project_brief")

    assert knowledge_main(["code", "architecture", "context-pack", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--mode", "project_brief"]) == 0
    cli_pack = json.loads(capsys.readouterr().out)
    _assert_context_pack(_v2(cli_pack), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, mode="project_brief")

    pack_id = _v2(cli_pack)["data"]["architecture_context_pack"]["pack_id"]
    assert knowledge_main(["code", "architecture", "context-pack-read", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--pack-id", pack_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    _assert_context_pack(_v2(cli_read), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, mode="project_brief")
