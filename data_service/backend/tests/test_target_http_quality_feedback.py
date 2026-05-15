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
    "local_path",
    "artifact_physical_path",
    "graphrag_cache_path",
    "cache_path",
    "physical_path",
    "internal_path",
    "debug_paths",
    "feedback_path",
    "rules_path",
    "plan_path",
    "path",
    "paths",
}


def _assert_no_internal_paths(payload):
    serialized = json.dumps(payload, ensure_ascii=False).lower()
    for forbidden in ["/quality/", "/workspace/", ".json", ".jsonl", ".parquet", "traceback"]:
        assert forbidden not in serialized

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                assert key not in FORBIDDEN_CONTRACT_KEYS
                assert not str(key).endswith("_path")
                assert not str(key).endswith("_paths")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _record_feedback(client: TestClient, workspace_id: str, payload: dict):
    return client.post(f"/api/workspaces/{workspace_id}/quality/feedback", json=payload)


def test_v16e1_quality_feedback_records_stable_projection_without_path_leakage(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Feedback")
    before_sources = root / workspace_id / "lifecycle" / "sources.json"
    before_sources_text = before_sources.read_text(encoding="utf-8") if before_sources.exists() else ""

    response = _record_feedback(
        client,
        workspace_id,
        {
            "target_type": "entity",
            "target_id": "entity-alpha",
            "action": "needs_review",
            "label": "Alpha",
            "suggested_value": "Alpha canonical",
            "reason": "Duplicate-looking entity",
            "metadata": {
                "score": 0.42,
                "source_path": str(root / workspace_id / "quality" / "feedback.jsonl"),
                "nested": {"debug_paths": [str(root / workspace_id / "graph" / "nodes.parquet")]},
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace_id"] == workspace_id
    assert payload["status"] == "ok"
    feedback = payload["data"]["feedback"]
    assert feedback["workspace_id"] == workspace_id
    assert feedback["feedback_id"]
    assert feedback["target_type"] == "entity"
    assert feedback["target_id"] == "entity-alpha"
    assert feedback["action"] == "needs_review"
    assert feedback["status"] == "recorded"
    assert feedback["artifact_ref"] == f"quality-feedback://{feedback['feedback_id']}"
    assert payload["artifact_refs"][0]["artifact_ref"] == feedback["artifact_ref"]
    assert payload["data"]["summary"]["feedback_count"] == 1
    _assert_no_internal_paths(payload)

    assert not (root / workspace_id / "lifecycle" / "operations").exists()
    assert (before_sources.read_text(encoding="utf-8") if before_sources.exists() else "") == before_sources_text
    assert not (root / workspace_id / "quality" / "correction_plan.json").exists()


def test_v16e1_quality_feedback_validation_boundaries_and_archived_workspace(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Feedback Boundaries")

    missing = _record_feedback(client, workspace_id, {"target_type": "entity", "target_id": "entity-alpha"})
    assert missing.status_code == 422

    unsupported_field = _record_feedback(
        client,
        workspace_id,
        {"target_type": "entity", "target_id": "entity-alpha", "action": "needs_review", "apply": True},
    )
    assert unsupported_field.status_code == 422

    path_target = _record_feedback(
        client,
        workspace_id,
        {"target_type": "entity", "target_id": "../secret.json", "action": "needs_review"},
    )
    assert path_target.status_code == 400
    assert "stable non-path" in path_target.json()["detail"]

    assert client.post(f"/api/workspaces/{workspace_id}/archive", json={}).status_code == 200
    archived = _record_feedback(
        client,
        workspace_id,
        {"target_type": "entity", "target_id": "entity-alpha", "action": "needs_review"},
    )
    assert archived.status_code == 200
    assert archived.json()["status"] == "blocked"
    assert archived.json()["data"]["error"]["code"] == "workspace_archived"
    _assert_no_internal_paths(archived.json())

    unknown = _record_feedback(
        client,
        "missing-workspace",
        {"target_type": "entity", "target_id": "entity-alpha", "action": "needs_review"},
    )
    assert unknown.status_code == 404


def test_v16e1_quality_feedback_surface_scope_and_auth(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Feedback Surface")
    assert _record_feedback(client, workspace_id, {"target_type": "page", "target_id": "page-alpha", "action": "mark_noise"}).status_code == 200

    assert client.post(f"/api/workspaces/{workspace_id}/quality/feedback/list", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/review", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/plan", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/build", json={}).status_code == 404

    compatibility = client.post(
        "/api/v1/knowledge/quality/feedback",
        json={"workspace": str(root / workspace_id), "target_type": "entity", "target_id": "compat", "action": "needs_review"},
    )
    assert compatibility.status_code == 200

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = _record_feedback(client, workspace_id, {"target_type": "page", "target_id": "auth", "action": "needs_review"})
    authorized = client.post(
        f"/api/workspaces/{workspace_id}/quality/feedback",
        json={"target_type": "page", "target_id": "auth", "action": "needs_review"},
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
