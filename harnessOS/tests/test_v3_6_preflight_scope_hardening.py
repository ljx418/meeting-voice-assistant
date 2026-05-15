"""V3.6/V4.0 preflight scope hardening tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.apps import ScopeContext
from core.protocol.auth import issue_capability_token


SECRET = "preflight-scope-secret"
LOCAL_ORIGIN = "http://localhost:5173"


def _scope(app_id: str = "meeting", project_id: str = "demo", workspace_id: str = "local") -> dict[str, str]:
    return {"app_id": app_id, "project_id": project_id, "workspace_id": workspace_id}


async def _rpc(service: GatewayService, method: str, params: dict | None = None):
    return await service.handle_rpc(RpcRequest(id=method, method=method, params=params or {}))


def _client(monkeypatch, gateway: GatewayService) -> TestClient:
    monkeypatch.setenv("HARNESS_CAPABILITY_TOKEN_SECRET", SECRET)
    monkeypatch.delenv("HARNESS_V3_5_DEV_MODE", raising=False)
    return TestClient(create_app(gateway_service=gateway))


def _token(gateway: GatewayService, app_id: str, capabilities: tuple[str, ...]) -> str:
    return issue_capability_token(
        app_profile=gateway.app_registry.get(app_id),
        project_id="demo",
        workspace_id="local",
        capabilities=capabilities,
        allowed_origins=(LOCAL_ORIGIN,),
        secret=SECRET,
    )


def _headers(gateway: GatewayService, app_id: str, capabilities: tuple[str, ...]) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(gateway, app_id, capabilities)}", "Origin": LOCAL_ORIGIN}


def test_session_close_and_resume_reject_cross_scope_direct_and_http(monkeypatch) -> None:
    async def run() -> None:
        service = GatewayService()
        started = await _rpc(service, "session.start", {"scope": _scope("meeting")})
        assert started.error is None
        session_id = started.result["session_id"]

        close_cross = await _rpc(service, "session.close", {"session_id": session_id, "scope": _scope("knowledge")})
        assert close_cross.error.code == "SCOPE_MISMATCH"

        resume_cross = await _rpc(service, "session.resume", {"session_id": session_id, "scope": _scope("knowledge")})
        assert resume_cross.error.code == "SCOPE_MISMATCH"

        close_same = await _rpc(service, "session.close", {"session_id": session_id, "scope": _scope("meeting")})
        assert close_same.error is None

        client = _client(monkeypatch, service)
        http_started = await _rpc(service, "session.start", {"scope": _scope("meeting")})
        http_session_id = http_started.result["session_id"]
        response = client.post(
            "/v1/rpc",
            json={"id": "close", "method": "session.close", "params": {"session_id": http_session_id}},
            headers=_headers(service, "knowledge", ("sessions",)),
        )
        assert response.json()["error"]["code"] == "SCOPE_MISMATCH"

    asyncio.run(run())


def test_memory_get_scope_capability_and_legacy_scope_guard(monkeypatch) -> None:
    service = GatewayService()
    memory = service.core_service.create_memory_record(
        session_id="sess_memory",
        scope_context=ScopeContext(app_id="meeting", project_id="demo", workspace_id="local"),
        content="same scope memory",
    )

    same = asyncio.run(_rpc(service, "memory.get", {"memory_id": memory.memory_id, "scope": _scope("meeting")}))
    assert same.error is None

    cross = asyncio.run(_rpc(service, "memory.get", {"memory_id": memory.memory_id, "scope": _scope("knowledge")}))
    assert cross.error.code == "SCOPE_MISMATCH"

    original_get_memory = service.core_service.get_memory

    class LegacyMemory:
        def model_dump(self, mode: str = "json") -> dict[str, str]:
            return {"memory_id": "mem_legacy", "session_id": "sess_legacy"}

    monkeypatch.setattr(service.core_service, "get_memory", lambda memory_id, trace_id=None: LegacyMemory())
    legacy_read = asyncio.run(_rpc(service, "memory.get", {"memory_id": "mem_legacy", "scope": _scope("meeting")}))
    assert legacy_read.error.code == "SCOPE_REQUIRED"
    monkeypatch.setattr(service.core_service, "get_memory", original_get_memory)

    client = _client(monkeypatch, service)
    missing_cap = client.post(
        "/v1/rpc",
        json={"id": "mem", "method": "memory.get", "params": {"memory_id": memory.memory_id}},
        headers=_headers(service, "meeting", ("sessions",)),
    )
    assert missing_cap.json()["error"]["code"] == "CAPABILITY_DENIED"

    cross_http = client.post(
        "/v1/rpc",
        json={"id": "mem", "method": "memory.get", "params": {"memory_id": memory.memory_id}},
        headers=_headers(service, "knowledge", ("memory",)),
    )
    assert cross_http.json()["error"]["code"] == "SCOPE_MISMATCH"
