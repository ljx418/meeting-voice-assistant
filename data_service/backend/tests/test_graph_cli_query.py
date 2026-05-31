import json
import sqlite3

from data_service.__main__ import _build_knowledge_parser, _run_parsed_args


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


def _write_workspace(root, workspace_id: str) -> None:
    workspace = root / workspace_id
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / ".data_service_workspace.json").write_text(
        json.dumps({"workspace_id": workspace_id, "name": workspace_id, "status": "active"}),
        encoding="utf-8",
    )
    db_path = workspace / "graphrag" / "state" / "graphrag.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE documents (id TEXT PRIMARY KEY, filename TEXT NOT NULL, file_path TEXT NOT NULL, authority TEXT, distilled_unit_count INTEGER NOT NULL DEFAULT 0, source_weight REAL NOT NULL DEFAULT 1.0, density_score REAL NOT NULL DEFAULT 1.0, primary_theme TEXT);
            CREATE TABLE entities (entity_id TEXT PRIMARY KEY, normalized_name TEXT NOT NULL UNIQUE, name TEXT NOT NULL, occurrence_count INTEGER NOT NULL DEFAULT 0, weighted_occurrence_count REAL NOT NULL DEFAULT 0, document_count INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE themes (theme_id TEXT PRIMARY KEY, normalized_label TEXT NOT NULL UNIQUE, label TEXT NOT NULL, weighted_score REAL NOT NULL DEFAULT 0, source_count INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE relationships (relationship_id TEXT PRIMARY KEY, source_node_id TEXT NOT NULL, target_node_id TEXT NOT NULL, source_node_kind TEXT NOT NULL, target_node_kind TEXT NOT NULL, relation_type TEXT NOT NULL, weight REAL NOT NULL DEFAULT 1.0, source_id TEXT, unit_id TEXT);
            CREATE TABLE distilled_units (unit_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, text TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0, confidence REAL NOT NULL DEFAULT 0);
            """
        )
        conn.execute("INSERT INTO documents (id, filename, file_path) VALUES ('doc1', 'doc.md', '/hidden/doc.md')")
        conn.execute("INSERT INTO entities VALUES ('entity:alpha', 'alpha', 'Alpha', 4, 4.0, 1)")
        conn.execute("INSERT INTO themes VALUES ('theme:governance', 'governance', 'Governance', 5.0, 1)")
        conn.execute("INSERT INTO relationships VALUES ('rel1', 'theme:governance', 'entity:alpha', 'theme', 'entity', 'about', 2.0, 'src1', 'unit1')")
        conn.execute("INSERT INTO distilled_units VALUES ('unit1', 'src1', 'Alpha governance signal', 0.9, 0.8)")
        conn.commit()


def _run_cli(args, capsys):
    parsed = _build_knowledge_parser().parse_args(args)
    code = _run_parsed_args(parsed)
    captured = capsys.readouterr()
    return code, captured


def test_v16c3_graph_query_cli_inventory_and_query(tmp_path, capsys):
    root = tmp_path / "managed"
    workspace_id = "cli-query"
    _write_workspace(root, workspace_id)

    parser = _build_knowledge_parser()
    top_action = next(action for action in parser._actions if getattr(action, "dest", None) == "command")
    assert set(top_action.choices) == {"build", "code", "graph", "quality", "query", "source", "trace", "workspace"}
    graph_parser = top_action.choices["graph"]
    graph_subparser = next(action for action in graph_parser._actions if getattr(action, "dest", None) == "graph_command")
    assert {"snapshot", "neighbors", "community", "query"} <= set(graph_subparser.choices)

    code, captured = _run_cli(
        [
            "graph",
            "query",
            "--workspace-root",
            str(root),
            "--workspace-id",
            workspace_id,
            "--query",
            "Alpha",
            "--top-k",
            "5",
            "--include-communities",
            "--json",
        ],
        capsys,
    )
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "ok"
    assert payload["data"]["query"] == "Alpha"
    assert payload["data"]["top_k"] == 5
    assert payload["data"]["nodes"][0]["node_id"] == "entity:alpha"
    assert "communities" in payload["data"]
    _assert_no_internal_paths(payload)


def test_v16c3_graph_query_cli_validation(tmp_path, capsys):
    root = tmp_path / "managed"
    workspace_id = "cli-query"
    _write_workspace(root, workspace_id)

    code, captured = _run_cli(
        ["graph", "query", "--workspace-root", str(root), "--workspace-id", workspace_id],
        capsys,
    )
    assert code == 2
    assert "q is required" in captured.err

    code, captured = _run_cli(
        ["graph", "query", "--workspace-root", str(root), "--workspace-id", workspace_id, "--query", "Alpha", "--top-k", "0"],
        capsys,
    )
    assert code == 2
    assert "top_k must be between 1 and 50" in captured.err

    code, captured = _run_cli(
        ["graph", "query", "--workspace-root", str(root), "--workspace-id", workspace_id, "--query", "Alpha", "--top-k", "51"],
        capsys,
    )
    assert code == 2
    assert "top_k must be between 1 and 50" in captured.err
