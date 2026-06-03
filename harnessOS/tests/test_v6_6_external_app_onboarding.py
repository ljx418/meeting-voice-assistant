from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.apps.external_onboarding import ExternalAppOnboardingError
from core.apps.v6_external_app_onboarding import (
    V6_ALLOWED_BFF_ROUTES,
    V6ExternalAppOnboardingPilot,
    make_v6_external_app_context,
)
from core.auth.tenant_boundary import IdentityContext


SCHEMA_DIR = Path("docs/design/V6.x/schemas")
COMMON_FIELDS = {
    "tenant_id",
    "workspace_id",
    "app_id",
    "service_account_id",
    "actor_id",
    "request_id",
    "correlation_id",
    "audit_ref",
    "policy_decision",
    "created_at",
}
FORBIDDEN_TEXT = (
    "raw secret",
    "raw token",
    "raw prompt",
    "raw connector payload",
    "raw artifact content",
    "signed URL",
    "sk-",
    "Authorization",
    "Bearer ",
)


def _identity(
    *,
    tenant_id: str = "tenant_v6_6",
    workspace_id: str = "workspace_v6_6",
    app_id: str = "app_v6_6",
    actor_id: str = "user_v6_6",
) -> IdentityContext:
    return IdentityContext(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        project_id="project_v6_6",
        app_id=app_id,
        actor_type="human_user",
        actor_id=actor_id,
        user_id=actor_id,
        service_account_id=None,
        agent_id=None,
        session_id=None,
        request_id=f"request_{tenant_id}",
        correlation_id=f"correlation_{tenant_id}",
    )


def _pilot_with_app() -> tuple[V6ExternalAppOnboardingPilot, object, str]:
    pilot = V6ExternalAppOnboardingPilot()
    ctx = make_v6_external_app_context(_identity(), service_account_id="svc_v6_6")
    registration = pilot.register_app(
        ctx,
        registration_id="external-app-v6-6",
        app_display_name="V6 外部应用",
        allowed_capabilities=["workflow.read", "artifact.read"],
        source="product_console",
        user_confirmed=True,
        credential_refs=["credential-ref://external-app-v6-6/primary"],
        active_session_refs=["session-ref://external-app-v6-6/browser"],
        pending_capability_grant_refs=["capability-grant-ref://external-app-v6-6/workflow-read"],
    )
    return pilot, ctx, registration["registration_id"]


def test_v6_6_schemas_parse_and_common_fields_are_required() -> None:
    schema_names = [
        "v6_6_external_app_registration.schema.json",
        "v6_6_domain_verification_decision.schema.json",
        "v6_6_origin_allowlist_decision.schema.json",
        "v6_6_quota_decision.schema.json",
        "v6_6_external_app_offboarding_evidence.schema.json",
        "v6_6_sdk_compatibility_policy.schema.json",
    ]

    for name in schema_names:
        schema = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False
        assert COMMON_FIELDS.issubset(set(schema["required"]))
        assert COMMON_FIELDS.issubset(set(schema["properties"]))


def test_external_app_registration_common_fields_and_redaction() -> None:
    pilot, _ctx, _registration_id = _pilot_with_app()
    registration = pilot._registrations["external-app-v6-6"]

    assert COMMON_FIELDS.issubset(registration)
    assert registration["service_account_id"] == "svc_v6_6"
    assert registration["policy_decision"] == "allow"
    assert registration["status"] == "registered"
    _assert_no_sensitive_text(registration)


def test_unverified_domain_origin_allowlist_denied() -> None:
    pilot, ctx, registration_id = _pilot_with_app()
    pending = pilot.create_domain_verification(
        ctx,
        registration_id=registration_id,
        domain="example.com",
        verification_method="dns_txt",
        mark_verified=False,
    )

    decision = pilot.allow_origin(ctx, registration_id=registration_id, origin="https://app.example.com", domain_verification_ref=pending["domain_verification_ref"])

    assert decision["policy_decision"] == "deny"
    assert decision["decision"] == "deny"
    assert decision["denial_reason"] == "domain_not_verified"


def test_verified_origin_allowed_and_unknown_origin_denied() -> None:
    pilot, ctx, registration_id = _pilot_with_app()
    verified = pilot.create_domain_verification(ctx, registration_id=registration_id, domain="example.com", verification_method="dns_txt", mark_verified=True)
    allowed = pilot.allow_origin(ctx, registration_id=registration_id, origin="https://app.example.com", domain_verification_ref=verified["domain_verification_ref"])
    unknown = pilot.evaluate_origin(ctx, registration_id=registration_id, origin="https://unknown.example.com")

    assert allowed["decision"] == "allow"
    assert unknown["decision"] == "deny"
    assert unknown["denial_reason"] == "unknown_origin"


