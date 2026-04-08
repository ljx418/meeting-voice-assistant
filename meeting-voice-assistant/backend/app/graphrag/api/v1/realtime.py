"""Real-time context injection API for knowledge graph queries."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...core.base import QueryResult
from ...core.registry import get_core
from ...service.context_injector import ContextInjector

router = APIRouter()

# Initialize context injector
_context_injector = ContextInjector()


class RealtimeQueryRequest(BaseModel):
    """Real-time query request with context injection."""
    query: str = Field(..., description="Query text")
    context: str = Field(..., description="Current meeting context to prepend to query")
    namespace: str = Field(default="default", description="Namespace to query")
    top_k: int = Field(default=5, ge=1, le=100, description="Number of top results (1-100)")


class SourceInfo(BaseModel):
    """Source chunk information."""
    doc_id: str
    chunk: str
    similarity: Optional[float] = None


class EntityInfoResponse(BaseModel):
    """Entity information for response."""
    name: str
    type: str
    description: Optional[str] = None


class RealtimeQueryResponse(BaseModel):
    """Real-time query response."""
    answer: str
    sources: List[SourceInfo]
    entities: List[EntityInfoResponse]


@router.post("/query", response_model=RealtimeQueryResponse)
async def query_with_realtime_context(
    request: RealtimeQueryRequest,
) -> RealtimeQueryResponse:
    """
    Query the knowledge graph with real-time context injection.

    - **query**: Query text (e.g., "这个项目的技术架构是什么？")
    - **context**: Current meeting context to prepend to the query
    - **namespace**: Namespace to query (default: "default")
    - **top_k**: Number of top results to return (1-100, default: 5)

    Returns the answer with source information and detected entities.
    """
    try:
        # Inject context into query
        enhanced_query = _context_injector.inject(request.query, request.context)

        # Execute query with enhanced query text
        core = get_core()
        result: QueryResult = await core.query(
            enhanced_query, request.namespace, request.top_k, None
        )

        # Build sources from source_chunks
        sources = []
        for chunk in result.source_chunks:
            sources.append(SourceInfo(
                doc_id=chunk.document_id,
                chunk=chunk.text[:500] if chunk.text else "",
                similarity=None,  # Not provided by underlying GraphRAG
            ))

        # Build entities
        entities = []
        for entity in result.entities:
            entities.append(EntityInfoResponse(
                name=entity.name,
                type=entity.entity_type,
                description=entity.description,
            ))

        return RealtimeQueryResponse(
            answer=result.answer,
            sources=sources,
            entities=entities,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Realtime query failed: {str(e)}")
