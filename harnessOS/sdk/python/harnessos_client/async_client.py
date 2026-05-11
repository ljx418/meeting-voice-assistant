"""Async Python SDK client.

The MVP async client delegates to a caller-provided async transport. It mirrors
the sync public surface only where a transport is supplied by tests or BFF code.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol
from uuid import uuid4

from .client import HarnessOSClient
from .models import CapabilityToken, EventSubscription, Scope


class AsyncJsonRpcTransport(Protocol):
    async def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        ...


class HarnessOSAsyncClient(HarnessOSClient):
    """Thin async JSON-RPC client."""

    def __init__(
        self,
        *,
        base_url: str,
        capability_token: str | CapabilityToken | None = None,
        scope: Scope | dict[str, Any] | None = None,
        timeout: float = 30.0,
        transport: Optional[AsyncJsonRpcTransport] = None,
    ) -> None:
        if transport is None:
            raise TypeError("HarnessOSAsyncClient requires an async transport in V3.5-D")
        super().__init__(base_url=base_url, capability_token=capability_token, scope=scope, timeout=timeout, transport=None)
        self._async_transport = transport

    async def rpc(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:  # type: ignore[override]
        self._ensure_allowed_method(method)
        payload_params = self._with_scope(params or {})
        request = {
            "id": f"sdk_{uuid4().hex}",
            "method": method,
            "params": payload_params,
        }
        headers = {}
        if self._capability_token:
            headers["Authorization"] = f"Bearer {self._capability_token}"
        response = await self._async_transport.request(request, headers=headers, timeout=self.timeout)
        return self._parse_response(response)

    async def session_start(self, *, model: Optional[str] = None, scope: Scope | dict[str, Any] | None = None) -> dict[str, Any]:  # type: ignore[override]
        return await self.rpc("session.start", self._params({"model": model}, scope=scope))

    async def events_subscribe(  # type: ignore[override]
        self,
        *,
        channels: Optional[list[str]] = None,
        mode: Optional[str] = None,
        session_id: Optional[str] = None,
        job_id: Optional[str] = None,
        artifact_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        scope: Scope | dict[str, Any] | None = None,
    ) -> EventSubscription:
        result = await self.rpc(
            "events.subscribe",
            self._params(
                {
                    "channels": channels,
                    "mode": mode,
                    "session_id": session_id,
                    "job_id": job_id,
                    "artifact_id": artifact_id,
                    "approval_id": approval_id,
                    "trace_id": trace_id,
                    "ttl_seconds": ttl_seconds,
                },
                scope=scope,
            ),
        )
        return EventSubscription.from_result(result, base_url=self.base_url)
