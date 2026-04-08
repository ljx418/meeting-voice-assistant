from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.base import CommunityInfo, EntityInfo, SourceChunk

router = APIRouter()


class QueryRequest(BaseModel):
    query_text: str
    namespace: str = "default"
    top_k: int = 10
    context: str | None = None


class QueryResponse(BaseModel):
    query_text: str
    answer: str
    source_chunks: list[SourceChunk]
    entities: list[EntityInfo]
    communities: list[CommunityInfo]
    confidence: float = 0.0


@router.post("/", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest) -> QueryResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


class RealtimeQueryRequest(BaseModel):
    query_text: str
    namespace: str = "default"
    realtime_context: str


@router.post("/realtime", response_model=QueryResponse)
async def query_with_realtime_context(
    request: RealtimeQueryRequest,
) -> QueryResponse:
    raise HTTPException(status_code=501, detail="Not implemented")
