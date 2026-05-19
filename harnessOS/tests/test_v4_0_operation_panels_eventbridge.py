"""V4.0-D operation panel EventBridge tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app
from tests.test_v4_0_operation_panels_bff_routes import SCOPE_QUERY, _gateway, _seed


def test_business_context_events_are_visible_through_bff_eventbridge(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", "v4-d-eventbridge")
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service, "v4_d_eventbridge"))
    instance_id = seeded["instance"]["workflow_instance_id"]
    client = TestClient(create_app(gateway_service=service))

    client.post(
        f"/bff/instances/{instance_id}/business-events{SCOPE_QUERY}",
        json={
            "event_type": "business.workflow.note_submitted",
            "event_id": "evt_visible",
            "payload": {"note": "事件进入上下文"},
            "binding": {"target_path": "context.business.event_note", "payload_path": "event.payload.note"},
        },
    )
    response = client.get(f"/bff/events/subscribe{SCOPE_QUERY}&channels=business,workflow_context&workflow_instance_id={instance_id}&follow=0")
    assert response.status_code == 200
    assert "event: business.event.received" in response.text
    assert "event: workflow.context.updated" in response.text
    assert "subscription_token" not in response.text
    assert "Authorization" not in response.text