def test_wrong_tenant_app_access_denied() -> None:
    pilot, _ctx, registration_id = _pilot_with_app()
    wrong_ctx = make_v6_external_app_context(_identity(tenant_id="tenant_other"), service_account_id="svc_v6_6")

    decision = pilot.evaluate_origin(wrong_ctx, registration_id=registration_id, origin="https://app.example.com")

    assert decision["decision"] == "deny"
    assert decision["policy_decision"] == "deny"
    assert decision["denial_reason"] == "scope_mismatch"


def test_quota_and_rate_limit_denials_are_auditable() -> None:
    pilot, ctx, registration_id = _pilot_with_app()
    quota_policy = pilot.create_quota_policy(ctx, registration_id=registration_id, limit_type="quota", limit_value=2, window_seconds=60)
    rate_policy = pilot.create_quota_policy(ctx, registration_id=registration_id, limit_type="rate_limit", limit_value=1, window_seconds=1)

    quota_denial = pilot.evaluate_quota(ctx, quota_policy_ref=quota_policy, current_usage=2, denial_type="quota")
    rate_denial = pilot.evaluate_quota(ctx, quota_policy_ref=rate_policy, current_usage=1, denial_type="rate_limit")

    assert quota_denial["decision"] == "deny_quota"
    assert quota_denial["policy_decision"] == "deny"
    assert quota_denial["audit_ref"].startswith("audit://")
    assert rate_denial["decision"] == "deny_rate_limit"
    assert rate_denial["audit_ref"].startswith("audit://")
    _assert_no_sensitive_text(quota_denial)
    _assert_no_sensitive_text(rate_denial)


def test_offboarding_revokes_credentials_origins_sessions_and_pending_grants() -> None:
    pilot, ctx, registration_id = _pilot_with_app()
    verified = pilot.create_domain_verification(ctx, registration_id=registration_id, domain="example.com", verification_method="dns_txt", mark_verified=True)
    pilot.allow_origin(ctx, registration_id=registration_id, origin="https://app.example.com", domain_verification_ref=verified["domain_verification_ref"])

    evidence = pilot.offboard_app(ctx, registration_id=registration_id)

    assert evidence["revoked_app_credentials"] is True
    assert evidence["revoked_origin_allowlist"] is True
    assert evidence["revoked_active_sessions"] is True
    assert evidence["revoked_pending_capability_grants"] is True
    assert evidence["revocation_refs"]
    assert pilot._registrations[registration_id]["status"] == "offboarded"
    _assert_no_sensitive_text(evidence)


def test_browser_sdk_no_direct_internal_runtime_route() -> None:
    pilot, ctx, _registration_id = _pilot_with_app()

    policy = pilot.sdk_compatibility_policy(
        ctx,
        requested_browser_routes=[
            "GET /bff/v6/runtime-report",
            "/v1/rpc",
            "/v1/events/subscribe",
            "/v1/internal/runtime",
            "/v1/internal/executor",
        ],
    )

    assert "GET /bff/v6/runtime-report" in policy["allowed_bff_routes"]
    assert "/v1/rpc" in policy["denied_internal_routes"]
    assert "/v1/events/subscribe" in policy["denied_internal_routes"]
    assert "/v1/internal/runtime" in policy["denied_internal_routes"]
    assert policy["browser_direct_runtime_route_denied"] is True
    assert policy["browser_direct_v1_rpc_denied"] is True
    assert policy["browser_direct_v1_events_subscribe_denied"] is True


def test_browser_sdk_known_bff_routes_are_allowlisted_without_runtime_truth() -> None:
    pilot, ctx, _registration_id = _pilot_with_app()

    policy = pilot.sdk_compatibility_policy(ctx, requested_browser_routes=sorted(V6_ALLOWED_BFF_ROUTES))

    assert policy["policy_decision"] == "allow"
    assert set(policy["allowed_bff_routes"]) == V6_ALLOWED_BFF_ROUTES
    assert policy["browser_direct_runtime_route_denied"] is True


def test_sensitive_fields_and_values_are_rejected() -> None:
    pilot = V6ExternalAppOnboardingPilot()
    ctx = make_v6_external_app_context(_identity(), service_account_id="svc_v6_6")

    with pytest.raises(ExternalAppOnboardingError) as excinfo:
        pilot.register_app(
            ctx,
            registration_id="external-app-v6-6-secret",
            app_display_name="secret=bad",
            allowed_capabilities=["workflow.read"],
            source="product_console",
            user_confirmed=True,
        )

    assert excinfo.value.code == "EXTERNAL_APP_REDACTION_DENIED"


def _assert_no_sensitive_text(data: object) -> None:
    serialized = json.dumps(data, ensure_ascii=False)
    lowered = serialized.lower()
    for item in FORBIDDEN_TEXT:
        assert item.lower() not in lowered
