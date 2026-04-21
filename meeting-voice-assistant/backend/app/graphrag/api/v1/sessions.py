"""Sessions API - Session lifecycle management endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...workspace_manager import get_workspace_manager, create_session_workspace
from ...core.registry import GraphRAGRegistry

router = APIRouter()


class CreateSessionResponse(BaseModel):
    """Response model for session creation."""
    session_id: str
    workspace_path: str
    status: str


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    workspace_path: str
    exists: bool


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""
    sessions: list[SessionInfo]
    total: int


class CleanupResponse(BaseModel):
    """Response model for session cleanup."""
    session_id: str
    status: str
    deleted_files: int = 0
    deleted_dirs: int = 0
    workspace_path: str


@router.post("/", response_model=CreateSessionResponse)
async def create_session() -> CreateSessionResponse:
    """
    Create a new session with isolated workspace.

    Each session gets its own GraphRAG workspace with:
    - Independent input/ directory
    - Independent output/ directory
    - Independent settings.yaml

    Returns the session_id and workspace path.
    """
    manager = get_workspace_manager()
    session_id = manager.generate_session_id()
    workspace_path = manager.create_workspace(session_id)

    # Pre-create the GraphRAG core instance for this session
    from ...core.registry import get_core
    get_core(session_id)

    return CreateSessionResponse(
        session_id=session_id,
        workspace_path=str(workspace_path),
        status="created",
    )


@router.get("/", response_model=SessionListResponse)
async def list_sessions() -> SessionListResponse:
    """
    List all existing sessions.

    Returns list of sessions with their workspace info.
    """
    manager = get_workspace_manager()
    workspaces = manager.list_workspaces()

    return SessionListResponse(
        sessions=[
            SessionInfo(
                session_id=w["session_id"],
                workspace_path=w["path"],
                exists=w["exists"],
            )
            for w in workspaces
        ],
        total=len(workspaces),
    )


@router.delete("/{session_id}", response_model=CleanupResponse)
async def cleanup_session(session_id: str) -> CleanupResponse:
    """
    Clean up a session's workspace and release resources.

    This will:
    - Delete the session's workspace directory (including all indexed data)
    - Remove the session's GraphRAG core instance from registry

    Args:
        session_id: The session ID to clean up

    Returns cleanup results.
    """
    if session_id == "default":
        raise HTTPException(status_code=400, detail="Cannot cleanup default session")

    manager = get_workspace_manager()

    # Check if workspace exists
    if not manager.workspace_exists(session_id):
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Clean up workspace
    try:
        result = manager.cleanup_workspace(session_id)

        # Remove core instance from registry
        GraphRAGRegistry.reset(session_id)

        return CleanupResponse(
            session_id=session_id,
            status="deleted",
            deleted_files=result.get("deleted_files", 0),
            deleted_dirs=result.get("deleted_dirs", 0),
            workspace_path=result.get("workspace_path", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/{session_id}/exists")
async def check_session(session_id: str) -> dict:
    """
    Check if a session exists.

    Args:
        session_id: The session ID to check

    Returns whether the session workspace exists.
    """
    manager = get_workspace_manager()
    exists = manager.workspace_exists(session_id)
    return {
        "session_id": session_id,
        "exists": exists,
    }
