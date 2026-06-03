from __future__ import annotations

import pytest

from core.observability.audit_export import AuditExportError, AuditExportService
from tests.v5_3_observability_support import make_context, make_policy, make_provider_invocation_event


def test_audit_export_requires_user_confirmation() -> None:
    context = make_context()
    event = make_provider_invocation_event(context)
    service = AuditExportService()

    with pytest.raises(AuditExportError) as excinfo:
        service.create_export_package(
            context,
            events=[event],
            retention_policy=make_policy(context),
            requested_by=context.actor_id,
            source="user",
            user_confirmed=False,
            time_range={"from": "2026-01-01T00:00:00Z", "to": "2026-01-02T00:00:00Z"},
        )

    assert excinfo.value.code == "AUDIT_EXPORT_CONFIRMATION_REQUIRED"


def test_agent_source_cannot_export_audit_package() -> None:
    context = make_context()
    event = make_provider_invocation_event(context)
    service = AuditExportService()

    with pytest.raises(AuditExportError) as excinfo:
        service.create_export_package(
            context,
            events=[event],
            retention_policy=make_policy(context),
            requested_by="agent_v5",
            source="agent",
            user_confirmed=True,
            time_range={"from": "2026-01-01T00:00:00Z", "to": "2026-01-02T00:00:00Z"},
        )

    assert excinfo.value.code == "AUDIT_EXPORT_AGENT_DENIED"


def test_audit_export_package_is_redacted_and_read_only() -> None:
    context = make_context()
    event = make_provider_invocation_event(context)
    service = AuditExportService()

    package = service.create_export_package(
        context,
        events=[event],
        retention_policy=make_policy(context),
        requested_by=context.actor_id,
        source="user",
        user_confirmed=True,
        time_range={"from": "2026-01-01T00:00:00Z", "to": "2026-01-02T00:00:00Z"},
    )
    data = package.to_dict()

    assert data["event_count"] == 1
    assert data["readonly"] is True
    assert set(data["allowed_actions"]) == {"view", "export", "open_evidence"}
    assert data["checksum"]
    assert data["redaction_status"] == "redacted"
