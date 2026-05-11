"""V3.5-B external API auth guard tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.service import GatewayService
from core.apps.profiles import AppProfile
from core.protocol.auth import issue_capability_token


SECRET = "phase-b-api-secret"
LOCAL_ORIGIN = "http://localhost:5173"


def _client(monkeypatch, gateway: GatewayService | None = None) -> TestClient:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    return TestClient(create_app(gateway_service=gateway or GatewayService()))


def _token(gateway: GatewayService, app_id: str = "meeting", *, capabilities: tuple[str, ...] | None = None) -> str:
    profile = gateway.app_registry.get(app_id)
    return issue_capability_token(
        app_profile=profile,
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )


def _headers(token: str, origin: str = LOCAL_ORIGIN) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Origin": origin}


def test_external_http_requires_token_and_dev_mode_is_explicit(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)

    missing = client.post("/v1/runs", json={"input": "你好"})
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "AUTH_REQUIRED"

    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    allowed = client.post("/v1/runs", json={"input": "你好"}, headers={"Origin": LOCAL_ORIGIN})
    assert allowed.status_code == 200
    assert allowed.headers["X-HarnessOS-Auth-Warning"] == "dev-mode-no-token"

    denied = client.post("/v1/runs", json={"input": "你好"}, headers={"Origin": "https://example.com"})
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "AUTH_FORBIDDEN"
    assert denied.json()["error"]["data"]["reason"] == "dev_mode_non_local_origin"


def test_token_origin_scope_and_capability_are_enforced(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("turns", "sessions"))

    origin_denied = client.post("/v1/runs", json={"input": "你好"}, headers=_headers(token, "http://localhost:3000"))
    assert origin_denied.status_code == 403
    assert origin_denied.json()["error"]["code"] == "AUTH_FORBIDDEN"

    scope_denied = client.post(
        "/v1/runs",
        json={"input": "你好", "scope": {"app_id": "knowledge"}},
        headers=_headers(token),
    )
    assert scope_denied.status_code == 403
    assert scope_denied.json()["error"]["code"] == "SCOPE_MISMATCH"

    missing_cap = client.post(
        "/v1/rpc",
        json={"id": "pack", "method": "pack.list", "params": {}},
        headers=_headers(token),
    )
    assert missing_cap.status_code == 200
    assert missing_cap.json()["error"]["code"] == "CAPABILITY_DENIED"


def test_request_without_scope_inherits_token_scope_and_resource_scope_is_checked(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)
    meeting_token = _token(gateway, "meeting", capabilities=("turns", "sessions"))
    knowledge_token = _token(gateway, "knowledge", capabilities=("sessions",))

    created = client.post("/v1/runs", json={"input": "你好"}, headers=_headers(meeting_token))
    assert created.status_code == 200
    assert created.json()["app_id"] == "meeting"
    session_id = created.json()["session_id"]

    same_scope = client.get(f"/v1/sessions/{session_id}", headers=_headers(meeting_token))
    assert same_scope.status_code == 200

    cross_scope = client.get(f"/v1/sessions/{session_id}", headers=_headers(knowledge_token))
    assert cross_scope.status_code == 403
    assert cross_scope.json()["error"]["code"] == "SCOPE_MISMATCH"


def test_nested_scope_conflict_and_scope_mode_all_are_rejected(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("turns", "sessions", "rpc"))

    conflict = client.post(
        "/v1/runs",
        json={"input": "你好", "app_id": "meeting", "scope": {"app_id": "knowledge"}},
        headers=_headers(token),
    )
    assert conflict.status_code == 403
    assert conflict.json()["error"]["code"] == "SCOPE_MISMATCH"

    scope_all = client.post(
        "/v1/rpc",
        json={"id": "all", "method": "session.list", "params": {"scope_mode": "all"}},
        headers=_headers(token),
    )
    assert scope_all.status_code == 200
    assert scope_all.json()["error"]["code"] == "METHOD_FORBIDDEN"


def test_method_list_include_forbidden_requires_admin_capability(monkeypatch) -> None:
    gateway = GatewayService()
    gateway.app_registry.register(
        AppProfile(
            app_id="admin_app",
            display_name="Admin",
            domain="admin",
            default_pack="admin",
            allowed_origins=(LOCAL_ORIGIN,),
            default_capabilities=("rpc", "admin"),
        )
    )
    client = _client(monkeypatch, gateway)
    normal = _token(gateway, capabilities=("rpc",))
    admin = _token(gateway, "admin_app", capabilities=("rpc", "admin"))

    denied = client.post(
        "/v1/rpc",
        json={"id": "methods", "method": "method.list", "params": {"include_forbidden": True}},
        headers=_headers(normal),
    )
    assert denied.json()["error"]["code"] == "METHOD_FORBIDDEN"

    allowed = client.post(
        "/v1/rpc",
        json={"id": "methods", "method": "method.list", "params": {"include_forbidden": True}},
        headers=_headers(admin),
    )
    assert allowed.json()["error"] is None
    methods = {entry["method"]: entry for entry in allowed.json()["result"]["methods"]}
    assert methods["meeting.process_recording"]["surface"] == "forbidden_by_default"


def test_legacy_debug_routes_are_not_exposed_without_admin_auth(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)
    token = _token(gateway, capabilities=("sessions",))

    missing = client.get("/api/agents/types")
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "AUTH_REQUIRED"

    denied = client.get("/api/agents/types", headers=_headers(token))
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "METHOD_FORBIDDEN"

    routing = client.post("/api/routing/intent", json={"user_input": "hello"}, headers=_headers(token))
    assert routing.status_code == 403
    assert routing.json()["error"]["code"] == "METHOD_FORBIDDEN"


def test_runs_stream_rejects_before_opening_stream(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)
    response = client.post("/v1/runs/stream", json={"input": "你好"})
    assert response.status_code == 401
    assert "text/event-stream" not in response.headers.get("content-type", "")
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_auth_errors_redact_token_strings(monkeypatch) -> None:
    gateway = GatewayService()
    client = _client(monkeypatch, gateway)
    token = "secret-token-value"
    response = client.post(
        "/v1/runs",
        json={"input": "你好"},
        headers={"Authorization": f"Bearer {token}", "Origin": LOCAL_ORIGIN},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_INVALID"
    assert token not in response.text
