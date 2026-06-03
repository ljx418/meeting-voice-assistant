from __future__ import annotations

from core.policies.controlled_executor_trial import ControlledExecutorTrialRunner
from tests.v5_3_observability_support import make_context


def test_trial_action_requires_user_confirmation() -> None:
    context = make_context()
    runner = ControlledExecutorTrialRunner()
    runner.seed_workflow(workflow_instance_id="synthetic_instance_v5_4b", station_ids=["scan"])

    result = runner.start_workflow(
        context,
        workflow_instance_id="synthetic_instance_v5_4b",
        source="user",
        actor_type="human_user",
        user_confirmed=False,
    )

    assert result.status == "blocked"
    assert result.blocked_reason == "missing_user_confirmation"
    assert result.runtime_evidence is None


def test_source_agent_trial_mutation_denied_even_when_user_confirmed() -> None:
    context = make_context(actor_type="agent", actor_id="agent_actor_v5_4b")
    runner = ControlledExecutorTrialRunner()
    runner.seed_workflow(workflow_instance_id="synthetic_instance_v5_4b", station_ids=["scan"])

    result = runner.start_workflow(
        context,
        workflow_instance_id="synthetic_instance_v5_4b",
        source="agent",
        actor_type="agent",
        user_confirmed=True,
    )

    assert result.status == "blocked"
    assert result.blocked_reason == "source_agent_cannot_execute_mutation"
    assert result.decision.agent_executable is False
