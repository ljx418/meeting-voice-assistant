import json

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
    lifecycle = workspace / "lifecycle"
    lifecycle.mkdir(parents=True, exist_ok=True)
    session = {
        "session_id": "ksess_alpha",
        "workspace_id": workspace_id,
        "external_id": "ksess_alpha",
        "session_type": "generic",
        "title": "ksess_alpha",
        "status": "active",
        "created_at": "2026-05-14T00:00:00Z",
        "updated_at": "2026-05-14T00:01:00Z",
        "metadata": {"workspace_path": "/hidden/workspace"},
    }
    (lifecycle / "sessions.json").write_text(json.dumps({"items": [session]}, ensure_ascii=False), encoding="utf-8")
    graph_path = workspace / "sessions" / "ksess_alpha" / "graph" / "graph.json"
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    graph_path.write_text(
        json.dumps(
            {
                "graph_model_version": "session-graph-1.0",
                "workspace_id": workspace_id,
                "scope": "session",
                "session_id": "ksess_alpha",
                "status": "ok",
                "nodes": [
                    {"id": "entity:alpha", "type": "entity", "label": "Alpha", "metadata": {"cache_path": "/hidden/cache"}},
                    {"id": "topic:plan", "type": "topic", "label": "Plan", "metadata": {}},
                ],
                "edges": [
                    {"id": "edge-1", "source": "entity:alpha", "target": "topic:plan", "type": "related", "weight": 0.8, "metadata": {"physical_path": "/hidden/artifact"}}
                ],
                "communities": [],
                "updated_at": "2026-05-14T00:02:00Z",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _run_cli(args, capsys):
    parsed = _build_knowledge_parser().parse_args(args)
    code = _run_parsed_args(parsed)
    captured = capsys.readouterr()
    return code, captured


def test_v16c4_graph_session_cli_inventory_list_and_detail(tmp_path, capsys):
    root = tmp_path / "managed"
    workspace_id = "cli-session"
    _write_workspace(root, workspace_id)

    parser = _build_knowledge_parser()
    top_action = next(action for action in parser._actions if getattr(action, "dest", None) == "command")
    assert set(top_action.choices) == {"build", "code", "graph", "quality", "query", "source", "trace", "workspace"}
    graph_parser = top_action.choices["graph"]
    graph_subparser = next(action for action in graph_parser._actions if getattr(action, "dest", None) == "graph_command")
    assert {"snapshot", "neighbors", "community", "query", "session"} <= set(graph_subparser.choices)

    code, captured = _run_cli(
        ["graph", "session", "--workspace-root", str(root), "--workspace-id", workspace_id, "--json"],
        capsys,
    )
    assert code == 0
    listed = json.loads(captured.out)
    assert listed["data"]["items"][0]["session_id"] == "ksess_alpha"
    assert "nodes" not in listed["data"]["items"][0]
    _assert_no_internal_paths(listed)

    code, captured = _run_cli(
        [
            "graph",
            "session",
            "--workspace-root",
            str(root),
            "--workspace-id",
            workspace_id,
            "--session-id",
            "ksess_alpha",
            "--include-nodes",
            "--include-edges",
            "--node-limit",
            "1",
            "--edge-limit",
            "1",
            "--json",
        ],
        capsys,
    )
    assert code == 0
    detail = json.loads(captured.out)
    assert detail["data"]["session"]["nodes"][0]["node_id"] == "entity:alpha"
    assert detail["data"]["session"]["edges"][0]["source_node_id"] == "entity:alpha"
    _assert_no_internal_paths(detail)


def test_v16c4_graph_session_cli_validation(tmp_path, capsys):
    root = tmp_path / "managed"
    workspace_id = "cli-session"
    _write_workspace(root, workspace_id)

    code, captured = _run_cli(
        ["graph", "session", "--workspace-root", str(root), "--workspace-id", workspace_id, "--limit", "0"],
        capsys,
    )
    assert code == 2
    assert "limit must be between 1 and 100" in captured.err

    code, captured = _run_cli(
        ["graph", "session", "--workspace-root", str(root), "--workspace-id", workspace_id, "--session-id", "ksess_alpha", "--node-limit", "0"],
        capsys,
    )
    assert code == 2
    assert "node_limit must be between 1 and 200" in captured.err

    code, captured = _run_cli(["graph", "session"], capsys)
    assert code != 0
    assert captured.err
