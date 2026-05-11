"""V3.5-D Python SDK MVP tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = ROOT / "sdk/python"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

import harnessos_client
from harnessos_client import (
    ApprovalConflictError,
    AuthRequiredError,
    EventCursorInvalidError,
    EventSubscription,
    HarnessOSAsyncClient,
    HarnessOSClient,
    MethodForbiddenError,
    Scope,
    ScopeMismatchError,
    TransportError,
)
from harnessos_client.protocol_snapshot import DEFAULT_METHODS, WRAPPER_METHODS

from apps.api import create_app
from apps.gateway.approvals import ApprovalStore
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.protocol.auth import issue_capability_token
from core.protocol.schemas.methods import METHOD_SCHEMAS


SECRET = "phase-d-sdk-secret"
LOCAL_ORIGIN = "http://localhost:5173"
FORBIDDEN_NAMES = {
    "generateMinutes",
    "ingestDocument",
    "runMeetingWorkflow",
    "generateVideo",
    "analyzePortfolio",
    "processRecording",
    "searchKnowledgeBase",
    "MeetingClient",
    "KnowledgeClient",
}


class MockTransport:
    def __init__(self, response: dict[str, Any] | None = None) -> None:
        self.response = response or {"id": "ok", "result": {"ok": True}}
        self.requests: list[tuple[dict[str, Any], dict[str, str]]] = []

    def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        self.requests.append((payload, headers))
        return self.response


class FailingTransport:
    def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        raise TransportError("connection refused bearer secret-token")


class AsyncMockTransport:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = list(responses)
        self.requests: list[tuple[dict[str, Any], dict[str, str]]] = []

    async def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        self.requests.append((payload, headers))
        return self.responses.pop(0)


class AsgiClientTransport:
    def __init__(self, client: TestClient, token: str) -> None:
        self.client = client
        self.token = token

    def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        merged_headers = {"Origin": LOCAL_ORIGIN, **headers}
        return self.client.post("/v1/rpc", json=payload, headers=merged_headers).json()


def _gateway(tmp_path: Path) -> GatewayService:
    runtime = GatewayRuntimePool(store=GatewaySessionStore(tmp_path / "sessions"))
    return GatewayService(
        runtime_pool=runtime,
        trace_store=TraceStore(tmp_path / "traces"),
        approval_store=ApprovalStore(tmp_path / "approvals"),
    )


def _token(gateway: GatewayService, *, capabilities: tuple[str, ...] | None = None) -> str:
    profile = gateway.app_registry.get("meeting")
    return issue_capability_token(
        app_profile=profile,
        capabilities=capabilities or profile.default_capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )


def _sdk(monkeypatch, tmp_path: Path, *, capabilities: tuple[str, ...] | None = None) -> tuple[HarnessOSClient, GatewayService]:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    gateway = _gateway(tmp_path)
    token = _token(gateway, capabilities=capabilities)
    app = create_app(gateway_service=gateway)
    transport = AsgiClientTransport(TestClient(app), token)
    client = HarnessOSClient(
        base_url="http://testserver",
        capability_token=token,
        scope=Scope(app_id="meeting"),
        transport=transport,
    )
    return client, gateway


def test_python_sdk_has_no_runtime_server_internal_imports() -> None:
    sdk_dir = ROOT / "sdk/python/harnessos_client"
    forbidden = ("apps.", "core.", "GatewayService", "RuntimeAdapter", "METHOD_SCHEMAS")
    for path in sdk_dir.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not any(item in text for item in forbidden), path


def test_public_api_surface_is_strict() -> None:
    expected = {
        "HarnessOSClient",
        "HarnessOSAsyncClient",
        "Scope",
        "RpcError",
        "ProtocolError",
        "HarnessOSError",
        "TransportError",
        "InvalidParamsError",
        "MethodNotFoundError",
        "SessionNotFoundError",
        "AuthRequiredError",
        "AuthInvalidError",
        "AuthForbiddenError",
        "CapabilityDeniedError",
        "ScopeMismatchError",
        "MethodForbiddenError",
        "ApprovalConflictError",
        "ApprovalNotFoundError",
        "ArtifactReadBlockedError",
        "EventCursorInvalidError",
        "PackNotFoundError",
        "ConnectorNotFoundError",
        "CapabilityToken",
        "EventSubscription",
    }
    assert set(harnessos_client.__all__) == expected
    for name in FORBIDDEN_NAMES:
        assert not hasattr(harnessos_client, name)
        assert name not in harnessos_client.__all__


def test_sdk_snapshot_is_schema_default_runtime_subset() -> None:
    server_default = {
        schema["method"]
        for schema in METHOD_SCHEMAS
        if schema["sdk_exposure"] == "default" and schema["runtime_handler"] is True
    }
    assert DEFAULT_METHODS <= server_default
    assert set(WRAPPER_METHODS.values()) == DEFAULT_METHODS


def test_rpc_injects_scope_and_bearer_token() -> None:
    transport = MockTransport()
    client = HarnessOSClient(
        base_url="http://localhost:8000",
        capability_token="cap-secret-token",
        scope=Scope(app_id="meeting", project_id="p1", workspace_id="w1"),
        transport=transport,
    )
    assert client.session_start(model="demo") == {"ok": True}
    payload, headers = transport.requests[0]
    assert payload["method"] == "session.start"
    assert payload["params"]["scope"] == {"app_id": "meeting", "project_id": "p1", "workspace_id": "w1"}
    assert headers["Authorization"] == "Bearer cap-secret-token"
    assert "cap-secret-token" not in repr(client)


def test_scope_override_same_allowed_and_conflict_rejected() -> None:
    transport = MockTransport()
    client = HarnessOSClient(base_url="http://localhost:8000", scope=Scope(app_id="meeting"), transport=transport)
    client.session_start(scope=Scope(app_id="meeting"))
    with pytest.raises(ScopeMismatchError):
        client.session_start(scope=Scope(app_id="knowledge"))


def test_low_level_rpc_rejects_forbidden_and_unknown_methods() -> None:
    client = HarnessOSClient(base_url="http://localhost:8000", transport=MockTransport())
    for method in ("meeting.process_recording", "pack.execute_stub", "workflow.execute_stub", "method.list"):
        with pytest.raises(MethodForbiddenError):
            client.rpc(method, {})


def test_response_shape_and_typed_error_mapping() -> None:
    with pytest.raises(TransportError):
        HarnessOSClient(base_url="http://localhost:8000", transport=MockTransport({"result": {}, "error": {"code": "INVALID_PARAMS"}})).session_start()
    with pytest.raises(TransportError):
        HarnessOSClient(base_url="http://localhost:8000", transport=MockTransport({"id": "x"})).session_start()
    with pytest.raises(AuthRequiredError):
        HarnessOSClient(
            base_url="http://localhost:8000",
            transport=MockTransport({"error": {"code": "AUTH_REQUIRED", "message": "missing bearer secret-token", "data": {"token": "abc"}}}),
        ).session_start()
    with pytest.raises(EventCursorInvalidError):
        HarnessOSClient(
            base_url="http://localhost:8000",
            transport=MockTransport({"error": {"code": "EVENT_CURSOR_INVALID", "message": "bad cursor"}}),
        ).events_subscribe(channels=["chat"])


def test_transport_error_redacts_tokens_in_string() -> None:
    client = HarnessOSClient(base_url="http://localhost:8000", capability_token="secret-token", transport=FailingTransport())
    with pytest.raises(TransportError) as exc:
        client.session_start()
    assert "secret-token" not in str(exc.value)


def test_event_subscription_url_normalization_and_repr_redaction() -> None:
    relative = EventSubscription.from_result(
        {
            "subscription_id": "sub_1",
            "transport": "eventsource",
            "eventsource_url": "/v1/events/subscribe?subscription_token=sub-secret&channels=chat",
            "subscription_token": "sub-secret",
            "replay_cursor": "cursor",
            "expires_at": "2026-05-11T00:00:00+00:00",
            "allowed_channels": ["chat"],
        },
        base_url="http://localhost:8000",
    )
    assert relative.eventsource_url.startswith("http://localhost:8000/v1/events/subscribe")
    assert relative.allowed_channels == ("chat",)
    assert relative.replay_cursor == "cursor"
    assert "sub-secret" not in repr(relative)
    assert "subscription_token=%5BREDACTED%5D" in repr(relative)

    absolute = EventSubscription.from_result(
        {
            "subscription_id": "sub_2",
            "transport": "eventsource",
            "eventsource_url": "https://example.test/events?subscription_token=abc",
            "subscription_token": "abc",
            "replay_cursor": "cursor",
        },
        base_url="http://localhost:8000",
    )
    assert absolute.eventsource_url == "https://example.test/events?subscription_token=abc"


def test_sdk_approval_respond_idempotency_conflict_and_nested_scope(monkeypatch, tmp_path: Path) -> None:
    client, gateway = _sdk(monkeypatch, tmp_path, capabilities=("approvals", "events", "turns", "artifacts", "jobs"))
    approval = gateway.approval_store.request(
        action="publish",
        request_summary="Publish",
        app_id="meeting",
    )
    scoped = Scope(app_id="meeting")

    approved = client.approval_respond(approval_id=approval["approval_id"], decision="approve", reason="ok", scope=scoped)
    assert approved["status"] == "approved"
    assert approved["idempotent"] is False

    repeated = client.approval_respond(approval_id=approval["approval_id"], decision="approve", scope=scoped)
    assert repeated["idempotent"] is True

    with pytest.raises(ApprovalConflictError):
        client.approval_respond(approval_id=approval["approval_id"], decision="reject", scope=scoped)

    reject = gateway.approval_store.request(action="reject", request_summary="Reject", app_id="meeting")
    rejected = client.approval_respond(approval_id=reject["approval_id"], decision="reject", scope={"app_id": "meeting"})
    assert rejected["status"] == "rejected"
    repeated_reject = client.approval_respond(approval_id=reject["approval_id"], decision="reject", scope={"app_id": "meeting"})
    assert repeated_reject["idempotent"] is True


def test_sdk_events_subscribe_integration(monkeypatch, tmp_path: Path) -> None:
    client, _ = _sdk(monkeypatch, tmp_path, capabilities=("events", "turns", "artifacts", "jobs", "approvals"))
    subscription = client.events_subscribe(channels=["chat"])
    assert subscription.eventsource_url.startswith("http://testserver/v1/events/subscribe")
    assert subscription.allowed_channels == ("chat",)
    assert subscription.expires_at
    assert subscription.replay_cursor
    assert subscription.subscription_token
    assert subscription.subscription_token not in repr(subscription)


def test_non_json_transport_response_maps_to_transport_error() -> None:
    class BadTransport:
        def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> Any:
            return json.loads("[]")

    client = HarnessOSClient(base_url="http://localhost:8000", transport=BadTransport())
    with pytest.raises(TransportError):
        client.session_start()


def test_async_sdk_session_events_and_error_mapping() -> None:
    async def run() -> None:
        transport = AsyncMockTransport(
            [
                {"id": "1", "result": {"session_id": "sess_async"}},
                {
                    "id": "2",
                    "result": {
                        "subscription_id": "sub_async",
                        "transport": "eventsource",
                        "eventsource_url": "/v1/events/subscribe?subscription_token=sub-secret",
                        "subscription_token": "sub-secret",
                        "replay_cursor": "cursor_async",
                        "expires_at": "2026-05-11T00:00:00+00:00",
                        "allowed_channels": ["chat"],
                    },
                },
                {"id": "3", "error": {"code": "AUTH_REQUIRED", "message": "missing bearer secret-token"}},
            ]
        )
        client = HarnessOSAsyncClient(
            base_url="http://localhost:8000",
            capability_token="cap-secret-token",
            scope=Scope(app_id="meeting"),
            transport=transport,
        )
        session = await client.session_start()
        assert session["session_id"] == "sess_async"
        subscription = await client.events_subscribe(channels=["chat"])
        assert subscription.eventsource_url.startswith("http://localhost:8000/v1/events/subscribe")
        assert "sub-secret" not in repr(subscription)
        assert "cap-secret-token" not in repr(client)
        with pytest.raises(AuthRequiredError) as exc:
            await client.session_start()
        assert "secret-token" not in str(exc.value)

    import asyncio

    asyncio.run(run())
