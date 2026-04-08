"""Document API - Document management endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from sqlalchemy import select, func

from ...storage.database import async_session, delete_document as db_delete_document
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
async def list_documents(
    namespace: str = Query(default="default", description="Namespace to filter by"),
) -> List[DocumentInfo]:
    """
    List all documents in a namespace.

    - **namespace**: Namespace to filter documents (default: "default")

    Returns a list of documents with metadata including entity count.
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
                .where(Document.namespace == namespace)
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
    namespace: str = Query(default="default", description="Namespace to verify ownership"),
) -> DocumentInfo:
    """
    Get details of a specific document.

    - **doc_id**: Document ID
    - **namespace**: Namespace to verify ownership (default: "default")

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
                .where(Document.id == doc_id, Document.namespace == namespace)
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


class DeleteResponse(BaseModel):
    """Delete response model."""
    status: str
    doc_id: str


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(
    doc_id: str,
    namespace: str = Query(default="default", description="Namespace to verify ownership"),
) -> DeleteResponse:
    """
    Delete a document and its associated entities.

    - **doc_id**: Document ID to delete
    - **namespace**: Namespace to verify ownership (default: "default")

    Returns deletion status.
    """
    try:
        # Attempt to delete directly - avoids TOCTOU race condition
        # since delete is idempotent (deleting non-existent returns 0 rows)
        deleted = await db_delete_document(doc_id, namespace)

        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")

        return DeleteResponse(status="deleted", doc_id=doc_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
