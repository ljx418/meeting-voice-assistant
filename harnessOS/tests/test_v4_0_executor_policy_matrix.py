"""V4.0-Q executor policy matrix contract tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_contract.json")
REQUIRED_ACTIONS = {
    "workflow.patch.apply": "user_confirmed_only",
    "workflow.patch.reject": "user_confirmed_only",
    "workflow.template.publish": "approval_gated_future",
    "approval.respond": "user_confirmed_only",
    "workflow.context.update": "user_confirmed_only",
    "business.event.emit": "user_confirmed_only",
    "workflow.instance.start": "approval_gated_future",
    "station.rerun": "approval_gated_future",
    "connector.call": "never_executor",
    "external_llm.call": "never_executor",
    "artifact.write": "approval_gated_future",
    "quality.evaluation.create": "approval_gated_future",
}


def _matrix() -> dict[str, dict]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    return {item["action"]: item for item in contract["policy_matrix"]}


def test_policy_matrix_covers_required_actions_and_classifications() -> None:
    matrix = _matrix()
    assert set(matrix) == set(REQUIRED_ACTIONS)
    for action, classification in REQUIRED_ACTIONS.items():
        assert matrix[action]["classification"] == classification


def test_policy_matrix_blocks_q_stage_executor_and_never_executor_allowlist() -> None:
    for action, item in _matrix().items():
        assert item["q_stage_callable_by_executor"] is False, action
        if item["classification"] == "never_executor":
            assert item["future_executor_eligible"] is False, action
        if item["classification"] == "approval_gated_future":
            assert item["requires_approval_gate"] is True, action
