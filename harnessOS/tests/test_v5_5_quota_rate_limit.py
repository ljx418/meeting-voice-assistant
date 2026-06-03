from __future__ import annotations

from core.apps.external_onboarding import ExternalAppOnboardingRegistry
from tests.v5_3_observability_support import make_context


def test_quota_denial_is_auditable_and_redacted() -> None:
    context = make_context()
    registry = ExternalAppOnboardingRegistry()
    registration = registry.register_app(
        context,
        app_registration_id="external_app_v5_5",
        display_name="Partner App",
        allowed_capabilities=["workflow.read"],
        source="user",
        user_confirmed=True,
    )
    policy = registry.create_quota_policy(
        context,
        app_registration_id=registration.app_registration_id,
        limit_type="requests",
        limit_value=10,
        window_seconds=60,
    )

    decision = registry.evaluate_quota(context, quota_policy_id=policy.quota_policy_id, usage_count=10).to_dict()

    assert decision["allowed"] is False
    assert decision["policy_decision"] == "deny"
    assert decision["evidence_ref"].startswith("evidence://")
    assert decision["request_id"] == context.request_id
    assert decision["correlation_id"] == context.correlation_id
    assert decision["redaction_status"] == "redacted"
