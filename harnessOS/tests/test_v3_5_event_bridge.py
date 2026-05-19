"""V3.5-C Browser Event Bridge contract tests."""

from __future__ import annotations

import asyncio
import json
from urllib.parse import urlsplit

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.api.routers.events import _collect_unsent_events
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.apps.profiles import AppProfile
from core.apps.scope import ScopeContext
from core.protocol.auth import issue_capability_token
from core.protocol.event_bridge import collect_event_envelopes, read_event_cursor
from core.protocol.schemas.events import EVENT_SCHEMAS


SECRET = "phase-c-event-secret"
LOCAL_ORIGIN = "http://localhost:5173"


def _gateway(tmp_path) -> GatewayService:
    runtime = GatewayRuntimePool(
        store=GatewaySessionStore(tmp_path / "sessions"),
        artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
    )
    return GatewayService(runtime_pool=runtime)


def _client(monkeypatch, gateway: GatewayService) -> TestClient:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    return TestClient(create_app(gateway_service=gateway))


def _token(gateway: GatewayService, *, capabilities: tuple[str, ...], app_id: str = "meeting", ttl_seconds: int = 3600) -> str:
    return issue_capability_token(
        app_profile=gateway.app_registry.get(app_id),
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        ttl_seconds=ttl_seconds,
        secret=SECRET,
    )


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Origin": LOCAL_ORIGIN}


def _rpc(client: TestClient, token: str, method: str, params: dict) -> dict:
    response = client.post("/v1/rpc", json={"id": method, "method": method, "params": params}, headers=_headers(token))
    assert response.status_code == 200
    return response.json()


def _sse_events(body: str) -> list[dict]:
    events = []
    for frame in body.strip().split("\n\n"):
        data_lines = [line.removeprefix("data: ") for line in frame.splitlines() if line.startswith("data: ")]
        if data_lines:
            events.append(json.loads("".join(data_lines)))
    return events


def _assert_event_matches_schema(event: dict, *, event_type: str, channel: str) -> None:
    schema = next(item for item in EVENT_SCHEMAS if item["type"] == event_type)
    required = set(schema["envelope_schema"]["required"])
    assert required <= set(event)
    assert event["type"] == event_type
    assert event["channel"] == channel
    assert isinstance(event["event_id"], str)
    assert isinstance(event["cursor"], str)
    assert isinstance(event["timestamp"], str)
    assert isinstance(event["scope"], dict)
    assert isinstance(event["data"], dict)


def test_events_subscribe_returns_signed_url_and_native_eventsource_needs_no_authorization(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "turns", "artifacts"))

    artifact = _rpc(
        client,
        token,
        "artifact.register_external",
        {
            "kind": "note",
            "external_asset_uri": "file:///tmp/a.txt",
            "metadata": {
                "capability_token": "cap-secret-token",
                "Authorization": "Bearer cap-secret-token",
                "raw_artifact_content": "raw content",
            },
            "scope": {"app_id": "meeting"},
        },
    )
    assert artifact.get("error") is None

    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["artifact"]})
    assert subscribed.get("error") is None
    result = subscribed["result"]
    assert set(result) >= {"eventsource_url", "subscription_token", "replay_cursor", "expires_at", "allowed_channels"}
    assert result["allowed_channels"] == ["artifact"]

    native = client.get(result["eventsource_url"] + "&follow=0")
    assert native.status_code == 200
    assert native.headers["content-type"].startswith("text/event-stream")
    events = _sse_events(native.text)
    assert events
    assert events[0]["type"] == "artifact.registered"
    assert events[0]["channel"] == "artifact"
    assert events[0]["scope"]["app_id"] == "meeting"
    assert result["subscription_token"] not in native.text
    assert "cap-secret-token" not in native.text
    assert "Authorization" not in native.text
    assert "raw_artifact_content" not in native.text


def test_fetch_stream_mode_accepts_bearer_token(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "turns"))

    response = client.get("/v1/events/subscribe?channels=chat&follow=0", headers=_headers(token))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")


def test_subscription_token_tamper_expiry_scope_and_channel_limits(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "turns"))

    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["chat"]})["result"]
    tampered = subscribed["eventsource_url"].replace("a", "b", 1)
    assert client.get(tampered + "&follow=0").json()["error"]["code"] == "SUBSCRIPTION_TOKEN_INVALID"

    scoped = client.get(subscribed["eventsource_url"] + "&app_id=knowledge&follow=0")
    assert scoped.status_code == 403
    assert scoped.json()["error"]["code"] == "SUBSCRIPTION_TOKEN_SCOPE_MISMATCH"

    channel = client.get(subscribed["eventsource_url"] + "&channels=job&follow=0")
    assert channel.status_code == 403
    assert channel.json()["error"]["code"] == "SUBSCRIPTION_TOKEN_CHANNEL_DENIED"

    expired_token = _token(gateway, capabilities=("events", "turns"), ttl_seconds=-1)
    expired = client.post(
        "/v1/rpc",
        json={"id": "events", "method": "events.subscribe", "params": {"channels": ["chat"]}},
        headers=_headers(expired_token),
    )
    assert expired.json()["error"]["code"] == "AUTH_INVALID"


