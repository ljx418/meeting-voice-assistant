from __future__ import annotations

from pathlib import Path


def test_v8_tui_contract_requires_agent_explainability_panels() -> None:
    text = Path("docs/design/V8.x/v8_agent_explainability_tui_contract.md").read_text(encoding="utf-8")

    for term in [
        "Workflow Agent Map",
        "Station Agent Detail",
        "Agent Capability Panel",
        "Forbidden Action Reason Panel",
        "Terminal Worker Handoff Panel",
    ]:
        assert term in text


def test_v8_evidence_contract_requires_station_agent_outputs() -> None:
    text = Path("docs/design/V8.x/v8_evidence_package_contract.md").read_text(encoding="utf-8")

    for term in [
        "station-agent-registry.json",
        "agent-context-envelopes.json",
        "agent-invocation-evidence.json",
        "agent-capability-decisions.json",
        "agent-run-results.json",
        "station_count == agent_descriptor_count",
    ]:
        assert term in text


def test_v8_gap_drawio_exists_and_has_required_pages() -> None:
    text = Path("docs/design/V8.x/v8_current_gap_analysis.drawio").read_text(encoding="utf-8")

    for page in ["01 总览", "02 目标架构", "03 当前差异", "04 开发计划", "05 验收门槛", "06 高风险边界"]:
        assert page in text
