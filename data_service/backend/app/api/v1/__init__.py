"""Versioned API routes for the standalone data service."""

from fastapi import APIRouter

from .data_service import router as data_service_router
from .health import router as health_router

router = APIRouter()
router.include_router(health_router)
router.include_router(data_service_router)

__all__ = ["router"]
