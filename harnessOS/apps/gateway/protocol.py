"""Project-owned protocol models for harnessOS gateway."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode="after")
    def validate_json_rpc_result_or_error(self) -> "RpcResponse":
        """JSON-RPC responses must contain exactly one terminal payload."""
        has_result = self.result is not None
        has_error = self.error is not None
        if has_result == has_error:
            raise ValueError("RpcResponse must include exactly one of result or error")
        return self


class GatewayEvent(BaseModel):
    """Normalized event emitted by the project gateway."""

    type: str
    session_id: Optional[str] = None
    turn_id: Optional[str] = None
    app_id: str = "default"
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    item_id: str = Field(default_factory=lambda: new_id("item"))
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)


class TurnResult(BaseModel):
    """Aggregated turn result for headless clients."""

    session_id: str
    turn_id: str
    final_text: str
    app_id: str = "default"
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    events: list[GatewayEvent] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Return whether the turn completed without a failed event."""
        return not any(event.type == "turn.failed" for event in self.events)
