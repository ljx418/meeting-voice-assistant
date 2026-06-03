from __future__ import annotations

import json

import pytest

from core.observability.audit_export import AuditExportError, AuditExportService, SecurityEventLog
from tests.v5_3_observability_support import make_context, make_policy, make_provider_invocation_event


def test_security_event_log_rejects_raw_payload_fields() -> None:
    context = make_context()
    log = SecurityEventLog()

    with pytest.raises(AuditExportError) as excinfo:
        log.record_event(
            context,
            event_type="workflow.raw_payload.rejected",
            operation="workflow.instance.start",
            target_refs={"workflow_instance_id": "instance_v5_3"},
            policy_decision="deny",
            metadata={"raw_artifact_content": "secret document body"},
        )

    assert excinfo.value.code == "AUDIT_REDACTION_DENIED"


def test_audit_export_does_not_leak_token_or_raw_payload_text() -> None:
    context = make_context()
    event = make_provider_invocation_event(context)
    package = AuditExportService().create_export_package(
        context,
        events=[event],
        retention_policy=make_policy(context),
        requested_by=context.actor_id,
        source="user",
        user_confirmed=True,
        time_range={"from": "2026-01-01T00:00:00Z", "to": "2026-01-02T00:00:00Z"},
    )

    dumped = json.dumps({"event": event.to_dict(), "package": package.to_dict()}, ensure_ascii=False)
    forbidden = [
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer ",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed URL",
    ]
    for token in forbidden:
        assert token not in dumped
