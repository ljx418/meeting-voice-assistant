"""V3.6/V4.0 preflight EventBridge channel permission tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.service import GatewayService
from core.protocol.auth import issue_capability_token


SECRET = "preflight-event-secret"
LOCAL_ORIGIN = "http://localhost:5173"


def _client(monkeypatch, gateway: GatewayService) -> TestClient:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    return TestClient(create_app(gateway_service=gateway))


def _headers(gateway: GatewayService, capabilities: tuple[str, ...]) -> dict[str, str]:
    token = issue_capability_token(
        app_profile=gateway.app_registry.get("meeting"),
        project_id="demo",
        workspace_id="local",
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )
    return {"Authorization": f"Bearer {token}", "Origin": LOCAL_ORIGIN}


def test_business_event_channel_requires_business_events_read_for_rpc_and_sse(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)

    missing = client.post(
        "/v1/rpc",
        json={"id": "events", "method": "events.subscribe", "params": {"channels": ["business"]}},
        headers=_headers(gateway, ("events",)),
    )
    assert missing.json()["error"]["code"] == "CAPABILITY_DENIED"
    assert "business_events.read" in missing.json()["error"]["data"]["missing_capabilities"]

    sse_missing = client.get(
        "/v1/events/subscribe?channels=business&app_id=meeting&project_id=demo&workspace_id=local",
        headers=_headers(gateway, ("events",)),
    )
    assert sse_missing.status_code == 403
    assert sse_missing.json()["error"]["code"] == "CAPABILITY_DENIED"

    allowed = client.post(
        "/v1/rpc",
        json={"id": "events", "method": "events.subscribe", "params": {"channels": ["business"]}},
        headers=_headers(gateway, ("events", "business_events.read")),
    )
    assert allowed.json().get("error") is None
    assert allowed.json()["result"]["allowed_channels"] == ["business"]
