"""V4.0-S production auth / tenant boundary design gate tests."""

from __future__ import annotations

import json
from pathlib import Path

from tests.v4_0_guard_utils import assert_no_forbidden_route_fragments


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_s_production_auth_tenant_boundary_design_contract.json")
FORBIDDEN_ROUTE_FRAGMENTS = {
    "/oauth",
    "/sso",
    "/oidc",
    "/saml",
    "/login/callback",
    "/tenant",
    "/admin/tenant",
    "/token/rotate",
    "/token/revoke",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_s_contract_exists_and_is_design_only() -> None:
    contract = _contract()
    assert contract["stage"] == "V4.0-S"
    assert contract["contract_type"] == "production_auth_tenant_boundary_follow_up_design"
    assert contract["runtime_enabled"] is False
    assert contract["production_auth_implementation_enabled"] is False
    assert contract["tenant_control_plane_enabled"] is False
    assert contract["oauth_sso_implementation_enabled"] is False
    assert contract["allowed_claim"] == "V4.0-S complete: production auth and tenant boundary follow-up design ready for review."


def test_s_does_not_add_forbidden_auth_tenant_or_token_routes() -> None:
    assert_no_forbidden_route_fragments(FORBIDDEN_ROUTE_FRAGMENTS)


def test_s_runtime_boundary_does_not_reclassify_v3_6_contract_as_auth_truth() -> None:
    runtime_boundary = _contract()["runtime_boundary"]
    assert runtime_boundary["v3_6_runtime_contract_changed"] is False
    assert runtime_boundary["workflow_template_tenant_control_plane"] is False
    assert runtime_boundary["workflow_draft_tenant_control_plane"] is False
    assert runtime_boundary["workflow_version_tenant_control_plane"] is False
    assert runtime_boundary["station_run_tenant_control_plane"] is False
    assert runtime_boundary["eventbridge_builds_auth_truth"] is False
