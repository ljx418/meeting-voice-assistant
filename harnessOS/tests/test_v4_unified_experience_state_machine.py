"""V4.x unified experience state machine contract tests."""

from __future__ import annotations

import json
from pathlib import Path


DOC = Path("docs/design/V4.x/v4_x_experience_state_machine.md")
SCHEMA = Path("docs/design/V4.x/schemas/experience_state.schema.json")
ACTION_SCHEMA = Path("docs/design/V4.x/schemas/available_actions.schema.json")


def test_state_machine_doc_defines_required_state_groups() -> None:
    text = DOC.read_text(encoding="utf-8")

    for heading in ["Workflow-level States", "Station-level States", "Evidence-level States"]:
        assert heading in text
    for state in ["IntentCaptured", "SpecDrafted", "DiffReady", "Recoverable", "RerunRequested", "EvidenceRecorded"]:
        assert state in text
    for field in [
        "available_actions",
        "blocked_actions",
        "requires_user_confirmation",
        "risk_level",
        "evidence_required",
    ]:
        assert field in text


def test_experience_state_schema_is_strict_and_multi_head_visible() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert schema["additionalProperties"] is False
    assert "visible_in" in schema["required"]
    visible_enum = set(schema["properties"]["visible_in"]["items"]["enum"])
    assert {
        "mission_console",
        "workflow_blueprint",
        "runtime_report",
        "review_console",
        "evidence_chain",
        "tui",
        "drawio",
        "html_report",
        "thin_web_console",
    }.issubset(visible_enum)


def test_available_action_schema_blocks_agent_execution_by_contract() -> None:
    schema = json.loads(ACTION_SCHEMA.read_text(encoding="utf-8"))

    assert schema["additionalProperties"] is False
    assert "agent_executable" in schema["required"]
    assert "user_confirmed_only" in schema["properties"]["policy_decision"]["enum"]
    assert "blocked" in schema["properties"]["policy_decision"]["enum"]

