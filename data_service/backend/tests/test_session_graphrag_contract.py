import json
import os
from argparse import _SubParsersAction

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import _build_knowledge_parser, _run_parsed_args
from data_service.mcp_tool_registry import all_tool_specs


FORBIDDEN_CONTRACT_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "artifact_physical_path",
    "graphrag_cache_path",
    "cache_path",
    "physical_path",
    "internal_path",
    "debug_paths",
    "db_path",
    "path",
    "paths",
    "local_path",
    "source_path",
    "original_path",
}

SESSION_MCP_BASELINE = {
    "knowledge_session_build_cancel",
    "knowledge_session_build_start",
    "knowledge_session_build_status",
    "knowledge_session_close",
    "knowledge_session_create",
    "knowledge_session_delete",
    "knowledge_session_get",
    "knowledge_session_ingest",
    "knowledge_session_list",
    "knowledge_session_query",
}


def _assert_no_internal_paths(payload):
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                assert key not in FORBIDDEN_CONTRACT_KEYS
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)


def _assert_stable_artifact_ref(value: str, *, workspace_root: str):
    assert value
    assert not os.path.isabs(value)
    assert workspace_root not in value
    assert not value.endswith(".json")
    assert not value.endswith(".parquet")
    assert not value.endswith(".md")
    assert "/" in value
    assert "://" in value


def _subparser_action(parser):
    return next(action for action in parser._actions if isinstance(action, _SubParsersAction))


def _cli_inventory() -> dict[str, list[str]]:
    top_action = _subparser_action(_build_knowledge_parser())
    inventory = {}
    for command, child_parser in top_action.choices.items():
        nested_actions = [action for action in child_parser._actions if isinstance(action, _SubParsersAction)]
        inventory[command] = sorted(nested_actions[0].choices) if nested_actions else []
    return {command: inventory[command] for command in sorted(inventory)}


def _run_cli(args, capsys):
    parsed = _build_knowledge_parser().parse_args(args)
    code = _run_parsed_args(parsed)
    captured = capsys.readouterr()
    return code, captured


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_session(root, workspace_id: str, session_id: str, *, with_graph: bool = True) -> None:
    workspace = root / workspace_id
    lifecycle = workspace / "lifecycle"
    lifecycle.mkdir(parents=True, exist_ok=True)
    session = {
        "session_id": session_id,
        "workspace_id": workspace_id,
        "external_id": session_id,
        "session_type": "generic",
        "title": session_id,
        "status": "active",
        "created_at": "2026-05-14T00:00:00Z",
        "updated_at": "2026-05-14T00:01:00Z",
        "metadata": {"stable": "ok", "workspace_path": "/hidden/workspace"},
    }
    registry_path = lifecycle / "sessions.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {"items": []}
    registry["items"] = [item for item in registry.get("items", []) if item.get("session_id") != session_id] + [session]
    registry_path.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    session_dir = workspace / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    if not with_graph:
        return
    graph = {
        "graph_model_version": "session-graph-1.0",
        "workspace_id": workspace_id,
        "scope": "session",
        "session_id": session_id,
        "status": "ok",
        "nodes": [
            {"id": "entity:alpha", "type": "entity", "label": "Alpha", "metadata": {"cache_path": "/hidden/cache"}},
            {"id": "topic:plan", "type": "topic", "label": "Plan", "metadata": {"source_path": "/hidden/source"}},
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "entity:alpha",
                "target": "topic:plan",
                "type": "related",
                "weight": 0.8,
                "metadata": {"physical_path": "/hidden/artifact"},
            }
        ],
        "communities": [{"id": "community-1", "entity_ids": ["entity:alpha"], "summary": "Session community"}],
        "updated_at": "2026-05-14T00:02:00Z",
    }
    graph_path = session_dir / "graph" / "graph.json"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")


def _session_core(payload: dict) -> dict:
    session = payload["data"]["session"]
    return {
        "workspace_id": session["workspace_id"],
        "session_id": session["session_id"],
        "status": session["status"],
        "node_count": session["node_count"],
        "edge_count": session["edge_count"],
        "community_count": session["community_count"],
        "artifact_ref": session["artifact_ref"],
        "node_id": session["nodes"][0]["node_id"],
        "edge_source": session["edges"][0]["source_node_id"],
    }


def test_v16d1_session_graph_target_http_and_cli_core_projection_match(tmp_path, monkeypatch, capsys):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Contract")
    _write_session(root, workspace_id, "ksess_alpha")

    response = client.get(
        f"/api/workspaces/{workspace_id}/graph/session",
        params={"session_id": "ksess_alpha", "include_nodes": True, "include_edges": True, "node_limit": 1, "edge_limit": 1},
    )
    assert response.status_code == 200
    target_payload = response.json()
    _assert_no_internal_paths(target_payload)

    code, captured = _run_cli(
        [
            "graph",
            "session",
            "--workspace-root",
            str(root),
            "--workspace-id",
            workspace_id,
            "--session-id",
            "ksess_alpha",
            "--include-nodes",
            "--include-edges",
            "--node-limit",
            "1",
            "--edge-limit",
            "1",
            "--json",
        ],
        capsys,
    )
    assert code == 0
    cli_payload = json.loads(captured.out)
    _assert_no_internal_paths(cli_payload)
    assert _session_core(target_payload) == _session_core(cli_payload)
    _assert_stable_artifact_ref(target_payload["data"]["session"]["artifact_ref"], workspace_root=str(root))


