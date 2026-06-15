import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import config
from app.main import app
from data_service.__main__ import _build_knowledge_parser
from argparse import _SubParsersAction
from test_target_http_source_preview import _import_text_source


FORBIDDEN_CONTRACT_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "session_storage_path",
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
    "raw_prompt",
    "raw_model_message",
    "embedding",
    "embedding_vector",
    "raw_response",
    "provider_response",
}


def _assert_no_internal_payload(payload):
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                assert key not in FORBIDDEN_CONTRACT_KEYS
                assert not str(key).endswith("_path")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    serialized = json.dumps(payload, ensure_ascii=False).lower()
    assert "raw prompt" not in serialized
    assert "raw_model_message" not in serialized
    assert "embedding_vector" not in serialized
    assert "/hidden/" not in serialized
    walk(payload)


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _create_session(client: TestClient, workspace_id: str, external_id: str) -> str:
    response = client.post(f"/api/workspaces/{workspace_id}/sessions", json={"external_id": external_id, "title": external_id})
    assert response.status_code == 200
    return response.json()["data"]["session"]["session_id"]


def _query(client: TestClient, workspace_id: str, session_id: str, payload: dict):
    return client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/query", json=payload)


def _write_session_graph(root: Path, workspace_id: str, session_id: str, *, status: str = "active") -> None:
    workspace = root / workspace_id
    lifecycle = workspace / "lifecycle"
    lifecycle.mkdir(parents=True, exist_ok=True)
    session = {
        "session_id": session_id,
        "workspace_id": workspace_id,
        "external_id": session_id,
        "session_type": "generic",
        "title": session_id,
        "status": status,
        "created_at": "2026-05-14T00:00:00Z",
        "updated_at": "2026-05-14T00:01:00Z",
        "metadata": {"stable": "ok", "workspace_path": "/hidden/workspace"},
    }
    (lifecycle / "sessions.json").write_text(json.dumps({"items": [session]}, ensure_ascii=False), encoding="utf-8")
    graph = {
        "graph_model_version": "session-graph-1.0",
        "workspace_id": workspace_id,
        "scope": "session",
        "session_id": session_id,
        "status": "ok",
        "nodes": [
            {
                "id": "entity:alpha",
                "type": "entity",
                "label": "Alpha",
                "metadata": {
                    "text": "Alpha planning note",
                    "cache_path": "/hidden/cache",
                    "raw_prompt": "do not leak",
                    "embedding_vector": [0.1, 0.2],
                },
                "source_refs": [{"source_id": "src_a", "source_path": "/hidden/source.md"}],
            },
            {"id": "topic:beta", "type": "topic", "label": "Beta", "metadata": {"text": "Beta"}},
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "entity:alpha",
                "target": "topic:beta",
                "type": "related",
                "weight": 0.8,
                "metadata": {"physical_path": "/hidden/artifact"},
            }
        ],
        "communities": [{"id": "community-1", "entity_ids": ["entity:alpha"], "summary": "Stable community", "metadata": {"local_path": "/hidden/c.json"}}],
        "updated_at": "2026-05-14T00:02:00Z",
    }
    graph_path = workspace / "sessions" / session_id / "graph" / "graph.json"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(json.dumps(graph, ensure_ascii=False), encoding="utf-8")


