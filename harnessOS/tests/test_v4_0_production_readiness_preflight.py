"""V4.0-R production readiness preflight contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_r_production_readiness_preflight_contract.json")
REQUIRED_CATEGORIES = {
    "auth_sso_oauth",
    "multi_tenant_isolation",
    "capability_token_lifecycle",
    "secret_management",
    "audit_retention",
    "observability_metrics_alerting",
    "rate_limit_abuse_control",
    "data_residency_export_deletion",
    "external_app_onboarding",
    "incident_recovery",
}
REQUIRED_GAP_FIELDS = {
    "gap_id",
    "category",
    "current_state",
    "required_production_state",
    "risk_level",
    "blocking_for_production",
    "evidence_source",
    "owner_area",
    "recommended_next_phase",
    "status",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_production_preflight_contract_exists_and_is_design_only() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-R"
    assert contract["contract_type"] == "production_readiness_preflight"
    assert contract["runtime_enabled"] is False
    assert contract["production_implementation_enabled"] is False
    assert contract["allowed_claim"] == "V4.0-R complete: production readiness preflight ready for review."


def test_every_required_gap_category_and_field_is_present() -> None:
    gaps = _contract()["production_gaps"]
    assert {gap["category"] for gap in gaps} == REQUIRED_CATEGORIES
    for gap in gaps:
        assert REQUIRED_GAP_FIELDS <= set(gap), gap
        assert gap["blocking_for_production"] is True
        assert gap["status"] == "open_gap"
        assert gap["risk_level"] in {"critical", "high", "medium", "low"}


def test_r_does_not_add_production_routes_or_frontend_clients() -> None:
    forbidden_fragments = {
        "/oauth",
        "/sso",
        "/tenant",
        "/admin/tenant",
        "/production/onboarding",
        "/token/rotate",
        "/token/revoke",
        "/quota",
        "/audit/export",
    }
    assert_no_forbidden_route_fragments(forbidden_fragments)
