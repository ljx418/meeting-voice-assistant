from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


FORBIDDEN_CONTRACT_KEYS = {"root_path", "path", "paths", "workspace_path", "debug_paths"}


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


def _assert_no_path_values(payload, *paths: Path):
    raw = str(payload)
    for path in paths:
        assert str(path) not in raw


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def test_v2_codebase_target_http_lifecycle_real_repo(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase1 Code")
    workspace = workspace_root / workspace_id

    imported = client.post(
        f"/api/workspaces/{workspace_id}/codebases",
        json={"path": str(repo_root), "metadata": {"purpose": "real-e2e"}},
    )
    assert imported.status_code == 200
    payload = imported.json()
    assert payload["status"] == "ok"
    codebase = payload["data"]["codebase"]
    assert codebase["codebase_id"] == "codebase_data_service"
    assert codebase["status"] == "active"
    assert codebase["metadata"] == {"purpose": "real-e2e"}
    assert payload["artifact_refs"][0]["artifact_ref"] == "codebase://codebase_data_service"
    _assert_no_internal_paths(payload)
    assert (workspace / "assets" / "codebase" / "codebase_data_service" / "codebase.json").exists()
    assert not (workspace / "lifecycle" / "sources.json").exists()

    duplicate = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo_root)})
    assert duplicate.status_code == 200
    assert duplicate.json()["data"]["created"] is False
    assert duplicate.json()["data"]["codebase"]["codebase_id"] == codebase["codebase_id"]
    _assert_no_internal_paths(duplicate.json())

    listed = client.get(f"/api/workspaces/{workspace_id}/codebases")
    assert listed.status_code == 200
    assert [item["codebase_id"] for item in listed.json()["data"]["items"]] == [codebase["codebase_id"]]
    _assert_no_internal_paths(listed.json())

    described = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase['codebase_id']}")
    assert described.status_code == 200
    assert described.json()["data"]["codebase"]["codebase_id"] == codebase["codebase_id"]
    _assert_no_internal_paths(described.json())

    archived = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase['codebase_id']}/archive", json={"reason": "done"})
    assert archived.status_code == 200
    assert archived.json()["data"]["codebase"]["status"] == "archived"
    assert archived.json()["data"]["codebase"]["archive_reason"] == "done"
    _assert_no_internal_paths(archived.json())

    active_list = client.get(f"/api/workspaces/{workspace_id}/codebases")
    assert active_list.status_code == 200
    assert active_list.json()["data"]["items"] == []

    archived_list = client.get(f"/api/workspaces/{workspace_id}/codebases", params={"include_archived": True})
    assert archived_list.status_code == 200
    assert [item["codebase_id"] for item in archived_list.json()["data"]["items"]] == [codebase["codebase_id"]]


def test_v2_codebase_target_http_blocks_bad_paths_and_archived_workspace(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    outside = tmp_path / "outside"
    outside.mkdir()
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase1 Block")

    blocked = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(outside)})
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked"
    assert blocked.json()["data"]["error"]["code"] == "path_not_allowed"
    _assert_no_internal_paths(blocked.json())
    _assert_no_path_values(blocked.json(), outside, repo_root)

    assert client.post(f"/api/workspaces/{workspace_id}/archive", json={}).status_code == 200
    archived_import = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo_root)})
    assert archived_import.status_code == 200
    assert archived_import.json()["status"] == "blocked"
    assert archived_import.json()["data"]["error"]["code"] == "workspace_archived"
