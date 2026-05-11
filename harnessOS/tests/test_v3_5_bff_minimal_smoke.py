"""V3.5-D2 Minimal BFF Smoke tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = ROOT / "sdk/python"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from harnessos_client import EventSubscription, Scope
from templates.bff.fastapi_minimal.app import create_app


class FakeSdkClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def session_start(self, *, model=None, scope=None):
        self.calls.append(("session_start", {"model": model, "scope": scope.to_dict()}))
        return {"session_id": "sess_demo", "state": "active", "scope": scope.to_dict()}

    def turn_start(self, *, input, session_id=None, domain=None, scope=None):
        self.calls.append(("turn_start", {"input": input, "session_id": session_id, "domain": domain, "scope": scope.to_dict()}))
        return {"session_id": session_id or "sess_demo", "turn_id": "turn_demo", "scope": scope.to_dict()}

    def approval_respond(self, *, approval_id, decision, reason=None, scope=None):
        self.calls.append(("approval_respond", {"approval_id": approval_id, "decision": decision, "reason": reason, "scope": scope.to_dict()}))
        return {"approval": {"approval_id": approval_id}, "status": "approved" if decision == "approve" else "rejected", "idempotent": False}

    def rpc(self, method, params):
        self.calls.append(("rpc", {"method": method, "params": params}))
        return {"method": method, "params": params}

    def events_subscribe(self, *, channels=None, scope=None):
        self.calls.append(("events_subscribe", {"channels": channels, "scope": scope.to_dict()}))
        return EventSubscription(
            subscription_id="sub_demo",
            transport="eventsource",
            eventsource_url="http://upstream.local/v1/events/subscribe?subscription_token=sub-secret",
            subscription_token="sub-secret",
            replay_cursor="cursor_demo",
            expires_at="2026-05-11T00:00:00+00:00",
            allowed_channels=tuple(channels or ("chat",)),
        )


class FakeUpstream:
    def __init__(self) -> None:
        self.closed = False
        self.url = ""
        self.frames = [
            b"id: cursor_1\n",
            b"event: artifact.registered\n",
            b"data: {\"event_id\":\"evt_1\"}\n\n",
        ]

    def __iter__(self):
        return iter(self.frames)

    def close(self) -> None:
        self.closed = True


def _client(fake_sdk: FakeSdkClient | None = None, upstream: FakeUpstream | None = None) -> tuple[TestClient, FakeSdkClient, FakeUpstream]:
    sdk = fake_sdk or FakeSdkClient()
    source = upstream or FakeUpstream()

    def opener(url: str):
        source.url = url
        return source

    app = create_app(sdk_client=sdk, upstream_opener=opener)
    return TestClient(app), sdk, source


def test_config_is_platform_neutral() -> None:
    config = json.loads((ROOT / "templates/bff/fastapi_minimal/config.example.json").read_text(encoding="utf-8"))
    text = json.dumps(config)
    assert config["identity_scope"]["app_id"] in {"reference_app", "demo_app"}
    assert "meeting" not in text
    assert "knowledge" not in text


def test_bff_template_has_no_server_internal_imports() -> None:
    template_dir = ROOT / "templates/bff/fastapi_minimal"
    forbidden = ("GatewayService", "RuntimeAdapter", "Core Store", "apps.gateway.service", "from apps.", "from core.")
    for path in template_dir.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not any(item in text for item in forbidden), path


def test_scope_identity_route_body_binding() -> None:
    client, sdk, _ = _client()
    ok = client.post(
        "/bff/session/start?app_id=reference_app&project_id=demo&workspace_id=local",
        json={"model": "demo", "scope": {"app_id": "reference_app", "project_id": "demo", "workspace_id": "local"}},
    )
    assert ok.status_code == 200
    assert ok.json()["scope"] == {"app_id": "reference_app", "project_id": "demo", "workspace_id": "local"}
    assert sdk.calls[-1][0] == "session_start"

    route_conflict = client.post("/bff/session/start?app_id=other_app", json={})
    assert route_conflict.status_code == 403
    assert route_conflict.json()["error"]["code"] == "SCOPE_MISMATCH"

    body_conflict = client.post("/bff/session/start", json={"scope": {"app_id": "other_app"}})
    assert body_conflict.status_code == 403
    assert body_conflict.json()["error"]["code"] == "SCOPE_MISMATCH"


def test_bff_rpc_allowlist_and_denylist() -> None:
    client, sdk, _ = _client()
    allowed = client.post("/bff/rpc", json={"method": "session.start", "params": {}})
    assert allowed.status_code == 200
    assert allowed.json()["method"] == "session.start"
    assert sdk.calls[-1][1]["params"]["scope"]["app_id"] == "reference_app"

    for method in (
        "meeting.process_recording",
        "knowledge.search",
        "approval.approve",
        "approval.reject",
        "pack.execute_stub",
        "workflow.execute_stub",
        "method.list",
    ):
        denied = client.post("/bff/rpc", json={"method": method, "params": {"include_forbidden": True}})
        assert denied.status_code == 403
        assert denied.json()["error"]["code"] == "METHOD_FORBIDDEN"

    scope_all = client.post("/bff/rpc", json={"method": "session.start", "params": {"scope_mode": "all"}})
    assert scope_all.status_code == 403
    assert scope_all.json()["error"]["code"] == "METHOD_FORBIDDEN"


def test_structured_routes_and_approval_respond_only() -> None:
    client, sdk, _ = _client()
    turn = client.post("/bff/turn/start", json={"input": "hello", "session_id": "sess_demo"})
    assert turn.status_code == 200
    assert turn.json()["turn_id"] == "turn_demo"

    approval = client.post("/bff/approval/respond", json={"approval_id": "appr_demo", "decision": "approve"})
    assert approval.status_code == 200
    assert approval.json()["status"] == "approved"
    assert [call[0] for call in sdk.calls][-2:] == ["turn_start", "approval_respond"]


def test_eventsource_proxy_preserves_frames_and_hides_subscription_token() -> None:
    client, sdk, upstream = _client()
    response = client.get("/bff/events/subscribe?channels=artifact")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "id: cursor_1" in response.text
    assert "event: artifact.registered" in response.text
    assert "data: {\"event_id\":\"evt_1\"}" in response.text
    assert "sub-secret" not in response.text
    assert "subscription_token=sub-secret" in upstream.url
    assert upstream.closed is True
    assert sdk.calls[-1] == ("events_subscribe", {"channels": ["artifact"], "scope": {"app_id": "reference_app", "project_id": "demo", "workspace_id": "local"}})


def test_eventsource_scope_failure_does_not_open_stream() -> None:
    client, _, upstream = _client()
    response = client.get("/bff/events/subscribe?app_id=other_app")
    assert response.status_code == 403
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert upstream.url == ""


def test_eventsource_upstream_auth_failure_does_not_open_stream() -> None:
    class AuthFailingSdk(FakeSdkClient):
        def events_subscribe(self, *, channels=None, scope=None):
            from harnessos_client import AuthRequiredError

            raise AuthRequiredError("AUTH_REQUIRED", "missing bearer cap-secret-token", {"token": "cap-secret-token"})

    client, _, upstream = _client(AuthFailingSdk())
    response = client.get("/bff/events/subscribe?channels=artifact")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
    assert "cap-secret-token" not in response.text
    assert upstream.url == ""


def test_eventsource_malformed_upstream_sse_has_stable_redacted_passthrough() -> None:
    class MalformedUpstream(FakeUpstream):
        def __init__(self) -> None:
            super().__init__()
            self.frames = [b"not-an-sse-frame with subscription_token=sub-secret\n\n"]

    client, _, upstream = _client(upstream=MalformedUpstream())
    response = client.get("/bff/events/subscribe?channels=artifact")
    assert response.status_code == 200
    assert "not-an-sse-frame" in response.text
    assert "sub-secret" not in response.text
    assert upstream.closed is True


def test_bff_does_not_call_runs_stream_by_default() -> None:
    template_dir = ROOT / "templates/bff/fastapi_minimal"
    for path in template_dir.glob("*.py"):
        assert "/v1/runs/stream" not in path.read_text(encoding="utf-8")


def test_secret_redaction_in_error_response() -> None:
    class FailingSdk(FakeSdkClient):
        def rpc(self, method, params):
            raise RuntimeError("failed with bearer cap-secret-token and subscription_token=sub-secret")

    client, _, _ = _client(FailingSdk())
    response = client.post("/bff/rpc", json={"method": "session.start", "params": {}})
    assert response.status_code == 400
    text = response.text
    assert "cap-secret-token" not in text
    assert "sub-secret" not in text
    assert "[REDACTED]" in text
