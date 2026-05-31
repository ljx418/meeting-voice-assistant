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
        conn.execute("INSERT INTO relationships VALUES ('rel1', 'entity:alpha', 'entity:beta', 'entity', 'entity', 'co_occurs', 2.0, 'src1', 'unit1')")
        conn.execute("INSERT INTO relationships VALUES ('rel2', 'entity:alpha', 'theme:governance', 'entity', 'theme', 'about', 1.0, 'src1', 'unit2')")
        conn.commit()


def test_v16c1_graph_neighbors_target_http_node_and_entity_queries(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph KB")
    _write_graph_db(root, workspace_id)

    by_node = client.get(
        f"/api/workspaces/{workspace_id}/graph/neighbors",
        params={"node_id": "entity:alpha", "depth": 1, "max_nodes": 10},
    )
    assert by_node.status_code == 200
    payload = by_node.json()
    assert payload["status"] == "ok"
    assert payload["workspace_id"] == workspace_id
    assert payload["data"]["node_id"] == "entity:alpha"
    assert payload["data"]["depth"] == 1
    assert payload["data"]["max_nodes"] == 10
    assert {node["node_id"] for node in payload["data"]["nodes"]} >= {"entity:alpha", "entity:beta"}
    assert payload["data"]["edges"]
    assert payload["artifact_refs"][0]["artifact_ref"].startswith("graph://")
    _assert_no_internal_paths(payload)

    by_entity = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"entity_id": "entity:alpha"})
    assert by_entity.status_code == 200
    assert by_entity.json()["data"]["entity_id"] == "entity:alpha"
    _assert_no_internal_paths(by_entity.json())


def test_v16c1_graph_neighbors_target_http_validation_and_missing_graph(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Missing")

    missing_root = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors")
    assert missing_root.status_code == 400
    both = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "n1", "entity_id": "n1"})
    assert both.status_code == 400
    bad_depth = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "n1", "depth": 4})
    assert bad_depth.status_code == 400
    bad_max = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "n1", "max_nodes": 501})
    assert bad_max.status_code == 400

    unavailable = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "entity:missing"})
    assert unavailable.status_code == 200
    assert unavailable.json()["status"] == "blocked"
    assert unavailable.json()["data"]["error"]["code"] == "graph_snapshot_unavailable"
    assert list((root / workspace_id / "lifecycle" / "operations").glob("*.json")) == []
    assert not (root / workspace_id / "lifecycle" / "sources.json").exists()


def test_v16c1_graph_neighbors_target_http_unknown_node_limits_auth_and_trace(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Limits")
    _write_graph_db(root, workspace_id)

    unknown = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "entity:missing"})
    assert unknown.status_code == 200
    assert unknown.json()["status"] == "blocked"
    assert unknown.json()["data"]["error"]["code"] == "unknown_graph_node"

    limited = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "entity:alpha", "max_nodes": 1})
    assert limited.status_code == 200
    assert len(limited.json()["data"]["nodes"]) == 1
    assert limited.json()["data"]["truncated"] is True
    _assert_no_internal_paths(limited.json())

    trace = client.get(f"/api/workspaces/{workspace_id}/sources/src_missing/trace")
    assert trace.status_code == 422

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "entity:alpha"})
    authorized = client.get(
        f"/api/workspaces/{workspace_id}/graph/neighbors",
        params={"node_id": "entity:alpha"},
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
