import json
from argparse import _SubParsersAction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import _build_knowledge_parser
from data_service.mcp_tool_registry import all_tool_specs


PLAN_PATH = Path("docs/V1.6/session-ingest-query-build-contract-plan.md")
EXPECTED_TARGET_ROUTES = {
    ("POST", "/api/workspaces/{workspace_id}/query"),
    ("POST", "/api/workspaces/{workspace_id}/distill"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/trace"),
    ("POST", "/api/workspaces"),
    ("GET", "/api/workspaces"),
    ("GET", "/api/workspaces/{workspace_id}"),
    ("POST", "/api/workspaces/{workspace_id}/archive"),
    ("POST", "/api/workspaces/{workspace_id}/sources"),
    ("GET", "/api/workspaces/{workspace_id}/sources"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}"),
    ("POST", "/api/workspaces/{workspace_id}/sources/{source_id}/remove"),
    ("POST", "/api/workspaces/{workspace_id}/build/start"),
    ("GET", "/api/workspaces/{workspace_id}/build/operations/{operation_id}"),
    ("POST", "/api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel"),
    ("GET", "/api/workspaces/{workspace_id}/graph/neighbors"),
    ("GET", "/api/workspaces/{workspace_id}/graph/community"),
    ("GET", "/api/workspaces/{workspace_id}/graph/query"),
    ("GET", "/api/workspaces/{workspace_id}/graph/session"),
    ("POST", "/api/workspaces/{workspace_id}/sessions"),
    ("GET", "/api/workspaces/{workspace_id}/sessions"),
    ("GET", "/api/workspaces/{workspace_id}/sessions/{session_id}"),
    ("POST", "/api/workspaces/{workspace_id}/sessions/{session_id}/close"),
    ("POST", "/api/workspaces/{workspace_id}/sessions/{session_id}/delete"),
    ("POST", "/api/workspaces/{workspace_id}/sessions/{session_id}/ingest"),
    ("POST", "/api/workspaces/{workspace_id}/sessions/{session_id}/query"),
    ("POST", "/api/workspaces/{workspace_id}/sessions/{session_id}/build/start"),
    ("GET", "/api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}"),
    ("POST", "/api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel"),
    ("POST", "/api/workspaces/{workspace_id}/quality/feedback"),
    ("GET", "/api/workspaces/{workspace_id}/quality/correction-rules"),
    ("POST", "/api/workspaces/{workspace_id}/quality/correction-rules"),
    ("POST", "/api/workspaces/{workspace_id}/quality/correction-rules/build"),
    ("POST", "/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review"),
    ("GET", "/api/workspaces/{workspace_id}/quality/correction-plan"),
    ("POST", "/api/workspaces/{workspace_id}/quality/correction-plan"),
}
SESSION_MCP_TOOLS = {
    "knowledge_session_ingest",
    "knowledge_session_query",
    "knowledge_session_build_start",
    "knowledge_session_build_status",
    "knowledge_session_build_cancel",
}
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


def _target_routes() -> set[tuple[str, str]]:
    routes = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        if path == "/api/workspaces" or path.startswith("/api/workspaces/"):
            for method in sorted(set(getattr(route, "methods", None) or []) - {"HEAD", "OPTIONS"}):
                routes.add((method, path))
    return routes


def _subparser_action(parser):
    return next(action for action in parser._actions if isinstance(action, _SubParsersAction))


def _cli_inventory() -> dict[str, list[str]]:
    top_action = _subparser_action(_build_knowledge_parser())
    inventory = {}
    for command, child_parser in top_action.choices.items():
        nested_actions = [action for action in child_parser._actions if isinstance(action, _SubParsersAction)]
        inventory[command] = sorted(nested_actions[0].choices) if nested_actions else []
    return {command: inventory[command] for command in sorted(inventory)}


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


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_session_graph(root: Path, workspace_id: str, session_id: str) -> None:
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
    (lifecycle / "sessions.json").write_text(json.dumps({"items": [session]}, ensure_ascii=False), encoding="utf-8")
    graph_path = workspace / "sessions" / session_id / "graph" / "graph.json"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(
        json.dumps(
            {
                "workspace_id": workspace_id,
                "scope": "session",
                "session_id": session_id,
                "status": "ok",
                "nodes": [{"id": "entity:alpha", "type": "entity", "label": "Alpha", "metadata": {"cache_path": "/hidden/cache"}}],
                "edges": [],
                "communities": [],
                "updated_at": "2026-05-14T00:02:00Z",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_v16d3_d4_d5_d6_surface_accepts_e_quality_minimal_routes_only():
    assert _target_routes() == EXPECTED_TARGET_ROUTES
    assert len(_target_routes()) == 35

    paths = {path for _, path in _target_routes()}
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/ingest" in paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/query" in paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/build/start" in paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}" in paths
    assert "/api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel" in paths
    assert "/api/workspaces/{workspace_id}/quality/feedback" in paths
    assert "/api/workspaces/{workspace_id}/quality/correction-rules" in paths
    assert "/api/workspaces/{workspace_id}/quality/correction-rules/build" in paths
    assert "/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review" in paths
    assert "/api/workspaces/{workspace_id}/quality/correction-plan" in paths
    assert not any("/quality/corrections/plan" in path for path in paths)
    assert not any("/quality/corrections/build" in path for path in paths)

    tools = {spec["name"] for spec in all_tool_specs()}
    assert len(tools) == 40
    assert SESSION_MCP_TOOLS <= tools

    inventory = _cli_inventory()
    assert set(inventory) == {"build", "graph", "quality", "query", "source", "trace", "workspace"}
    assert inventory["graph"] == ["community", "neighbors", "query", "session", "snapshot"]


def test_v16d3_existing_session_surfaces_remain_bounded_and_d4_ingest_is_scoped(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "D3 Session Plan")

    created = client.post(
        f"/api/workspaces/{workspace_id}/sessions",
        json={"external_id": "d3-session", "metadata": {"workspace_path": "/hidden/root", "stable": "ok"}},
    )
    assert created.status_code == 200
    assert created.json()["data"]["session"]["artifact_ref"].startswith("session://")
    _assert_no_internal_paths(created.json())

    session_id = created.json()["data"]["session"]["session_id"]
    missing_ingest_payload = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/ingest", json={})
    assert missing_ingest_payload.status_code == 200
    assert missing_ingest_payload.json()["status"] == "blocked"
    assert missing_ingest_payload.json()["data"]["error"]["code"] == "invalid_session_ingest_request"
    missing_query_payload = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/query", json={})
    assert missing_query_payload.status_code == 200
    assert missing_query_payload.json()["status"] == "blocked"
    assert missing_query_payload.json()["data"]["error"]["code"] == "invalid_session_query_request"
    build_start = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/build/start", json={})
    assert build_start.status_code == 200
    assert build_start.json()["operation_id"].startswith("sop_")
    assert client.get(f"/api/workspaces/{workspace_id}/quality").status_code == 404

    _write_session_graph(root, workspace_id, "ksess_graph")
    graph_session = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"session_id": "ksess_graph"})
    assert graph_session.status_code == 200
    assert graph_session.json()["data"]["session"]["artifact_ref"].startswith("graph-session://")
    _assert_no_internal_paths(graph_session.json())

    assert not (root / workspace_id / "lifecycle" / "operations").exists()
    assert not (root / workspace_id / "lifecycle" / "sources.json").exists()


def test_v16d3_contract_plan_exists_and_marks_future_capabilities_not_opened():
    text = PLAN_PATH.read_text(encoding="utf-8")
    assert "D3 is a planning and contract hardening phase only. It opens no public surface." in text
    for required in [
        "knowledge_session_ingest",
        "knowledge_session_query",
        "knowledge_session_build_start",
        "knowledge_session_build_status",
        "knowledge_session_build_cancel",
        "D4 accepted",
        "D5 accepted",
        "planned / not opened",
        "D4 completed: Session Ingest Target HTTP Minimal Surface",
        "D5 completed: Session Query Target HTTP Minimal Surface",
        "D6 completed",
        "D6 accepted",
    ]:
        assert required in text
    forbidden_implemented = [
        "quality target HTTP accepted",
    ]
    assert not any(item in text for item in forbidden_implemented)
