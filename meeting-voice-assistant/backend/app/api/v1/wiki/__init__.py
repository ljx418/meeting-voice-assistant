"""
Wiki API 路由

基于 ADR-002 设计文档实现
Wiki 与 GraphRAG 集成
"""

from fastapi import APIRouter

from .pages import router as pages_router
from .categories import router as categories_router
from .tags import router as tags_router
from .generate import router as generate_router
from .search import router as search_router
from .workflow import router as workflow_router

router = APIRouter(prefix="/wiki", tags=["Wiki"])

router.include_router(pages_router)
router.include_router(categories_router)
router.include_router(tags_router)
router.include_router(generate_router)
router.include_router(search_router)
router.include_router(workflow_router)
