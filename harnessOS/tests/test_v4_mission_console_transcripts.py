"""V4.x Mission Console transcript tests."""

from __future__ import annotations

from pathlib import Path


DOC = Path("docs/design/V4.x/v4_x_mission_console_prd.md")
TRANSCRIPT = Path("docs/design/V4.x/evidence/unified-experience/mission_console_transcript.txt")


def test_mission_console_prd_defines_main_commands_and_agent_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for command in ["/create workflow", "/show diff", "/confirm apply", "/run", "/rerun station", "/show evidence"]:
        assert command in text
    for forbidden in ["auto apply", "auto publish", "auto run", "auto rerun"]:
        assert forbidden in text


def test_mission_console_transcript_shows_user_confirmation() -> None:
    text = TRANSCRIPT.read_text(encoding="utf-8")

    assert "state=IntentCaptured" in text
    assert "state=SpecDrafted" in text
    assert "state=DiffReady" in text
    assert "user_confirmed=true" in text
    assert "source=mission_console" in text
    assert "Evidence Chain 只读展示" in text
    assert "不能 auto apply / publish / run / rerun" in text

