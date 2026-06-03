"""V4.3 serial video evidence package tests."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.v4_3_serial_video_evidence import DEFAULT_OUTPUT_DIR, FORBIDDEN_TERMS, generate_serial_video_evidence


def test_video_evidence_package_can_be_rebuilt(tmp_path) -> None:
    manifest = generate_serial_video_evidence(tmp_path)

    assert manifest["status"] == "completed"
    assert "video_workflow.drawio" in manifest["files"]
    assert "video_run_report.html" in manifest["files"]
    assert "operation-evidence.json" in manifest["files"]


def test_video_evidence_package_contains_required_outputs() -> None:
    required = {
        "tui-transcript.txt",
        "video_workflow.yaml",
        "video_workflow.json",
        "video_workflow.schema.json",
        "video_workflow.drawio",
        "video_workflow_status.drawio",
        "video_artifact_lineage.drawio",
        "video_run_report.html",
        "video_artifacts.html",
        "video_quality.html",
        "video_evidence.html",
        "runtime-result.json",
        "attempt-history.json",
        "downstream-stale.json",
        "operation-evidence.json",
        "result-summary.md",
    }
    assert required.issubset({path.name for path in DEFAULT_OUTPUT_DIR.iterdir() if path.is_file()})


def test_video_evidence_package_uses_real_fixture_and_runtime_results() -> None:
    runtime = json.loads((DEFAULT_OUTPUT_DIR / "runtime-result.json").read_text(encoding="utf-8"))
    evidence = json.loads((DEFAULT_OUTPUT_DIR / "operation-evidence.json").read_text(encoding="utf-8"))
    spec = json.loads((DEFAULT_OUTPUT_DIR / "video_workflow.json").read_text(encoding="utf-8"))

    assert runtime["backed_by"] == "v4_3_serial_video_runtime"
    assert runtime["status"] == "completed"
    assert len(runtime["nodes"]) == 6
    assert len(runtime["artifacts"]) == 6
    assert spec["context_refs"][0]["value_label"] == "tests/fixtures/v4_3/video_brief/launch_brief.md"
    assert [node["station_id"] for node in runtime["nodes"]] == [
        "writer_agent",
        "storyboard_agent",
        "copywriting_agent",
        "editing_plan_agent",
        "quality_review_agent",
        "publish_preparation_agent",
    ]
    assert {"workflow.instance.start", "station.rerun", "workflow.instance.continue_downstream"}.issubset(
        {item["operation"] for item in evidence}
    )
    assert all(item["source"] != "agent" for item in evidence)


def test_video_html_reports_are_read_only_and_redacted() -> None:
    html_files = ["video_run_report.html", "video_artifacts.html", "video_quality.html", "video_evidence.html"]
    combined = "\n".join((DEFAULT_OUTPUT_DIR / filename).read_text(encoding="utf-8") for filename in html_files)

    assert "<form" not in combined.lower()
    assert "type=\"submit\"" not in combined.lower()
    for forbidden_copy in ["自动应用", "自动发布", "Agent 已执行", "Agent 已发布"]:
        assert forbidden_copy not in combined
    for term in FORBIDDEN_TERMS:
        assert term not in combined


def test_video_drawio_outputs_are_xml_files() -> None:
    for filename in ["video_workflow.drawio", "video_workflow_status.drawio", "video_artifact_lineage.drawio"]:
        text = (DEFAULT_OUTPUT_DIR / filename).read_text(encoding="utf-8")
        assert text.startswith("<mxfile")
        assert "<mxGraphModel>" in text
