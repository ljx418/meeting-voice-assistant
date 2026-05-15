import sqlite3

from fastapi.testclient import TestClient

from app.config import config
from app.main import app


FORBIDDEN_CONTRACT_KEYS = {
    "workspace_path",
    "root_path",
    "filesystem_path",
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


def _write_graph_db(root, workspace_id: str) -> None:
    db_path = root / workspace_id / "graphrag" / "state" / "graphrag.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                authority TEXT,
                distilled_unit_count INTEGER NOT NULL DEFAULT 0,
                source_weight REAL NOT NULL DEFAULT 1.0,
                density_score REAL NOT NULL DEFAULT 1.0,
                primary_theme TEXT
            );
            CREATE TABLE entities (
                entity_id TEXT PRIMARY KEY,
                normalized_name TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                occurrence_count INTEGER NOT NULL DEFAULT 0,
                weighted_occurrence_count REAL NOT NULL DEFAULT 0,
                document_count INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE themes (
                theme_id TEXT PRIMARY KEY,
                normalized_label TEXT NOT NULL UNIQUE,
                label TEXT NOT NULL,
                weighted_score REAL NOT NULL DEFAULT 0,
                source_count INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE relationships (
                relationship_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                source_node_kind TEXT NOT NULL,
                target_node_kind TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL NOT NULL DEFAULT 1.0,
                source_id TEXT,
                unit_id TEXT
            );
            """
        )
        conn.execute("INSERT INTO documents (id, filename, file_path) VALUES ('doc1', 'doc.md', '/hidden/doc.md')")
        conn.execute("INSERT INTO entities VALUES ('entity:alpha', 'alpha', 'Alpha', 4, 4.0, 1)")
        conn.execute("INSERT INTO entities VALUES ('entity:beta', 'beta', 'Beta', 3, 3.0, 1)")
        conn.execute("INSERT INTO themes VALUES ('theme:governance', 'governance', 'Governance', 5.0, 1)")
        conn.execute("INSERT INTO relationships VALUES ('rel1', 'theme:governance', 'entity:alpha', 'theme', 'entity', 'about', 2.0, 'src1', 'unit1')")
        conn.execute("INSERT INTO relationships VALUES ('rel2', 'theme:governance', 'entity:beta', 'theme', 'entity', 'about', 1.0, 'src1', 'unit2')")
        conn.commit()


def test_v16c2_graph_community_target_http_list_detail_and_members(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Community")
    _write_graph_db(root, workspace_id)

    listed = client.get(f"/api/workspaces/{workspace_id}/graph/community")
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["status"] == "ok"
    assert payload["workspace_id"] == workspace_id
    assert payload["data"]["limit"] == 20
    assert payload["data"]["items"][0]["community_id"] == "community-1"
    assert payload["data"]["items"][0]["title"] == "Governance"
    assert "members" not in payload["data"]["items"][0]
    assert payload["artifact_refs"][0]["artifact_ref"] == f"graph://{workspace_id}/communities"
    _assert_no_internal_paths(payload)

    detail = client.get(
        f"/api/workspaces/{workspace_id}/graph/community",
        params={"community_id": "community-1", "limit": 1, "include_members": True},
    )
    assert detail.status_code == 200
    detail_payload = detail.json()
    community = detail_payload["data"]["community"]
    assert detail_payload["data"]["community_id"] == "community-1"
    assert community["community_id"] == "community-1"
    assert {member["node_id"] for member in community["members"]} >= {"theme:governance", "entity:alpha"}
    assert "limit" not in detail_payload["data"]
    _assert_no_internal_paths(detail_payload)


def test_v16c2_graph_community_target_http_validation_missing_unknown_and_side_effects(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Community Missing")

    bad_limit = client.get(f"/api/workspaces/{workspace_id}/graph/community", params={"limit": 0})
    assert bad_limit.status_code == 400
    too_large = client.get(f"/api/workspaces/{workspace_id}/graph/community", params={"limit": 101})
    assert too_large.status_code == 400

    unavailable = client.get(f"/api/workspaces/{workspace_id}/graph/community")
    assert unavailable.status_code == 200
    assert unavailable.json()["status"] == "blocked"
    assert unavailable.json()["data"]["error"]["code"] == "graph_community_unavailable"
    assert list((root / workspace_id / "lifecycle" / "operations").glob("*.json")) == []
    assert not (root / workspace_id / "lifecycle" / "sources.json").exists()

    _write_graph_db(root, workspace_id)
    unknown = client.get(f"/api/workspaces/{workspace_id}/graph/community", params={"community_id": "community-missing"})
    assert unknown.status_code == 200
    assert unknown.json()["status"] == "blocked"
    assert unknown.json()["data"]["error"]["code"] == "unknown_graph_community"

    unknown_workspace = client.get("/api/workspaces/unknown-workspace/graph/community")
    assert unknown_workspace.status_code == 404


def test_v16c2_graph_community_target_http_auth_neighbors_and_no_extra_routes(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Community Auth")
    _write_graph_db(root, workspace_id)

    neighbors = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "entity:alpha"})
    assert neighbors.status_code == 200

    graph_query = client.get(f"/api/workspaces/{workspace_id}/graph/query")
    graph_session = client.get(f"/api/workspaces/{workspace_id}/graph/session")
    assert graph_query.status_code == 422
    assert graph_session.status_code == 200

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = client.get(f"/api/workspaces/{workspace_id}/graph/community")
    authorized = client.get(
        f"/api/workspaces/{workspace_id}/graph/community",
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
