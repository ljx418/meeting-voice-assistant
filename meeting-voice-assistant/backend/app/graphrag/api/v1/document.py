"""Document API - Document management endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from sqlalchemy import select, func

from ...storage.database import async_session, delete_document as db_delete_document, clear_all_data as db_clear_all_data
from ...storage.models import Document, Entity

router = APIRouter()


class DocumentInfo(BaseModel):
    """Document information model."""
    id: str
    filename: str
    indexed_at: Optional[str] = None
    chunk_count: int = 0
    entity_count: int = 0


@router.get("/", response_model=List[DocumentInfo])
async def list_documents() -> List[DocumentInfo]:
    """
    List all documents in the current environment.

    Returns a list of documents with metadata including entity count.

    Note: Environment isolation is handled via separate GRAPHRAG_WORKSPACE directories.
    """
    try:
        async with async_session() as session:
            # Get documents with entity counts
            stmt = (
                select(
                    Document.id,
                    Document.filename,
                    Document.indexed_at,
                    Document.chunk_count,
                    func.count(Entity.id).label("entity_count"),
                )
                .outerjoin(Entity, Document.id == Entity.doc_id)
                .where(Document.namespace == "default")
                .group_by(Document.id)
            )
            result = await session.execute(stmt)
            rows = result.all()

            documents = []
            for row in rows:
                documents.append(DocumentInfo(
                    id=row.id,
                    filename=row.filename,
                    indexed_at=row.indexed_at.isoformat() if row.indexed_at else None,
                    chunk_count=row.chunk_count or 0,
                    entity_count=row.entity_count or 0,
                ))

            return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document(
    doc_id: str,
) -> DocumentInfo:
    """
    Get details of a specific document.

    - **doc_id**: Document ID

    Returns document details including entity count.
    """
    try:
        async with async_session() as session:
            # Get document with entity count
            stmt = (
                select(
                    Document.id,
                    Document.filename,
                    Document.indexed_at,
                    Document.chunk_count,
                    func.count(Entity.id).label("entity_count"),
                )
                .outerjoin(Entity, Document.id == Entity.doc_id)
                .where(Document.id == doc_id, Document.namespace == "default")
                .group_by(Document.id)
            )
            result = await session.execute(stmt)
            row = result.one_or_none()

            if not row:
                raise HTTPException(status_code=404, detail="Document not found")

            return DocumentInfo(
                id=row.id,
                filename=row.filename,
                indexed_at=row.indexed_at.isoformat() if row.indexed_at else None,
                chunk_count=row.chunk_count or 0,
                entity_count=row.entity_count or 0,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


class CheckDuplicateRequest(BaseModel):
    """检查重复请求模型"""
    filename: str


class CheckDuplicateResponse(BaseModel):
    """检查重复响应模型"""
    exists: bool
    doc_id: Optional[str] = None
    entity_count: int = 0


@router.post("/check-duplicate", response_model=CheckDuplicateResponse)
async def check_duplicate(request: CheckDuplicateRequest) -> CheckDuplicateResponse:
    """
    检查文件名是否已存在

    - **filename**: 要检查的文件名

    Returns 是否存在及文档信息
    """
    try:
        async with async_session() as session:
            stmt = (
                select(Document.id, func.count(Entity.id).label("entity_count"))
                .outerjoin(Entity, Document.id == Entity.doc_id)
                .where(Document.filename == request.filename, Document.namespace == "default")
                .group_by(Document.id)
            )
            result = await session.execute(stmt)
            row = result.one_or_none()

            if row:
                return CheckDuplicateResponse(
                    exists=True,
                    doc_id=row.id,
                    entity_count=row.entity_count or 0,
                )
            return CheckDuplicateResponse(exists=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check duplicate: {str(e)}")


class ClearAllRequest(BaseModel):
    """清空所有数据请求模型"""
    confirm: str


class ClearAllResponse(BaseModel):
    """清空所有数据响应模型"""
    status: str
    deleted_documents: int
    deleted_entities: int
    deleted_relationships: int
    deleted_communities: int


@router.delete("/clear-all", response_model=ClearAllResponse)
async def clear_all(request: ClearAllRequest) -> ClearAllResponse:
    """
    清空当前环境下的所有数据（危险操作）

    - **confirm**: 必须输入 "DELETE ALL" 确认

    Returns 删除统计
    """
    if request.confirm != "DELETE ALL":
        raise HTTPException(status_code=400, detail="Invalid confirmation text")

    try:
        result = await db_clear_all_data("default")
        return ClearAllResponse(status="deleted", **result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")


class DeleteResponse(BaseModel):
    """Delete response model."""
    status: str
    doc_id: str


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(
    doc_id: str,
) -> DeleteResponse:
    """
    Delete a document and its associated entities.

    - **doc_id**: Document ID to delete

    Returns deletion status.
    """
    try:
        # Attempt to delete directly - avoids TOCTOU race condition
        # since delete is idempotent (deleting non-existent returns 0 rows)
        deleted = await db_delete_document(doc_id, "default")

        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")

        return DeleteResponse(status="deleted", doc_id=doc_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
