"""V4.3 video Drawio and HTML report tests."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from scripts.v4_3_serial_video_evidence import FORBIDDEN_TERMS


EVIDENCE_DIR = Path("docs/design/V4.3/evidence/serial-video-workflow")
DRAWIO_REPORTS = ["video_workflow.drawio", "video_workflow_status.drawio", "video_artifact_lineage.drawio"]
HTML_REPORTS = ["video_run_report.html", "video_artifacts.html", "video_quality.html", "video_evidence.html"]


def test_video_drawio_outputs_are_valid_xml() -> None:
    for filename in DRAWIO_REPORTS:
        root = ElementTree.fromstring((EVIDENCE_DIR / filename).read_text(encoding="utf-8"))
        assert root.tag == "mxfile"
        assert root.find("diagram") is not None


def test_video_workflow_drawio_contains_all_agent_stations() -> None:
    text = (EVIDENCE_DIR / "video_workflow.drawio").read_text(encoding="utf-8")

    for station_id in [
        "writer_agent",
        "storyboard_agent",
        "copywriting_agent",
        "editing_plan_agent",
        "quality_review_agent",
        "publish_preparation_agent",
    ]:
        assert station_id in text
    assert "edge_writer_agent_storyboard_agent" in text


def test_video_html_reports_are_read_only() -> None:
    for filename in HTML_REPORTS:
        text = (EVIDENCE_DIR / filename).read_text(encoding="utf-8")
        lowered = text.lower()
        assert "<form" not in lowered
        assert "<button" not in lowered
        assert "method=\"post\"" not in lowered
        assert "fetch(" not in lowered
        assert "只读" in text


def test_video_reports_do_not_leak_tokens_or_raw_payloads() -> None:
    for filename in [*DRAWIO_REPORTS, *HTML_REPORTS]:
        text = (EVIDENCE_DIR / filename).read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            assert term not in text
