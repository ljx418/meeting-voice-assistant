"""Minimal API-key auth helpers for the standalone data service."""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import config

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str]) -> str:
    expected = (config.api.api_key or "").strip()
    if not expected:
        if config.jwt.dev_mode and config.jwt.dev_bypass_auth:
            return config.jwt.dev_user_id or "local-dev"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
        )
    if api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return "api-key"
