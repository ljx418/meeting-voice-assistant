from __future__ import annotations

import pytest

from core.apps.external_onboarding import ExternalAppOnboardingError, ExternalAppOnboardingRegistry
from tests.v5_3_observability_support import make_context


def _registry_with_app() -> tuple[ExternalAppOnboardingRegistry, str]:
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
    return registry, registration.app_registration_id


def test_unverified_origin_is_denied() -> None:
    context = make_context()
    registry, app_registration_id = _registry_with_app()
    verification = registry.create_domain_verification(
        context,
        app_registration_id=app_registration_id,
        domain="example.com",
        verification_method="dns_txt",
    )

    with pytest.raises(ExternalAppOnboardingError) as excinfo:
        registry.allow_origin(
            context,
            app_registration_id=app_registration_id,
            origin="https://app.example.com",
            domain_verification_id=verification.domain_verification_id,
        )

    assert excinfo.value.code == "ORIGIN_VERIFICATION_REQUIRED"


def test_verified_domain_allows_matching_origin_and_blocks_unknown_origin() -> None:
    context = make_context()
    registry, app_registration_id = _registry_with_app()
    verification = registry.create_domain_verification(
        context,
        app_registration_id=app_registration_id,
        domain="example.com",
        verification_method="dns_txt",
    )
    verified = registry.mark_domain_verified(context, domain_verification_id=verification.domain_verification_id, evidence_ref="evidence://domain/example")
    entry = registry.allow_origin(
        context,
        app_registration_id=app_registration_id,
        origin="https://app.example.com",
        domain_verification_id=verified.domain_verification_id,
    )

    assert entry.policy_decision == "allow"
    assert registry.evaluate_origin(context, app_registration_id=app_registration_id, origin="https://app.example.com").origin == "https://app.example.com"
    with pytest.raises(ExternalAppOnboardingError) as excinfo:
        registry.evaluate_origin(context, app_registration_id=app_registration_id, origin="https://evil.example.net")
    assert excinfo.value.code == "ORIGIN_ALLOWLIST_DENIED"
