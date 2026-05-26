"""V4.0-W external app production onboarding follow-up design tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_w_external_app_production_onboarding_design_contract.json")
REQUIRED_GAPS = {
    "app_registration",
    "domain_verification",
    "origin_allowlist_review",
    "tenant_provisioning",
    "service_account_lifecycle",
    "token_rotation_revocation",
    "sdk_versioning_policy",
    "api_compatibility_policy",
    "quota_rate_limit",
    "abuse_detection",
    "customer_offboarding",
    "data_export_deletion",
    "support_runbook",
}
FORBIDDEN_ROUTES = {
    "/production/onboarding",
    "/app/register",
    "/domain/verify",
    "/tenant/provision",
    "/service-account",
    "/quota",
    "/customer/offboard",
    "/data/export",
    "/data/delete",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_w_contract_is_design_only() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-W"
    assert contract["contract_type"] == "external_app_production_onboarding_follow_up_design"
    assert contract["runtime_enabled"] is False
    assert contract["production_external_app_onboarding_enabled"] is False
    assert contract["tenant_provisioning_enabled"] is False
    assert contract["quota_runtime_enabled"] is False
    assert contract["allowed_claim"] == "V4.0-W complete: external app production onboarding follow-up design ready for review."


def test_w_onboarding_gap_matrix_covers_required_gaps() -> None:
    contract = _contract()
    assert set(contract["onboarding_gap_matrix"]) == REQUIRED_GAPS
    for gap in contract["gap_details"]:
        assert gap["gap_id"] in REQUIRED_GAPS
        assert gap["current_status"] == "gap_only"
        assert gap["blocking_for_production"] is True


def test_w_dev_local_boundary_does_not_claim_production_external_app_support() -> None:
    boundary = _contract()["dev_local_boundary"]
    assert boundary["v3_5_sdk_bff_embed_is_dev_local_baseline"] is True
    assert boundary["production_ready_external_app_support"] is False
    assert boundary["production_customer_onboarding_ready"] is False


def test_w_does_not_add_external_app_production_routes() -> None:
    assert_no_forbidden_route_fragments(FORBIDDEN_ROUTES)
