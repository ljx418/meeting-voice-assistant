"""V4.0-X production readiness consolidation gate tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_x_production_readiness_consolidation_gate_contract.json")
REQUIRED_SOURCE_STAGES = {"v4_0_r", "v4_0_s", "v4_0_t", "v4_0_u", "v4_0_v", "v4_0_w"}
REQUIRED_BLOCKING_CATEGORIES = {
    "auth_sso_oauth",
    "multi_tenant_isolation",
    "capability_token_lifecycle",
    "secret_management",
    "observability_audit_retention",
    "external_app_onboarding",
    "rate_limit_abuse_control",
    "data_residency_export_deletion",
    "incident_recovery",
}
FORBIDDEN_ROUTES = {
    "/oauth",
    "/sso",
    "/oidc",
    "/saml",
    "/login/callback",
    "/tenant",
    "/admin/tenant",
    "/token/rotate",
    "/token/revoke",
    "/secret",
    "/secrets",
    "/audit/export",
    "/production/onboarding",
    "/quota",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_x_contract_consolidates_r_through_w_sources() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-X"
    assert contract["contract_type"] == "production_readiness_consolidation_gate"
    assert contract["runtime_enabled"] is False
    assert contract["production_implementation_enabled"] is False
    source_text = "\n".join(contract["source_contracts"])
    for stage in REQUIRED_SOURCE_STAGES:
        assert stage in source_text


def test_x_blocking_categories_are_complete_and_false_ready_flags_remain_false() -> None:
    contract = _contract()
    assert set(contract["blocking_categories"]) == REQUIRED_BLOCKING_CATEGORIES
    result = contract["consolidated_result"]
    assert result["ready_for_implementation_review"] is True
    assert result["production_ready"] is False
    assert result["enterprise_auth_ready"] is False
    assert result["multi_tenant_control_plane_ready"] is False
    assert result["external_app_production_ready"] is False
    assert result["controlled_executor_ready"] is False


def test_x_does_not_add_production_implementation_routes() -> None:
    assert_no_forbidden_route_fragments(FORBIDDEN_ROUTES)
