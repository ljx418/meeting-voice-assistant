"""Target HTTP routes for V2 codebase assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_common import bounded_int, envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Intelligence"], dependencies=[Depends(verify_knowledge_access)])


class CodebaseImportRequest(BaseModel):
    path: str = Field(..., description="Local codebase root path")
    codebase_id: Optional[str] = Field(default=None, description="Optional stable codebase identifier")
    name: Optional[str] = Field(default=None, description="Optional display name")
    metadata: dict[str, Any] = Field(default_factory=dict)
    scan_policy: dict[str, Any] = Field(default_factory=dict)


class CodebaseArchiveRequest(BaseModel):
    reason: str = ""


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _registry_for(workspace_id: str) -> tuple[WorkspaceRuntime, Path, dict[str, Any], CodebaseRegistry]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    registry = CodebaseRegistry(workspace, workspace_id=str(meta["workspace_id"]))
    return runtime, workspace, meta, registry


def _blocked(*, workspace_id: str, message: str, code: str, next_actions: list[str] | None = None) -> dict[str, Any]:
    return envelope(
        workspace_id=workspace_id,
        status="blocked",
        warnings=[message],
        next_actions=next_actions,
        data={"error": {"code": code, "message": message, "retryable": False}},
    )


def _blocked_from_error(*, workspace_id: str, error: str) -> dict[str, Any]:
    code = _error_code(error)
    return _blocked(
        workspace_id=workspace_id,
        message=_error_message(code, error),
        code=code,
        next_actions=["knowledge_codebase_import"],
    )


@router.post("/{workspace_id}/codebases")
async def import_codebase(workspace_id: str, request: CodebaseImportRequest) -> dict[str, Any]:
    _runtime_obj, _workspace, meta, registry = _registry_for(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message="Workspace is archived and cannot import codebases",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    try:
        result = registry.import_codebase(
            path=request.path,
            codebase_id=request.codebase_id,
            name=request.name,
            metadata=request.metadata,
            scan_policy=request.scan_policy,
        )
    except ValueError as exc:
        return _blocked_from_error(workspace_id=str(meta["workspace_id"]), error=str(exc))

    asset = result["asset"]
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=[{"type": "codebase", "codebase_id": asset.codebase_id, "artifact_ref": f"codebase://{asset.codebase_id}"}],
        next_actions=["knowledge_codebase_snapshot", "knowledge_project_inventory"],
        data={"codebase": asset.public_dict(), "created": bool(result["created"])},
    )


@router.get("/{workspace_id}/codebases")
async def list_codebases(workspace_id: str, include_archived: bool = False, limit: int = 100) -> dict[str, Any]:
    _runtime_obj, _workspace, meta, registry = _registry_for(workspace_id)
    bounded_limit = bounded_int(limit, default=100, minimum=1, maximum=500, field="limit")
    items = [asset.public_dict() for asset in registry.list_codebases(include_archived=include_archived, limit=bounded_limit)]
    return envelope(workspace_id=str(meta["workspace_id"]), data={"items": items})


@router.get("/{workspace_id}/codebases/{codebase_id}")
async def describe_codebase(workspace_id: str, codebase_id: str) -> dict[str, Any]:
    _runtime_obj, _workspace, meta, registry = _registry_for(workspace_id)
    try:
        asset = registry.describe(codebase_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown codebase_id: {codebase_id}") from exc
    except ValueError as exc:
        return _blocked_from_error(workspace_id=str(meta["workspace_id"]), error=str(exc))
    return envelope(workspace_id=str(meta["workspace_id"]), data={"codebase": asset.public_dict()})


@router.post("/{workspace_id}/codebases/{codebase_id}/archive")
async def archive_codebase(workspace_id: str, codebase_id: str, request: CodebaseArchiveRequest) -> dict[str, Any]:
    _runtime_obj, _workspace, meta, registry = _registry_for(workspace_id)
    if meta.get("status") == "archived":
        return _blocked(
            workspace_id=str(meta["workspace_id"]),
            message="Workspace is archived and cannot archive codebases",
            code="workspace_archived",
            next_actions=["knowledge_workspace_describe"],
        )
    try:
        asset = registry.archive(codebase_id, reason=request.reason)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown codebase_id: {codebase_id}") from exc
    except ValueError as exc:
        return _blocked_from_error(workspace_id=str(meta["workspace_id"]), error=str(exc))
    return envelope(workspace_id=str(meta["workspace_id"]), data={"codebase": asset.public_dict()})


def _error_code(error: str) -> str:
    if "outside allowed roots" in error.lower():
        return "path_not_allowed"
    if error in {"CODEBASE_PATH_NOT_FOUND", "CODEBASE_PATH_NOT_DIRECTORY", "CODEBASE_ID_CONFLICT"}:
        return error
    if "codebase_id" in error.lower():
        return "INVALID_CODEBASE_ID"
    return "CODEBASE_IMPORT_FAILED"


def _error_message(code: str, error: str) -> str:
    if code == "path_not_allowed":
        return error
    if code == "CODEBASE_PATH_NOT_FOUND":
        return "Codebase path does not exist"
    if code == "CODEBASE_PATH_NOT_DIRECTORY":
        return "Codebase path is not a directory"
    if code == "CODEBASE_ID_CONFLICT":
        return "codebase_id already exists for a different root path"
    return error or "Codebase import failed"
