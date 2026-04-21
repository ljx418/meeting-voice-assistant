"""
Wiki Pages API

基于 ADR-002 设计文档实现
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.core.wiki.service import get_wiki_service
from app.models.wiki import (
    WikiDocument, WikiDocumentCreate, WikiDocumentUpdate,
    APIResponse, PaginatedResponse
)

router = APIRouter(prefix="/pages", tags=["Wiki Pages"])


@router.get("", response_model=PaginatedResponse)
async def list_pages(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category_id: Optional[str] = Query(None, description="分类 ID"),
    tag_id: Optional[str] = Query(None, description="标签 ID"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    include_unpublished: bool = Query(False, description="包含未发布页面")
):
    """列出 Wiki 页面（支持分页、分类、标签过滤）"""
    service = get_wiki_service()
    pages, total = service.list_pages(
        page=page,
        page_size=page_size,
        category_id=category_id,
        tag_id=tag_id,
        search=search,
        include_unpublished=include_unpublished
    )
    return PaginatedResponse(
        items=[p.model_dump() for p in pages],
        total=total,
        page=page,
        size=page_size
    )


@router.get("/{page_id}", response_model=WikiDocument)
async def get_page(page_id: str):
    """获取单个 Wiki 页面"""
    service = get_wiki_service()
    page = service.get_page(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.get("/slug/{slug}", response_model=WikiDocument)
async def get_page_by_slug(slug: str):
    """通过 slug 获取 Wiki 页面"""
    service = get_wiki_service()
    page = service.get_page_by_slug(slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.post("", response_model=WikiDocument)
async def create_page(data: WikiDocumentCreate):
    """创建新 Wiki 页面"""
    service = get_wiki_service()
    page = service.create_page(
        title=data.title,
        content=data.content,
        category_id=data.category_id,
        meeting_id=data.meeting_id,
        tags=data.tags,
        is_published=False
    )
    return page


@router.put("/{page_id}", response_model=WikiDocument)
async def update_page(page_id: str, data: WikiDocumentUpdate):
    """更新 Wiki 页面"""
    service = get_wiki_service()

    # 检查页面是否存在
    existing = service.get_page(page_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Page not found")

    page = service.update_page(
        page_id=page_id,
        title=data.title,
        content=data.content,
        category_id=data.category_id,
        tags=data.tags,
        change_summary=data.change_summary
    )
    if not page:
        raise HTTPException(status_code=500, detail="Failed to update page")
    return page


@router.delete("/{page_id}")
async def delete_page(page_id: str):
    """删除 Wiki 页面"""
    service = get_wiki_service()
    success = service.delete_page(page_id)
    if not success:
        raise HTTPException(status_code=404, detail="Page not found")
    return APIResponse(success=True, message="Page deleted")


@router.get("/{page_id}/versions")
async def get_page_versions(page_id: str):
    """获取页面版本历史"""
    service = get_wiki_service()
    versions = service.get_page_versions(page_id)
    return {"items": [v.model_dump() for v in versions]}


@router.post("/{page_id}/revert/{version}", response_model=WikiDocument)
async def revert_page(page_id: str, version: int):
    """恢复到指定版本"""
    service = get_wiki_service()
    page = service.revert_to_version(page_id, version)
    if not page:
        raise HTTPException(status_code=404, detail="Version not found")
    return page
