from __future__ import annotations

import json

from tests.v5_3_observability_support import make_context, make_provider_invocation_event


def test_observability_event_has_required_identity_and_correlation_fields() -> None:
    context = make_context()
    event = make_provider_invocation_event(context)

    data = event.to_dict()

    assert data["tenant_id"] == context.tenant_id
    assert data["workspace_id"] == context.workspace_id
    assert data["actor_id"] == context.actor_id
    assert data["request_id"] == context.request_id
    assert data["correlation_id"] == context.correlation_id
    assert data["event_type"] == "provider.invocation.recorded"
    assert data["redaction_status"] == "redacted"
    assert "provider_profile_id" in data["target_refs"]
    assert "evidence_ref" in data["source_refs"]

    dumped = json.dumps(data, ensure_ascii=False)
    assert "MINIMAX_API_KEY" not in dumped
    assert "Authorization" not in dumped
    assert "Bearer " not in dumped
    assert "raw_artifact_content" not in dumped
