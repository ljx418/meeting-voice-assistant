"""Synchronous Python SDK client."""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from .errors import MethodForbiddenError, ProtocolError, TransportError, error_from_rpc
from .models import CapabilityToken, EventSubscription, Scope
from .protocol_snapshot import WRAPPER_METHODS, is_default_method, is_forbidden_method
from .transport import JsonRpcTransport, UrllibJsonRpcTransport


class HarnessOSClient:
    """Thin JSON-RPC client for harnessOS V3.5 default protocol surface."""

    def __init__(
        self,
        *,
        base_url: str,
        capability_token: str | CapabilityToken | None = None,
        scope: Scope | dict[str, Any] | None = None,
        timeout: float = 30.0,
        transport: Optional[JsonRpcTransport] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.scope = Scope.from_value(scope) or Scope()
        self._capability_token = capability_token.value if isinstance(capability_token, CapabilityToken) else capability_token
        self._transport = transport or UrllibJsonRpcTransport(f"{self.base_url}/v1/rpc")

    def __repr__(self) -> str:
        token_state = "set" if self._capability_token else "unset"
        return f"HarnessOSClient(base_url={self.base_url!r}, capability_token={token_state}, scope={self.scope!r})"

    def rpc(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Call one allowed default JSON-RPC method."""
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
        response = self._transport.request(request, headers=headers, timeout=self.timeout)
        return self._parse_response(response)

    def session_start(self, *, model: Optional[str] = None, scope: Scope | dict[str, Any] | None = None) -> dict[str, Any]:
        return self.rpc("session.start", self._params({"model": model}, scope=scope))

    def turn_start(
        self,
        *,
        input: str,
        session_id: Optional[str] = None,
        domain: Optional[str] = None,
        scope: Scope | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.rpc("turn.start", self._params({"input": input, "session_id": session_id, "domain": domain}, scope=scope))

    def events_subscribe(
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
        result = self.rpc(
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

    def artifact_list(self, *, session_id: Optional[str] = None, kind: Optional[str] = None, scope: Scope | dict[str, Any] | None = None) -> dict[str, Any]:
        return self.rpc("artifact.list", self._params({"session_id": session_id, "kind": kind}, scope=scope))

    def artifact_read_metadata(self, *, artifact_id: str, scope: Scope | dict[str, Any] | None = None) -> dict[str, Any]:
        return self.rpc("artifact.read_metadata", self._params({"artifact_id": artifact_id}, scope=scope))

    def artifact_register_external(
        self,
        *,
        kind: str,
        external_asset_uri: str,
        scope: Scope | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.rpc("artifact.register_external", self._params({"kind": kind, "external_asset_uri": external_asset_uri}, scope=scope))

    def artifact_lineage(
        self,
        *,
        artifact_id: Optional[str] = None,
        session_id: Optional[str] = None,
        scope: Scope | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.rpc("artifact.lineage", self._params({"artifact_id": artifact_id, "session_id": session_id}, scope=scope))

    def job_get(self, *, job_id: str, scope: Scope | dict[str, Any] | None = None) -> dict[str, Any]:
        return self.rpc("job.get", self._params({"job_id": job_id}, scope=scope))

    def job_list(
        self,
        *,
        session_id: Optional[str] = None,
        status: Optional[str] = None,
        scope: Scope | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.rpc("job.list", self._params({"session_id": session_id, "status": status}, scope=scope))

    def approval_respond(
        self,
        *,
        approval_id: str,
        decision: str,
        reason: Optional[str] = None,
        scope: Scope | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.rpc("approval.respond", self._params({"approval_id": approval_id, "decision": decision, "reason": reason}, scope=scope))

    def connector_health(self, *, connector_id: str) -> dict[str, Any]:
        return self.rpc("connector.health", {"connector_id": connector_id})

    def pack_list(self) -> dict[str, Any]:
        return self.rpc("pack.list", {})

    def pack_get(self, *, app_id: Optional[str] = None, pack_id: Optional[str] = None) -> dict[str, Any]:
        return self.rpc("pack.get", self._clean({"app_id": app_id, "pack_id": pack_id}))

    @property
    def wrapper_methods(self) -> dict[str, str]:
        return dict(WRAPPER_METHODS)

    def _params(self, params: dict[str, Any], *, scope: Scope | dict[str, Any] | None) -> dict[str, Any]:
        payload = self._clean(params)
        override = Scope.from_value(scope)
        if override is not None:
            self.scope.ensure_compatible(override)
            payload["scope"] = override.to_dict()
        return payload

    def _with_scope(self, params: dict[str, Any]) -> dict[str, Any]:
        payload = self._clean(params)
        if "scope" in payload:
            override = Scope.from_value(payload["scope"])
            if override is not None:
                self.scope.ensure_compatible(override)
            return payload
        payload["scope"] = self.scope.to_dict()
        return payload

    def _ensure_allowed_method(self, method: str) -> None:
        if is_forbidden_method(method) or not is_default_method(method):
            raise MethodForbiddenError(
                "METHOD_FORBIDDEN",
                f"method is not part of the SDK default surface: {method}",
                {"method": method},
            )

    @staticmethod
    def _clean(params: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in params.items() if value is not None}

    @staticmethod
    def _parse_response(response: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(response, dict):
            raise TransportError("malformed JSON-RPC response: response must be an object")
        has_result = "result" in response and response.get("result") is not None
        has_error = "error" in response and response.get("error") is not None
        if has_result == has_error:
            raise TransportError("malformed JSON-RPC response: expected exactly one of result or error")
        if has_error:
            error = response.get("error")
            if not isinstance(error, dict):
                raise TransportError("malformed JSON-RPC response: error must be an object")
            raise error_from_rpc(error)
        result = response.get("result")
        if not isinstance(result, dict):
            raise TransportError("malformed JSON-RPC response: result must be an object")
        return result
