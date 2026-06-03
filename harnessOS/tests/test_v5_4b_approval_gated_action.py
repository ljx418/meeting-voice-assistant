from __future__ import annotations

from core.policies.controlled_executor_trial import ControlledExecutorTrialRunner
from tests.v5_3_observability_support import make_context


def test_high_risk_action_remains_approval_gated_and_not_executed() -> None:
    context = make_context()
    result = ControlledExecutorTrialRunner().evaluate_high_risk_action(
        context,
        operation="workflow.template.publish",
        target_refs={"workflow_version_id": "version_v5_4b"},
        source="user",
        actor_type="human_user",
        user_confirmed=True,
        risk_flags=("high_risk",),
    )
    data = result.to_dict()

    assert data["status"] == "blocked"
    assert data["decision"]["policy_decision"] == "approval_required"
    assert data["decision"]["requires_approval"] is True
    assert data["decision"]["approval_gate"]["approval_required"] is True
    assert data["runtime_evidence"] is None