def test_v16d1_session_graph_error_envelope_and_artifact_distinctions(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Contract Errors")
    other_workspace_id = _create_workspace(client, "Session Contract Other")
    _write_session(root, workspace_id, "ksess_missing", with_graph=False)
    _write_session(root, workspace_id, "ksess_alpha", with_graph=True)

    unknown_session = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"session_id": "ksess_unknown"})
    missing_artifact = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"session_id": "ksess_missing"})
    cross_workspace = client.get(f"/api/workspaces/{other_workspace_id}/graph/session", params={"session_id": "ksess_alpha"})
    invalid_limit = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"limit": 0})

    assert unknown_session.status_code == 200
    assert unknown_session.json()["status"] == "blocked"
    assert unknown_session.json()["data"]["error"]["code"] == "unknown_session_id"
    assert unknown_session.json()["data"]["error"]["retryable"] is False

    assert missing_artifact.status_code == 200
    assert missing_artifact.json()["status"] == "blocked"
    assert missing_artifact.json()["data"]["error"]["code"] == "session_graph_no_artifact"
    assert missing_artifact.json()["data"]["error"]["code"] != unknown_session.json()["data"]["error"]["code"]
    _assert_stable_artifact_ref(missing_artifact.json()["data"]["artifact_ref"], workspace_root=str(root))

    assert cross_workspace.status_code == 200
    assert cross_workspace.json()["status"] == "blocked"
    assert cross_workspace.json()["data"]["error"]["code"] == "unknown_session_id"
    assert "ksess_alpha" in cross_workspace.json()["warnings"][0]

    assert invalid_limit.status_code == 400
    assert not (root / workspace_id / "lifecycle" / "operations").exists()
    assert not (root / workspace_id / "lifecycle" / "sources.json").exists()


def test_v16d1_session_contract_baseline_and_d2_surface_boundaries_remain_explicit():
    current_tools = {spec["name"] for spec in all_tool_specs()}
    assert len(current_tools) >= 61
    assert SESSION_MCP_BASELINE <= current_tools
    assert {
        "knowledge_codebase_import",
        "knowledge_codebase_list",
        "knowledge_codebase_snapshot",
        "knowledge_project_inventory",
        "knowledge_codebase_describe",
        "knowledge_codebase_archive",
        "knowledge_code_symbol_search",
        "knowledge_public_surface_trace",
        "knowledge_project_overview",
        "knowledge_agent_context_pack",
        "knowledge_devwiki_build",
        "knowledge_devwiki_read",
        "knowledge_code_graph_build",
        "knowledge_code_graph_snapshot",
        "knowledge_code_graph_neighbors",
        "knowledge_code_graph_mermaid",
        "knowledge_code_quality_feedback",
        "knowledge_code_quality_summary",
        "knowledge_code_quality_rules_build",
        "knowledge_code_quality_rule_review",
        "knowledge_code_quality_plan",
    } <= current_tools

    inventory = _cli_inventory()
    assert set(inventory) == {"build", "code", "graph", "quality", "query", "source", "trace", "workspace"}
    assert inventory["code"] == ["architecture", "architecture-intent", "archive", "coding-agent", "context-pack", "describe", "devwiki", "graph", "import", "inventory", "list", "overview", "platform", "quality", "snapshot", "symbols", "trace"]
    assert inventory["graph"] == ["community", "neighbors", "query", "session", "snapshot"]

    data_service_routes = {
        (method, getattr(route, "path", ""))
        for route in app.routes
        for method in sorted(set(getattr(route, "methods", None) or []) - {"HEAD", "OPTIONS"})
        if getattr(route, "path", "").startswith("/api/workspaces")
    }
    target_paths = {path for _, path in data_service_routes}
    assert len(data_service_routes) >= 82
    assert "/api/workspaces/{workspace_id}/graph/session" in target_paths
    assert "/api/workspaces/{workspace_id}/sessions" in target_paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}" in target_paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/ingest" in target_paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/query" in target_paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/build/start" in target_paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}" in target_paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel" in target_paths
    assert "/api/workspaces/{workspace_id}/quality/feedback" in target_paths
    assert "/api/workspaces/{workspace_id}/quality/correction-rules" in target_paths
    assert "/api/workspaces/{workspace_id}/quality/correction-rules/build" in target_paths
    assert "/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review" in target_paths
    assert "/api/workspaces/{workspace_id}/quality/correction-plan" in target_paths
    assert "/api/workspaces/{workspace_id}/codebases/{codebase_id}/overview" in target_paths
    assert "/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack" in target_paths
    assert "/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}" in target_paths
    assert "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph" in target_paths
    assert "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/neighbors" in target_paths
    assert "/api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid" in target_paths
    assert "/api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/summary" in target_paths
    assert not any("/quality/corrections" in path for path in target_paths)
