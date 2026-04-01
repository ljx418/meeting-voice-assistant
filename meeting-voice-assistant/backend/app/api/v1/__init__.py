"""
API v1 路由
"""

from fastapi import APIRouter

from .ws import router as ws_router
from .health import router as health_router
from .upload import router as upload_router

router = APIRouter()

router.include_router(ws_router, tags=["WebSocket"])
router.include_router(health_router, tags=["Health"])
router.include_router(upload_router, tags=["Upload"])
