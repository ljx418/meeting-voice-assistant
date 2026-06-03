"""V4.3 serial video deterministic runner tests."""

from __future__ import annotations

from pathlib import Path

from core.workflows.v4_3_serial_video import VIDEO_STATIONS, assert_no_forbidden_text, run_serial_video_workflow


BRIEF_PATH = Path("tests/fixtures/v4_3/video_brief/launch_brief.md")


def _brief() -> str:
    return BRIEF_PATH.read_text(encoding="utf-8")


def test_video_runner_uses_real_brief_fixture_and_generates_station_artifacts() -> None:
    run = run_serial_video_workflow(brief_text=_brief(), brief_path=BRIEF_PATH.as_posix(), scope={"app_id": "reference_app"})

    assert run["status"] == "completed"
    assert run["backed_by"] == "v4_3_serial_video_runtime"
    assert [node["station_id"] for node in run["nodes"]] == [station["station_id"] for station in VIDEO_STATIONS]
    assert {artifact["name"] for artifact in run["artifacts"]} == {
        "script_outline.md",
        "storyboard.md",
        "short_copy.md",
        "editing_plan.md",
        "quality_review.json",
        "publish_package.md",
    }
    assert run["quality_report"]["status"] == "passed"
    assert "HarnessOS Headless 发布视频 Brief" in run["quality_report"]["brief_title"]
    assert_no_forbidden_text(run)


def test_video_runner_can_simulate_middle_station_failure() -> None:
    run = run_serial_video_workflow(
        brief_text=_brief(),
        brief_path=BRIEF_PATH.as_posix(),
        scope={"app_id": "reference_app"},
        simulate_failure_station="storyboard_agent",
    )

    assert run["status"] == "failed"
    storyboard = next(node for node in run["nodes"] if node["station_id"] == "storyboard_agent")
    copywriting = next(node for node in run["nodes"] if node["station_id"] == "copywriting_agent")
    assert storyboard["status"] == "failed"
    assert copywriting["status"] == "pending"
    assert "Deterministic video station failed" in storyboard["error"]
    assert_no_forbidden_text(run)
