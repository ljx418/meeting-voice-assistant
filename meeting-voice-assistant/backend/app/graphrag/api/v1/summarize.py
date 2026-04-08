"""Summarize API - Knowledge graph summarization endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...core.base import SummaryResult
from ...core.registry import get_core

router = APIRouter()


class SummarizeRequest(BaseModel):
    """Summarize request model."""
    namespace: str = Field(default="default", description="Namespace to summarize")
    query: Optional[str] = Field(default=None, description="Optional custom query for summary")


class CommunityResponse(BaseModel):
    """Community information for response."""
    id: str
    level: int
    summary: Optional[str] = None
    entities_count: int = 0


class SummarizeResponse(BaseModel):
    """Summarize response model."""
    summary: str
    communities: List[CommunityResponse]


@router.post("/", response_model=SummarizeResponse)
async def summarize_knowledge(request: SummarizeRequest) -> SummarizeResponse:
    """
    Generate a summary of the knowledge graph.

    - **namespace**: Namespace to summarize (default: "default")
    - **query**: Optional custom query for summary (default: comprehensive summary)

    Returns a summary of the knowledge graph with community information.
    """
    try:
        core = get_core()
        result: SummaryResult = await core.summarize(request.namespace, request.query)

        # Build communities response
        communities = []
        for comm in result.community_summaries:
            communities.append(CommunityResponse(
                id=comm.community_id,
                level=comm.level,
                summary=comm.summary,
                entities_count=len(comm.entity_ids) if comm.entity_ids else 0,
            ))

        return SummarizeResponse(
            summary=result.summary,
            communities=communities,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarize failed: {str(e)}")