def test_event_envelopes_match_schema_shape_and_dedupe(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "artifacts"))
    for index in range(2):
        _rpc(
            client,
            token,
            "artifact.register_external",
            {"kind": "note", "external_asset_uri": f"file:///tmp/{index}.txt", "scope": {"app_id": "meeting"}},
        )

    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["artifact"]})["result"]
    events = _sse_events(client.get(subscribed["eventsource_url"] + "&follow=0").text)
    event_types = {schema["type"] for schema in EVENT_SCHEMAS}
    assert len({event["event_id"] for event in events}) == len(events)
    for event in events:
        assert event["type"] in event_types
        assert event["channel"] == "artifact"
        assert {"event_id", "type", "channel", "cursor", "timestamp", "scope", "data"} <= set(event)


def test_job_approval_trace_and_artifact_blocked_envelopes_match_schemas(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    base_profile = gateway.app_registry.get("meeting")
    gateway.app_registry.register(
        AppProfile(
            app_id=base_profile.app_id,
            display_name=base_profile.display_name,
            domain=base_profile.domain,
            default_pack=base_profile.default_pack,
            connector_refs=base_profile.connector_refs,
            allowed_origins=base_profile.allowed_origins,
            default_capabilities=(*base_profile.default_capabilities, "traces.read"),
            embed_policy=base_profile.embed_policy,
        )
    )
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "artifacts", "jobs", "approvals", "traces.read"))
    scope = ScopeContext(app_id="meeting")

    job = gateway.core_service.create_job(workflow_id="reference.workflow", scope=scope)
    gateway.core_service.update_job(job_id=job.job_id, status="running", progress=0.5)
    gateway.core_service.update_job(job_id=job.job_id, status="completed", progress=1.0)

    approval = gateway.approval_store.request(action="publish", request_summary="Publish", app_id="meeting")
    pending = gateway.approval_store.request(action="review", request_summary="Review", app_id="meeting")
    _rpc(
        client,
        token,
        "approval.respond",
        {"approval_id": approval["approval_id"], "decision": "approve", "scope": {"app_id": "meeting"}},
    )

    trace = gateway.trace_store.record_artifact_operation(
        operation="list",
        artifact={"artifact_id": "art_trace", "app_id": "meeting", "name": "trace"},
    )
    gateway.core_service.record_gateway_trace(trace)

    registered = _rpc(
        client,
        token,
        "artifact.register_external",
        {
            "kind": "recording",
            "mime": "video/mp4",
            "external_asset_uri": "file:///tmp/clip.mp4",
            "scope": {"app_id": "meeting"},
        },
    )["result"]["artifact"]
    blocked = asyncio.run(
        gateway.handle_rpc(
            RpcRequest(
                id="blocked",
                method="artifact.read",
                params={"artifact_id": registered["artifact_id"], "scope": {"app_id": "meeting"}},
            )
        )
    )
    assert blocked.error is not None
    assert blocked.error.code == "ARTIFACT_READ_BLOCKED"

    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["job", "approval", "trace", "artifact"]})["result"]
    events = _sse_events(client.get(subscribed["eventsource_url"] + "&follow=0").text)
    by_type = {event["type"]: event for event in events}

    _assert_event_matches_schema(by_type["job.running"], event_type="job.running", channel="job")
    _assert_event_matches_schema(by_type["job.completed"], event_type="job.completed", channel="job")
    _assert_event_matches_schema(by_type["approval.approved"], event_type="approval.approved", channel="approval")
    assert "approval.required" in by_type
    assert by_type["approval.required"]["approval_id"] == pending["approval_id"]
    _assert_event_matches_schema(by_type["approval.required"], event_type="approval.required", channel="approval")
    _assert_event_matches_schema(by_type["trace.recorded"], event_type="trace.recorded", channel="trace")
    _assert_event_matches_schema(by_type["artifact.read_blocked"], event_type="artifact.read_blocked", channel="artifact")
    assert "artifact.created" not in by_type


