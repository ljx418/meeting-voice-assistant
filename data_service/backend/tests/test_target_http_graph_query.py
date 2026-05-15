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
            CREATE TABLE distilled_units (
                unit_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                text TEXT NOT NULL,
                importance REAL NOT NULL DEFAULT 0,
                confidence REAL NOT NULL DEFAULT 0
            );
            """
        )
        conn.execute("INSERT INTO documents (id, filename, file_path) VALUES ('doc1', 'doc.md', '/hidden/doc.md')")
        conn.execute("INSERT INTO entities VALUES ('entity:alpha', 'alpha', 'Alpha', 4, 4.0, 1)")
        conn.execute("INSERT INTO entities VALUES ('entity:beta', 'beta', 'Beta', 3, 3.0, 1)")
        conn.execute("INSERT INTO themes VALUES ('theme:governance', 'governance', 'Governance', 5.0, 1)")
        conn.execute("INSERT INTO relationships VALUES ('rel1', 'theme:governance', 'entity:alpha', 'theme', 'entity', 'about', 2.0, 'src1', 'unit1')")
        conn.execute("INSERT INTO relationships VALUES ('rel2', 'entity:alpha', 'entity:beta', 'entity', 'entity', 'co_occurs', 1.0, 'src1', 'unit2')")
        conn.execute("INSERT INTO distilled_units VALUES ('unit1', 'src1', 'Alpha governance signal', 0.9, 0.8)")
        conn.commit()


def test_v16c3_graph_query_target_http_returns_stable_payload(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Query")
    _write_graph_db(root, workspace_id)

    response = client.get(
        f"/api/workspaces/{workspace_id}/graph/query",
        params={"q": "Alpha", "top_k": 5, "include_communities": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["workspace_id"] == workspace_id
    assert payload["data"]["query"] == "Alpha"
    assert payload["data"]["top_k"] == 5
    assert payload["data"]["answer"]
    assert payload["data"]["nodes"][0]["node_id"] == "entity:alpha"
    assert "edges" in payload["data"]
    assert "communities" in payload["data"]
    assert payload["artifact_refs"][0]["artifact_ref"] == f"graph://{workspace_id}/query"
    _assert_no_internal_paths(payload)

    without_sections = client.get(
        f"/api/workspaces/{workspace_id}/graph/query",
        params={"q": "Alpha", "include_nodes": False, "include_edges": False},
    )
    assert without_sections.status_code == 200
    assert "nodes" not in without_sections.json()["data"]
    assert "edges" not in without_sections.json()["data"]
    assert "communities" not in without_sections.json()["data"]


def test_v16c3_graph_query_target_http_validation_missing_graph_and_side_effects(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Query Missing")

    missing_q = client.get(f"/api/workspaces/{workspace_id}/graph/query")
    assert missing_q.status_code == 422
    empty_q = client.get(f"/api/workspaces/{workspace_id}/graph/query", params={"q": "  "})
    assert empty_q.status_code == 400
    bad_top_k = client.get(f"/api/workspaces/{workspace_id}/graph/query", params={"q": "Alpha", "top_k": 0})
    assert bad_top_k.status_code == 400
    too_large = client.get(f"/api/workspaces/{workspace_id}/graph/query", params={"q": "Alpha", "top_k": 51})
    assert too_large.status_code == 400

    unavailable = client.get(f"/api/workspaces/{workspace_id}/graph/query", params={"q": "Alpha"})
    assert unavailable.status_code == 200
    assert unavailable.json()["status"] == "blocked"
    assert unavailable.json()["data"]["error"]["code"] == "graph_query_unavailable"
    assert list((root / workspace_id / "lifecycle" / "operations").glob("*.json")) == []
    assert not (root / workspace_id / "lifecycle" / "sources.json").exists()

    unknown_workspace = client.get("/api/workspaces/unknown-workspace/graph/query", params={"q": "Alpha"})
    assert unknown_workspace.status_code == 404


def test_v16c3_graph_query_target_http_auth_c1_c2_and_no_session_quality(tmp_path, monkeypatch):
    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Graph Query Auth")
    _write_graph_db(root, workspace_id)

    neighbors = client.get(f"/api/workspaces/{workspace_id}/graph/neighbors", params={"node_id": "entity:alpha"})
    community = client.get(f"/api/workspaces/{workspace_id}/graph/community")
    assert neighbors.status_code == 200
    assert community.status_code == 200

    graph_session = client.get(f"/api/workspaces/{workspace_id}/graph/session")
    session = client.get(f"/api/workspaces/{workspace_id}/session")
    quality = client.get(f"/api/workspaces/{workspace_id}/quality")
    assert graph_session.status_code == 200
    assert session.status_code == 404
    assert quality.status_code == 404

    monkeypatch.setenv("DATA_SERVICE_REQUIRE_API_KEY", "true")
    monkeypatch.setattr(config.api, "api_key", "target-key")
    monkeypatch.setattr(config.jwt, "dev_mode", False)
    monkeypatch.setattr(config.jwt, "dev_bypass_auth", False)
    unauthorized = client.get(f"/api/workspaces/{workspace_id}/graph/query", params={"q": "Alpha"})
    authorized = client.get(
        f"/api/workspaces/{workspace_id}/graph/query",
        params={"q": "Alpha"},
        headers={"X-API-Key": "target-key"},
    )
    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
