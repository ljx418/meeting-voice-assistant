"""Minimal standalone configuration for the extracted data service."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class APIConfig:
    api_key: str = os.getenv("API_KEY", "")


@dataclass
class JWTConfig:
    dev_mode: bool = _env_bool("JWT_DEV_MODE", True)
    dev_bypass_auth: bool = _env_bool("JWT_DEV_BYPASS_AUTH", True)
    dev_user_id: str = os.getenv("JWT_DEV_USER_ID", "dev_user")
    secret_key: str = os.getenv("JWT_SECRET_KEY", "data-service-dev-secret")


@dataclass
class AppConfig:
    api: APIConfig
    jwt: JWTConfig


config = AppConfig(api=APIConfig(), jwt=JWTConfig())
