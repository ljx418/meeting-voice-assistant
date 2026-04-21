"""Session API - Session-based workspace lifecycle management."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...workspace_manager import get_workspace_manager
from ...core.registry import GraphRAGRegistry

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateSessionResponse(BaseModel):
    """Response model for session creation."""
    session_id: str
    workspace_path: str
    message: str


class SessionInfo(BaseModel):
    """Session information."""
    session_id: str
    path: str
    exists: bool


class CleanupResponse(BaseModel):
    """Response model for session cleanup."""
    session_id: str
    deleted_files: int
    deleted_dirs: int
    workspace_path: str


@router.post("/", response_model=CreateSessionResponse)
async def create_session() -> CreateSessionResponse:
    """
    Create a new isolated workspace for a GraphRAG session.

    Each session gets its own:
    - input/ directory for source documents
    - output/ directory for indexed data
    - graphrag.db for metadata
    - settings.yaml for configuration

    Use the returned session_id in subsequent API calls to operate on this session's data.

    Returns:
        session_id: Unique session identifier (UUID, 12 chars)
        workspace_path: Path to the session's workspace
        message: Human-readable status message
    """
    try:
        manager = get_workspace_manager()
        session_id = manager.generate_session_id()

        workspace_path = manager.create_workspace(session_id)

        # Pre-initialize the GraphRAG adapter for this session
        GraphRAGRegistry.get_instance(session_id)

        logger.info(f"Created session {session_id} with workspace at {workspace_path}")

        return CreateSessionResponse(
            session_id=session_id,
            workspace_path=str(workspace_path),
            message=f"Session workspace created successfully"
        )
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/", response_model=list[SessionInfo])
async def list_sessions() -> list[SessionInfo]:
    """
    List all existing session workspaces.

    Returns:
        List of sessions with their workspace information
    """
    try:
        manager = get_workspace_manager()
        workspaces = manager.list_workspaces()
        return [SessionInfo(**w) for w in workspaces]
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.get("/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str) -> SessionInfo:
    """
    Get information about a specific session.

    Args:
        session_id: Session identifier

    Returns:
        Session workspace information
    """
    manager = get_workspace_manager()

    if not manager.workspace_exists(session_id):
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    workspace_path = manager.get_workspace(session_id)

    return SessionInfo(
        session_id=session_id,
        path=str(workspace_path),
        exists=True,
    )


@router.delete("/{session_id}", response_model=CleanupResponse)
async def cleanup_session(session_id: str) -> CleanupResponse:
    """
    Clean up a session workspace.

    This will:
    1. Remove all indexed data (output/)
    2. Remove all source documents (input/)
    3. Remove the workspace directory
    4. Remove the session instance from registry

    Args:
        session_id: Session identifier to clean up

    Returns:
        Cleanup results including counts of deleted files/directories
    """
    try:
        manager = get_workspace_manager()

        if not manager.workspace_exists(session_id):
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Remove from registry
        GraphRAGRegistry.reset(session_id)

        # Cleanup workspace directory
        result = manager.cleanup_workspace(session_id)

        logger.info(f"Cleaned up session {session_id}: {result}")

        return CleanupResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cleanup session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup session: {str(e)}")
