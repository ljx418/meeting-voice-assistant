"""harnessOS gateway package."""

import warnings

warnings.filterwarnings(
    "ignore",
    message=r"urllib3 v2 only supports OpenSSL 1\.1\.1\+.*",
    category=Warning,
    module=r"urllib3(\.|$)",
)

from apps.gateway.protocol import GatewayEvent, RpcError, RpcRequest, RpcResponse, TurnResult


def __getattr__(name: str):
    """Lazily expose heavy gateway classes without import-time cycles."""
    if name == "GatewayRuntimePool":
        from apps.gateway.runtime import GatewayRuntimePool

        return GatewayRuntimePool
    if name == "GatewayService":
        from apps.gateway.service import GatewayService

        return GatewayService
    raise AttributeError(name)

__all__ = [
    "GatewayEvent",
    "GatewayRuntimePool",
    "GatewayService",
    "RpcError",
    "RpcRequest",
    "RpcResponse",
    "TurnResult",
]
