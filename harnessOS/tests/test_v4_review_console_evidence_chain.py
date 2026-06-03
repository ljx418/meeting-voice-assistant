import json
from pathlib import Path

from core.workflows.v4_unified_experience import build_review_action


def test_review_action_is_handoff_contract_not_execution():
    action = build_review_action(
        operation="workflow.patch.apply",
        source="review_console",
        actor_type="human",
    )
    assert action["requires_user_confirmation"] is True
    assert action["policy_decision"] == "user_confirmed_only"
    assert action["operation_executed"] is False


def test_review_action_blocks_agent_mutation():
    action = build_review_action(
        operation="approval.respond",
        source="agent",
        actor_type="agent",
    )
    assert action["requires_user_confirmation"] is True
    assert action["policy_decision"] == "blocked"
    assert action["operation_executed"] is False


def test_evidence_report_actions_are_readonly():
    schema = json.loads(Path("docs/design/V4.x/schemas/evidence_report.schema.json").read_text())
    assert schema["properties"]["readonly"]["const"] is True
    assert set(schema["properties"]["report_actions"]["items"]["enum"]) == {
        "view",
        "export",
        "open_handoff",
    }


def test_development_plan_forbids_evidence_mutation_buttons():
    text = Path("docs/design/V4.x/v4_x_unified_development_plan.md").read_text()
    assert "Evidence Chain 不得出现 Apply / Publish / Approve / Reject / Execute / Run" in text
    assert "EvidenceReportDTO 只允许 view / export / open_handoff" in text
