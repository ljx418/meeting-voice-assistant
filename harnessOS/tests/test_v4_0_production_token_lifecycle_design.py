"""V4.0-T production token lifecycle follow-up design tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_t_production_token_lifecycle_design_contract.json")
REQUIRED_CAPABILITIES = {
    "issuance",
    "expiration",
    "rotation",
    "revocation",
    "origin_binding",
    "audience_binding",
    "scope_binding",
    "emergency_revoke",
    "token_audit",
}
FORBIDDEN_ROUTES = {
    "/token/rotate",
    "/token/revoke",
    "/token/refresh",
    "/token/introspect",
    "/token/emergency-revoke",
    "/oauth",
    "/sso",
    "/oidc",
    "/saml",
    "/login/callback",
    "/tenant",
    "/admin/tenant",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_t_contract_is_design_only() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-T"
    assert contract["contract_type"] == "production_token_lifecycle_follow_up_design"
    assert contract["runtime_enabled"] is False
    assert contract["production_token_lifecycle_implementation_enabled"] is False
    assert contract["allowed_claim"] == "V4.0-T complete: production token lifecycle follow-up design ready for review."


def test_t_lifecycle_matrix_covers_required_capabilities_as_blocking_gaps() -> None:
    matrix = {item["capability"]: item for item in _contract()["token_lifecycle_matrix"]}
    assert set(matrix) == REQUIRED_CAPABILITIES
    for capability, item in matrix.items():
        assert item["current_status"] == "design_gap", capability
        assert item["blocking_for_production"] is True, capability
        assert item["risk_level"] in {"critical", "high"}, capability
        assert item["required_controls"], capability


def test_t_keeps_agent_and_executor_inactive() -> None:
    boundary = _contract()["agent_executor_boundary"]
    assert boundary["source_agent_can_execute_mutation"] is False
    assert boundary["capability_token_can_bypass_user_confirmation"] is False
    assert boundary["executor_capabilities_active"] is False
    assert boundary["future_executor_claims_enable_execution_in_t"] is False


def test_t_does_not_add_token_auth_or_tenant_routes() -> None:
    assert_no_forbidden_route_fragments(FORBIDDEN_ROUTES)


def test_t_event_payload_does_not_build_token_truth() -> None:
    event_truth = _contract()["event_truth_boundary"]
    assert event_truth["eventbridge_triggers_refresh_only"] is True
    assert event_truth["event_payload_builds_token_truth"] is False
    assert event_truth["fake_token_event_payload_trusted"] is False
