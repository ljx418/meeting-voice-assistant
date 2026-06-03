"""V4.2-A Drawio renderer evidence tests."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from scripts.v4_2_headless_evidence import FORBIDDEN_TERMS


EVIDENCE_DIR = Path("docs/design/V4.2/evidence/headless-interaction")


def test_drawio_outputs_are_valid_xml() -> None:
    for filename in ["workflow.drawio", "workflow_status.drawio", "artifact_lineage.drawio"]:
        text = (EVIDENCE_DIR / filename).read_text(encoding="utf-8")
        root = ElementTree.fromstring(text)
        assert root.tag == "mxfile"
        assert root.find("diagram") is not None


def test_workflow_drawio_contains_spec_nodes_and_edges() -> None:
    text = (EVIDENCE_DIR / "workflow.drawio").read_text(encoding="utf-8")

    for station_id in [
        "folder_input",
        "folder_scan",
        "markdown_filter",
        "markdown_parse",
        "folder_group",
        "per_folder_summary",
        "overview_summary",
        "quality_check",
        "artifact_publish",
    ]:
        assert station_id in text
    assert "edge_folder_input_folder_scan" in text


def test_drawio_outputs_are_redacted_and_read_only() -> None:
    for filename in ["workflow.drawio", "workflow_status.drawio", "artifact_lineage.drawio"]:
        text = (EVIDENCE_DIR / filename).read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            assert term not in text
        assert "runtime truth" not in text.lower()
