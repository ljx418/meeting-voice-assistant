"""V4.0 preflight document/protocol alignment tests."""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET


def test_v4_0_drawio_uses_frozen_v3_6_protocol_names() -> None:
    path = Path("docs/design/V4.0/v4_target_architecture_workflow_console.drawio")
    text = path.read_text(encoding="utf-8")

    for forbidden in ("workflow.invoke", "workflow.observe", "workflow.review"):
        assert forbidden not in text
    for required in (
        "workflow.board.get",
        "workflow.instance.status",
        "station.output.list",
        "workflow.patch.*",
        "workflow.template.publish",
        "approval.respond",
        "business.event.*",
        "workflow.context.*",
        "artifact.lineage",
        "quality.evaluation.*",
    ):
        assert required in text
    ET.fromstring(text)


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
