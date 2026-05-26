"""V4.0-Y controlled executor implementation gate tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_y_controlled_executor_implementation_gate_contract.json")
FORBIDDEN_ROUTES = {
    "/execute",
    "/run",
    "/agent/execute",
    "/connector/call",
    "/external-llm/call",
    "/executor/dry-run",
    "/kill-switch",
    "/rollback",
    "/admin-override",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_y_contract_is_gate_only_not_executor_implementation() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-Y"
    assert contract["contract_type"] == "controlled_executor_implementation_gate"
    assert contract["runtime_enabled"] is False
    assert contract["controlled_executor_implementation_enabled"] is False
    assert contract["executor_worker_enabled"] is False
    assert contract["executor_runtime_service_enabled"] is False
    assert contract["allowed_claim"] == "V4.0-Y complete: controlled executor implementation gate ready for review."


def test_y_executor_requirements_remain_blocking_before_executor() -> None:
    requirements = _contract()["implementation_gate_requirements"]
    assert len(requirements) >= 6
    for item in requirements:
        assert item["blocking_before_executor"] is True, item
    assert any(item["current_status"] == "not_implemented" for item in requirements)


def test_y_agent_boundary_rejects_all_mutations_and_calls() -> None:
    boundary = _contract()["agent_boundary"]
    for field, value in boundary.items():
        assert value is False, field


def test_y_does_not_add_executor_or_control_routes() -> None:
    assert_no_forbidden_route_fragments(FORBIDDEN_ROUTES)


def test_y_event_payload_does_not_build_executor_truth() -> None:
    event_truth = _contract()["event_truth_boundary"]
    assert event_truth["eventbridge_triggers_refresh_only"] is True
    assert event_truth["fake_executor_event_payload_trusted"] is False
    assert event_truth["event_payload_builds_executor_truth"] is False
