"""V4.0-U production secret management follow-up design tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_u_production_secret_management_design_contract.json")
REQUIRED_SECRET_CLASSES = {
    "capability_token",
    "subscription_token",
    "connector_secret",
    "external_llm_api_key",
    "upstream_signed_url",
    "raw_prompt",
}
FORBIDDEN_ROUTES = {
    "/secret",
    "/secrets",
    "/admin/secret",
    "/admin/secrets",
    "/token/rotate",
    "/token/revoke",
    "/audit/export",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_u_contract_is_design_only() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-U"
    assert contract["contract_type"] == "production_secret_management_follow_up_design"
    assert contract["runtime_enabled"] is False
    assert contract["production_secret_manager_enabled"] is False
    assert contract["secret_admin_routes_enabled"] is False
    assert contract["allowed_claim"] == "V4.0-U complete: production secret management follow-up design ready for review."


def test_u_secret_matrix_blocks_sensitive_values_from_dto_dom_event_and_audit() -> None:
    matrix = {item["secret_class"]: item for item in _contract()["secret_boundary_matrix"]}
    assert set(matrix) == REQUIRED_SECRET_CLASSES
    for secret_class, item in matrix.items():
        assert item["blocking_for_production"] is True, secret_class
        assert item["dto_allowed"] is False, secret_class
        assert item["dom_allowed"] is False, secret_class
        assert item["event_payload_allowed"] is False, secret_class
        assert item["audit_summary_allowed"] is False, secret_class


def test_u_sandbox_boundary_keeps_future_executor_redacted_only() -> None:
    boundary = _contract()["sandbox_boundary"]
    assert boundary["future_executor_reads_redacted_bff_dtos_only"] is True
    assert boundary["direct_secret_store_access"] is False
    assert boundary["raw_connector_payload_access"] is False
    assert boundary["raw_artifact_content_access"] is False
    assert boundary["raw_trace_payload_access"] is False


def test_u_does_not_add_secret_or_audit_export_routes() -> None:
    assert_no_forbidden_route_fragments(FORBIDDEN_ROUTES)
