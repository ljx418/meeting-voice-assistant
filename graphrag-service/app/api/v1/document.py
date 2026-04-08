from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    namespace: str
    status: str
    entity_count: int = 0
    created_at: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


@router.get("/", response_model=DocumentListResponse)
async def list_documents(namespace: str = "default") -> DocumentListResponse:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(document_id: str, namespace: str = "default") -> DocumentInfo:
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{document_id}")
async def delete_document(document_id: str, namespace: str = "default") -> dict:
    raise HTTPException(status_code=501, detail="Not implemented")
