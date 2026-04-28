"""Project-owned protocol models for harnessOS gateway."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def new_id(prefix: str) -> str:
    """Create a compact stable-looking protocol identifier."""
    return f"{prefix}_{uuid4().hex[:12]}"


class RpcError(BaseModel):
    """JSON-RPC style error payload."""

    code: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


class RpcRequest(BaseModel):
    """One gateway RPC request."""

    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None


class RpcResponse(BaseModel):
    """One gateway RPC response."""

    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[RpcError] = None


class GatewayEvent(BaseModel):
    """Normalized event emitted by the project gateway."""

    type: str
    session_id: Optional[str] = None
    turn_id: Optional[str] = None
    item_id: str = Field(default_factory=lambda: new_id("item"))
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)


class TurnResult(BaseModel):
    """Aggregated turn result for headless clients."""

    session_id: str
    turn_id: str
    final_text: str
    events: list[GatewayEvent] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Return whether the turn completed without a failed event."""
        return not any(event.type == "turn.failed" for event in self.events)
