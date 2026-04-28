"""Configuration helpers for the harnessOS gateway."""

from __future__ import annotations

import json
from pathlib import Path

from apps.gateway.models import GatewayConfig


def default_gateway_config_path(workspace: str | Path | None = None) -> Path:
    """Return the local gateway config path."""
    root = Path(workspace or ".").expanduser().resolve()
    return root / ".harnessos" / "gateway.json"


def load_gateway_config(workspace: str | Path | None = None) -> GatewayConfig:
    """Load gateway configuration from the local workspace."""
    path = default_gateway_config_path(workspace)
    if not path.exists():
        return GatewayConfig()
    return GatewayConfig.model_validate_json(path.read_text(encoding="utf-8"))


def save_gateway_config(
    config: GatewayConfig,
    workspace: str | Path | None = None,
) -> Path:
    """Persist gateway configuration to the local workspace."""
    path = default_gateway_config_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def load_gateway_config_dict(workspace: str | Path | None = None) -> dict:
    """Load gateway configuration as a plain dict."""
    path = default_gateway_config_path(workspace)
    if not path.exists():
        return GatewayConfig().model_dump(mode="json")
    return json.loads(path.read_text(encoding="utf-8"))
