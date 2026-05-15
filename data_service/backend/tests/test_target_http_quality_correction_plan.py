import json
from pathlib import Path

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
    for forbidden in [
        "/quality/",
        "/workspace/",
        ".json",
        ".jsonl",
        ".parquet",
        ".md",
        "traceback",
        "raw patch",
        "raw impact",
    ]:
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


def _review_rule(client: TestClient, workspace_id: str, rule_id: str, status: str):
    response = client.post(
        f"/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review",
        json={"status": status},
    )
    assert response.status_code == 200
    return response


def _set_rule_status(root: Path, workspace_id: str, rule_id: str, status: str):
    path = root / workspace_id / "quality" / "correction_rules.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for rule in payload["rules"]:
        if rule["rule_id"] == rule_id:
            rule["status"] = status
            break
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _fingerprint(path: Path):
    if path.is_file():
        return path.read_text(encoding="utf-8")
    if path.is_dir():
        return sorted(str(item.relative_to(path)) for item in path.rglob("*"))
    return path.exists()


def test_v16e4_quality_correction_plan_get_missing_and_generate_plan_only(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Plan")
    workspace = root / workspace_id
    plan_path = workspace / "quality" / "correction_plan.json"

    missing = client.get(f"/api/workspaces/{workspace_id}/quality/correction-plan")
    assert missing.status_code == 200
    assert missing.json()["status"] == "blocked"
    assert missing.json()["data"]["error"]["code"] == "quality_correction_plan_no_artifact"
    assert not plan_path.exists()

    approved_rule_id = _create_rule(client, workspace_id, target_id="entity-approved")
    draft_rule_id = _create_rule(client, workspace_id, target_id="entity-draft")
    rejected_rule_id = _create_rule(client, workspace_id, target_id="entity-rejected")
    archived_rule_id = _create_rule(client, workspace_id, target_id="entity-archived")
    revoked_rule_id = _create_rule(client, workspace_id, target_id="entity-revoked")
    active_rule_id = _create_rule(client, workspace_id, target_id="entity-active")
    applied_rule_id = _create_rule(client, workspace_id, target_id="entity-applied")
    _review_rule(client, workspace_id, approved_rule_id, "approved")
    _review_rule(client, workspace_id, rejected_rule_id, "rejected")
    _review_rule(client, workspace_id, archived_rule_id, "archived")
    _review_rule(client, workspace_id, revoked_rule_id, "revoked")
    _set_rule_status(root, workspace_id, active_rule_id, "active")
    _set_rule_status(root, workspace_id, applied_rule_id, "applied")

    before = {
        "plan": _fingerprint(plan_path),
        "rules": _fingerprint(workspace / "quality" / "correction_rules.json"),
        "reviews": _fingerprint(workspace / "quality" / "correction_reviews.json"),
        "governance": _fingerprint(workspace / "quality" / "read_time_governance.json"),
        "sources": _fingerprint(workspace / "lifecycle" / "sources.json"),
        "operations": _fingerprint(workspace / "lifecycle" / "operations"),
        "llmwiki": _fingerprint(workspace / "llmwiki"),
        "graph": _fingerprint(workspace / "graphrag"),
        "sessions": _fingerprint(workspace / "sessions"),
    }

    generated = client.post(f"/api/workspaces/{workspace_id}/quality/correction-plan", json={})
    assert generated.status_code == 200
    payload = generated.json()
    assert payload["status"] == "ok"
    assert payload["operation_id"] is None
    data = payload["data"]
    assert data["workspace_id"] == workspace_id
    assert data["plan_id"].startswith("qplan_")
    assert data["rule_count"] == 1
    assert data["action_count"] == 1
    assert data["included_rule_ids"] == [approved_rule_id]
    assert data["excluded_rule_counts"]["draft"] == 1
    assert data["excluded_rule_counts"]["rejected"] == 1
    assert data["excluded_rule_counts"]["archived"] == 1
    assert data["excluded_rule_counts"]["revoked"] == 1
    assert data["excluded_rule_counts"]["active"] == 1
    assert data["excluded_rule_counts"]["applied"] == 1
    assert data["artifact_ref"] == f"quality-correction-plan://{workspace_id}"
    assert data["actions"][0] == {
        "action_id": f"action_{approved_rule_id}",
        "rule_id": approved_rule_id,
        "target_type": "entity",
        "target_id": "entity-approved",
        "action": "rename_target",
        "label": "Alpha",
        "summary": "rename_target entity entity-approved to Alpha canonical",
        "status": "planned",
    }
    assert "proposed_value" not in data["actions"][0]
    assert "impact" not in data["actions"][0]
    assert "target_engines" not in data["actions"][0]
    _assert_no_internal_paths(payload)

    assert before["plan"] is False
    assert plan_path.exists()
    assert _fingerprint(workspace / "quality" / "correction_rules.json") == before["rules"]
    assert _fingerprint(workspace / "quality" / "correction_reviews.json") == before["reviews"]
    assert _fingerprint(workspace / "quality" / "read_time_governance.json") == before["governance"]
    assert _fingerprint(workspace / "lifecycle" / "sources.json") == before["sources"]
    assert _fingerprint(workspace / "lifecycle" / "operations") == before["operations"]
    assert _fingerprint(workspace / "llmwiki") == before["llmwiki"]
    assert _fingerprint(workspace / "graphrag") == before["graph"]
    assert _fingerprint(workspace / "sessions") == before["sessions"]

    fetched = client.get(f"/api/workspaces/{workspace_id}/quality/correction-plan")
    assert fetched.status_code == 200
    assert fetched.json()["data"]["plan_id"] == data["plan_id"]
    _assert_no_internal_paths(fetched.json())

    repeated = client.post(f"/api/workspaces/{workspace_id}/quality/correction-plan", json={})
    assert repeated.status_code == 200
    repeated_data = repeated.json()["data"]
    assert repeated_data["plan_id"] == data["plan_id"]
    assert repeated_data["replaced_existing"] is True
    assert repeated_data["previous_plan_id"] == data["plan_id"]


def test_v16e4_quality_correction_plan_archived_workspace_and_surface_scope(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Plan Archived")
    rule_id = _create_rule(client, workspace_id)
    _review_rule(client, workspace_id, rule_id, "approved")
    assert client.post(f"/api/workspaces/{workspace_id}/quality/correction-plan", json={}).status_code == 200
    assert client.post(f"/api/workspaces/{workspace_id}/archive", json={}).status_code == 200

    archived_get = client.get(f"/api/workspaces/{workspace_id}/quality/correction-plan")
    assert archived_get.status_code == 200
    assert archived_get.json()["status"] == "ok"
    archived_post = client.post(f"/api/workspaces/{workspace_id}/quality/correction-plan", json={})
    assert archived_post.status_code == 200
    assert archived_post.json()["status"] == "blocked"
    assert archived_post.json()["data"]["error"]["code"] == "workspace_archived"

    unsupported_field = client.post(f"/api/workspaces/{workspace_id}/quality/correction-plan", json={"apply": True})
    assert unsupported_field.status_code == 422
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/build", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/build", json={}).status_code == 404

    compatibility = client.post(
        "/api/v1/knowledge/quality/corrections/plan",
        json={"workspace": str(root / workspace_id)},
    )
    assert compatibility.status_code == 200


def test_v16e4_quality_correction_plan_auth_boundary(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Plan Auth")
    rule_id = _create_rule(client, workspace_id)
    _review_rule(client, workspace_id, rule_id, "approved")

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)

    unauthorized_get = client.get(f"/api/workspaces/{workspace_id}/quality/correction-plan")
    unauthorized_post = client.post(f"/api/workspaces/{workspace_id}/quality/correction-plan", json={})
    authorized_post = client.post(
        f"/api/workspaces/{workspace_id}/quality/correction-plan",
        json={},
        headers={"X-API-Key": "target-key"},
    )
    authorized_get = client.get(
        f"/api/workspaces/{workspace_id}/quality/correction-plan",
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized_get.status_code == 401
    assert unauthorized_post.status_code == 401
    assert authorized_post.status_code == 200
    assert authorized_get.status_code == 200
