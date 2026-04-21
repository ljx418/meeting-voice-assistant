"""
Wiki Categories API

基于 ADR-002 设计文档实现
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List

from app.core.wiki.service import get_wiki_service
from app.models.wiki import APIResponse

router = APIRouter(prefix="/categories", tags=["Wiki Categories"])


@router.get("", response_model=List[dict])
async def list_categories():
    """获取所有分类"""
    service = get_wiki_service()
    return service.list_categories()


@router.get("/tree")
async def get_category_tree():
    """获取分类树形结构"""
    service = get_wiki_service()
    return service.get_category_tree()


@router.get("/{category_id}")
async def get_category(category_id: str):
    """获取单个分类"""
    service = get_wiki_service()
    category = service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("")
async def create_category(
    name: str,
    description: Optional[str] = None,
    parent_id: Optional[str] = None,
    sort_order: int = 0
):
    """创建分类"""
    service = get_wiki_service()
    category_id = service.create_category(
        name=name,
        description=description,
        parent_id=parent_id,
        sort_order=sort_order
    )
    return APIResponse(success=True, data={"id": category_id})


@router.put("/{category_id}")
async def update_category(
    category_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    parent_id: Optional[str] = None,
    sort_order: Optional[int] = None
):
    """更新分类"""
    service = get_wiki_service()
    success = service.update_category(
        cat_id=category_id,
        name=name,
        description=description,
        parent_id=parent_id,
        sort_order=sort_order
    )
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return APIResponse(success=True)


@router.delete("/{category_id}")
async def delete_category(category_id: str):
    """删除分类"""
    service = get_wiki_service()
    success = service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return APIResponse(success=True, message="Category deleted")