def test_last_event_id_takes_precedence_over_query_cursor(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "artifacts"))
    for index in range(2):
        _rpc(
            client,
            token,
            "artifact.register_external",
            {"kind": "note", "external_asset_uri": f"file:///tmp/cursor-{index}.txt", "scope": {"app_id": "meeting"}},
        )
    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["artifact"]})["result"]
    first = _sse_events(client.get(subscribed["eventsource_url"] + "&follow=0").text)
    assert len(first) == 2

    query_cursor = first[0]["cursor"]
    last_event_id = first[1]["cursor"]
    response = client.get(
        subscribed["eventsource_url"] + f"&follow=0&cursor={query_cursor}",
        headers={"Last-Event-ID": last_event_id},
    )
    assert _sse_events(response.text) == []


def test_cursor_scope_mismatch_and_invalid_cursor(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "artifacts"))
    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["artifact"]})["result"]

    invalid = client.get(subscribed["eventsource_url"] + "&cursor=not-a-cursor&follow=0")
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "EVENT_CURSOR_INVALID"

    other_scope = gateway.app_registry.get("knowledge")
    other_token = issue_capability_token(
        app_profile=other_scope,
        capabilities=("events", "artifacts"),
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )
    other_sub = _rpc(client, other_token, "events.subscribe", {"channels": ["artifact"]})["result"]
    mismatch = client.get(subscribed["eventsource_url"] + f"&cursor={other_sub['replay_cursor']}&follow=0")
    assert mismatch.status_code == 403
    assert mismatch.json()["error"]["code"] == "SCOPE_MISMATCH"


def test_heartbeat_is_streamed_but_not_persisted(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "turns"))
    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["chat"]})["result"]

    response = client.get(subscribed["eventsource_url"] + "&follow=1&heartbeat_interval=0.01&max_heartbeats=1")
    assert response.status_code == 200
    assert ": heartbeat" in response.text
    assert "data:" not in response.text

    scope = gateway._resolve_request_scope({"scope": {"app_id": "meeting"}})
    assert collect_event_envelopes(gateway, scope=scope, channels=["chat"]) == []


def test_follow_stream_collects_events_created_after_subscription(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "artifacts"))
    scope = gateway._resolve_request_scope({"scope": {"app_id": "meeting"}})
    start_sequence = read_event_cursor(None, scope)
    sent_keys: set[tuple[str, str]] = set()

    events, last_sequence = _collect_unsent_events(
        gateway,
        scope=scope,
        channels=["artifact"],
        filters={},
        last_sequence=start_sequence,
        sent_keys=sent_keys,
    )
    assert events == []
    assert last_sequence == start_sequence

    _rpc(
        client,
        token,
        "artifact.register_external",
        {"kind": "note", "external_asset_uri": "file:///tmp/follow.txt", "scope": {"app_id": "meeting"}},
    )
    events, last_sequence = _collect_unsent_events(
        gateway,
        scope=scope,
        channels=["artifact"],
        filters={},
        last_sequence=last_sequence,
        sent_keys=sent_keys,
    )
    assert [event["type"] for event in events] == ["artifact.registered"]
    assert last_sequence == 0
    repeated, repeated_sequence = _collect_unsent_events(
        gateway,
        scope=scope,
        channels=["artifact"],
        filters={},
        last_sequence=last_sequence,
        sent_keys=sent_keys,
    )
    assert repeated == []
    assert repeated_sequence == last_sequence


def test_subscription_token_origin_is_bound(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "turns"))
    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["chat"]})["result"]

    allowed = client.get(subscribed["eventsource_url"] + "&follow=0", headers={"Origin": LOCAL_ORIGIN})
    assert allowed.status_code == 200
    denied = client.get(subscribed["eventsource_url"] + "&follow=0", headers={"Origin": "https://evil.example"})
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "AUTH_FORBIDDEN"


def test_runs_stream_remains_compatibility_path_and_preauth(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    missing = client.post("/v1/runs/stream", json={"input": "hello"})
    assert missing.status_code == 401
    assert missing.headers["content-type"].startswith("application/json")
    assert missing.json()["error"]["code"] == "AUTH_REQUIRED"


def test_events_subscribe_url_is_path_only(monkeypatch, tmp_path) -> None:
    gateway = _gateway(tmp_path)
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("events", "turns"))
    subscribed = _rpc(client, token, "events.subscribe", {"channels": ["chat"]})["result"]
    parsed = urlsplit(subscribed["eventsource_url"])
    assert parsed.scheme == ""
    assert parsed.netloc == ""
    assert parsed.path == "/v1/events/subscribe"
    assert read_event_cursor(subscribed["replay_cursor"], gateway._resolve_request_scope({"scope": {"app_id": "meeting"}})) == -1
