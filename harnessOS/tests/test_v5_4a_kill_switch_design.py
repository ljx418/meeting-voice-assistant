from __future__ import annotations

from core.policies.executor_safety import CapabilityDecisionService, KillSwitchRegistry, RequestedAction
from tests.v5_3_observability_support import make_context


def test_workspace_kill_switch_denies_future_trial_action() -> None:
    context = make_context()
    kill_switches = KillSwitchRegistry()
    kill_switches.disable_workspace(context.workspace_id)
    decision = CapabilityDecisionService(kill_switches=kill_switches).evaluate(
        context,
        RequestedAction(
            operation="workflow.instance.start",
            source="user",
            actor_type="human_user",
            target_refs={"workflow_instance_id": "instance_v5_4a"},
            user_confirmed=True,
        ),
    )

    assert decision.allowed is False
    assert decision.reason == "kill_switch:workspace_kill_switch_active"
    assert decision.runtime_execution_allowed is False


def test_capability_revocation_denies_future_trial_action() -> None:
    context = make_context()
    kill_switches = KillSwitchRegistry()
    kill_switches.revoke_capability("executor.user_confirmed_execute")
    decision = CapabilityDecisionService(kill_switches=kill_switches).evaluate(
        context,
        RequestedAction(
            operation="workflow.instance.start",
            source="user",
            actor_type="human_user",
            target_refs={"workflow_instance_id": "instance_v5_4a"},
            user_confirmed=True,
            capability_refs=("executor.user_confirmed_execute",),
        ),
    )

    assert decision.allowed is False
    assert decision.reason == "kill_switch:capability_revoked"


def test_runtime_evidence_contract_exists_but_does_not_enable_execution() -> None:
    contract = CapabilityDecisionService().evidence_contract().to_dict()

    assert contract["readonly"] is True
    assert contract["runtime_execution_allowed"] is False
    for field in ("operation", "source", "actor_type", "user_confirmed", "policy_decision", "correlation_id"):
        assert field in contract["required_fields"]
