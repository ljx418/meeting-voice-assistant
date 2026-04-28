"""Gateway models for harnessOS."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GatewayConfig(BaseModel):
    """Persistent gateway configuration."""

    model: str | None = None
    provider_profile: str | None = None
    permission_mode: str = "default"
    sandbox_enabled: bool = False
    log_level: str = "INFO"
    metadata: dict[str, str] = Field(default_factory=dict)


class GatewayState(BaseModel):
    """Runtime gateway status snapshot."""

    running: bool = False
    active_sessions: int = 0
    model: str | None = None
    last_error: str | None = None
