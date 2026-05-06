"""Registry-based RPC method routing for the gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional


RpcHandler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


@dataclass(frozen=True)
class RpcMethodSpec:
    """Metadata for one registered RPC method."""

    method: str
    handler: RpcHandler
    capability: Optional[str] = None
    alias_of: Optional[str] = None
    description: str = ""

    def public_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "method": self.method,
            "capability": self.capability,
            "alias_of": self.alias_of,
            "description": self.description,
        }
        return {key: value for key, value in payload.items() if value is not None}


class RpcRouter:
    """Small method registry used by GatewayService transports."""

    def __init__(self) -> None:
        self._methods: Dict[str, RpcMethodSpec] = {}

    def register(
        self,
        method: str,
        handler: RpcHandler,
        *,
        capability: Optional[str] = None,
        alias_of: Optional[str] = None,
        description: str = "",
    ) -> None:
        if method in self._methods:
            raise ValueError(f"RPC method already registered: {method}")
        self._methods[method] = RpcMethodSpec(
            method=method,
            handler=handler,
            capability=capability,
            alias_of=alias_of,
            description=description,
        )

    async def dispatch(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        spec = self._methods.get(method)
        if spec is None:
            raise LookupError(f"Unsupported method: {method}")
        return await spec.handler(params)

    def capabilities(self) -> Dict[str, bool]:
        capabilities: Dict[str, bool] = {}
        for spec in self._methods.values():
            if spec.capability:
                capabilities[spec.capability] = True
        return dict(sorted(capabilities.items()))

    def list_methods(self) -> List[Dict[str, Any]]:
        return [self._methods[method].public_dict() for method in sorted(self._methods)]

    def has_method(self, method: str) -> bool:
        return method in self._methods
