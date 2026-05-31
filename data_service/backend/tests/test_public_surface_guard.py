import ast
import json
from argparse import _SubParsersAction
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service import DataService
from data_service.__main__ import _build_knowledge_parser
from data_service.mcp_tool_registry import all_tool_specs


BASELINE_PATH = Path("docs/V1.6/public-surface-baseline.json")
OVERLAY_ROOT = Path("docs/V1.6/public-surface-overlays")
IGNORED_HTTP_METHODS = {"HEAD", "OPTIONS"}
PRODUCTION_SCAN_ROOTS = [
    Path("backend/data_service"),
    Path("backend/app/graphrag/service"),
    Path("backend/app/llmwiki"),
]
UPPER_LAYER_IMPORT_PARTS = {
    "meeting",
    "asr",
    "interview",
    "learning",
    "ide_plugin",
    "agent_workflow",
}
V2_CODEBASE_TOOLS = {
    "knowledge_codebase_import",
    "knowledge_codebase_list",
    "knowledge_codebase_snapshot",
    "knowledge_codebase_describe",
    "knowledge_codebase_archive",
}
V2_TARGET_ROUTE_ADDITIONS = {
    ("GET", "/api/workspaces/-/ai-provider/health"),
    ("GET", "/api/workspaces/{workspace_id}/capabilities"),
    ("GET", "/api/workspaces/{workspace_id}/codebases"),
    ("POST", "/api/workspaces/{workspace_id}/codebases"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/archive"),
    ("POST", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots"),
    ("GET", "/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots/{snapshot_id}"),
    ("GET", "/api/workspaces/{workspace_id}/guide"),
    ("POST", "/api/workspaces/{workspace_id}/studio/artifacts"),
    ("POST", "/api/workspaces/{workspace_id}/research"),
    ("POST", "/api/workspaces/{workspace_id}/folder-collections/scan"),
    ("POST", "/api/workspaces/{workspace_id}/workflows/folder-summary/runs"),
    ("POST", "/api/workspaces/{workspace_id}/agent-workflows/draft"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id:path}/trace"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/preview"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}"),
    ("GET", "/api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}"),
}


def _baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def _accepted_overlays() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(OVERLAY_ROOT.glob("v1_*.json"))]


def _as_route_set(routes) -> set[tuple[str, str]]:
    return {(method.upper(), path) for method, path in routes}


def _diff(current: set, expected: set) -> dict:
    return {
        "added": sorted(current - expected),
        "removed": sorted(expected - current),
    }


def _subparser_action(parser):
    return next(action for action in parser._actions if isinstance(action, _SubParsersAction))


def _knowledge_cli_inventory() -> dict[str, list[str]]:
    top_action = _subparser_action(_build_knowledge_parser())
    inventory = {}
    for command, child_parser in top_action.choices.items():
        nested_actions = [action for action in child_parser._actions if isinstance(action, _SubParsersAction)]
        inventory[command] = sorted(nested_actions[0].choices) if nested_actions else []
    return {command: inventory[command] for command in sorted(inventory)}


def _data_service_http_routes() -> set[tuple[str, str]]:
    routes = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        if not (path.startswith("/api/v1/knowledge/") or path == "/api/workspaces" or path.startswith("/api/workspaces/")):
            continue
        for method in sorted(set(getattr(route, "methods", None) or []) - IGNORED_HTTP_METHODS):
            routes.add((method.upper(), path))
    return routes


def _imported_module_parts(path: Path) -> set[str]:
    parts = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts.update(alias.name.lower().split("."))
        elif isinstance(node, ast.ImportFrom) and node.module:
            parts.update(node.module.lower().split("."))
    return parts


def test_v16a_mcp_registry_matches_v15_public_surface_baseline():
    baseline = _baseline()["mcp"]
    expected_tools = set(baseline["tools"])
    current_tools = {spec["name"] for spec in all_tool_specs()}

    assert len(current_tools) == baseline["tool_count"] + len(V2_CODEBASE_TOOLS)
    assert _diff(current_tools, expected_tools) == {"added": sorted(V2_CODEBASE_TOOLS), "removed": []}

    graph_session_baseline = {
        "knowledge_graph_neighbors",
        "knowledge_graph_snapshot",
        "knowledge_community_summary",
        "knowledge_session_build_cancel",
        "knowledge_session_build_start",
        "knowledge_session_build_status",
        "knowledge_session_close",
        "knowledge_session_create",
        "knowledge_session_delete",
        "knowledge_session_get",
        "knowledge_session_ingest",
        "knowledge_session_list",
        "knowledge_session_query",
    }
    assert graph_session_baseline <= current_tools


def test_v16a_knowledge_cli_parser_matches_v15_public_surface_baseline():
    baseline = _baseline()["cli"]
    overlays = _accepted_overlays()
    current_inventory = _knowledge_cli_inventory()
    expected_nested = {command: list(items) for command, items in baseline["nested_commands"].items()}
    for overlay in overlays:
        for command, additions in (overlay.get("allowed_cli_nested_additions") or {}).items():
            expected_nested.setdefault(command, [])
            expected_nested[command] = sorted(set(expected_nested[command]) | set(additions or []))

    assert set(current_inventory) == set(baseline["top_level_commands"]) | {"code"}
    expected_nested["code"] = ["archive", "describe", "import", "list", "snapshot"]
    assert current_inventory == expected_nested


