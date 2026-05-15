import json

from fastapi.testclient import TestClient

from app.config import config
from app.main import app


FORBIDDEN_CONTRACT_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "rules_path",
    "plan_path",
    "source_path",
    "original_path",
    "local_path",
    "artifact_physical_path",
    "graphrag_cache_path",
    "cache_path",
    "physical_path",
    "internal_path",
    "debug_paths",
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


def _rule_payload(**overrides):
    payload = {
        "target_type": "entity",
        "target_id": "entity-alpha",
        "action": "rename_suggest",
        "label": "Alpha",
        "suggested_value": "Alpha canonical",
        "reason": "Normalize duplicate entity label",
        "metadata": {"source": "target-http"},
    }
    payload.update(overrides)
    return payload


def _create_rule(client: TestClient, workspace_id: str, **overrides) -> str:
    response = client.post(f"/api/workspaces/{workspace_id}/quality/correction-rules", json=_rule_payload(**overrides))
    assert response.status_code == 200
    return response.json()["data"]["rule_id"]


def _review_rule(client: TestClient, workspace_id: str, rule_id: str, payload: dict):
    return client.post(f"/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review", json=payload)


def _fingerprint(path):
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return path.exists()


def _set_rule_status(root, workspace_id: str, rule_id: str, status: str):
    path = root / workspace_id / "quality" / "correction_rules.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for rule in payload["rules"]:
        if rule["rule_id"] == rule_id:
            rule["status"] = status
            break
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def test_v16e3_quality_correction_review_updates_status_only_without_plan_side_effects(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Review")
    workspace = root / workspace_id
    rule_id = _create_rule(client, workspace_id)
    plan_path = workspace / "quality" / "correction_plan.json"
    watched = {
        "plan": _fingerprint(plan_path),
        "operations": (workspace / "lifecycle" / "operations").exists(),
        "sources": _fingerprint(workspace / "lifecycle" / "sources.json"),
        "llmwiki": (workspace / "llmwiki").exists(),
        "graph": (workspace / "graphrag").exists(),
        "sessions": (workspace / "sessions").exists(),
    }

    response = _review_rule(client, workspace_id, rule_id, {"status": "approved", "reviewer": "body-user", "note": "looks right"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["data"]["rule_id"] == rule_id
    assert payload["data"]["status"] == "approved"
    assert payload["data"]["reviewer"] == "body-user"
    assert payload["data"]["rule"]["status"] == "approved"
    assert "correction_plan_summary" not in payload["data"]
    _assert_no_internal_paths(payload)

    assert _fingerprint(plan_path) == watched["plan"]
    assert (workspace / "lifecycle" / "operations").exists() == watched["operations"]
    assert _fingerprint(workspace / "lifecycle" / "sources.json") == watched["sources"]
    assert (workspace / "llmwiki").exists() == watched["llmwiki"]
    assert (workspace / "graphrag").exists() == watched["graph"]
    assert (workspace / "sessions").exists() == watched["sessions"]

    listed = client.get(f"/api/workspaces/{workspace_id}/quality/correction-rules?status=approved")
    assert listed.status_code == 200
    assert listed.json()["data"]["rules"][0]["rule_id"] == rule_id


def test_v16e3_quality_correction_review_validation_transitions_and_cross_workspace_isolation(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Review A")
    other_workspace_id = _create_workspace(client, "Quality Review B")
    rule_id = _create_rule(client, workspace_id)

    body_rule_id = _review_rule(client, workspace_id, rule_id, {"rule_id": rule_id, "status": "approved"})
    assert body_rule_id.status_code == 422

    bad_status = _review_rule(client, workspace_id, rule_id, {"status": "active"})
    assert bad_status.status_code == 400

    draft_reset = _review_rule(client, workspace_id, rule_id, {"status": "draft"})
    assert draft_reset.status_code == 200
    approved = _review_rule(client, workspace_id, rule_id, {"status": "approved"})
    assert approved.status_code == 200
    approved_again = _review_rule(client, workspace_id, rule_id, {"status": "approved"})
    assert approved_again.status_code == 200
    rejected = _review_rule(client, workspace_id, rule_id, {"status": "rejected"})
    assert rejected.status_code == 200
    back_to_approved = _review_rule(client, workspace_id, rule_id, {"status": "approved"})
    assert back_to_approved.status_code == 200
    archived = _review_rule(client, workspace_id, rule_id, {"status": "archived"})
    assert archived.status_code == 200
    archived_to_approved = _review_rule(client, workspace_id, rule_id, {"status": "approved"})
    assert archived_to_approved.status_code == 200
    revoked = _review_rule(client, workspace_id, rule_id, {"status": "revoked"})
    assert revoked.status_code == 200
    revoked_to_approved = _review_rule(client, workspace_id, rule_id, {"status": "approved"})
    assert revoked_to_approved.status_code == 200

    _set_rule_status(root, workspace_id, rule_id, "active")
    active_review = _review_rule(client, workspace_id, rule_id, {"status": "approved"})
    assert active_review.status_code == 400
    assert "active/applied" in active_review.json()["detail"]
    _set_rule_status(root, workspace_id, rule_id, "applied")
    applied_review = _review_rule(client, workspace_id, rule_id, {"status": "rejected"})
    assert applied_review.status_code == 400

    cross_workspace = _review_rule(client, other_workspace_id, rule_id, {"status": "approved"})
    assert cross_workspace.status_code == 400
    assert "Unknown correction rule" in cross_workspace.json()["detail"]
    unknown = _review_rule(client, workspace_id, "rule_missing", {"status": "approved"})
    assert unknown.status_code == 400


def test_v16e3_quality_correction_review_surface_scope_auth_and_compatibility(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Review Scope")
    workspace = root / workspace_id
    rule_id = _create_rule(client, workspace_id)

    unsupported_field = _review_rule(client, workspace_id, rule_id, {"status": "approved", "apply": True})
    assert unsupported_field.status_code == 422
    long_reviewer = _review_rule(client, workspace_id, rule_id, {"status": "approved", "reviewer": "x" * 300})
    assert long_reviewer.status_code == 422

    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/plan", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/build", json={}).status_code == 404
    assert client.get(f"/api/workspaces/{workspace_id}/quality/corrections/plan").status_code == 404

    compatibility = client.post(
        "/api/v1/knowledge/quality/corrections/review",
        json={"workspace": str(workspace), "rule_id": rule_id, "status": "approved"},
    )
    assert compatibility.status_code == 200

    archived_workspace_id = _create_workspace(client, "Quality Review Archived")
    archived_rule_id = _create_rule(client, archived_workspace_id)
    assert client.post(f"/api/workspaces/{archived_workspace_id}/archive", json={}).status_code == 200
    archived = _review_rule(client, archived_workspace_id, archived_rule_id, {"status": "approved"})
    assert archived.status_code == 200
    assert archived.json()["status"] == "blocked"
    assert archived.json()["data"]["error"]["code"] == "workspace_archived"

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = _review_rule(client, workspace_id, rule_id, {"status": "approved"})
    authorized = client.post(
        f"/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review",
        json={"status": "approved"},
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
