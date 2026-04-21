"""Extract entities and relationships from meeting transcript text."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...core.base import EntityInfo
from ...core.registry import get_core

router = APIRouter()


class ExtractRequest(BaseModel):
    """Entity extraction request from transcript text."""
    text: str = Field(..., description="Meeting transcript text to extract entities from")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")
    namespace: str = Field(default="default", description="Namespace for storage")


class EntityResponse(BaseModel):
    """Extracted entity information."""
    name: str
    type: str
    description: Optional[str] = None


class ExtractResponse(BaseModel):
    """Entity extraction response."""
    success: bool
    entities: List[EntityResponse]
    summary: str = Field(default="", description="Brief summary of extracted entities")


@router.post("/", response_model=ExtractResponse)
async def extract_entities(request: ExtractRequest) -> ExtractResponse:
    """
    Extract entities and relationships from meeting transcript text.

    This endpoint takes raw transcript text and:
    1. Saves it as a temporary document
    2. Runs GraphRAG indexing to extract entities
    3. Returns the extracted entities and a summary

    This is used in the meeting pipeline:
    Audio → ASR → GraphRAG.extract() → LLMAnalyzer (with context)
    """
    import logging
    logger = logging.getLogger(__name__)

    session_id = request.session_id or f"extract_{uuid.uuid4().hex[:8]}"
    temp_filename = f"{session_id}_transcript.txt"

    try:
        # Step 1: Save transcript text as a temporary file for GraphRAG
        from ...config import settings
        workspace_input = settings.GRAPHRAG_WORKSPACE / "input"
        workspace_input.mkdir(parents=True, exist_ok=True)
        file_path = workspace_input / temp_filename

        # Write transcript text to file
        file_path.write_text(request.text, encoding='utf-8')
        logger.info(f"[Extract {session_id}] Saved transcript to {file_path}")

        # Step 2: Index the document with GraphRAG
        core = get_core()
        result = await core.index_document(file_path, namespace=request.namespace)

        if result.status == "failed":
            logger.warning(f"[Extract {session_id}] Indexing failed: {result.error}")
            # Continue anyway to try extracting from what we have

        # Step 3: Query the extracted entities
        # Use the transcript content to get entity information
        entities = []
        summary_parts = []

        # Try to get entities from the graph
        try:
            # Query for entity information using the transcript as context
            query_result = await core.query(
                query_text="列出这个会议中提到的所有关键实体（人物、项目、技术、决策等）及其描述",
                namespace=request.namespace,
                top_k=20,
                context=request.text[:2000],  # First 2000 chars as context
            )

            for entity in query_result.entities:
                entities.append(EntityResponse(
                    name=entity.name,
                    type=entity.entity_type,
                    description=entity.description,
                ))

            if query_result.answer:
                summary_parts.append(query_result.answer)

        except Exception as e:
            logger.warning(f"[Extract {session_id}] Entity query failed: {e}")

        # Build summary from entities if no answer from query
        if not summary_parts and entities:
            entity_types = {}
            for e in entities:
                entity_types[e.type] = entity_types.get(e.type, 0) + 1
            summary_parts.append(f"提取到 {len(entities)} 个实体，包括：{', '.join(f'{k}({v})' for k, v in entity_types.items())}")

        # Clean up: remove the temp file after processing
        try:
            file_path.unlink()
            logger.info(f"[Extract {session_id}] Cleaned up temp file")
        except Exception as e:
            logger.warning(f"[Extract {session_id}] Failed to clean up temp file: {e}")

        return ExtractResponse(
            success=True,
            entities=entities,
            summary=summary_parts[0] if summary_parts else f"提取到 {len(entities)} 个实体",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Extract {session_id}] Entity extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")