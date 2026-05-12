"""V3.5-F Full BFF Template E2E smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = ROOT / "sdk/python"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from harnessos_client import EventSubscription
from templates.bff.fastapi.app import create_app


CONFIG = {
    "demo_identity_mode": True,
    "harnessos_capability_token": "server-side-placeholder-token",
    "identity_scope": {"app_id": "reference_app", "project_id": "demo", "workspace_id": "local"},
    "demo_capabilities": [
        "sessions",
        "turns",
        "events",
        "artifacts.read",
        "artifacts.write",
        "jobs",
        "approvals",
        "packs.read",
        "connectors.read",
    ],
}


class FakeSdkClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def session_start(self, *, model=None, scope=None):
        self.calls.append(("session_start", {"model": model, "scope": _scope(scope)}))
        return {"session_id": "sess_demo", "scope": _scope(scope)}

    def turn_start(self, *, input, session_id=None, domain=None, scope=None):
        self.calls.append(("turn_start", {"input": input, "session_id": session_id, "domain": domain, "scope": _scope(scope)}))
        return {"turn_id": "turn_demo", "session_id": session_id or "sess_demo", "scope": _scope(scope)}

    def artifact_list(self, *, session_id=None, kind=None, scope=None):
        self.calls.append(("artifact_list", {"session_id": session_id, "kind": kind, "scope": _scope(scope)}))
        return {"artifacts": [], "count": 0}

    def artifact_register_external(self, *, kind, external_asset_uri, scope=None):
        self.calls.append(("artifact_register_external", {"kind": kind, "external_asset_uri": external_asset_uri, "scope": _scope(scope)}))
        return {"artifact": {"artifact_id": "art_ext", "kind": kind}, "scope": _scope(scope)}

    def artifact_read_metadata(self, *, artifact_id, scope=None):
        self.calls.append(("artifact_read_metadata", {"artifact_id": artifact_id, "scope": _scope(scope)}))
        return {"artifact_id": artifact_id, "metadata": {}}

    def artifact_lineage(self, *, artifact_id=None, session_id=None, scope=None):
        self.calls.append(("artifact_lineage", {"artifact_id": artifact_id, "session_id": session_id, "scope": _scope(scope)}))
        return {"artifacts": [], "edges": [], "roots": [], "leaves": [], "count": 0}

    def job_list(self, *, session_id=None, status=None, scope=None):
        self.calls.append(("job_list", {"session_id": session_id, "status": status, "scope": _scope(scope)}))
        return {"jobs": [], "count": 0}

    def job_get(self, *, job_id, scope=None):
        self.calls.append(("job_get", {"job_id": job_id, "scope": _scope(scope)}))
        return {"job_id": job_id, "status": "completed"}

    def approval_respond(self, *, approval_id, decision, reason=None, scope=None):
        self.calls.append(("approval_respond", {"approval_id": approval_id, "decision": decision, "reason": reason, "scope": _scope(scope)}))
        return {"approval": {"approval_id": approval_id}, "status": "approved", "idempotent": False}

    def connector_health(self, *, connector_id):
        self.calls.append(("connector_health", {"connector_id": connector_id}))
        return {"connector": {"connector_id": connector_id}, "health": {"status": "ok"}}

    def pack_list(self):
        self.calls.append(("pack_list", {}))
        return {"packs": [], "count": 0}

    def pack_get(self, *, app_id=None, pack_id=None):
        self.calls.append(("pack_get", {"app_id": app_id, "pack_id": pack_id}))
        return {"pack": {"pack_id": pack_id or app_id or "reference_app"}}

    def rpc(self, method, params):
        self.calls.append(("rpc", {"method": method, "params": params}))
        return {"method": method, "params": params}

    def events_subscribe(self, *, channels=None, scope=None):
        self.calls.append(("events_subscribe", {"channels": channels, "scope": _scope(scope)}))
        return EventSubscription(
            subscription_id="sub_demo",
            transport="eventsource",
            eventsource_url="http://upstream.local/v1/events/subscribe?subscription_token=sub-secret",
            subscription_token="sub-secret",
            replay_cursor="cursor_demo",
            allowed_channels=tuple(channels or ("chat",)),
        )


class FakeUpstream:
    def __init__(self) -> None:
        self.url = ""
        self.closed = False
        self.frames = [
            b"id: upstream_cursor_1\n",
            b"event: job.running\n",
            b"data: {\"event_id\":\"evt_1\"}\n\n",
        ]

    def __iter__(self):
        return iter(self.frames)

    def close(self) -> None:
        self.closed = True


def _client(config: dict[str, Any] | None = None) -> tuple[TestClient, FakeSdkClient, FakeUpstream]:
    sdk = FakeSdkClient()
    upstream = FakeUpstream()

    def opener(url: str):
        upstream.url = url
        return upstream

    app = create_app(config={**CONFIG, **(config or {})}, sdk_client=sdk, upstream_opener=opener)
    return TestClient(app), sdk, upstream


def test_config_error_blocks_proxy_but_not_health() -> None:
    app = create_app(config={"demo_identity_mode": True})
    client = TestClient(app)
    assert client.get("/bff/health").json()["status"] == "degraded"
    response = client.post("/bff/sessions", json={})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_NOT_CONFIGURED"


def test_demo_identity_mode_adds_warning_header() -> None:
    client, _, _ = _client()
    response = client.get("/bff/health")
    assert response.headers["X-HarnessOS-BFF-Warning"].startswith("demo identity mode")


def test_identity_route_body_scope_binding_and_scope_expansion_rejection() -> None:
    client, sdk, _ = _client()
    ok = client.post(
        "/bff/sessions?app_id=reference_app&project_id=demo&workspace_id=local",
        json={"scope": {"app_id": "reference_app", "project_id": "demo", "workspace_id": "local"}},
    )
    assert ok.status_code == 200
    assert ok.json()["scope"]["app_id"] == "reference_app"
    assert sdk.calls[-1][0] == "session_start"

    route_conflict = client.post("/bff/sessions?app_id=other_app", json={})
    assert route_conflict.status_code == 403
    assert route_conflict.json()["error"]["code"] == "SCOPE_MISMATCH"

    body_conflict = client.post("/bff/sessions", json={"scope": {"app_id": "other_app"}})
    assert body_conflict.status_code == 403
    assert body_conflict.json()["error"]["code"] == "SCOPE_MISMATCH"


def test_bff_side_capability_policy_and_artifact_write_capability() -> None:
    client, _, _ = _client()
    denied = client.post("/bff/artifacts/external", headers={"x-demo-capabilities": "artifacts.read"}, json={"kind": "note", "external_asset_uri": "file:///tmp/a.txt"})
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "CAPABILITY_DENIED"

    ok = client.post(
        "/bff/artifacts/external",
        headers={"x-demo-capabilities": "artifacts.read,artifacts.write"},
        json={"kind": "note", "external_asset_uri": "file:///tmp/a.txt"},
    )
    assert ok.status_code == 200
    assert ok.json()["artifact"]["artifact_id"] == "art_ext"


def test_bff_rpc_allowlist_and_events_subscribe_denied() -> None:
    client, sdk, _ = _client()
    allowed = client.post("/bff/rpc", json={"method": "session.start", "params": {}})
    assert allowed.status_code == 200
    assert allowed.json()["method"] == "session.start"
    assert sdk.calls[-1][0] == "rpc"

    for method in (
        "events.subscribe",
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


def test_structured_routes_cover_default_template_surface() -> None:
    client, sdk, _ = _client()
    assert client.post("/bff/sessions", json={"model": "demo"}).status_code == 200
    assert client.post("/bff/turns", json={"input": "hello", "session_id": "sess_demo"}).status_code == 200
    assert client.get("/bff/artifacts").status_code == 200
    assert client.post("/bff/artifacts/external", json={"kind": "note", "external_asset_uri": "file:///tmp/a.txt"}).status_code == 200
    assert client.get("/bff/artifacts/art_1/metadata").status_code == 200
    assert client.get("/bff/artifacts/art_1/lineage").status_code == 200
    assert client.get("/bff/jobs").status_code == 200
    assert client.get("/bff/jobs/job_1").status_code == 200
    assert client.post("/bff/approvals/appr_1/respond", json={"decision": "approve"}).status_code == 200
    assert client.get("/bff/packs").status_code == 200
    assert client.get("/bff/packs/reference_pack").status_code == 200
    assert client.get("/bff/connectors/dummy_connector/health").status_code == 200
    assert [call[0] for call in sdk.calls] == [
        "session_start",
        "turn_start",
        "artifact_list",
        "artifact_register_external",
        "artifact_read_metadata",
        "artifact_lineage",
        "job_list",
        "job_get",
        "approval_respond",
        "pack_list",
        "pack_get",
        "connector_health",
    ]


def test_eventsource_proxy_hides_token_and_propagates_last_event_id() -> None:
    client, sdk, upstream = _client()
    response = client.get("/bff/events/subscribe?channels=job&cursor=query_cursor", headers={"Last-Event-ID": "last_cursor"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "id: upstream_cursor_1" in response.text
    assert "event: job.running" in response.text
    assert "sub-secret" not in response.text
    assert "subscription_token=sub-secret" in upstream.url
    assert "cursor=last_cursor" in upstream.url
    assert "cursor=query_cursor" not in upstream.url
    assert upstream.closed is True
    assert sdk.calls[-1][0] == "events_subscribe"


def test_eventsource_scope_failure_does_not_open_stream() -> None:
    client, _, upstream = _client()
    response = client.get("/bff/events/subscribe?app_id=other_app")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "SCOPE_MISMATCH"
    assert upstream.url == ""


def test_secret_redaction_in_error_response() -> None:
    class FailingSdk(FakeSdkClient):
        def rpc(self, method, params):
            raise RuntimeError("failed Authorization: Bearer cap-secret-token subscription_token=sub-secret http://x/events?subscription_token=sub-secret")

    app = create_app(config=CONFIG, sdk_client=FailingSdk(), upstream_opener=lambda url: FakeUpstream())
    response = TestClient(app).post("/bff/rpc", json={"method": "session.start", "params": {}})
    assert response.status_code == 400
    assert "cap-secret-token" not in response.text
    assert "sub-secret" not in response.text
    assert "[REDACTED]" in response.text


def _scope(scope: Any) -> dict[str, Any]:
    if hasattr(scope, "to_dict"):
        return scope.to_dict()
    return dict(scope or {})
