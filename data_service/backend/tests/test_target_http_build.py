import json

from fastapi.testclient import TestClient

from app.config import config
from app.main import app


FORBIDDEN_CONTRACT_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "source_path",
    "original_path",
    "artifact_physical_path",
    "workspace_layout",
    "artifact_layout",
    "internal_path",
    "debug_paths",
    "cache_path",
    "physical_path",
    "local_path",
    "path",
    "paths",
    "traceback",
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


def _write_operation(root, workspace_id: str, operation_id: str, *, status: str = "queued") -> None:
    operation_dir = root / workspace_id / "lifecycle" / "operations"
    operation_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "operation_id": operation_id,
        "workspace_id": workspace_id,
        "mode": "full",
        "paths": [str(root / workspace_id / "sources" / "imported" / "raw.md")],
        "status": status,
        "stage": status,
        "progress": 1.0 if status == "completed" else 0.0,
        "error": {
            "message": "failed",
            "traceback": f"{root}/internal/file.py",
            "path": f"{root}/internal/file.py",
        } if status == "failed" else None,
        "retryable": status == "failed",
        "artifacts": [str(root / workspace_id / "llmwiki" / "physical.md")],
        "results": [{"engine": "llmwiki", "status": "ok", "meta": {"path": str(root / "hidden")}}],
        "created_at": "2026-05-13T00:00:00Z",
        "updated_at": "2026-05-13T00:00:00Z",
        "completed_at": "2026-05-13T00:00:00Z" if status in {"completed", "failed"} else None,
    }
    (operation_dir / f"{operation_id}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_v16b3_build_target_http_start_status_and_no_path_leakage(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "note.md"
    source_file.write_text("# Build\n\nTarget HTTP build.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Build KB")
    imported = client.post(f"/api/workspaces/{workspace_id}/sources", json={"paths": [str(source_file)]})
    assert imported.status_code == 200

    started = client.post(f"/api/workspaces/{workspace_id}/build/start", json={"mode": "llmwiki_only"})
    assert started.status_code == 200
    start_payload = started.json()
    assert start_payload["operation_id"].startswith("op_")
    assert start_payload["data"]["operation_id"] == start_payload["operation_id"]
    assert start_payload["status"] in {"queued", "running", "completed", "blocked", "failed"}
    assert (root / workspace_id / "lifecycle" / "operations" / f"{start_payload['operation_id']}.json").exists()
    _assert_no_internal_paths(start_payload)

    status = client.get(f"/api/workspaces/{workspace_id}/build/operations/{start_payload['operation_id']}")
    assert status.status_code == 200
    status_payload = status.json()
    assert status_payload["operation_id"] == start_payload["operation_id"]
    assert status_payload["data"]["operation_id"] == start_payload["operation_id"]
    _assert_no_internal_paths(status_payload)


def test_v16b3_build_target_http_cancel_unknown_cross_workspace_and_terminal(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_a = _create_workspace(client, "Build A")
    workspace_b = _create_workspace(client, "Build B")
    _write_operation(root, workspace_a, "op_manual_queued", status="queued")
    _write_operation(root, workspace_a, "op_manual_done", status="completed")

    missing_workspace = client.get("/api/workspaces/missing/build/operations/op_any")
    assert missing_workspace.status_code == 404

    missing_operation = client.get(f"/api/workspaces/{workspace_a}/build/operations/op_missing")
    assert missing_operation.status_code == 200
    assert missing_operation.json()["status"] == "blocked"
    assert missing_operation.json()["data"]["error"]["code"] == "unknown_operation_id"

    cross_status = client.get(f"/api/workspaces/{workspace_b}/build/operations/op_manual_queued")
    assert cross_status.status_code == 200
    assert cross_status.json()["status"] == "blocked"

    cancelled = client.post(f"/api/workspaces/{workspace_a}/build/operations/op_manual_queued/cancel", json={"reason": "test"})
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    _assert_no_internal_paths(cancelled.json())

    terminal_cancel = client.post(f"/api/workspaces/{workspace_a}/build/operations/op_manual_done/cancel", json={})
    assert terminal_cancel.status_code == 200
    assert terminal_cancel.json()["status"] == "completed"
    assert terminal_cancel.json()["warnings"]
    _assert_no_internal_paths(terminal_cancel.json())


def test_v16b3_build_target_http_archived_invalid_path_and_compatibility_retained(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    outside_root = tmp_path / "outside"
    source_root.mkdir()
    outside_root.mkdir()
    allowed_file = source_root / "allowed.md"
    outside_file = outside_root / "outside.md"
    allowed_file.write_text("allowed", encoding="utf-8")
    outside_file.write_text("outside", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Build Compat")

    invalid_mode = client.post(f"/api/workspaces/{workspace_id}/build/start", json={"mode": "new_mode"})
    assert invalid_mode.status_code == 400

    disallowed = client.post(f"/api/workspaces/{workspace_id}/build/start", json={"paths": [str(outside_file)]})
    assert disallowed.status_code == 400
    traversal = client.post(f"/api/workspaces/{workspace_id}/build/start", json={"paths": [str(source_root / ".." / "outside" / "outside.md")]})
    assert traversal.status_code == 400

    before_sources = root / workspace_id / "lifecycle" / "sources.json"
    before_payload = before_sources.read_text(encoding="utf-8") if before_sources.exists() else ""
    allowed = client.post(f"/api/workspaces/{workspace_id}/build/start", json={"paths": [str(allowed_file)], "mode": "llmwiki_only"})
    assert allowed.status_code == 200
    after_payload = before_sources.read_text(encoding="utf-8") if before_sources.exists() else ""
    assert after_payload == before_payload

    compat_status = client.post(
        "/api/v1/knowledge/build/status",
        json={"workspace_id": workspace_id, "operation_id": allowed.json()["operation_id"]},
    )
    assert compat_status.status_code == 200

    assert client.post(f"/api/workspaces/{workspace_id}/archive", json={}).status_code == 200
    archived = client.post(f"/api/workspaces/{workspace_id}/build/start", json={})
    assert archived.status_code == 200
    assert archived.json()["status"] == "blocked"


def test_v16b3_build_target_http_source_trace_and_auth_unchanged(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Auth Build")
    missing_trace = client.get(f"/api/workspaces/{workspace_id}/sources/src_missing/trace")
    assert missing_trace.status_code == 422

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)

    unauthorized = client.post(f"/api/workspaces/{workspace_id}/build/start", json={})
    authorized = client.post(f"/api/workspaces/{workspace_id}/build/start", json={}, headers={"X-API-Key": "target-key"})

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
