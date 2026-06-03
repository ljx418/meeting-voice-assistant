from __future__ import annotations

from core.policies.executor_safety import CapabilityDecisionService, RequestedAction
from tests.v5_3_observability_support import make_context


def test_high_risk_action_is_approval_gated_without_execution() -> None:
    context = make_context()
    decision = CapabilityDecisionService().evaluate(
        context,
        RequestedAction(
            operation="workflow.template.publish",
            source="user",
            actor_type="human_user",
            target_refs={"workflow_version_id": "version_v5_4a"},
            user_confirmed=True,
            risk_flags=("high_risk",),
        ),
    )

    assert decision.policy_decision == "approval_required"
    assert decision.requires_approval is True
    assert decision.approval_gate is not None
    assert "publish_workflow" in decision.risk_flags
    assert decision.runtime_execution_allowed is False
    assert decision.allowed is False


def test_user_confirmed_action_allows_handoff_only_not_runtime_execution() -> None:
    context = make_context()
    decision = CapabilityDecisionService().evaluate(
        context,
        RequestedAction(
            operation="workflow.instance.start",
            source="user",
            actor_type="human_user",
            target_refs={"workflow_instance_id": "instance_v5_4a"},
            user_confirmed=True,
        ),
    )

    assert decision.allowed is True
    assert decision.capability_decision == "allow_for_handoff_only"
    assert decision.runtime_execution_allowed is False
    assert set(decision.allowed_actions) == {"open_handoff", "record_evidence"}


def test_missing_user_confirmation_denied() -> None:
    context = make_context()
    decision = CapabilityDecisionService().evaluate(
        context,
        RequestedAction(
            operation="station.rerun",
            source="user",
            actor_type="human_user",
            target_refs={"station_run_id": "run_v5_4a"},
            user_confirmed=False,
        ),
    )

    assert decision.allowed is False
    assert decision.reason == "missing_user_confirmation"
    assert decision.requires_user_confirmation is True
