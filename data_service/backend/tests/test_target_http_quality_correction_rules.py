import json

from fastapi.testclient import TestClient

from app.config import config
from app.main import app


FORBIDDEN_CONTRACT_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "rules_path",
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


def _post_rule(client: TestClient, workspace_id: str, payload: dict):
    return client.post(f"/api/workspaces/{workspace_id}/quality/correction-rules", json=payload)


def _list_rules(client: TestClient, workspace_id: str, query: str = ""):
    return client.get(f"/api/workspaces/{workspace_id}/quality/correction-rules{query}")


def _file_fingerprint(path):
    return path.read_text(encoding="utf-8") if path.exists() else None


def test_v16e2_quality_correction_rules_list_and_create_stable_projection(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Correction Rules")
    workspace = root / workspace_id
    plan_path = workspace / "quality" / "correction_plan.json"
    operations_dir = workspace / "lifecycle" / "operations"
    sources_path = workspace / "lifecycle" / "sources.json"

    empty = _list_rules(client, workspace_id)
    assert empty.status_code == 200
    empty_payload = empty.json()
    assert empty_payload["data"]["rules"] == []
    assert empty_payload["data"]["count"] == 0
    assert empty_payload["data"]["truncated"] is False
    _assert_no_internal_paths(empty_payload)
    assert not plan_path.exists()

    response = _post_rule(
        client,
        workspace_id,
        _rule_payload(
            metadata={
                "note": "ok",
                "rules_path": str(workspace / "quality" / "correction_rules.json"),
                "nested": {"source_path": str(workspace / "row" / "raw.md")},
            }
        ),
    )
    assert response.status_code == 200
    payload = response.json()
    rule = payload["data"]["rule"]
    assert payload["workspace_id"] == workspace_id
    assert payload["status"] == "ok"
    assert payload["data"]["operation"] == "created"
    assert payload["data"]["rule_id"] == rule["rule_id"]
    assert rule["rule_id"].startswith("rule_manual_")
    assert rule["status"] == "draft"
    assert rule["target_type"] == "entity"
    assert rule["target_id"] == "entity-alpha"
    assert rule["action"] == "rename_suggest"
    assert rule["suggested_value"] == "Alpha canonical"
    assert payload["data"]["artifact_ref"] == f"quality-correction-rules://{workspace_id}"
    _assert_no_internal_paths(payload)

    rules_file = workspace / "quality" / "correction_rules.json"
    assert rules_file.exists()
    assert not plan_path.exists()
    assert not operations_dir.exists()
    assert not sources_path.exists()

    listed = _list_rules(client, workspace_id, "?limit=1&status=draft")
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert listed_payload["data"]["count"] == 1
    assert listed_payload["data"]["rules"][0]["rule_id"] == rule["rule_id"]
    assert listed_payload["data"]["truncated"] is False
    assert listed_payload["data"]["artifact_ref"] == f"quality-correction-rules://{workspace_id}"
    _assert_no_internal_paths(listed_payload)


def test_v16e2_quality_correction_rules_validation_update_and_cross_workspace_isolation(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Rules A")
    other_workspace_id = _create_workspace(client, "Quality Rules B")
    created = _post_rule(client, workspace_id, _rule_payload())
    assert created.status_code == 200
    rule_id = created.json()["data"]["rule_id"]

    unsupported_status = _post_rule(client, workspace_id, _rule_payload(status="approved"))
    assert unsupported_status.status_code == 422

    bad_action = _post_rule(client, workspace_id, _rule_payload(action="approve"))
    assert bad_action.status_code == 400

    missing_suggested = _post_rule(client, workspace_id, _rule_payload(suggested_value=""))
    assert missing_suggested.status_code == 400

    path_target = _post_rule(client, workspace_id, _rule_payload(target_id="../quality/correction_rules.json"))
    assert path_target.status_code == 400

    stable_ref_target = _post_rule(client, workspace_id, _rule_payload(target_id="entity://stable/ref", action="needs_review", suggested_value=""))
    assert stable_ref_target.status_code == 200

    too_deep = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": "too-deep"}}}}}}}}}
    deep_metadata = _post_rule(client, workspace_id, _rule_payload(metadata=too_deep))
    assert deep_metadata.status_code == 400

    updated = _post_rule(
        client,
        workspace_id,
        _rule_payload(rule_id=rule_id, label="Alpha updated", suggested_value="Alpha canonical updated"),
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["operation"] == "updated"
    assert updated.json()["data"]["rule"]["rule_id"] == rule_id
    assert updated.json()["data"]["rule"]["label"] == "Alpha updated"

    cross_workspace = _post_rule(client, other_workspace_id, _rule_payload(rule_id=rule_id))
    assert cross_workspace.status_code == 400
    assert "Unknown correction rule" in cross_workspace.json()["detail"]
    other_list = _list_rules(client, other_workspace_id)
    assert other_list.status_code == 200
    assert other_list.json()["data"]["rules"] == []

    rules_path = root / workspace_id / "quality" / "correction_rules.json"
    rules_payload = json.loads(rules_path.read_text(encoding="utf-8"))
    rules_payload["rules"][0]["status"] = "approved"
    rules_path.write_text(json.dumps(rules_payload, ensure_ascii=False), encoding="utf-8")
    terminal_update = _post_rule(client, workspace_id, _rule_payload(rule_id=rule_id, label="Should fail"))
    assert terminal_update.status_code == 400
    assert "terminal correction rules cannot be updated" in terminal_update.json()["detail"]


def test_v16e2_quality_correction_rules_side_effect_boundaries_surface_scope_and_auth(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Rules Scope")
    workspace = root / workspace_id
    correction_plan = workspace / "quality" / "correction_plan.json"
    review_artifacts = [workspace / "quality" / "review.json", workspace / "quality" / "reviews.json"]
    source_paths = [
        workspace / "lifecycle" / "sources.json",
        workspace / "llmwiki",
        workspace / "graphrag",
        workspace / "sessions",
        workspace / "session",
    ]
    before = {
        "plan": _file_fingerprint(correction_plan),
        "reviews": [_file_fingerprint(path) for path in review_artifacts],
        "sources": [_file_fingerprint(path) if path.is_file() else path.exists() for path in source_paths],
        "operations": (workspace / "lifecycle" / "operations").exists(),
    }

    response = _post_rule(client, workspace_id, _rule_payload(action="mark_noise", suggested_value=""))
    assert response.status_code == 200
    assert (workspace / "quality" / "correction_rules.json").exists()
    assert _file_fingerprint(correction_plan) == before["plan"]
    assert [_file_fingerprint(path) for path in review_artifacts] == before["reviews"]
    assert [_file_fingerprint(path) if path.is_file() else path.exists() for path in source_paths] == before["sources"]
    assert (workspace / "lifecycle" / "operations").exists() == before["operations"]

    assert client.post(f"/api/workspaces/{workspace_id}/quality/feedback", json={"target_type": "page", "target_id": "page-alpha", "action": "mark_noise"}).status_code == 200
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/review", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/plan", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/corrections/build", json={}).status_code == 404
    assert client.get(f"/api/workspaces/{workspace_id}/quality/corrections").status_code == 404

    assert client.post(f"/api/workspaces/{workspace_id}/archive", json={}).status_code == 200
    archived = _post_rule(client, workspace_id, _rule_payload(action="needs_review", suggested_value=""))
    assert archived.status_code == 200
    assert archived.json()["status"] == "blocked"
    assert archived.json()["data"]["error"]["code"] == "workspace_archived"

    compatibility = client.post(
        "/api/v1/knowledge/quality/corrections",
        json={"workspace": str(workspace), "limit": 5},
    )
    assert compatibility.status_code == 200

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = _list_rules(client, workspace_id)
    authorized = client.get(
        f"/api/workspaces/{workspace_id}/quality/correction-rules",
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
