"""Standalone health check endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()
_started_at = datetime.now(timezone.utc)


@router.get("/health")
async def health_check() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "status": "healthy",
        "service": "data_service",
        "uptime": max((now - _started_at).total_seconds(), 0.0),
        "timestamp": now.isoformat().replace("+00:00", "Z"),
    }
