from pathlib import Path

from fastapi.testclient import TestClient

from app.config import config
from app.main import app


FORBIDDEN_CONTRACT_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
    "artifact_physical_path",
    "workspace_layout",
    "artifact_layout",
    "internal_path",
    "bound_paths",
    "path",
    "paths",
}


def _assert_no_internal_paths(payload):
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                assert key not in FORBIDDEN_CONTRACT_KEYS
                if key == "debug_paths":
                    raise AssertionError("target HTTP default response must not include debug_paths")
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)


def test_v16b1_workspace_target_http_lifecycle(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)

    created = client.post("/api/workspaces", json={"name": "Research Vault", "owner": "team", "tags": ["v16b1"]})
    assert created.status_code == 200
    create_payload = created.json()
    assert create_payload["status"] == "ok"
    assert create_payload["operation_id"] is None
    assert create_payload["workspace_id"] == "research-vault"
    assert create_payload["artifact_refs"][0]["artifact_ref"] == "workspace://research-vault"
    workspace = create_payload["data"]["workspace"]
    assert workspace == {
        "workspace_id": "research-vault",
        "name": "Research Vault",
        "owner": "team",
        "tags": ["v16b1"],
        "status": "active",
        "created_at": workspace["created_at"],
        "updated_at": workspace["updated_at"],
        "archived_at": None,
        "archive_reason": "",
    }
    _assert_no_internal_paths(create_payload)

    listed = client.get("/api/workspaces", params={"limit": 10, "tag": "v16b1"})
    assert listed.status_code == 200
    list_payload = listed.json()
    assert list_payload["status"] == "ok"
    assert [item["workspace_id"] for item in list_payload["data"]["items"]] == ["research-vault"]
    _assert_no_internal_paths(list_payload)

    described = client.get("/api/workspaces/research-vault")
    assert described.status_code == 200
    describe_payload = described.json()
    assert describe_payload["workspace_id"] == "research-vault"
    assert describe_payload["data"]["workspace"]["workspace_id"] == "research-vault"
    assert describe_payload["data"]["source_summary"]["source_count"] == 0
    _assert_no_internal_paths(describe_payload)

    archived = client.post("/api/workspaces/research-vault/archive", json={"reason": "done"})
    assert archived.status_code == 200
    archive_payload = archived.json()
    assert archive_payload["status"] == "ok"
    assert archive_payload["operation_id"] is None
    assert archive_payload["data"]["workspace"]["status"] == "archived"
    assert archive_payload["data"]["workspace"]["archive_reason"] == "done"
    _assert_no_internal_paths(archive_payload)

    archived_again = client.post("/api/workspaces/research-vault/archive", json={"reason": "done again"})
    assert archived_again.status_code == 200
    assert archived_again.json()["data"]["workspace"]["status"] == "archived"
    assert archived_again.json()["data"]["workspace"]["archive_reason"] == "done again"
    _assert_no_internal_paths(archived_again.json())


def test_v16b1_workspace_target_http_unknown_workspace_and_bound_paths_contract(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)

    missing = client.get("/api/workspaces/missing-workspace")
    assert missing.status_code == 404
    assert "Unknown workspace_id" in missing.json()["detail"]

    bound_paths = client.post("/api/workspaces", json={"name": "Bound", "bound_paths": [str(source_root)]})
    assert bound_paths.status_code == 422
    assert not (root / "bound" / "lifecycle" / "sources.json").exists()

    traversal = client.post("/api/workspaces", json={"name": "../escape"})
    assert traversal.status_code == 200
    assert traversal.json()["workspace_id"] == "..-escape"
    _assert_no_internal_paths(traversal.json())


def test_v16b1_workspace_target_http_compatibility_routes_retained(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)

    target_created = client.post("/api/workspaces", json={"name": "Compat KB", "owner": "ops"})
    assert target_created.status_code == 200
    target_workspace = target_created.json()["data"]["workspace"]

    compat_described = client.post("/api/v1/knowledge/workspaces/describe", json={"workspace_id": "compat-kb"})
    assert compat_described.status_code == 200
    compat_workspace = compat_described.json()["data"]["workspace"]
    assert compat_workspace["workspace_id"] == target_workspace["workspace_id"]
    assert compat_workspace["name"] == target_workspace["name"]
    assert compat_workspace["owner"] == target_workspace["owner"]

    compat_listed = client.post("/api/v1/knowledge/workspaces/list", json={"limit": 10})
    assert compat_listed.status_code == 200
    assert any(item["workspace_id"] == "compat-kb" for item in compat_listed.json()["data"]["items"])

    compat_archived = client.post("/api/v1/knowledge/workspaces/create", json={"name": "Legacy Create"})
    assert compat_archived.status_code == 200
    legacy_workspace = compat_archived.json()["data"]["workspace"]
    assert legacy_workspace["workspace_id"] == "legacy-create"
    target_described = client.get("/api/workspaces/legacy-create")
    assert target_described.status_code == 200
    assert target_described.json()["data"]["workspace"]["workspace_id"] == "legacy-create"
    _assert_no_internal_paths(target_described.json())


def test_v16b1_workspace_target_http_archived_workspace_keeps_existing_write_rules(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "note.md"
    source_file.write_text("# Archived\n\nShould be blocked.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    assert client.post("/api/workspaces", json={"name": "Archived KB"}).status_code == 200
    assert client.post("/api/workspaces/archived-kb/archive", json={}).status_code == 200

    import_response = client.post(
        "/api/v1/knowledge/sources/import",
        json={"workspace": str(root / "archived-kb"), "paths": [str(source_file)]},
    )
    assert import_response.status_code == 200
    payload = import_response.json()
    assert payload["status"] == "blocked"
    assert payload["data"]["error"]["code"] == "workspace_archived"


def test_v16b1_workspace_target_http_auth_matches_existing_api_boundary(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)

    client = TestClient(app)
    unauthorized = client.get("/api/workspaces")
    authorized = client.get("/api/workspaces", headers={"X-API-Key": "target-key"})

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
