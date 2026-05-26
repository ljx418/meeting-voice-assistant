"""V4.0-Q executor approval gate design tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_contract.json")


def _approval_gate() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))["approval_gate_design"]


def test_approval_gate_is_design_only_and_covers_high_risk_conditions() -> None:
    gate = _approval_gate()
    assert gate["implemented_in_q"] is False
    assert gate["creates_approval_request_in_q"] is False
    assert gate["calls_approval_respond_in_q"] is False
    assert set(gate["high_risk_conditions"]) >= {
        "requires_approval=true",
        "high risk_flags",
        "external side effect",
        "connector mutation",
        "publish workflow",
        "context mutation",
        "business event emit",
        "artifact write",
        "quality score mutation",
    }


def test_q_does_not_add_executor_approval_or_admin_routes() -> None:
    assert_no_forbidden_route_fragments(
        {"/executor/approval", "/approval-gate", "/admin-override", "/kill-switch", "/rollback"}
    )
