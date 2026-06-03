from __future__ import annotations

from core.apps.external_onboarding import ExternalAppOnboardingRegistry, SDKCompatibilityPolicy, validate_sdk_compatibility
from tests.v5_6_console_support import make_context


def test_external_app_admin_uses_tenant_bound_registration() -> None:
    context = make_context()
    registry = ExternalAppOnboardingRegistry()
    registration = registry.register_app(
        context,
        app_registration_id="app_registration_v5_6_test",
        display_name="控制台应用",
        allowed_capabilities=["workflow.report.view"],
        source="user",
        user_confirmed=True,
    )
    data = registration.to_dict()
    assert data["tenant_id"] == context.tenant_id
    assert data["workspace_id"] == context.workspace_id
    assert data["app_id"] == context.app_id
    assert data["redaction_status"] == "redacted"


def test_sdk_browser_policy_allows_bff_only_paths() -> None:
    data = validate_sdk_compatibility(
        SDKCompatibilityPolicy(
            sdk_name="harnessos-web",
            sdk_version="5.6.0",
            api_version="v5",
            compatibility_status="supported",
            deprecated_at=None,
            sunset_at=None,
            migration_guide_ref=None,
            browser_allowed_paths=("/bff/v5/console", "/assets/"),
        )
    )
    assert "/bff/v5/console" in data["browser_allowed_paths"]
    assert "/v1/rpc" not in data["browser_allowed_paths"]
    assert "/v1/events/subscribe" not in data["browser_allowed_paths"]

