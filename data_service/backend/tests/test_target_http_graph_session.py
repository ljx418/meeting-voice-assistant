import json

from fastapi.testclient import TestClient

from app.config import config
from app.main import app


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
    (lifecycle / "sessions.json").write_text(json.dumps({"items": [session]}, ensure_ascii=False), encoding="utf-8")
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
            {"id": "entity:alpha", "type": "entity", "label": "Alpha", "metadata": {"kind": "stable", "cache_path": "/hidden/cache"}},
            {"id": "topic:plan", "type": "topic", "label": "Plan", "metadata": {"source_path": "/hidden/source"}},
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "entity:alpha",
                "target": "topic:plan",
                "type": "related",
                "weight": 0.8,
                "metadata": {"stable": "yes", "physical_path": "/hidden/artifact"},
            }
        ],
        "communities": [{"id": "community-1", "entity_ids": ["entity:alpha"], "summary": "Session community"}],
        "updated_at": "2026-05-14T00:02:00Z",
    }
    graph_path = session_dir / "graph" / "graph.json"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")


def test_v16c4_graph_session_target_http_list_detail_and_projection(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Session")
    _write_session(root, workspace_id, "ksess_alpha")

    listed = client.get(f"/api/workspaces/{workspace_id}/graph/session")
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert listed_payload["status"] == "ok"
    assert listed_payload["data"]["items"][0]["session_id"] == "ksess_alpha"
    assert listed_payload["data"]["items"][0]["node_count"] == 2
    assert "nodes" not in listed_payload["data"]["items"][0]
    assert "edges" not in listed_payload["data"]["items"][0]
    _assert_no_internal_paths(listed_payload)

    detail = client.get(
        f"/api/workspaces/{workspace_id}/graph/session",
        params={"session_id": "ksess_alpha", "include_nodes": True, "include_edges": True, "node_limit": 1, "edge_limit": 1},
    )
    assert detail.status_code == 200
    payload = detail.json()
    session = payload["data"]["session"]
    assert session["session_id"] == "ksess_alpha"
    assert session["artifact_ref"] == f"graph-session://{workspace_id}/ksess_alpha"
    assert session["nodes"][0]["node_id"] == "entity:alpha"
    assert session["nodes_truncated"] is True
    assert session["edges"][0]["source_node_id"] == "entity:alpha"
    assert session["edges_truncated"] is False
    _assert_no_internal_paths(payload)


def test_v16c4_graph_session_target_http_validation_missing_and_side_effects(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Session Missing")
    _write_session(root, workspace_id, "ksess_missing", with_graph=False)

    bad_limit = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"limit": 0})
    too_large = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"limit": 101})
    bad_node_limit = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"session_id": "ksess_missing", "node_limit": 0})
    assert bad_limit.status_code == 400
    assert too_large.status_code == 400
    assert bad_node_limit.status_code == 400

    unknown = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"session_id": "ksess_unknown"})
    assert unknown.status_code == 200
    assert unknown.json()["status"] == "blocked"
    assert unknown.json()["data"]["error"]["code"] == "unknown_session_id"

    missing = client.get(f"/api/workspaces/{workspace_id}/graph/session", params={"session_id": "ksess_missing"})
    assert missing.status_code == 200
    assert missing.json()["status"] == "blocked"
    assert missing.json()["data"]["error"]["code"] == "session_graph_no_artifact"
    assert list((root / workspace_id / "lifecycle" / "operations").glob("*.json")) == []
    assert not (root / workspace_id / "lifecycle" / "sources.json").exists()

    unknown_workspace = client.get("/api/workspaces/unknown-workspace/graph/session")
    assert unknown_workspace.status_code == 404


def test_v16c4_graph_session_target_http_cross_workspace_auth_and_d2_lifecycle_boundary(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Session A")
    other_workspace_id = _create_workspace(client, "Graph Session B")
    _write_session(root, workspace_id, "ksess_alpha")

    cross = client.get(f"/api/workspaces/{other_workspace_id}/graph/session", params={"session_id": "ksess_alpha"})
    assert cross.status_code == 200
    assert cross.json()["data"]["error"]["code"] == "unknown_session_id"

    sessions = client.get(f"/api/workspaces/{workspace_id}/sessions")
    session_ingest = client.post(f"/api/workspaces/{workspace_id}/sessions/ksess_alpha/ingest", json={})
    session_query = client.post(f"/api/workspaces/{workspace_id}/sessions/ksess_alpha/query", json={})
    session_build = client.post(f"/api/workspaces/{workspace_id}/sessions/ksess_alpha/build/start", json={})
    quality = client.get(f"/api/workspaces/{workspace_id}/quality")
    assert sessions.status_code == 200
    assert session_ingest.status_code == 200
    assert session_ingest.json()["status"] == "blocked"
    assert session_ingest.json()["data"]["error"]["code"] == "invalid_session_ingest_request"
    assert session_query.status_code == 200
    assert session_query.json()["status"] == "blocked"
    assert session_query.json()["data"]["error"]["code"] == "invalid_session_query_request"
    assert session_build.status_code == 200
    assert session_build.json()["operation_id"].startswith("sop_")
    assert quality.status_code == 404

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = client.get(f"/api/workspaces/{workspace_id}/graph/session")
    authorized = client.get(f"/api/workspaces/{workspace_id}/graph/session", headers={"X-API-Key": "target-key"})
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
