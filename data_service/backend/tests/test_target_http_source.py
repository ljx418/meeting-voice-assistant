from pathlib import Path

from fastapi.testclient import TestClient

from app.config import config
from app.main import app
from data_service import DataService


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
    "path",
    "paths",
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


def test_v16b2_source_target_http_lifecycle_and_no_path_leakage(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "note.md"
    source_file.write_text("# Source\n\nTarget HTTP source lifecycle.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Source KB")
    workspace = root / workspace_id

    imported = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={"paths": [str(source_file)], "metadata": {"kind": "file"}},
    )
    assert imported.status_code == 200
    import_payload = imported.json()
    assert import_payload["status"] == "ok"
    source = import_payload["data"]["sources"][0]
    assert source["workspace_id"] == workspace_id
    assert source["source_id"].startswith("src_")
    assert source["status"] == "active"
    assert source["ingest_status"] == "pending"
    assert source["metadata"] == {"kind": "file"}
    assert source["artifact_ref"] == f"source://{source['source_id']}"
    assert import_payload["operation_id"] is None
    _assert_no_internal_paths(import_payload)
    assert list((workspace / "lifecycle" / "operations").glob("*.json")) == []

    text_import = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={"texts": [{"title": "Text note", "content": "inline source", "metadata": {"kind": "text"}}]},
    )
    assert text_import.status_code == 200
    assert text_import.json()["data"]["sources"][0]["metadata"] == {"kind": "text"}
    _assert_no_internal_paths(text_import.json())

    listed = client.get(f"/api/workspaces/{workspace_id}/sources", params={"limit": 10})
    assert listed.status_code == 200
    list_payload = listed.json()
    assert [item["source_id"] for item in list_payload["data"]["items"]][:1] == [source["source_id"]]
    _assert_no_internal_paths(list_payload)

    described = client.get(f"/api/workspaces/{workspace_id}/sources/{source['source_id']}")
    assert described.status_code == 200
    describe_payload = described.json()
    assert describe_payload["data"]["source"]["source_id"] == source["source_id"]
    _assert_no_internal_paths(describe_payload)

    removed = client.post(
        f"/api/workspaces/{workspace_id}/sources/{source['source_id']}/remove",
        json={"reason": "retired"},
    )
    assert removed.status_code == 200
    remove_payload = removed.json()
    assert remove_payload["data"]["source"]["status"] == "removed"
    assert remove_payload["data"]["source"]["remove_reason"] == "retired"
    _assert_no_internal_paths(remove_payload)

    removed_again = client.post(
        f"/api/workspaces/{workspace_id}/sources/{source['source_id']}/remove",
        json={"reason": "again"},
    )
    assert removed_again.status_code == 200
    assert removed_again.json()["data"]["source"]["status"] == "removed"
    _assert_no_internal_paths(removed_again.json())


def test_v16b2_source_target_http_errors_isolation_and_path_validation(tmp_path, monkeypatch):
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
    workspace_a = _create_workspace(client, "Source A")
    workspace_b = _create_workspace(client, "Source B")

    missing_workspace = client.get("/api/workspaces/missing/sources")
    assert missing_workspace.status_code == 404
    assert "Unknown workspace_id" in missing_workspace.json()["detail"]

    imported = client.post(f"/api/workspaces/{workspace_a}/sources", json={"paths": [str(allowed_file)]})
    assert imported.status_code == 200
    source_id = imported.json()["data"]["sources"][0]["source_id"]

    missing_source = client.get(f"/api/workspaces/{workspace_a}/sources/src_missing")
    assert missing_source.status_code == 404
    assert "Unknown source_id" in missing_source.json()["detail"]

    cross_describe = client.get(f"/api/workspaces/{workspace_b}/sources/{source_id}")
    assert cross_describe.status_code == 404
    cross_remove = client.post(f"/api/workspaces/{workspace_b}/sources/{source_id}/remove", json={})
    assert cross_remove.status_code == 404

    disallowed = client.post(f"/api/workspaces/{workspace_a}/sources", json={"paths": [str(outside_file)]})
    assert disallowed.status_code == 200
    assert disallowed.json()["status"] == "blocked"

    traversal = client.post(f"/api/workspaces/{workspace_a}/sources", json={"paths": [str(source_root / ".." / "outside" / "outside.md")]})
    assert traversal.status_code == 200
    assert traversal.json()["status"] == "blocked"

    duplicate = client.post(f"/api/workspaces/{workspace_a}/sources", json={"paths": [str(allowed_file)]})
    assert duplicate.status_code == 200
    assert duplicate.json()["data"]["sources"][0]["source_id"] == source_id


def test_v16b2_source_target_http_archived_workspace_and_compatibility_retained(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "note.md"
    source_file.write_text("# Compat\n\nSource compatibility.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Compat Source")

    target_import = client.post(f"/api/workspaces/{workspace_id}/sources", json={"paths": [str(source_file)]})
    assert target_import.status_code == 200
    source_id = target_import.json()["data"]["sources"][0]["source_id"]

    compat_list = client.post("/api/v1/knowledge/sources/list", json={"workspace": str(root / workspace_id), "limit": 10})
    assert compat_list.status_code == 200
    assert any(item["source_id"] == source_id for item in compat_list.json()["data"]["items"])

    compat_remove = client.post(
        "/api/v1/knowledge/sources/remove",
        json={"workspace": str(root / workspace_id), "source_id": source_id, "reason": "compat"},
    )
    assert compat_remove.status_code == 200

    assert client.post(f"/api/workspaces/{workspace_id}/archive", json={}).status_code == 200
    archived_import = client.post(f"/api/workspaces/{workspace_id}/sources", json={"paths": [str(source_file)]})
    assert archived_import.status_code == 200
    assert archived_import.json()["status"] == "blocked"

    archived_remove = client.post(f"/api/workspaces/{workspace_id}/sources/{source_id}/remove", json={})
    assert archived_remove.status_code == 200
    assert archived_remove.json()["status"] == "blocked"


def test_v16b2_source_trace_target_route_unchanged(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Trace KB")
    imported = client.post(
        f"/api/workspaces/{workspace_id}/sources",
        json={"texts": [{"title": "Trace", "content": "Source trace remains baseline.", "metadata": {"kind": "text"}}]},
    )
    assert imported.status_code == 200
    source_id = imported.json()["data"]["sources"][0]["source_id"]

    trace = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/trace", params={"limit": 5})
    assert trace.status_code == 200
    payload = trace.json()
    assert payload["status"] == "ok"
    assert payload["data"]["trace"]["source_id"] == source_id


def test_v16b2_source_target_http_auth_matches_existing_api_boundary(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)

    client = TestClient(app)
    unauthorized = client.get("/api/workspaces/missing/sources")
    authorized = client.get("/api/workspaces/missing/sources", headers={"X-API-Key": "target-key"})

    assert unauthorized.status_code == 401
    assert authorized.status_code == 404
