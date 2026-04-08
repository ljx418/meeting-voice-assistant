from pydantic import BaseModel

from app.core.base import EntityInfo, SourceChunk

router = APIRouter()


class RealtimeInjectionRequest(BaseModel):
    text: str
    namespace: str = "default"
    metadata: dict | None = None


class RealtimeInjectionResponse(BaseModel):
    injection_id: str
    status: str
    entities_extracted: int = 0


@router.post("/inject", response_model=RealtimeInjectionResponse)
async def inject_realtime_context(
    request: RealtimeInjectionRequest,
) -> RealtimeInjectionResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


class RealtimeQueryRequest(BaseModel):
    query_text: str
    namespace: str = "default"
    top_k: int = 5


class RealtimeQueryResponse(BaseModel):
    query_text: str
    answer: str
    source_chunks: list[SourceChunk]
    entities: list[EntityInfo]


@router.post("/query", response_model=RealtimeQueryResponse)
async def query_with_realtime(request: RealtimeQueryRequest) -> RealtimeQueryResponse:
    raise HTTPException(status_code=501, detail="Not implemented")
