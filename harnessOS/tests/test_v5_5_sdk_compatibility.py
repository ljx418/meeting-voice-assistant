from __future__ import annotations

import pytest

from core.apps.external_onboarding import ExternalAppOnboardingError, SDKCompatibilityPolicy, validate_sdk_compatibility


def test_sdk_compatibility_blocks_direct_browser_internal_routes() -> None:
    policy = SDKCompatibilityPolicy(
        sdk_name="harnessos-browser",
        sdk_version="5.5.0",
        api_version="v5",
        compatibility_status="compatible",
        deprecated_at=None,
        sunset_at=None,
        migration_guide_ref="docs://sdk/migration/v5",
        browser_allowed_paths=("/bff/workflows", "/v1/rpc"),
    )

    with pytest.raises(ExternalAppOnboardingError) as excinfo:
        validate_sdk_compatibility(policy)

    assert excinfo.value.code == "SDK_BROWSER_ROUTE_DENIED"


def test_sdk_compatibility_returns_redacted_policy_for_safe_paths() -> None:
    policy = SDKCompatibilityPolicy(
        sdk_name="harnessos-browser",
        sdk_version="5.5.0",
        api_version="v5",
        compatibility_status="compatible",
        deprecated_at=None,
        sunset_at=None,
        migration_guide_ref="docs://sdk/migration/v5",
        browser_allowed_paths=("/bff/workflows", "/bff/reports"),
    )

    data = validate_sdk_compatibility(policy)

    assert data["redaction_status"] == "redacted"
    assert "/v1/rpc" not in data["browser_allowed_paths"]
    assert "/v1/events/subscribe" not in data["browser_allowed_paths"]
