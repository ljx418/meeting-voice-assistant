"""Configuration for the V3.5-F FastAPI BFF template."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harnessos_client import Scope

from .errors import BffError


DEFAULT_CAPABILITIES = (
    "sessions",
    "turns",
    "events",
    "artifacts.read",
    "artifacts.write",
    "jobs",
    "approvals",
    "packs.read",
    "connectors.read",
)


@dataclass(frozen=True)
class BffSettings:
    harnessos_base_url: str
    harnessos_capability_token: str | None
    allowed_origins: tuple[str, ...]
    allow_credentials: bool
    demo_identity_mode: bool
    identity_scope: Scope
    demo_capabilities: frozenset[str]
    config_error: str | None = None

    @property
    def warning_header(self) -> str | None:
        if self.demo_identity_mode:
            return "demo identity mode is enabled; replace IdentityProvider before production"
        return None


def load_settings(config: dict[str, Any] | None = None) -> BffSettings:
    source = dict(config or {})
    token_env = str(source.get("harnessos_capability_token_env") or "HARNESSOS_CAPABILITY_TOKEN")
    token = source.get("harnessos_capability_token") or os.getenv(token_env)
    allowed_origins = _list_from_value(source.get("allowed_origins") or os.getenv("BFF_ALLOWED_ORIGINS") or "http://localhost:5173")
    allow_credentials = _bool(source.get("allow_credentials"), os.getenv("BFF_ALLOW_CREDENTIALS"), default=True)
    demo_identity_mode = _bool(source.get("demo_identity_mode"), os.getenv("BFF_DEMO_IDENTITY_MODE"), default=False)
    identity_scope = Scope.from_value(
        source.get("identity_scope")
        or {
            "app_id": os.getenv("BFF_DEFAULT_APP_ID") or "reference_app",
            "project_id": os.getenv("BFF_DEFAULT_PROJECT_ID") or "demo",
            "workspace_id": os.getenv("BFF_DEFAULT_WORKSPACE_ID") or "local",
        }
    ) or Scope(app_id="reference_app", project_id="demo", workspace_id="local")
    capabilities = frozenset(str(item) for item in source.get("demo_capabilities") or DEFAULT_CAPABILITIES)

    if "*" in allowed_origins and allow_credentials:
        raise BffError("INVALID_CONFIG", 'BFF_ALLOWED_ORIGINS="*" cannot be used with credentials enabled.', status_code=500)

    config_error = None
    if not demo_identity_mode:
        config_error = "BFF_DEMO_IDENTITY_MODE must be explicitly enabled or replaced with a real IdentityProvider."
    if not token:
        missing = "HARNESSOS_CAPABILITY_TOKEN is required for proxy routes."
        config_error = f"{config_error} {missing}" if config_error else missing

    return BffSettings(
        harnessos_base_url=str(source.get("harnessos_base_url") or os.getenv("HARNESSOS_BASE_URL") or "http://127.0.0.1:8000"),
        harnessos_capability_token=str(token) if token else None,
        allowed_origins=tuple(allowed_origins),
        allow_credentials=allow_credentials,
        demo_identity_mode=demo_identity_mode,
        identity_scope=identity_scope,
        demo_capabilities=capabilities,
        config_error=config_error,
    )


def load_config(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _list_from_value(value: Any) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _bool(primary: Any, secondary: Any, *, default: bool) -> bool:
    value = primary if primary is not None else secondary
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
