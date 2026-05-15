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
    for forbidden in ["/quality/", "/workspace/", ".json", ".jsonl", ".parquet", ".md", "traceback", "raw"]:
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


def _feedback_payload(**overrides):
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


def _post_feedback(client: TestClient, workspace_id: str, **overrides):
    response = client.post(f"/api/workspaces/{workspace_id}/quality/feedback", json=_feedback_payload(**overrides))
    assert response.status_code == 200
    return response


def _review_rule(client: TestClient, workspace_id: str, rule_id: str, status: str):
    response = client.post(
        f"/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review",
        json={"status": status},
    )
    assert response.status_code == 200
    return response


def _rules_payload(root: Path, workspace_id: str) -> dict:
    return json.loads((root / workspace_id / "quality" / "correction_rules.json").read_text(encoding="utf-8"))


def _set_rule_status(root: Path, workspace_id: str, rule_id: str, status: str):
    payload = _rules_payload(root, workspace_id)
    for rule in payload["rules"]:
        if rule["rule_id"] == rule_id:
            rule["status"] = status
            break
    (root / workspace_id / "quality" / "correction_rules.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def _fingerprint(path: Path):
    if path.is_file():
        return path.read_text(encoding="utf-8")
    if path.is_dir():
        return sorted(str(item.relative_to(path)) for item in path.rglob("*"))
    return path.exists()


def test_v16e5_quality_correction_rules_build_empty_body_and_reserved_route(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Rules Build")
    workspace = root / workspace_id

    empty = client.post(f"/api/workspaces/{workspace_id}/quality/correction-rules/build", json={})
    assert empty.status_code == 200
    payload = empty.json()
    assert payload["status"] == "ok"
    assert payload["operation_id"] is None
    assert payload["data"]["status"] == "built"
    assert payload["data"]["count"] == 0
    assert payload["data"]["rules"] == []
    assert payload["data"]["truncated"] is False
    assert payload["data"]["artifact_ref"] == f"quality-correction-rules://{workspace_id}"
    _assert_no_internal_paths(payload)

    reserved = client.post(
        f"/api/workspaces/{workspace_id}/quality/correction-rules/build/review",
        json={"status": "approved"},
    )
    assert reserved.status_code == 404

    for field in ["status", "review", "approve", "apply", "rebuild_plan", "path", "source_path", "rules_path", "plan_path"]:
        rejected = client.post(f"/api/workspaces/{workspace_id}/quality/correction-rules/build", json={field: True})
        assert rejected.status_code == 422

    assert (workspace / "quality" / "correction_rules.json").exists()
    assert not (workspace / "quality" / "correction_plan.json").exists()


def test_v16e5_quality_correction_rules_build_preserves_review_and_does_not_mutate_plan(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Rules Build Preserve")
    workspace = root / workspace_id

    _post_feedback(client, workspace_id, target_id="entity-approved")
    _post_feedback(client, workspace_id, target_id="entity-rejected")
    _post_feedback(client, workspace_id, target_id="entity-archived")
    _post_feedback(client, workspace_id, target_id="entity-revoked")
    _post_feedback(client, workspace_id, target_id="entity-active")
    _post_feedback(client, workspace_id, target_id="entity-applied")
    rules = _rules_payload(root, workspace_id)["rules"]
    ids_by_target = {rule["target_id"]: rule["rule_id"] for rule in rules}
    _review_rule(client, workspace_id, ids_by_target["entity-approved"], "approved")
    _review_rule(client, workspace_id, ids_by_target["entity-rejected"], "rejected")
    _review_rule(client, workspace_id, ids_by_target["entity-archived"], "archived")
    _review_rule(client, workspace_id, ids_by_target["entity-revoked"], "revoked")
    _set_rule_status(root, workspace_id, ids_by_target["entity-active"], "active")
    _set_rule_status(root, workspace_id, ids_by_target["entity-applied"], "applied")

    generated_plan = client.post(f"/api/workspaces/{workspace_id}/quality/correction-plan", json={})
    assert generated_plan.status_code == 200
    _post_feedback(client, workspace_id, target_id="entity-new")

    before = {
        "plan": _fingerprint(workspace / "quality" / "correction_plan.json"),
        "reviews": _fingerprint(workspace / "quality" / "correction_reviews.json"),
        "governance": _fingerprint(workspace / "quality" / "read_time_governance.json"),
        "sources": _fingerprint(workspace / "lifecycle" / "sources.json"),
        "operations": _fingerprint(workspace / "lifecycle" / "operations"),
        "llmwiki": _fingerprint(workspace / "llmwiki"),
        "graph": _fingerprint(workspace / "graphrag"),
        "sessions": _fingerprint(workspace / "sessions"),
    }

    response = client.post(f"/api/workspaces/{workspace_id}/quality/correction-rules/build", json={})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "correction_plan_may_be_stale" in payload["warnings"]
    assert "knowledge_correction_plan" in payload["next_actions"]
    assert payload["data"]["count"] == 7
    assert payload["data"]["limit"] == 50
    assert payload["data"]["truncated"] is False
    assert payload["data"]["summary"]["status_counts"]["approved"] == 1
    assert payload["data"]["summary"]["status_counts"]["rejected"] == 1
    assert payload["data"]["summary"]["status_counts"]["archived"] == 1
    assert payload["data"]["summary"]["status_counts"]["revoked"] == 1
    assert payload["data"]["summary"]["status_counts"]["active"] == 1
    assert payload["data"]["summary"]["status_counts"]["applied"] == 1
    assert payload["data"]["summary"]["status_counts"]["draft"] == 1
    _assert_no_internal_paths(payload)

    rebuilt = _rules_payload(root, workspace_id)["rules"]
    statuses = {rule["target_id"]: rule["status"] for rule in rebuilt}
    assert statuses["entity-approved"] == "approved"
    assert statuses["entity-rejected"] == "rejected"
    assert statuses["entity-archived"] == "archived"
    assert statuses["entity-revoked"] == "revoked"
    assert statuses["entity-active"] == "active"
    assert statuses["entity-applied"] == "applied"
    assert statuses["entity-new"] == "draft"

    assert _fingerprint(workspace / "quality" / "correction_plan.json") == before["plan"]
    assert _fingerprint(workspace / "quality" / "correction_reviews.json") == before["reviews"]
    assert _fingerprint(workspace / "quality" / "read_time_governance.json") == before["governance"]
    assert _fingerprint(workspace / "lifecycle" / "sources.json") == before["sources"]
    assert _fingerprint(workspace / "lifecycle" / "operations") == before["operations"]
    assert _fingerprint(workspace / "llmwiki") == before["llmwiki"]
    assert _fingerprint(workspace / "graphrag") == before["graph"]
    assert _fingerprint(workspace / "sessions") == before["sessions"]

    assert client.post(f"/api/workspaces/{workspace_id}/quality/build", json={}).status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/quality/correction-plan/build", json={}).status_code == 404


def test_v16e5_quality_correction_rules_build_archived_auth_and_compatibility(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Quality Rules Build Auth")
    workspace = root / workspace_id
    _post_feedback(client, workspace_id)

    compatibility = client.post(
        "/api/v1/knowledge/quality/corrections/build",
        json={"workspace": str(workspace)},
    )
    assert compatibility.status_code == 200

    assert client.post(f"/api/workspaces/{workspace_id}/archive", json={}).status_code == 200
    archived = client.post(f"/api/workspaces/{workspace_id}/quality/correction-rules/build", json={})
    assert archived.status_code == 200
    assert archived.json()["status"] == "blocked"
    assert archived.json()["data"]["error"]["code"] == "workspace_archived"

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = client.post(f"/api/workspaces/{workspace_id}/quality/correction-rules/build", json={})
    authorized = client.post(
        f"/api/workspaces/{workspace_id}/quality/correction-rules/build",
        json={},
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
