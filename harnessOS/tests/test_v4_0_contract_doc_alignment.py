"""V4.0 preflight document/protocol alignment tests."""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET


V4_DOCS = Path("docs/design/V4.0")


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_v4_0_gap_docs_and_drawio_exist_and_are_valid() -> None:
    md = V4_DOCS / "v4_0_current_gap_analysis.md"
    drawio = V4_DOCS / "v4_0_current_gap_analysis.drawio"

    assert md.exists()
    assert drawio.exists()
    ET.fromstring(drawio.read_text(encoding="utf-8"))


def test_v4_0_only_gap_drawio_is_active() -> None:
    drawios = sorted(path.name for path in V4_DOCS.glob("*.drawio"))
    assert drawios == ["v4_0_current_gap_analysis.drawio"]


def test_v4_0_docs_use_frozen_v3_6_protocol_names() -> None:
    docs = [
        V4_DOCS / "v4_0_current_gap_analysis.md",
        V4_DOCS / "v4_0_ui_contract_map.md",
        V4_DOCS / "v4_0_event_contract_map.md",
        V4_DOCS / "v4_0_stitch_prototype_mapping.md",
        V4_DOCS / "v4_0_current_gap_analysis.drawio",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in docs)

    for forbidden in ("workflow.invoke", "workflow.observe", "workflow.review"):
        assert forbidden not in text
    for required in (
        "workflow.board.get",
        "workflow.instance.status",
        "station.output.list",
        "workflow.patch.propose",
        "workflow.patch.diff",
        "workflow.patch.apply",
        "workflow.patch.reject",
        "workflow.template.publish",
        "approval.respond",
        "business.event.emit",
        "workflow.context.get",
        "workflow.context.update",
        "artifact.lineage",
        "quality.evaluation.get",
        "quality.evaluation.list",
    ):
        assert required in text


def test_v4_0_ui_allowlist_covers_required_screens() -> None:
    text = _read("docs/design/V4.0/v4_0_ui_contract_map.md")
    required_methods = {
        "V4.0-0": (
            "workflow.template.list",
            "workflow.template.get",
            "workflow.version.list",
            "workflow.version.get",
        ),
        "V4.0-A": (
            "workflow.instance.get",
            "workflow.instance.list",
            "workflow.instance.status",
            "station.run.list",
            "workflow.board.get",
            "station.output.list",
            "artifact.read_metadata",
            "artifact.lineage",
            "job.get",
            "job.list",
        ),
        "V4.0-B": (
            "workflow.patch.propose",
            "workflow.patch.diff",
            "workflow.patch.apply",
            "workflow.patch.reject",
            "workflow.template.publish",
        ),
        "V4.0-C": (
            "events.subscribe",
            "approval.respond",
            "workflow.context.get",
        ),
        "V4.0-D": (
            "quality.evaluation.get",
            "quality.evaluation.list",
            "workflow.context.update",
            "business.event.emit",
            "business.event.bind",
        ),
    }
    for phase, methods in required_methods.items():
        assert phase in text
        for method in methods:
            assert method in text
    assert "Dev/demo-only RPC" in text
    assert "workflow.instance.start" in text


def test_v4_0_event_contract_keeps_quality_trace_only() -> None:
    text = _read("docs/design/V4.0/v4_0_event_contract_map.md")
    for live_event in (
        "approval.required",
        "workflow.instance.started",
        "workflow.instance.completed",
        "workflow.instance.failed",
        "station.run.started",
        "station.run.completed",
        "station.run.failed",
        "station.run.waiting_approval",
        "artifact.registered",
        "business.event.received",
        "workflow.context.updated",
        "workflow.patch.proposed",
        "workflow.patch.applied",
        "workflow.patch.rejected",
    ):
        assert live_event in text
    assert "quality.evaluated" in text
    quality_index = text.index("quality.evaluated")
    trace_only_index = text.index("Trace-only Events")
    assert quality_index > trace_only_index


def test_v4_0_mock_to_real_checklist_has_required_columns_and_transient_state() -> None:
    text = _read("docs/design/V4.0/v4_0_mock_to_real_contract_checklist.md")
    for column in (
        "UI 区域",
        "UI 字段",
        "来源",
        "对应 API",
        "是否可持久化",
        "是否可写回 runtime",
        "是否包含敏感信息",
        "是否需要 redaction",
        "mock 到期阶段",
    ):
        assert column in text
    for transient in (
        "selected node",
        "canvas zoom",
        "node x/y",
        "panel collapsed",
        "side panel width",
        "active tab",
        "filter keyword",
    ):
        assert transient in text
    assert "UI-only transient" in text


def test_v4_0_frontend_stack_decision_freezes_react_workflow_console() -> None:
    text = _read("docs/design/V4.0/v4_0_frontend_stack_decision.md")
    assert "React + Vite + TypeScript" in text
    assert "apps/workflow-console/" in text
    assert "apps/web" in text
    assert "Vue 3 + Vite" in text


def test_v3_6_docs_do_not_reference_missing_station_run_test_file() -> None:
    docs = [
        Path("docs/design/V3.6/v3_6_acceptance_plan.md"),
        Path("docs/design/V3.6/v3_6_development_plan_workflow_runtime.md"),
        Path("docs/design/V3.6/v3_6_current_gap_analysis.md"),
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "tests/test_v3_6_station_run.py" not in text
        assert "tests/test_v3_6_workflow_runtime.py" in text
