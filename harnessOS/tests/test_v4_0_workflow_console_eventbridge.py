"""V4.0-A2 Workflow Console BFF EventBridge proxy tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app

from tests.test_v4_0_workflow_console_bff_routes import SCOPE_QUERY, _gateway, _seed


def test_bff_eventbridge_preserves_sse_shape_and_hides_upstream_tokens(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", "v4-a2-events")
    service = _gateway(tmp_path)
    seeded = asyncio.run(_seed(service, "v4_a2_events"))
    artifact_id = seeded["runs"][0]["output_artifact_ids"][0]
    client = TestClient(create_app(gateway_service=service))

    response = client.get(f"/bff/events/subscribe{SCOPE_QUERY}&channels=artifact&artifact_id={artifact_id}&follow=0")
    assert response.status_code == 200
    body = response.text
    assert "id: " in body
    assert "event: artifact.registered" in body
    assert "data: " in body
    assert artifact_id in body
    for forbidden in ("subscription_token", "capability_token", "Authorization", "upstream signed", "/v1/events/subscribe"):
        assert forbidden not in body


def test_bff_eventbridge_auth_failure_does_not_open_stream(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    service = _gateway(tmp_path)
    client = TestClient(create_app(gateway_service=service))

    response = client.get("/bff/events/subscribe?channels=artifact&follow=0")
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_bff_eventbridge_cursor_replay_accepts_last_event_id(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", "v4-a2-events")
    service = _gateway(tmp_path)
    asyncio.run(_seed(service, "v4_a2_cursor"))
    client = TestClient(create_app(gateway_service=service))

    first = client.get(f"/bff/events/subscribe{SCOPE_QUERY}&channels=artifact&follow=0")
    cursor = [line.split(": ", 1)[1] for line in first.text.splitlines() if line.startswith("id: ")][-1]
    second = client.get(
        f"/bff/events/subscribe{SCOPE_QUERY}&channels=artifact&follow=0",
        headers={"Last-Event-ID": cursor},
    )
    assert second.status_code == 200
    assert "event: artifact.registered" not in second.text
