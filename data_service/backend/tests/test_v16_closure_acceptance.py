import json
from pathlib import Path

from test_public_surface_guard import (
    _accepted_overlays,
    _as_route_set,
    _baseline,
    _data_service_http_routes,
    _knowledge_cli_inventory,
)


DOC_ROOT = Path("docs/V1.6")
OVERLAY_ROOT = DOC_ROOT / "public-surface-overlays"
BASELINE_JSON = DOC_ROOT / "public-surface-baseline.json"
CLOSURE_REPORT = DOC_ROOT / "PHASE-V1.6-CLOSURE-ACCEPTANCE-REPORT-2026-05-16.md"
E5_REPORT = DOC_ROOT / "PHASE-V1.6-E5-QUALITY-CORRECTION-RULES-BUILD-TARGET-HTTP-REPORT-2026-05-15.md"
F2_REPORT = DOC_ROOT / "PHASE-V1.6-F2-CONSOLE-GOVERNANCE-POLISH-REPORT-2026-05-16.md"
E5_FOCUSED_TEST = Path("backend/tests/test_target_http_quality_correction_rules_build.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _target_routes() -> set[tuple[str, str]]:
    routes = _data_service_http_routes()
    return {route for route in routes if route[1] == "/api/workspaces" or route[1].startswith("/api/workspaces/")}


def _overlay_paths() -> set[str]:
    return {path.name for path in OVERLAY_ROOT.glob("v1_6_*.json")}


def test_closure_preconditions_have_accepted_e5_and_f2_reports():
    assert E5_REPORT.exists()
    assert F2_REPORT.exists()
    assert E5_FOCUSED_TEST.exists()

    e5 = _read(E5_REPORT).lower()
    f2 = _read(F2_REPORT).lower()

    assert "final decision" in e5
    assert "accepted" in e5
    assert "final decision" in f2
    assert "accepted" in f2
    assert "frontend build result" in f2
    assert "npm run build" in f2
    assert "passed" in f2


def test_closure_public_surface_inventory_preserves_v16_frozen_35_route_subset():
    baseline = _baseline()
    overlays = [overlay for overlay in _accepted_overlays() if str(overlay.get("phase", "")).startswith("v1.6")]
    current_target = _target_routes()
    baseline_target = _as_route_set(baseline["target_http"]["allowlist"])
    overlay_target = set()
    for overlay in overlays:
        overlay_target |= _as_route_set(overlay["allowed_target_http_additions"])
    v16_target = baseline_target | overlay_target

    assert len(baseline_target) == 3
    assert len(v16_target) == 35
    assert v16_target <= current_target

    blocked_fragments = ("correction-apply", "correction-execution", "/apply")
    for _, path in current_target:
        if path.endswith("/coding-agent/patch-sandbox/previews/{preview_id}/apply"):
            continue
        assert not any(fragment in path for fragment in blocked_fragments)


def test_closure_baseline_json_remains_v15_only_and_overlay_set_is_exact():
    baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    assert baseline["mcp"]["tool_count"] == 40
    assert baseline["cli"]["top_level_commands"] == [
        "build",
        "graph",
        "quality",
        "query",
        "source",
        "trace",
        "workspace",
    ]
    assert baseline["target_http"]["allowlist"] == [
        ["POST", "/api/workspaces/{workspace_id}/query"],
        ["POST", "/api/workspaces/{workspace_id}/distill"],
        ["GET", "/api/workspaces/{workspace_id}/sources/{source_id}/trace"],
    ]

    expected = {
        "v1_6_b1.json",
        "v1_6_b2.json",
        "v1_6_b3.json",
        "v1_6_c1.json",
        "v1_6_c2.json",
        "v1_6_c3.json",
        "v1_6_c4.json",
        "v1_6_d2.json",
        "v1_6_d4.json",
        "v1_6_d5.json",
        "v1_6_d6.json",
        "v1_6_e1.json",
        "v1_6_e2.json",
        "v1_6_e3.json",
        "v1_6_e4.json",
        "v1_6_e5.json",
    }
    assert _overlay_paths() == expected

    for forbidden in ("v1_6_a.json", "v1_6_d1.json", "v1_6_d3.json", "v1_6_f1.json", "v1_6_f2.json", "v1_6_closure.json"):
        assert forbidden not in _overlay_paths()


def test_closure_cli_current_accepted_baseline_is_unchanged():
    inventory = _knowledge_cli_inventory()

    assert sorted(inventory) == ["build", "code", "graph", "quality", "query", "source", "trace", "workspace"]
    assert inventory["code"] == ["architecture", "architecture-intent", "archive", "coding-agent", "context-pack", "describe", "devwiki", "graph", "import", "inventory", "list", "overview", "platform", "quality", "snapshot", "symbols", "trace"]
    assert inventory["graph"] == ["community", "neighbors", "query", "session", "snapshot"]
    assert set(inventory["graph"]) - {"community", "neighbors", "query", "session", "snapshot"} == set()


def test_closure_docs_agree_on_route_count_and_boundaries():
    docs = {
        "README.md": _read(DOC_ROOT / "README.md"),
        "target-http-routes-plan.md": _read(DOC_ROOT / "target-http-routes-plan.md"),
        "current-vs-target-gap.md": _read(DOC_ROOT / "current-vs-target-gap.md"),
        "console-governance-evidence-plan.md": _read(DOC_ROOT / "console-governance-evidence-plan.md"),
    }

    for name, text in docs.items():
        assert "35" in text, name
        assert "MCP" in text, name
        assert "40" in text, name

    combined = "\n".join(docs.values()).lower()
    assert "service governance console" in combined
    assert "end-user knowledge consumption app" in combined
    assert "not end-user knowledge consumption app" in combined
    assert "correction apply" in combined
    assert "not implemented" in combined or "not opened" in combined
    assert "v1.7" not in combined or "planned" in combined


def test_closure_report_records_allowed_change_scope_without_functional_changes():
    assert CLOSURE_REPORT.exists()
    text = _read(CLOSURE_REPORT)

    assert "No functional code changes" in text
    assert "No backend public surface change" in text
    assert "frontend behavior not touched" in text
    assert "backend route/MCP/CLI not touched" in text
    assert "target HTTP route count = 35" in text
    assert "correction apply target HTTP remains not implemented" in text
    assert "V1.7 capabilities remain planned only" in text
    assert "Final decision: accepted" in text
