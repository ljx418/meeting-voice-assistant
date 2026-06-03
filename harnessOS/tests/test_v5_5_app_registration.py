from __future__ import annotations

import pytest

from core.apps.external_onboarding import ExternalAppOnboardingError, ExternalAppOnboardingRegistry
from tests.v5_3_observability_support import make_context


def test_app_registration_is_tenant_bound_and_user_confirmed() -> None:
    context = make_context()
    registry = ExternalAppOnboardingRegistry()

    registration = registry.register_app(
        context,
        app_registration_id="external_app_v5_5",
        display_name="Partner Knowledge App",
        allowed_capabilities=["workflow.read", "artifact.read"],
        source="user",
        user_confirmed=True,
    )
    data = registration.to_dict()

    assert data["tenant_id"] == context.tenant_id
    assert data["workspace_id"] == context.workspace_id
    assert data["app_id"] == context.app_id
    assert data["owner_actor_id"] == context.actor_id
    assert data["status"] == "active"
    assert data["redaction_status"] == "redacted"


def test_app_registration_rejects_agent_source_and_missing_confirmation() -> None:
    context = make_context()
    registry = ExternalAppOnboardingRegistry()

    with pytest.raises(ExternalAppOnboardingError) as missing:
        registry.register_app(
            context,
            app_registration_id="external_app_v5_5",
            display_name="Partner App",
            allowed_capabilities=["workflow.read"],
            source="user",
            user_confirmed=False,
        )
    assert missing.value.code == "EXTERNAL_APP_CONFIRMATION_REQUIRED"

    with pytest.raises(ExternalAppOnboardingError) as agent:
        registry.register_app(
            context,
            app_registration_id="external_app_agent_v5_5",
            display_name="Partner App",
            allowed_capabilities=["workflow.read"],
            source="agent",
            user_confirmed=True,
        )
    assert agent.value.code == "EXTERNAL_APP_AGENT_DENIED"
