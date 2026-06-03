import subprocess
from pathlib import Path


DOC = Path("docs/V1.6/console-governance-evidence-plan.md")
BASELINE_JSON = Path("docs/V1.6/public-surface-baseline.json")
GAP_DOC = Path("docs/V1.6/current-vs-target-gap.md")
DRAWIO = Path("docs/V1.6/current-vs-target-gap.drawio")
FRONTEND_CONTRACT = Path("frontend/src/data/mcpContract.ts")
KNOWLEDGE_PAGE = Path("frontend/src/pages/KnowledgePage.vue")


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
    assert "D overlays +10" in text
    assert "B overlays +11" in text
    assert "C overlays +4" in text
    assert "= 35" in text
    assert "route count remains 35" in text
    assert "MCP tool count remains 40" in text
    assert "CLI top-level and nested diffs remain none" in text
    assert "graph neighbors" in text
    assert "graph community" in text
    assert "graph query" in text
    assert "graph session" in text


def test_console_governance_evidence_keeps_baseline_and_f2_boundaries():
    text = _read(DOC)
    baseline = _read(BASELINE_JSON)

    assert '"tool_count": 40' in baseline
    assert '"target_http"' in baseline
    assert "V1.5 baseline is immutable" in text
    assert "F2 updates only governance evidence display" in text
    assert "Closure acceptance is completed" in text
    assert "/knowledge` remains a service governance console" in text
    assert "no new backend public surface" in text
    assert "no backend public surface change" in text
    assert "external contract" in text
    assert "raw internal path" in text
    assert "must not be described as closure acceptance" in text


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
    assert "Closure Acceptance" in gap
    assert "planned" in gap


def test_frontend_governance_evidence_is_static_display_only():
    contract = _read(FRONTEND_CONTRACT)
    page = _read(KNOWLEDGE_PAGE)
    evidence_source = contract.split("export const governanceBaselineEvidence", 1)[1].split("export const mcpToolContracts", 1)[0]

    assert "governanceBaselineEvidence" in contract
    assert "governanceOverlayEvidence" in contract
    assert "governanceCapabilityEvidence" in contract
    assert "acceptedGraphCliNestedAdditions" in contract
    assert "Current target HTTP" in contract
    assert "65" in evidence_source
    assert "MCP tool count" in contract
    assert "40" in evidence_source
    assert "B overlays +11" in contract
    assert "C overlays +4" in contract
    assert "D overlays +10" in contract
    assert "E overlays +7" in contract
    assert "Closure acceptance" in contract
    assert "not implemented" in contract
    assert "service governance console" in contract
    assert "not end-user knowledge consumption app" in contract

    for blocked in [
        "workspace_path",
        "root_path",
        "filesystem_path",
        "artifact_physical_path",
        "graphrag_cache_path",
        "cache_path",
        "physical_path",
        "internal_path",
        "debug_paths",
        "source_path",
        "original_path",
        "local_path",
    ]:
        assert blocked not in evidence_source

    assert "V1.6 Governance Evidence" in page
    assert "公开面证据" in page
    assert "target HTTP 65" in page
    assert "MCP 61" in page
    assert "CLI top-level 8" in page
    assert "F2 is display-only console governance evidence polish" in page
    assert "no backend public surface" in page


def test_f2_does_not_stage_unrelated_public_surface_baseline_changes():
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "docs/V1.6/public-surface-baseline.json", "docs/V1.6/public-surface-overlays"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert tracked == ""
