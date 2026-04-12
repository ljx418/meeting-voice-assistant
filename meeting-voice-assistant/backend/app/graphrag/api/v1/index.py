"""Index API - Document indexing endpoints."""

import json
import uuid
from pathlib import Path
from typing import List, Optional, AsyncGenerator

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ...core.base import IndexResult
from ...core.registry import get_core
from ...storage.database import save_document
from ...config import settings

router = APIRouter()

# Supported file extensions for indexing
ALLOWED_EXTENSIONS = {
    '.txt', '.md', '.pdf', '.docx', '.doc',
    '.pptx', '.xlsx', '.csv', '.json', '.jsonl',
    '.html', '.xml', '.eml', '.msg'
}


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
) -> dict:
    """
    Index an uploaded document.

    - **doc**: The document file to index (multipart/form-data)

    Returns indexing results including entity/relationship/community counts.

    Note: Environment isolation is handled via separate GRAPHRAG_WORKSPACE directories.
    No namespace parameter needed - all documents in a given environment share the same index.
    """
    if not doc.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate file extension
    ext = Path(doc.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Generate document ID
    doc_id = str(uuid.uuid4())

    # Determine file path in workspace (directly under input/, no namespace subdirectory)
    workspace_input = settings.GRAPHRAG_WORKSPACE / "input"
    workspace_input.mkdir(parents=True, exist_ok=True)
    file_path = workspace_input / doc.filename

    # Save uploaded file
    try:
        content = await doc.read()
        file_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Index the document using core (namespace is fixed "default" for backward compat)
    try:
        core = get_core()
        result: IndexResult = await core.index_document(file_path, namespace="default")

        # Save document record to database
        await save_document(
            doc_id=doc_id,
            namespace="default",
            filename=doc.filename,
            file_path=str(file_path),
            chunk_count=None,
            entity_count=result.entity_count,
        )

        response = {
            "doc_id": doc_id,
            "status": result.status,
            "entities_count": result.entity_count,
            "relationships_count": result.relationship_count,
            "communities_count": result.community_count,
        }
        if result.error:
            response["error"] = result.error
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


async def index_progress_stream(
    doc: UploadFile,
    file_path: Path,
    doc_id: str,
) -> AsyncGenerator[str, None]:
    """生成 SSE 事件流"""
    core = get_core()

    # 流式索引
    async for event in core.index_document_stream(file_path, namespace="default"):
        yield f"data: {json.dumps(event)}\n\n"

        # 如果是完成或错误事件，保存文档记录
        if event["stage"] in ("complete", "error"):
            if event["stage"] == "complete":
                details = event.get("details", {})
                await save_document(
                    doc_id=doc_id,
                    namespace="default",
                    filename=doc.filename,
                    file_path=str(file_path),
                    chunk_count=None,
                    entity_count=details.get("entity_count", 0),
                )


@router.post("/stream")
async def index_document_stream(
    doc: UploadFile = File(...),
):
    """
    Index an uploaded document with streaming progress (SSE).

    - **doc**: The document file to index (multipart/form-data)

    Returns Server-Sent Events (SSE) stream with progress updates.

    Event stages:
    - detecting_language (5%): 检测文档语言
    - language_detected (10%): 语言检测完成
    - indexing (15-95%): 索引处理中
    - parsing (95%): 解析结果
    - complete (100%): 索引完成
    - error: 索引失败
    """
    if not doc.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate file extension
    ext = Path(doc.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Generate document ID
    doc_id = str(uuid.uuid4())

    # Determine file path in workspace
    workspace_input = settings.GRAPHRAG_WORKSPACE / "input"
    workspace_input.mkdir(parents=True, exist_ok=True)
    file_path = workspace_input / doc.filename

    # Save uploaded file first
    try:
        content = await doc.read()
        file_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Return SSE stream
    return StreamingResponse(
        index_progress_stream(doc, file_path, doc_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        },
    )


class BatchIndexResponse(BaseModel):
    """Batch index response model."""
    total: int
    succeeded: int
    failed: int
    results: List[dict]


@router.post("/batch", response_model=BatchIndexResponse)
async def index_documents_batch(
    file_paths: List[str] = Form(...),
) -> BatchIndexResponse:
    """
    Batch index multiple documents.

    - **file_paths**: List of file paths to index

    Returns batch indexing results.

    Note: Environment isolation is handled via separate GRAPHRAG_WORKSPACE directories.
    """
    if not file_paths:
        raise HTTPException(status_code=400, detail="No file paths provided")

    try:
        core = get_core()
        paths = [Path(p) for p in file_paths]
        result = await core.index_documents_batch(paths, namespace="default")

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
