from pathlib import Path


def test_mission_console_transcript_contains_closed_loop_states():
    text = Path("docs/design/V4.x/evidence/unified-experience/mission_console_transcript.txt").read_text()
    for state in [
        "IntentCaptured",
        "SpecDrafted",
        "SchemaValidated",
        "DiffReady",
        "AwaitingConfirmation",
    ]:
        assert state in text
    assert "user_confirmed=true" in text
    assert "source=mission_console" in text
    assert "不能 auto apply / publish / run / rerun" in text


def test_mission_console_plan_does_not_claim_agent_executor():
    text = Path("docs/design/V4.x/v4_x_unified_development_plan.md").read_text()
    assert "Mission Console 不能被描述为 Agent executor" in text
    assert "source=agent 不能执行 mutation" in text
