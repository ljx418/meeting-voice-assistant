from __future__ import annotations

import pytest

from core.policies.executor_safety import CapabilityDecisionService, ExecutorSafetyError, RequestedAction
from tests.v5_3_observability_support import make_context


def test_source_agent_mutation_remains_denied_even_with_executor_capability() -> None:
    context = make_context(actor_type="agent", actor_id="agent_actor_v5_4a")
    decision = CapabilityDecisionService().evaluate(
        context,
        RequestedAction(
            operation="workflow.patch.apply",
            source="agent",
            actor_type="agent",
            target_refs={"workflow_patch_id": "patch_v5_4a"},
            user_confirmed=True,
            capability_refs=("executor.user_confirmed_execute",),
        ),
    )

    assert decision.allowed is False
    assert decision.agent_executable is False
    assert decision.runtime_execution_allowed is False
    assert decision.reason == "source_agent_cannot_execute_mutation"


def test_sandbox_boundary_rejects_token_and_raw_payload() -> None:
    context = make_context()
    with pytest.raises(ExecutorSafetyError) as excinfo:
        CapabilityDecisionService().evaluate(
            context,
            RequestedAction(
                operation="workflow.instance.start",
                source="user",
                actor_type="human_user",
                target_refs={"workflow_instance_id": "instance_v5_4a"},
                user_confirmed=True,
                payload_refs={"raw_connector_payload": "Authorization: Bearer sk-test"},
            ),
        )

    assert excinfo.value.code == "EXECUTOR_SANDBOX_DENIED"


def test_sandbox_boundary_rejects_direct_runtime_truth_write() -> None:
    context = make_context()
    with pytest.raises(ExecutorSafetyError) as excinfo:
        CapabilityDecisionService().evaluate(
            context,
            RequestedAction(
                operation="workflow.instance.start",
                source="user",
                actor_type="human_user",
                target_refs={"direct_workflowstore_write": "WorkflowStore.write"},
                user_confirmed=True,
            ),
        )

    assert excinfo.value.reason == "direct_runtime_truth_write"
