"""
Wiki Search API

基于 ADR-002 设计文档实现
"""

from fastapi import APIRouter, Query
from typing import Optional

from app.core.wiki.service import get_wiki_service

router = APIRouter(prefix="/search", tags=["Wiki Search"])


@router.get("")
async def search_pages(
    q: str = Query(..., description="搜索关键词"),
    category_id: Optional[str] = Query(None, description="分类 ID"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
):
    """全文搜索 Wiki 页面"""
    service = get_wiki_service()
    results = service.search(query=q, category_id=category_id, limit=limit)
    return {
        "query": q,
        "results": [r.model_dump() for r in results],
        "total": len(results)
    }


@router.post("/semantic")
async def semantic_search(
    query: str,
    category_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """GraphRAG 语义搜索"""
    service = get_wiki_service()
    result = await service.semantic_search(
        query=query,
        category_id=category_id,
        limit=limit
    )
    return result
