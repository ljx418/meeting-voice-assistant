from pathlib import Path

from fastapi.testclient import TestClient

from app.config import config
from app.main import app


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


def _assert_session_source_ref(value: str):
    assert value.startswith("session-source://")
    assert not value.endswith((".json", ".parquet", ".md"))
    assert "/sessions/" not in value
    assert "/workspace/" not in value


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _create_session(client: TestClient, workspace_id: str, external_id: str) -> str:
    response = client.post(f"/api/workspaces/{workspace_id}/sessions", json={"external_id": external_id, "title": external_id})
    assert response.status_code == 200
    return response.json()["data"]["session"]["session_id"]


def _ingest(client: TestClient, workspace_id: str, session_id: str, payload: dict):
    return client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/ingest", json=payload)


def test_v16d4_session_ingest_target_http_content_records_and_projection(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Ingest")
    session_id = _create_session(client, workspace_id, "d4-ingest")

    content_ingest = _ingest(
        client,
        workspace_id,
        session_id,
        {
            "source_type": "note",
            "content_format": "markdown",
            "title": "Session note",
            "content": "# Notes",
            "metadata": {
                "stable": "ok",
                "workspace_path": "/hidden/workspace",
                "nested": {"local_path": "/hidden/source.md", "safe": True},
            },
        },
    )
    assert content_ingest.status_code == 200
    content_payload = content_ingest.json()
    assert content_payload["status"] == "ok"
    assert content_payload["operation_id"] is None
    source = content_payload["data"]["source"]
    assert source["workspace_id"] == workspace_id
    assert source["session_id"] == session_id
    assert source["source_id"]
    assert source["session_source_id"] == source["source_id"]
    assert source["source_scope"] == "session"
    assert source["record_count"] == 1
    assert source["status"] == "ingested"
    assert source["metadata"]["stable"] == "ok"
    assert "workspace_path" not in source["metadata"]
    assert "local_path" not in source["metadata"]["nested"]
    assert content_payload["artifact_refs"][0]["artifact_ref"] == source["artifact_ref"]
    _assert_session_source_ref(source["artifact_ref"])
    _assert_no_internal_paths(content_payload)

    records_ingest = _ingest(
        client,
        workspace_id,
        session_id,
        {
            "source_type": "turns",
            "content_format": "turns",
            "title": "Turns",
            "records": [{"record_id": "r1", "speaker": "A", "text": "hello"}],
        },
    )
    assert records_ingest.status_code == 200
    assert records_ingest.json()["data"]["source"]["record_count"] == 1
    _assert_no_internal_paths(records_ingest.json())

    duplicate = _ingest(client, workspace_id, session_id, {"content": "# Notes", "title": "Session note"})
    assert duplicate.status_code == 200
    assert duplicate.json()["data"]["source"]["source_scope"] == "session"

    assert not (root / workspace_id / "lifecycle" / "sources.json").exists()
    assert not (root / workspace_id / "lifecycle" / "operations").exists()
    assert not (root / workspace_id / "sessions" / session_id / "operations").exists()
    assert not (root / workspace_id / "sessions" / session_id / "graph").exists()


def test_v16d4_session_ingest_validation_and_session_state_boundaries(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Ingest Boundary")
    other_workspace_id = _create_workspace(client, "Session Ingest Other")
    session_id = _create_session(client, workspace_id, "d4-boundary")

    missing = _ingest(client, workspace_id, session_id, {})
    both = _ingest(client, workspace_id, session_id, {"content": "x", "records": [{"text": "x"}]})
    bad_format = _ingest(client, workspace_id, session_id, {"content": "x", "content_format": "binary"})
    bad_records = _ingest(client, workspace_id, session_id, {"records": ["not-object"], "content_format": "turns"})
    too_many_records = _ingest(client, workspace_id, session_id, {"records": [{"text": "x"}] * 1001, "content_format": "turns"})
    too_large_content = _ingest(client, workspace_id, session_id, {"content": "x" * (2 * 1024 * 1024 + 1)})
    for response in [missing, both, bad_format, bad_records, too_many_records, too_large_content]:
        assert response.status_code == 200
        assert response.json()["status"] == "blocked"
        assert response.json()["data"]["error"]["code"] == "invalid_session_ingest_request"

    invalid_source_type = _ingest(client, workspace_id, session_id, {"source_type": "", "content": "x"})
    assert invalid_source_type.status_code == 422

    related_paths = _ingest(client, workspace_id, session_id, {"content": "x", "related_paths": ["../secret"]})
    assert related_paths.status_code == 422

    unknown_workspace = _ingest(client, "unknown-workspace", session_id, {"content": "x"})
    assert unknown_workspace.status_code == 404

    unknown_session = _ingest(client, workspace_id, "ksess_unknown", {"content": "x"})
    assert unknown_session.status_code == 200
    assert unknown_session.json()["status"] == "blocked"
    assert unknown_session.json()["data"]["error"]["code"] == "unknown_session_id"

    cross_workspace = _ingest(client, other_workspace_id, session_id, {"content": "x"})
    assert cross_workspace.status_code == 200
    assert cross_workspace.json()["status"] == "blocked"
    assert cross_workspace.json()["data"]["error"]["code"] == "unknown_session_id"

    closed = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/close")
    assert closed.status_code == 200
    closed_default = _ingest(client, workspace_id, session_id, {"content": "x"})
    assert closed_default.status_code == 200
    assert closed_default.json()["data"]["error"]["code"] == "session_closed"

    closed_allowed = _ingest(client, workspace_id, session_id, {"content": "x", "allow_closed_write": True})
    assert closed_allowed.status_code == 200
    assert closed_allowed.json()["status"] == "ok"

    deleted = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/delete")
    assert deleted.status_code == 200
    deleted_allowed = _ingest(client, workspace_id, session_id, {"content": "x", "allow_closed_write": True})
    assert deleted_allowed.status_code == 200
    assert deleted_allowed.json()["status"] == "blocked"
    assert deleted_allowed.json()["data"]["error"]["code"] == "session_disposed"

    archived_workspace = _create_workspace(client, "Session Ingest Archived")
    archived_session = _create_session(client, archived_workspace, "archived-session")
    assert client.post(f"/api/workspaces/{archived_workspace}/archive", json={"reason": "done"}).status_code == 200
    archived_ingest = _ingest(client, archived_workspace, archived_session, {"content": "x"})
    assert archived_ingest.status_code == 200
    assert archived_ingest.json()["data"]["error"]["code"] == "workspace_archived"


def test_v16d4_session_ingest_keeps_other_public_surfaces_closed(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Ingest Surface")
    session_id = _create_session(client, workspace_id, "d4-surface")

    assert _ingest(client, workspace_id, session_id, {"content": "x"}).status_code == 200
    empty_query = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/query", json={})
    assert empty_query.status_code == 200
    assert empty_query.json()["status"] == "blocked"
    assert empty_query.json()["data"]["error"]["code"] == "invalid_session_query_request"
    build_start = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/build/start", json={})
    assert build_start.status_code == 200
    assert build_start.json()["operation_id"].startswith("sop_")
    assert client.get(f"/api/workspaces/{workspace_id}/quality").status_code == 404
    assert client.get(f"/api/workspaces/{workspace_id}/graph/session").status_code == 200

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = _ingest(client, workspace_id, session_id, {"content": "x"})
    authorized = client.post(
        f"/api/workspaces/{workspace_id}/sessions/{session_id}/ingest",
        json={"content": "x"},
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
