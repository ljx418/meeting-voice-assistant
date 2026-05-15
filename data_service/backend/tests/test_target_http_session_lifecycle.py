from pathlib import Path

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


def _assert_session_ref(value: str):
    assert value.startswith("session://")
    assert "/" not in value.removeprefix("session://")
    assert not value.endswith((".json", ".parquet", ".md"))


def test_v16d2_session_lifecycle_target_http_create_list_get_close_delete(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Lifecycle")
    other_workspace_id = _create_workspace(client, "Session Lifecycle Other")

    created = client.post(
        f"/api/workspaces/{workspace_id}/sessions",
        json={
            "external_id": "meeting-001",
            "session_type": "meeting",
            "title": "Planning",
            "metadata": {
                "stable": "ok",
                "workspace_path": "/hidden/workspace",
                "artifact_physical_path": "/hidden/artifact.json",
            },
        },
    )
    assert created.status_code == 200
    create_payload = created.json()
    assert create_payload["status"] == "ok"
    assert create_payload["operation_id"] is None
    assert create_payload["data"]["created"] is True
    session = create_payload["data"]["session"]
    session_id = session["session_id"]
    assert session["workspace_id"] == workspace_id
    assert session["status"] == "active"
    assert session["artifact_ref"] == f"session://{session_id}"
    assert create_payload["artifact_refs"][0]["artifact_ref"] == f"session://{session_id}"
    _assert_session_ref(session["artifact_ref"])
    _assert_no_internal_paths(create_payload)

    duplicate = client.post(f"/api/workspaces/{workspace_id}/sessions", json={"external_id": "meeting-001"})
    assert duplicate.status_code == 200
    assert duplicate.json()["data"]["created"] is False
    assert duplicate.json()["data"]["session"]["session_id"] == session_id
    _assert_no_internal_paths(duplicate.json())

    listed = client.get(f"/api/workspaces/{workspace_id}/sessions", params={"limit": 20})
    assert listed.status_code == 200
    list_payload = listed.json()
    assert list_payload["data"]["limit"] == 20
    assert list_payload["data"]["include_deleted"] is False
    assert [item["session_id"] for item in list_payload["data"]["items"]] == [session_id]
    _assert_no_internal_paths(list_payload)

    other_list = client.get(f"/api/workspaces/{other_workspace_id}/sessions")
    assert other_list.status_code == 200
    assert other_list.json()["data"]["items"] == []

    detail = client.get(f"/api/workspaces/{workspace_id}/sessions/{session_id}")
    assert detail.status_code == 200
    assert detail.json()["data"]["session"]["session_id"] == session_id
    _assert_no_internal_paths(detail.json())

    cross_detail = client.get(f"/api/workspaces/{other_workspace_id}/sessions/{session_id}")
    assert cross_detail.status_code == 200
    assert cross_detail.json()["status"] == "blocked"
    assert cross_detail.json()["data"]["error"]["code"] == "unknown_session_id"

    closed = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/close")
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"
    assert closed.json()["data"]["session"]["status"] == "closed"
    assert closed.json()["data"]["session"]["closed_at"]
    _assert_no_internal_paths(closed.json())

    closed_again = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/close")
    assert closed_again.status_code == 200
    assert closed_again.json()["data"]["session"]["status"] == "closed"

    deleted = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/delete")
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "disposed"
    assert deleted.json()["data"]["session"]["status"] == "disposed"
    assert deleted.json()["data"]["session"]["deleted_at"]
    _assert_no_internal_paths(deleted.json())

    deleted_detail = client.get(f"/api/workspaces/{workspace_id}/sessions/{session_id}")
    assert deleted_detail.status_code == 200
    assert deleted_detail.json()["data"]["session"]["status"] == "disposed"

    default_after_delete = client.get(f"/api/workspaces/{workspace_id}/sessions")
    assert default_after_delete.status_code == 200
    assert default_after_delete.json()["data"]["items"] == []

    include_deleted = client.get(f"/api/workspaces/{workspace_id}/sessions", params={"include_deleted": True})
    assert include_deleted.status_code == 200
    assert include_deleted.json()["data"]["items"][0]["status"] == "disposed"

    deleted_again = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/delete")
    assert deleted_again.status_code == 200
    assert deleted_again.json()["data"]["session"]["status"] == "disposed"

    close_deleted = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/close")
    assert close_deleted.status_code == 200
    assert close_deleted.json()["data"]["session"]["status"] == "disposed"

    cross_close = client.post(f"/api/workspaces/{other_workspace_id}/sessions/{session_id}/close")
    cross_delete = client.post(f"/api/workspaces/{other_workspace_id}/sessions/{session_id}/delete")
    assert cross_close.json()["data"]["error"]["code"] == "unknown_session_id"
    assert cross_delete.json()["data"]["error"]["code"] == "unknown_session_id"

    assert not (root / workspace_id / "lifecycle" / "operations").exists()
    assert not (root / workspace_id / "lifecycle" / "sources.json").exists()


def test_v16d2_session_lifecycle_target_http_validation_boundaries_and_existing_surfaces(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Lifecycle Boundary")

    unknown_workspace = client.get("/api/workspaces/unknown-workspace/sessions")
    assert unknown_workspace.status_code == 404

    unknown_session = client.get(f"/api/workspaces/{workspace_id}/sessions/ksess_unknown")
    assert unknown_session.status_code == 200
    assert unknown_session.json()["status"] == "blocked"
    assert unknown_session.json()["data"]["error"]["code"] == "unknown_session_id"

    invalid_limit = client.get(f"/api/workspaces/{workspace_id}/sessions", params={"limit": 0})
    too_large_limit = client.get(f"/api/workspaces/{workspace_id}/sessions", params={"limit": 101})
    assert invalid_limit.status_code == 400
    assert too_large_limit.status_code == 400

    archived = client.post(f"/api/workspaces/{workspace_id}/archive", json={"reason": "done"})
    assert archived.status_code == 200
    blocked_create = client.post(f"/api/workspaces/{workspace_id}/sessions", json={"external_id": "archived"})
    assert blocked_create.status_code == 200
    assert blocked_create.json()["status"] == "blocked"
    assert blocked_create.json()["data"]["error"]["code"] == "workspace_archived"

    graph_session = client.get(f"/api/workspaces/{workspace_id}/graph/session")
    assert graph_session.status_code == 200
    assert graph_session.json()["data"]["items"] == []

    empty_ingest = client.post(f"/api/workspaces/{workspace_id}/sessions/ksess_alpha/ingest", json={})
    assert empty_ingest.status_code == 200
    assert empty_ingest.json()["status"] == "blocked"
    assert empty_ingest.json()["data"]["error"]["code"] == "workspace_archived"
    empty_query = client.post(f"/api/workspaces/{workspace_id}/sessions/ksess_alpha/query", json={})
    assert empty_query.status_code == 200
    assert empty_query.json()["status"] == "blocked"
    assert empty_query.json()["data"]["error"]["code"] == "invalid_session_query_request"
    session_build = client.post(f"/api/workspaces/{workspace_id}/sessions/ksess_alpha/build/start", json={})
    assert session_build.status_code == 200
    assert session_build.json()["data"]["error"]["code"] == "workspace_archived"
    assert client.get(f"/api/workspaces/{workspace_id}/quality").status_code == 404

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = client.get(f"/api/workspaces/{workspace_id}/sessions")
    authorized = client.get(f"/api/workspaces/{workspace_id}/sessions", headers={"X-API-Key": "target-key"})
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
