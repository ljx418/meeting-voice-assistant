"""Community API - Community management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ...storage.database import async_session
from ...storage.models import Community, Entity, Relationship
from sqlalchemy import select, func, or_

router = APIRouter()


class CommunitySummaryResponse(BaseModel):
    """社区摘要响应模型"""
    community_id: str
    level: Optional[int] = None
    summary: Optional[str] = None
    entity_count: int = 0
    relationship_count: int = 0


@router.get("/{community_id}/summary", response_model=CommunitySummaryResponse)
async def get_community_summary(community_id: str) -> CommunitySummaryResponse:
    """
    获取社区摘要信息

    - **community_id**: 社区 ID

    Returns 社区详情包括实体数量、关系数量
    """
    try:
        async with async_session() as session:
            # 获取社区信息
            comm_stmt = select(Community).where(Community.id == community_id)
            comm_result = await session.execute(comm_stmt)
            community = comm_result.scalar_one_or_none()

            if not community:
                raise HTTPException(status_code=404, detail="Community not found")

            # 统计该社区的实体数量
            ent_stmt = select(func.count(Entity.id)).where(
                Entity.community_id == community_id
            )
            ent_result = await session.execute(ent_stmt)
            entity_count = ent_result.scalar() or 0

            # 统计关系数量（两端实体都在该社区）
            ent_ids_stmt = select(Entity.id).where(Entity.community_id == community_id)
            ent_ids_result = await session.execute(ent_ids_stmt)
            ent_ids = [row[0] for row in ent_ids_result.fetchall()]

            rel_count = 0
            if ent_ids:
                rel_stmt = select(func.count(Relationship.id)).where(
                    or_(
                        Relationship.source_entity_id.in_(ent_ids),
                        Relationship.target_entity_id.in_(ent_ids)
                    )
                )
                rel_result = await session.execute(rel_stmt)
                rel_count = rel_result.scalar() or 0

            return CommunitySummaryResponse(
                community_id=community_id,
                level=community.level,
                summary=community.summary,
                entity_count=entity_count,
                relationship_count=rel_count,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get community summary: {str(e)}")