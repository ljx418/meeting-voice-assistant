"""
API v1 路由
"""

from fastapi import APIRouter

from .ws import router as ws_router
from .health import router as health_router
from .upload import router as upload_router
from .wiki import router as wiki_router
from .interview import router as interview_router
from .auth import router as auth_router
from .logs import router as logs_router
from .data_service import router as data_service_router

router = APIRouter()

router.include_router(ws_router, tags=["WebSocket"])
router.include_router(health_router, tags=["Health"])
router.include_router(upload_router, tags=["Upload"])
router.include_router(wiki_router, tags=["Wiki"])
router.include_router(interview_router, tags=["Interview"])
router.include_router(auth_router, tags=["认证"])
router.include_router(logs_router, tags=["日志"])
router.include_router(data_service_router)