def _fingerprint_tree(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {
        str(item.relative_to(path)): item.read_text(encoding="utf-8")
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


def _cli_inventory() -> dict[str, list[str]]:
    top_action = next(action for action in _build_knowledge_parser()._actions if isinstance(action, _SubParsersAction))
    inventory = {}
    for command, child_parser in top_action.choices.items():
        nested_actions = [action for action in child_parser._actions if isinstance(action, _SubParsersAction)]
        inventory[command] = sorted(nested_actions[0].choices) if nested_actions else []
    return {command: inventory[command] for command in sorted(inventory)}


def test_v16d5_session_query_target_http_success_projection_and_read_only(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Query")
    session_id = _create_session(client, workspace_id, "d5-query")
    ingest = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/ingest", json={"content": "Alpha planning note", "title": "Alpha"})
    assert ingest.status_code == 200
    _write_session_graph(root, workspace_id, session_id)

    session_dir = root / workspace_id / "sessions" / session_id
    before_session = _fingerprint_tree(session_dir)
    before_workspace_sources = _fingerprint_tree(root / workspace_id / "lifecycle")
    before_quality = _fingerprint_tree(root / workspace_id / "quality")

    response = _query(client, workspace_id, session_id, {"query": "Alpha"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["operation_id"] is None
    data = payload["data"]
    assert data["workspace_id"] == workspace_id
    assert data["session_id"] == session_id
    assert data["query"] == "Alpha"
    assert data["top_k"] == 8
    assert data["answer"].startswith("Session graph returned")
    assert data["evidence"] == []
    assert data["evidence_refs"] == []
    assert data["evidence_state"] == "graph_only_no_evidence"
    assert data["results"][0]["source_id"] == "entity:alpha"
    assert data["items"][0]["source_id"] == "entity:alpha"
    assert data["nodes"][0]["node_id"] == "entity:alpha"
    assert data["edges"][0]["source_node_id"] == "entity:alpha"
    assert data["communities"][0]["community_id"] == "community-1"
    assert data["artifact_ref"] == f"graph-session://{workspace_id}/{session_id}"
    assert payload["artifact_refs"][0]["artifact_ref"] == data["artifact_ref"]
    _assert_no_internal_payload(payload)

    assert _fingerprint_tree(session_dir) == before_session
    assert _fingerprint_tree(root / workspace_id / "lifecycle") == before_workspace_sources
    assert not (root / workspace_id / "sessions" / session_id / "operations").exists()
    assert not (root / workspace_id / "lifecycle" / "operations").exists()
    assert _fingerprint_tree(root / workspace_id / "quality") == before_quality


def test_v11s1_session_query_returns_resolvable_evidence_span_ids(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Query Evidence")
    source_id = _import_text_source(
        client,
        workspace_id,
        title="S1 Session Evidence Source",
        content="Session precise navigation should preserve source id, unit id, and evidence id for a highlighted source span.",
    )
    session_id = _create_session(client, workspace_id, "s1-query")
    ingest = client.post(
        f"/api/workspaces/{workspace_id}/sessions/{session_id}/ingest",
        json={"content": "Session precise navigation should preserve identifiers.", "title": "S1 session note"},
    )
    assert ingest.status_code == 200
    _write_session_graph(root, workspace_id, session_id)

    response = _query(client, workspace_id, session_id, {"query": "precise navigation preserve source id unit evidence", "top_k": 4})
    assert response.status_code == 200
    payload = response.json()
    _assert_no_internal_payload(payload)
    data = payload["data"]
    assert data["evidence_state"] == "has_evidence_span_ids"
    assert data["evidence"]
    assert data["evidence_refs"] == data["evidence"]

    evidence = data["evidence"][0]
    assert evidence["source_id"] == source_id
    assert evidence["unit_id"].startswith("unit_")
    assert evidence["evidence_id"].startswith("ev_")
    assert evidence["snippet"]
    assert "source_ref" not in evidence
    assert "artifact_ref" not in evidence

    source_response = client.get(f"/api/workspaces/{workspace_id}/sources/{evidence['source_id']}")
    assert source_response.status_code == 200
    unit_response = client.get(f"/api/workspaces/{workspace_id}/sources/{evidence['source_id']}/units/{evidence['unit_id']}")
    assert unit_response.status_code == 200
    span_response = client.get(
        f"/api/workspaces/{workspace_id}/sources/{evidence['source_id']}/units/{evidence['unit_id']}/evidence/{evidence['evidence_id']}"
    )
    assert span_response.status_code == 200
    span = span_response.json()["data"]["evidence_span"]
    assert span["source_id"] == evidence["source_id"]
    assert span["unit_id"] == evidence["unit_id"]
    assert span["evidence_id"] == evidence["evidence_id"]
    assert span["offset_basis"] == "normalized_text"
    assert span["offset_range"] == "half_open"
    assert span["text_basis"] == "document_unit_text"


def test_v16d5_session_query_validation_missing_artifacts_and_session_state(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Query Boundary")
    other_workspace_id = _create_workspace(client, "Session Query Other")
    session_id = _create_session(client, workspace_id, "d5-boundary")

    invalid_cases = [
        _query(client, workspace_id, session_id, {}),
        _query(client, workspace_id, session_id, {"query": ""}),
        _query(client, workspace_id, session_id, {"query": "   "}),
        _query(client, workspace_id, session_id, {"query": "x" * 4097}),
        _query(client, workspace_id, session_id, {"query": "x", "top_k": "bad"}),
        _query(client, workspace_id, session_id, {"query": "x", "top_k": 0}),
        _query(client, workspace_id, session_id, {"query": "x", "top_k": -1}),
        _query(client, workspace_id, session_id, {"query": "x", "top_k": 51}),
    ]
    for response in invalid_cases:
        assert response.status_code == 200
        assert response.json()["status"] == "blocked"
        assert response.json()["data"]["error"]["code"] == "invalid_session_query_request"

    unsupported = _query(client, workspace_id, session_id, {"query": "x", "include_workspace_context": True})
    assert unsupported.status_code == 422

    missing_artifact = _query(client, workspace_id, session_id, {"query": "x"})
    assert missing_artifact.status_code == 200
    assert missing_artifact.json()["status"] == "blocked"
    assert missing_artifact.json()["data"]["error"]["code"] == "session_graph_no_artifact"
    assert not (root / workspace_id / "sessions" / session_id / "graph").exists()
    assert not (root / workspace_id / "sessions" / session_id / "operations").exists()

    unknown_workspace = _query(client, "unknown-workspace", session_id, {"query": "x"})
    assert unknown_workspace.status_code == 404

    unknown_session = _query(client, workspace_id, "ksess_unknown", {"query": "x"})
    assert unknown_session.status_code == 200
    assert unknown_session.json()["data"]["error"]["code"] == "unknown_session_id"

    cross_workspace = _query(client, other_workspace_id, session_id, {"query": "x"})
    assert cross_workspace.status_code == 200
    assert cross_workspace.json()["data"]["error"]["code"] == "unknown_session_id"

    _write_session_graph(root, workspace_id, session_id)
    assert client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/close").status_code == 200
    closed_query = _query(client, workspace_id, session_id, {"query": "Alpha"})
    assert closed_query.status_code == 200
    assert closed_query.json()["status"] == "ok"

    assert client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/delete").status_code == 200
    deleted_query = _query(client, workspace_id, session_id, {"query": "Alpha"})
    assert deleted_query.status_code == 200
    assert deleted_query.json()["status"] == "blocked"
    assert deleted_query.json()["data"]["error"]["code"] == "session_disposed"


def test_v16d5_session_query_surface_auth_and_cli_inventory(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Query Surface")
    session_id = _create_session(client, workspace_id, "d5-surface")
    _write_session_graph(root, workspace_id, session_id)

    assert _query(client, workspace_id, session_id, {"query": "Alpha"}).status_code == 200
    build_start = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/build/start", json={})
    assert build_start.status_code == 200
    assert build_start.json()["operation_id"].startswith("sop_")
    assert client.get(f"/api/workspaces/{workspace_id}/quality").status_code == 404
    assert client.get(f"/api/workspaces/{workspace_id}/graph/session").status_code == 200
    assert client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/ingest", json={"content": "x"}).status_code == 200

    inventory = _cli_inventory()
    assert set(inventory) == {"build", "code", "graph", "quality", "query", "source", "trace", "workspace"}
    assert inventory["code"] == ["architecture", "architecture-intent", "archive", "coding-agent", "context-pack", "describe", "devwiki", "graph", "import", "inventory", "list", "overview", "platform", "quality", "snapshot", "symbols", "trace"]
    assert inventory["graph"] == ["community", "neighbors", "query", "session", "snapshot"]

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = _query(client, workspace_id, session_id, {"query": "Alpha"})
    authorized = client.post(
        f"/api/workspaces/{workspace_id}/sessions/{session_id}/query",
        json={"query": "Alpha"},
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
