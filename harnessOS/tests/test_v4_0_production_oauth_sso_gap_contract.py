"""V4.0-S OAuth / SSO gap contract tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_s_production_auth_tenant_boundary_design_contract.json")
REQUIRED_CAPABILITIES = {
    "identity provider registration",
    "OIDC discovery",
    "SAML metadata",
    "JWKS rotation",
    "login callback",
    "session binding",
    "tenant mapping",
    "user provisioning",
    "group mapping",
    "logout",
    "token expiration",
    "token revocation",
    "audit trail",
}


def test_oauth_sso_capabilities_remain_gap_only_or_planned_future() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    gaps = {item["capability"]: item["status"] for item in contract["oauth_sso_gap_contract"]}
    assert set(gaps) == REQUIRED_CAPABILITIES
    for capability, status in gaps.items():
        assert status in {"gap_only", "planned_future"}, capability
        assert status not in {"implemented", "ready", "enabled"}
