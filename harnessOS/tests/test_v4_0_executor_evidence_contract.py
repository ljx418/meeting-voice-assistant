"""V4.0-Q executor evidence and rollback contract tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_contract.json")


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_executor_evidence_contract_fields_are_defined_but_not_created_in_q() -> None:
    evidence = _contract()["evidence_contract"]
    assert evidence["creates_real_executor_evidence_in_q"] is False
    assert set(evidence["fields"]) >= {
        "proposal_id",
        "handoff_id",
        "user_confirmed",
        "approval_id",
        "capability_decision",
        "policy_decision",
        "runtime_result_ref",
        "correlation_id",
        "idempotency_key",
        "redaction_status",
        "created_at",
        "created_by",
    }


def test_rollback_and_kill_switch_are_design_only() -> None:
    rollback = _contract()["rollback_and_kill_switch_design"]
    assert rollback["implemented_in_q"] is False
    assert set(rollback["items"]) >= {
        "per-agent kill switch",
        "per-workspace kill switch",
        "capability revocation",
        "operation timeout",
        "idempotency key",
        "rollback descriptor",
        "manual recovery path",
        "audit retention",
    }


def test_event_truth_forbids_executor_truth_from_payload() -> None:
    event_truth = _contract()["event_truth"]
    assert event_truth["eventbridge_payload_can_construct_truth"] is False
    assert set(event_truth["forbidden_truth_from_event_payload"]) >= {
        "executor truth",
        "agent action truth",
        "patch truth",
        "approval truth",
        "evidence truth",
        "board/status truth",
        "context truth",
    }
