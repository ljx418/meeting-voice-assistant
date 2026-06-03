"""V4.2-A TUI transcript contract tests."""

from __future__ import annotations

from pathlib import Path


TRANSCRIPT = Path("docs/design/V4.2/evidence/headless-interaction/tui-transcript.txt")


def test_tui_read_commands_are_read_only() -> None:
    text = TRANSCRIPT.read_text(encoding="utf-8")

    for command in [
        "harness tui",
        "harness workflow diff",
        "harness workflow status",
        "harness artifacts list",
        "harness quality report",
        "harness evidence show",
    ]:
        line = next(item for item in text.splitlines() if command in item)
        assert "read_only=true" in line


def test_tui_mutating_commands_are_v41_backed_or_transcript_only() -> None:
    text = TRANSCRIPT.read_text(encoding="utf-8")

    for command in ["harness workflow apply", "harness workflow publish", "harness workflow run"]:
        line = next(item for item in text.splitlines() if command in item)
        assert "user_confirmed=true" in line
        assert "source=editing_panel" in line or "source=run_panel" in line
        assert "backed_by=v4_1_local_workflow_path" in line
        assert "transcript_only=false" in line

    rerun_line = next(item for item in text.splitlines() if "harness station rerun" in item)
    assert "transcript_only=true" in rerun_line
    assert "generic_runtime=false" in rerun_line


def test_tui_transcript_blocks_direct_browser_routes() -> None:
    text = TRANSCRIPT.read_text(encoding="utf-8")

    assert "browser_direct_v1_rpc=false" in text
    assert "browser_direct_v1_events_subscribe=false" in text
    assert "/v1/rpc" not in text
    assert "/v1/events/subscribe" not in text
