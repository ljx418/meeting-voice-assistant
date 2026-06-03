from __future__ import annotations

from core.policies.executor_safety import CANDIDATE_POLICY_MATRIX, ExecutorPolicyMatrix


def test_every_candidate_operation_has_classification() -> None:
    matrix = ExecutorPolicyMatrix()
    items = {item.operation: item for item in matrix.items()}

    assert set(items) == set(CANDIDATE_POLICY_MATRIX)
    for item in items.values():
        assert item.classification in {
            "forbidden",
            "proposal_only",
            "handoff_only",
            "user_confirmed_only",
            "approval_gated_future",
            "never_executor",
        }
        assert item.agent_executable is False
        assert item.runtime_execution_allowed is False


def test_never_executor_operations_never_enter_allowlist() -> None:
    matrix = ExecutorPolicyMatrix()

    assert matrix.item_for("connector.call").classification == "never_executor"
    assert matrix.item_for("external_llm.call").classification == "never_executor"
    for operation in ("connector.call", "external_llm.call"):
        item = matrix.item_for(operation)
        assert item.agent_executable is False
        assert item.runtime_execution_allowed is False
