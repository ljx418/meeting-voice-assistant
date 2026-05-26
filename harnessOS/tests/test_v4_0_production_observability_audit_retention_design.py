"""V4.0-V production observability and audit retention follow-up design tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_v_production_observability_audit_retention_design_contract.json")
REQUIRED_GAPS = {
    "trace_retention",
    "operation_evidence_retention",
    "governance_review_export",
    "security_audit_log",
    "correlation_id_coverage",
    "idempotency_key_coverage",
    "metrics_alerting",
    "error_taxonomy",
}
FORBIDDEN_ROUTES = {
    "/audit/export",
    "/metrics/admin",
    "/observability/admin",
    "/incident/timeline",
    "/slo",
    "/sla",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_v_contract_is_design_only() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-V"
    assert contract["contract_type"] == "production_observability_audit_retention_follow_up_design"
    assert contract["runtime_enabled"] is False
    assert contract["production_observability_platform_enabled"] is False
    assert contract["production_audit_export_enabled"] is False
    assert contract["allowed_claim"] == "V4.0-V complete: production observability and audit retention follow-up design ready for review."


def test_v_gap_matrix_covers_required_observability_and_audit_items() -> None:
    matrix = {item["gap_id"]: item for item in _contract()["observability_gap_matrix"]}
    assert set(matrix) == REQUIRED_GAPS
    for gap_id, item in matrix.items():
        assert item["blocking_for_production"] is True, gap_id
        assert item["current_status"] in {"dev_local_baseline", "gap_only", "partial_dev_local"}, gap_id


def test_v_operation_evidence_is_not_production_audit_export() -> None:
    boundary = _contract()["evidence_boundary"]
    assert boundary["v4_0_m_operation_evidence_is_dev_local_baseline"] is True
    assert boundary["production_audit_retention_ready"] is False
    assert boundary["production_audit_export_ready"] is False
    assert boundary["event_payload_builds_audit_truth"] is False


def test_v_does_not_add_observability_or_audit_export_routes() -> None:
    assert_no_forbidden_route_fragments(FORBIDDEN_ROUTES)
