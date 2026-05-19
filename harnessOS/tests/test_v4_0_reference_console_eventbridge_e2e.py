"""V4.0-E reference console EventBridge E2E tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console, sse_events


def test_reference_console_bff_eventbridge_replays_business_context_and_approval(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", "v4-e-events")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service))
    instance_id = seeded["instance"]["workflow_instance_id"]
    client = TestClient(create_app(gateway_service=service))

    response = client.get(
        f"/bff/events/subscribe{SCOPE_QUERY}&channels=approval,business,workflow_context&workflow_instance_id={instance_id}"
    )
    assert response.status_code == 200
    events = sse_events(response.text)
    by_type = {event["type"]: event for event in events}
    assert "approval.required" in by_type
    assert "business.event.received" in by_type
    assert "workflow.context.updated" in by_type
    assert by_type["business.event.received"]["workflow_instance_id"] == instance_id
    assert by_type["workflow.context.updated"]["workflow_instance_id"] == instance_id
    assert by_type["business.event.received"]["_sse_id"]
    assert by_type["business.event.received"]["_sse_event"] == "business.event.received"
    assert_no_forbidden_text(events)

    last_cursor = events[-1]["cursor"]
    replay = client.get(
        f"/bff/events/subscribe{SCOPE_QUERY}&channels=approval,business,workflow_context&workflow_instance_id={instance_id}",
        headers={"Last-Event-ID": last_cursor},
    )
    assert replay.status_code == 200
    assert sse_events(replay.text) == []


def test_reference_console_eventbridge_auth_failure_does_not_open_stream(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    service = build_gateway(tmp_path)
    client = TestClient(create_app(gateway_service=service))

    response = client.get("/bff/events/subscribe?channels=business&app_id=reference_app&project_id=demo_a&workspace_id=local")
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
