"""Index API - Document indexing endpoints."""

import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from ...core.base import IndexResult
from ...core.registry import get_core
from ...storage.database import save_document
from ...config import settings

router = APIRouter()


class IndexResponse(BaseModel):
    """Index response model."""
    doc_id: str
    status: str
    entities_count: int = 0
    relationships_count: int = 0
    communities_count: int = 0


@router.post("/", response_model=dict)
async def index_document(
    doc: UploadFile = File(...),
    namespace: str = Form(default="default"),
) -> dict:
    """
    Index an uploaded document.

    - **doc**: The document file to index (multipart/form-data)
    - **namespace**: Namespace for the document (default: "default")

    Returns indexing results including entity/relationship/community counts.
    """
    if not doc.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Generate document ID
    doc_id = str(uuid.uuid4())

    # Determine file path in workspace
    workspace_input = settings.GRAPHRAG_WORKSPACE / "input" / namespace
    workspace_input.mkdir(parents=True, exist_ok=True)
    file_path = workspace_input / doc.filename

    # Save uploaded file
    try:
        content = await doc.read()
        file_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Index the document using core
    try:
        core = get_core()
        result: IndexResult = await core.index_document(file_path, namespace)

        # Save document record to database
        await save_document(
            doc_id=doc_id,
            namespace=namespace,
            filename=doc.filename,
            file_path=str(file_path),
            chunk_count=None,
            entity_count=result.entity_count,
        )

        return {
            "doc_id": doc_id,
            "status": result.status,
            "entities_count": result.entity_count,
            "relationships_count": result.relationship_count,
            "communities_count": result.communities_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


class BatchIndexResponse(BaseModel):
    """Batch index response model."""
    total: int
    succeeded: int
    failed: int
    results: List[dict]


@router.post("/batch", response_model=BatchIndexResponse)
async def index_documents_batch(
    file_paths: List[str] = Form(...),
    namespace: str = Form(default="default"),
) -> BatchIndexResponse:
    """
    Batch index multiple documents.

    - **file_paths**: List of file paths to index
    - **namespace**: Namespace for the documents (default: "default")

    Returns batch indexing results.
    """
    if not file_paths:
        raise HTTPException(status_code=400, detail="No file paths provided")

    try:
        core = get_core()
        paths = [Path(p) for p in file_paths]
        result = await core.index_documents_batch(paths, namespace)

        return BatchIndexResponse(
            total=result.total,
            succeeded=result.succeeded,
            failed=result.failed,
            results=[
                {
                    "doc_id": r.document_id,
                    "status": r.status,
                    "entity_count": r.entity_count,
                    "relationship_count": r.relationship_count,
                    "community_count": r.community_count,
                }
                for r in result.results
            ],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch indexing failed: {str(e)}")
