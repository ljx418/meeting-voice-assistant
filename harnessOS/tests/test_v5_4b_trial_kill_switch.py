from __future__ import annotations

from core.policies.controlled_executor_trial import ControlledExecutorTrialRunner
from core.policies.executor_safety import CapabilityDecisionService, KillSwitchRegistry
from tests.v5_3_observability_support import make_context


def test_trial_kill_switch_blocks_action_before_synthetic_state_change() -> None:
    context = make_context()
    kill_switches = KillSwitchRegistry()
    kill_switches.disable_workspace(context.workspace_id)
    runner = ControlledExecutorTrialRunner(decision_service=CapabilityDecisionService(kill_switches=kill_switches))
    before = runner.seed_workflow(workflow_instance_id="synthetic_instance_v5_4b", station_ids=["scan"]).to_dict()

    result = runner.start_workflow(
        context,
        workflow_instance_id="synthetic_instance_v5_4b",
        source="user",
        actor_type="human_user",
        user_confirmed=True,
    )
    after = runner.workflow_states["synthetic_instance_v5_4b"].to_dict()

    assert result.status == "blocked"
    assert result.blocked_reason == "kill_switch:workspace_kill_switch_active"
    assert before == after
