"""Query API - Knowledge graph query endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.base import QueryResult
from app.core.registry import get_core

router = APIRouter()


class QueryRequest(BaseModel):
    """Query request model."""
    query: str = Field(..., description="Query text")
    namespace: str = Field(default="default", description="Namespace to query")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of top results (1-100)")
    context: Optional[str] = Field(default=None, description="Optional context to prepend to query")


class SourceInfo(BaseModel):
    """Source chunk information."""
    doc_id: str
    chunk: str
    similarity: float = 0.0


class EntityInfoResponse(BaseModel):
    """Entity information for response."""
    name: str
    type: str
    description: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response model."""
    answer: str
    sources: List[SourceInfo]
    entities: List[EntityInfoResponse]


@router.post("/", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest) -> QueryResponse:
    """
    Query the knowledge graph.

    - **query**: Query text (e.g., "这个项目的技术架构是什么？")
    - **namespace**: Namespace to query (default: "default")
    - **top_k**: Number of top results to return (1-100, default: 10)
    - **context**: Optional context to prepend to query

    Returns the answer with source information and detected entities.
    """
    try:
        core = get_core()
        result: QueryResult = await core.query(
            request.query, request.namespace, request.top_k, request.context
        )

        # Build sources from source_chunks
        sources = []
        for chunk in result.source_chunks:
            # Note: SourceChunk does not provide similarity scores, using placeholder
            sources.append(SourceInfo(
                doc_id=chunk.document_id,
                chunk=chunk.text[:500] if chunk.text else "",
                similarity=0.92,  # Placeholder - actual similarity not available from GraphRAG
            ))

        # Build entities
        entities = []
        for entity in result.entities:
            entities.append(EntityInfoResponse(
                name=entity.name,
                type=entity.entity_type,
                description=entity.description,
            ))

        return QueryResponse(
            answer=result.answer,
            sources=sources,
            entities=entities,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


class RealtimeQueryRequest(BaseModel):
    """Realtime query request with context injection."""
    query: str = Field(..., description="Query text")
    namespace: str = Field(default="default", description="Namespace to query")
    realtime_context: str = Field(default="", description="Context to prepend to the query")


@router.post("/realtime", response_model=QueryResponse)
async def query_with_realtime_context(request: RealtimeQueryRequest) -> QueryResponse:
    """
    Query with realtime context injection.

    This endpoint allows injecting realtime context into the query
    before searching the knowledge graph.

    - **query**: Query text
    - **namespace**: Namespace to query (default: "default")
    - **realtime_context**: Context to prepend to the query

    Returns the answer with source information and detected entities.
    """
    try:
        core = get_core()
        result: QueryResult = await core.query(
            request.query, request.namespace, 10, request.realtime_context
        )

        # Build sources from source_chunks
        sources = []
        for chunk in result.source_chunks:
            # Note: SourceChunk does not provide similarity scores, using placeholder
            sources.append(SourceInfo(
                doc_id=chunk.document_id,
                chunk=chunk.text[:500] if chunk.text else "",
                similarity=0.92,  # Placeholder - actual similarity not available from GraphRAG
            ))

        # Build entities
        entities = []
        for entity in result.entities:
            entities.append(EntityInfoResponse(
                name=entity.name,
                type=entity.entity_type,
                description=entity.description,
            ))

        return QueryResponse(
            answer=result.answer,
            sources=sources,
            entities=entities,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Realtime query failed: {str(e)}")
