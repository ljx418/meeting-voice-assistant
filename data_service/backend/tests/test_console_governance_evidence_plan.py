import subprocess
from pathlib import Path


DOC = Path("docs/V1.6/console-governance-evidence-plan.md")
BASELINE_JSON = Path("docs/V1.6/public-surface-baseline.json")
GAP_DOC = Path("docs/V1.6/current-vs-target-gap.md")
DRAWIO = Path("docs/V1.6/current-vs-target-gap.drawio")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_console_governance_evidence_matrix_records_current_public_surface():
    text = _read(DOC)

    assert "| phase | status | public surface delta | target HTTP count | MCP count | CLI top-level/nested diff |" in text
    assert "V1.5 immutable baseline" in text
    assert "V1.6-A Public Surface Guard" in text
    assert "B1/B2/B3 overlays +11" in text
    assert "C1/C2/C3/C4 overlays +4" in text
    assert "D1 planning 0" in text
    assert "D3 planning 0" in text
    assert "D4/D5/D6 overlays +5" in text
    assert "E1/E2/E3/E4/E5 overlays +7" in text
    assert "= 35" in text
    assert "route count remains 35" in text
    assert "MCP tool count remains 40" in text
    assert "CLI top-level and nested diffs remain none" in text


def test_console_governance_evidence_keeps_baseline_and_f2_boundaries():
    text = _read(DOC)
    baseline = _read(BASELINE_JSON)

    assert '"tool_count": 40' in baseline
    assert '"target_http"' in baseline
    assert "V1.5 baseline is immutable" in text
    assert "F2 remains planned" in text
    assert "not implemented" in text
    assert "/knowledge` remains a service governance console" in text
    assert "no new backend public surface" in text
    assert "no frontend behavior change" in text
    assert "external contract" in text
    assert "raw internal path" in text
    assert "must not be described as implemented" in text


def test_gap_markdown_and_drawio_are_synced_for_f1_route_count():
    gap = _read(GAP_DOC)
    drawio = _read(DRAWIO)

    for text in (gap, drawio):
        assert "target HTTP" in text
        assert "35" in text
        assert "F1" in text
        assert "F2" in text
        assert "planned" in text
        assert "MCP" in text
        assert "40" in text

    assert "A guard: +0" in gap
    assert "D1 planning: +0" in gap
    assert "D3 planning: +0" in gap
    assert "current target HTTP route count = 35" in gap
    assert "F2 Console Governance Polish" in gap


def test_f1_does_not_touch_frontend_or_knowledge_static_assets():
    status = subprocess.run(
        ["git", "status", "--short", "--", "frontend", "backend/app/static/knowledge_console"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert status == ""
