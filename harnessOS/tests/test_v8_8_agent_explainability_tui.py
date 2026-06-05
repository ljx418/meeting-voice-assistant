from pathlib import Path

from core.product_console.v8_agent_explainability_tui import (
    DEFAULT_V88_EVIDENCE_DIR,
    build_v8_8_agent_explainability_state,
    write_v8_8_agent_explainability_evidence,
)


def test_v8_8_state_is_readonly_and_shows_required_panels() -> None:
    state = build_v8_8_agent_explainability_state()
    data = state.to_dict()
    panel_ids = {panel["panel_id"] for panel in data["panels"]}

    assert state.status == "PASS"
    assert data["readonly"] is True
    assert {
        "workflow_agent_map",
        "station_agent_detail",
        "agent_capability",
        "agent_context",
        "agent_invocation",
        "terminal_worker_handoff",
        "agent_evidence_links",
        "workflow_explainer_agent_summary",
    }.issubset(panel_ids)
    assert data["global_assertions"]["station_agent_visible_for_each_station"] is True
    assert data["global_assertions"]["forbidden_reasons_visible"] is True
    assert data["global_assertions"]["does_not_construct_runtime_truth"] is True


def test_v8_8_evidence_package_outputs(tmp_path: Path) -> None:
    state = write_v8_8_agent_explainability_evidence(output_dir=tmp_path)
    assert state.status == "PASS"

    required = [
        "index.html",
        "tui-screen.html",
        "agent-explainability-state.json",
        "acceptance-data.json",
        "claims-scan.md",
        "redaction-scan.md",
        "result-summary.md",
    ]
    assert [name for name in required if not (tmp_path / name).exists()] == []
    html = (tmp_path / "tui-screen.html").read_text(encoding="utf-8")
    assert "Workflow Agent Map" in html
    assert "Terminal Worker Handoff Panel" in html
    assert "data-readonly=\"true\"" in html
    assert "status: PASS" in (tmp_path / "claims-scan.md").read_text(encoding="utf-8")
    assert "status: PASS" in (tmp_path / "redaction-scan.md").read_text(encoding="utf-8")


def test_v8_8_default_evidence_dir_is_v8_design_path() -> None:
    assert DEFAULT_V88_EVIDENCE_DIR.as_posix().endswith("docs/design/V8.x/evidence/v8-8-agent-explainability-tui")
