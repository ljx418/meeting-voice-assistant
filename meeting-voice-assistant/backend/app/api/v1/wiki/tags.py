"""
Wiki Tags API

基于 ADR-002 设计文档实现
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List

from app.core.wiki.service import get_wiki_service
from app.models.wiki import APIResponse

router = APIRouter(prefix="/tags", tags=["Wiki Tags"])


@router.get("", response_model=List[dict])
async def list_tags():
    """获取所有标签"""
    service = get_wiki_service()
    return service.list_tags()


@router.get("/{tag_id}")
async def get_tag(tag_id: str):
    """获取单个标签"""
    service = get_wiki_service()
    tag = service.get_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("")
async def create_tag(name: str, color: str = "#6B7280"):
    """创建标签"""
    service = get_wiki_service()
    tag_id = service.create_tag(name=name, color=color)
    return APIResponse(success=True, data={"id": tag_id})


@router.put("/{tag_id}")
async def update_tag(
    tag_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None
):
    """更新标签"""
    service = get_wiki_service()
    success = service.update_tag(tag_id=tag_id, name=name, color=color)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return APIResponse(success=True)


@router.delete("/{tag_id}")
async def delete_tag(tag_id: str):
    """删除标签"""
    service = get_wiki_service()
    success = service.delete_tag(tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return APIResponse(success=True, message="Tag deleted")