def test_v16_current_http_route_inventory_matches_v15_baseline_plus_accepted_overlays():
    baseline = _baseline()
    overlays = _accepted_overlays()
    current_routes = _data_service_http_routes()
    expected_target = _as_route_set(baseline["target_http"]["allowlist"])
    allowed_target_additions = set()
    for overlay in overlays:
        allowed_target_additions |= _as_route_set(overlay["allowed_target_http_additions"])
    expected_compat = _as_route_set(baseline["compatibility_http"]["routes"])
    expected_current_target = expected_target | allowed_target_additions | V2_TARGET_ROUTE_ADDITIONS

    current_target = {route for route in current_routes if route[1] == "/api/workspaces" or route[1].startswith("/api/workspaces/")}
    current_compat = {route for route in current_routes if route[1].startswith(baseline["compatibility_http"]["required_prefix"])}

    assert current_compat
    assert current_compat == expected_compat
    assert current_target == expected_current_target
    assert _diff(current_target, expected_target) == {"added": sorted(allowed_target_additions | V2_TARGET_ROUTE_ADDITIONS), "removed": []}
    assert _diff(current_target, expected_current_target) == {"added": [], "removed": []}
    assert current_routes == expected_compat | expected_current_target

    allowed_quality_target_paths = {
        "/api/workspaces/{workspace_id}/quality/feedback",
        "/api/workspaces/{workspace_id}/quality/correction-rules",
        "/api/workspaces/{workspace_id}/quality/correction-rules/build",
        "/api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review",
        "/api/workspaces/{workspace_id}/quality/correction-plan",
    }
    allowed_additions = allowed_target_additions | V2_TARGET_ROUTE_ADDITIONS
    allowed_addition_paths = {path for _, path in allowed_additions}
    for method, path in current_target - expected_target:
        assert path in allowed_addition_paths
        if "/quality" in path:
            assert path in allowed_quality_target_paths
        if "/graph" in path:
            assert path in {
                "/api/workspaces/{workspace_id}/graph/neighbors",
                "/api/workspaces/{workspace_id}/graph/community",
                "/api/workspaces/{workspace_id}/graph/query",
                "/api/workspaces/{workspace_id}/graph/session",
            }
        if "/codebases" in path:
            assert (method, path) in V2_TARGET_ROUTE_ADDITIONS

    assert len(current_target) == len(expected_current_target)


def test_v16a_boundary_guard_has_no_upper_layer_production_imports():
    violations = []
    for root in PRODUCTION_SCAN_ROOTS:
        for path in root.rglob("*.py"):
            imported_parts = _imported_module_parts(path)
            blocked = sorted(imported_parts & UPPER_LAYER_IMPORT_PARTS)
            if blocked:
                violations.append({"path": str(path), "blocked_import_parts": blocked})

    assert violations == []


def test_v16a_target_http_contract_smoke_matches_legacy_contracts(tmp_path, monkeypatch):
    from data_service.models import QueryMode

    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    workspace_id = "v16a-guard"
    workspace = root / workspace_id
    doc = tmp_path / "v16a-source.md"
    doc.write_text("# V1.6-A Guard\n\nPublic surface guard validates target HTTP contract stability.\n", encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)
    source_id = service.read_distill_bundle(limit=5)["sources"][0]["source_id"]

    client = TestClient(app)
    legacy_query = client.post(
        "/api/v1/knowledge/query",
        json={"workspace": str(workspace), "query": "V1.6-A", "mode": QueryMode.HYBRID.value, "top_k": 5},
    )
    target_query = client.post(
        f"/api/workspaces/{workspace_id}/query",
        json={"query": "V1.6-A", "mode": QueryMode.HYBRID.value, "top_k": 5},
    )
    assert target_query.status_code == 200
    assert target_query.json()["query"] == legacy_query.json()["query"]
    assert target_query.json()["coverage_status"] in {"no_sources", "insufficient_evidence", "source_supported"}

    legacy_distill = client.post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "limit": 5, "typed_unit_type": "concept"},
    )
    target_distill = client.post(
        f"/api/workspaces/{workspace_id}/distill",
        json={"limit": 5, "typed_unit_type": "concept"},
    )
    assert target_distill.status_code == 200
    assert target_distill.json() == legacy_distill.json()

    legacy_trace = client.post(
        "/api/v1/knowledge/source/trace",
        json={"workspace": str(workspace), "source_id": source_id, "limit": 5},
    )
    assert legacy_trace.status_code == 200

    target_trace_slug = client.get(f"/api/workspaces/{workspace_id}/sources/{source_id}/trace", params={"limit": 5})
    assert target_trace_slug.status_code == 422

    target_workspace = client.post("/api/workspaces", json={"name": "V1.6-A target trace registry source"})
    assert target_workspace.status_code == 200
    target_workspace_id = target_workspace.json()["workspace_id"]
    target_import = client.post(
        f"/api/workspaces/{target_workspace_id}/sources",
        json={
            "texts": [
                {
                    "title": "V1.6-A target trace source",
                    "content": "Public surface guard validates registry source trace contract stability.",
                    "metadata": {"kind": "text"},
                }
            ]
        },
    )
    assert target_import.status_code == 200
    target_source_id = target_import.json()["data"]["sources"][0]["source_id"]
    target_trace = client.get(f"/api/workspaces/{target_workspace_id}/sources/{target_source_id}/trace", params={"limit": 5})
    assert target_trace.status_code == 200
    target_payload = target_trace.json()
    assert target_payload["status"] == "ok"
    assert target_payload["data"]["trace"]["source_id"] == target_source_id
