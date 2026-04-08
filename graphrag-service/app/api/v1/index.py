from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class IndexRequest(BaseModel):
    file_path: str
    namespace: str = "default"


class IndexResponse(BaseModel):
    document_id: str
    namespace: str
    status: str
    entity_count: int = 0
    relationship_count: int = 0
    community_count: int = 0


@router.post("/", response_model=IndexResponse)
async def index_document(request: IndexRequest) -> IndexResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


class BatchIndexRequest(BaseModel):
    file_paths: list[str]
    namespace: str = "default"


class BatchIndexResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: list[IndexResponse]


@router.post("/batch", response_model=BatchIndexResponse)
async def index_documents_batch(request: BatchIndexRequest) -> BatchIndexResponse:
    raise HTTPException(status_code=501, detail="Not implemented")
