from pydantic import BaseModel

from app.core.base import CommunityInfo

router = APIRouter()


class SummarizeRequest(BaseModel):
    namespace: str = "default"
    query: str | None = None


class SummarizeResponse(BaseModel):
    summary: str
    community_summaries: list[CommunityInfo]
    total_entities: int = 0
    total_communities: int = 0


@router.post("/", response_model=SummarizeResponse)
async def summarize_knowledge(request: SummarizeRequest) -> SummarizeResponse:
    raise HTTPException(status_code=501, detail="Not implemented")
