from __future__ import annotations

from core.observability.audit_export import IncidentTimelineBuilder
from tests.v5_3_observability_support import make_context, make_provider_invocation_event


def test_incident_timeline_is_read_only_and_correlation_backed() -> None:
    context = make_context()
    event = make_provider_invocation_event(context)

    timeline = IncidentTimelineBuilder().build(context, incident_id="incident_v5_3", events=[event], severity="warning")

    assert len(timeline) == 1
    data = timeline[0].to_dict()
    assert data["readonly"] is True
    assert data["correlation_id"] == context.correlation_id
    assert data["event_ref"] == event.event_id
    assert data["evidence_ref"]
    assert set(data["allowed_actions"]) == {"view", "export", "open_evidence"}
    forbidden_actions = {"Apply", "Publish", "Approve", "Reject", "Execute", "Run"}
    assert forbidden_actions.isdisjoint(set(data["allowed_actions"]))
