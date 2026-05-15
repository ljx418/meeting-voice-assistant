import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import config
from app.main import app
from data_service.session_service import SessionKnowledgeService


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
    "traceback",
}


def _assert_no_internal_paths(payload):
    serialized = json.dumps(payload, ensure_ascii=False).lower()
    for forbidden in ["/sessions/", "/graph/", "/distill/", ".json", ".parquet", "traceback"]:
        assert forbidden not in serialized

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                assert key not in FORBIDDEN_CONTRACT_KEYS
                assert not str(key).endswith("_path")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _create_session(client: TestClient, workspace_id: str, external_id: str) -> str:
    response = client.post(f"/api/workspaces/{workspace_id}/sessions", json={"external_id": external_id, "title": external_id})
    assert response.status_code == 200
    return response.json()["data"]["session"]["session_id"]


def _ingest(client: TestClient, workspace_id: str, session_id: str, content: str = "Alpha planning note"):
    response = client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/ingest", json={"content": content, "title": "Alpha"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    return response


def _session_build_start(client: TestClient, workspace_id: str, session_id: str, payload: dict | None = None):
    return client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/build/start", json=payload or {})


def _session_build_status(client: TestClient, workspace_id: str, session_id: str, operation_id: str):
    return client.get(f"/api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}")


def _session_build_cancel(client: TestClient, workspace_id: str, session_id: str, operation_id: str, payload: dict | None = None):
    return client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel", json=payload or {})


def _fingerprint_tree(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {str(item.relative_to(path)): item.read_text(encoding="utf-8") for item in sorted(path.rglob("*")) if item.is_file()}


def test_v16d6_session_build_start_status_projection_and_side_effect_boundaries(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Build")
    session_id = _create_session(client, workspace_id, "d6-build")
    _ingest(client, workspace_id, session_id)

    before_workspace_sources = _fingerprint_tree(root / workspace_id / "lifecycle" / "sources.json")
    before_quality = _fingerprint_tree(root / workspace_id / "quality")
    response = _session_build_start(client, workspace_id, session_id)
    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace_id"] == workspace_id
    assert payload["status"] in {"queued", "running", "succeeded", "failed", "cancelled", "blocked"}
    operation_id = payload["operation_id"]
    assert operation_id.startswith("sop_")
    assert payload["data"]["workspace_id"] == workspace_id
    assert payload["data"]["session_id"] == session_id
    assert payload["data"]["operation_id"] == operation_id
    assert payload["data"]["artifact_ref"] == f"session-build://{session_id}/{operation_id}"
    assert payload["artifact_refs"][0]["artifact_ref"] == f"session-build://{session_id}/{operation_id}"
    _assert_no_internal_paths(payload)

    status = _session_build_status(client, workspace_id, session_id, operation_id)
    assert status.status_code == 200
    assert status.json()["operation_id"] == operation_id
    assert status.json()["data"]["session_id"] == session_id
    _assert_no_internal_paths(status.json())

    assert _fingerprint_tree(root / workspace_id / "lifecycle" / "sources.json") == before_workspace_sources
    assert _fingerprint_tree(root / workspace_id / "quality") == before_quality
    assert not (root / workspace_id / "lifecycle" / "operations").exists()


def test_v16d6_session_build_validation_cancel_and_isolation(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Build Boundary")
    other_workspace_id = _create_workspace(client, "Session Build Other")
    session_id = _create_session(client, workspace_id, "d6-boundary")
    other_session_id = _create_session(client, workspace_id, "d6-other-session")
    _ingest(client, workspace_id, session_id)

    invalid_mode = _session_build_start(client, workspace_id, session_id, {"mode": "workspace"})
    assert invalid_mode.status_code == 200
    assert invalid_mode.json()["status"] == "blocked"
    assert invalid_mode.json()["data"]["error"]["code"] == "invalid_session_build_request"

    unsupported = _session_build_start(client, workspace_id, session_id, {"mode": "full", "paths": ["../secret"]})
    assert unsupported.status_code == 422

    unknown_workspace = _session_build_status(client, "unknown-workspace", session_id, "sop_missing")
    assert unknown_workspace.status_code == 404
    unknown_session = _session_build_start(client, workspace_id, "ksess_unknown")
    assert unknown_session.status_code == 200
    assert unknown_session.json()["data"]["error"]["code"] == "unknown_session_id"
    unknown_operation = _session_build_status(client, workspace_id, session_id, "sop_missing")
    assert unknown_operation.status_code == 200
    assert unknown_operation.json()["data"]["error"]["code"] == "unknown_operation_id"

    service = SessionKnowledgeService(root / workspace_id, workspace_id=workspace_id)
    queued = service.start_build(session_id=session_id, mode="full")
    operation_id = queued["operation_id"]

    cross_workspace = _session_build_status(client, other_workspace_id, session_id, operation_id)
    assert cross_workspace.status_code == 200
    assert cross_workspace.json()["data"]["error"]["code"] == "unknown_session_id"
    cross_session = _session_build_status(client, workspace_id, other_session_id, operation_id)
    assert cross_session.status_code == 200
    assert cross_session.json()["data"]["error"]["code"] == "unknown_operation_id"

    cancelled = _session_build_cancel(client, workspace_id, session_id, operation_id, {"reason": "test"})
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert service.get_operation(session_id, operation_id)["status"] == "cancelled"
    _assert_no_internal_paths(cancelled.json())

    terminal_cancel = _session_build_cancel(client, workspace_id, session_id, operation_id)
    assert terminal_cancel.status_code == 200
    assert terminal_cancel.json()["status"] == "cancelled"
    assert terminal_cancel.json()["warnings"]

    disposed_session = _create_session(client, workspace_id, "d6-disposed")
    assert client.post(f"/api/workspaces/{workspace_id}/sessions/{disposed_session}/delete").status_code == 200
    disposed_start = _session_build_start(client, workspace_id, disposed_session)
    assert disposed_start.status_code == 200
    assert disposed_start.json()["data"]["error"]["code"] == "session_disposed"

    no_source_session = _create_session(client, workspace_id, "d6-no-source")
    no_source_start = _session_build_start(client, workspace_id, no_source_session)
    assert no_source_start.status_code == 200
    assert no_source_start.json()["operation_id"].startswith("sop_")

    duplicate_start = _session_build_start(client, workspace_id, session_id)
    assert duplicate_start.status_code == 200
    assert duplicate_start.json()["operation_id"].startswith("sop_")
    assert duplicate_start.json()["operation_id"] != operation_id


def test_v16d6_session_build_keeps_existing_surfaces_and_auth(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Session Build Surface")
    session_id = _create_session(client, workspace_id, "d6-surface")
    _ingest(client, workspace_id, session_id)

    assert _session_build_start(client, workspace_id, session_id).status_code == 200
    assert client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/query", json={"query": "Alpha"}).status_code == 200
    assert client.post(f"/api/workspaces/{workspace_id}/sessions/{session_id}/ingest", json={"content": "x"}).status_code == 200
    assert client.get(f"/api/workspaces/{workspace_id}/sessions").status_code == 200
    assert client.get(f"/api/workspaces/{workspace_id}/graph/session").status_code == 200
    assert client.get(f"/api/workspaces/{workspace_id}/quality").status_code == 404

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = _session_build_start(client, workspace_id, session_id)
    authorized = client.post(
        f"/api/workspaces/{workspace_id}/sessions/{session_id}/build/start",
        json={},
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
