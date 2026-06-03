from __future__ import annotations

import pytest

from core.apps.external_onboarding import ExternalAppOnboardingError, ExternalAppOnboardingRegistry
from tests.v5_3_observability_support import make_context


def test_offboarding_revokes_app_access_and_records_redacted_evidence() -> None:
    context = make_context()
    registry = ExternalAppOnboardingRegistry()
    registration = registry.register_app(
        context,
        app_registration_id="external_app_v5_5",
        display_name="Partner App",
        allowed_capabilities=["workflow.read", "artifact.read"],
        source="user",
        user_confirmed=True,
    )

    record = registry.offboard_app(
        context,
        app_registration_id=registration.app_registration_id,
        revoked_capability_refs=["capability://workflow.read"],
        revoked_credential_refs=["credential_ref_partner"],
    ).to_dict()

    assert record["redaction_status"] == "redacted"
    assert record["data_export_status"] == "completed"
    assert record["deletion_status"] == "scheduled"
    assert registry.registrations[registration.app_registration_id].status == "revoked"

    with pytest.raises(ExternalAppOnboardingError) as excinfo:
        registry.evaluate_origin(context, app_registration_id=registration.app_registration_id, origin="https://app.example.com")
    assert excinfo.value.code == "EXTERNAL_APP_REVOKED"
