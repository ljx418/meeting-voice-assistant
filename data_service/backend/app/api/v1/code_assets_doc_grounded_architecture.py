"""HTTP routes for V2.37 document-grounded architecture reconstruction."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.doc_grounded_architecture.service import DocGroundedArchitectureService
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Doc Grounded Architecture"], dependencies=[Depends(verify_knowledge_access)])


class DocGroundedBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)
    mode: str = Field(default="architecture_review")
    max_tokens: int = Field(default=12000)


class DocGroundedBriefRequest(BaseModel):
    mode: str = Field(default="architecture_review")
    role: str = Field(default="coding_agent")
    max_tokens: int = Field(default=12000)


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/build")
async def build_doc_grounded_architecture(workspace_id: str, codebase_id: str, request: DocGroundedBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = DocGroundedArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_pipeline(codebase_id, snapshot_id=request.snapshot_id, mode=request.mode, max_tokens=request.max_tokens)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    return _ok(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), "doc_grounded_architecture", payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/report")
async def read_doc_grounded_report(workspace_id: str, codebase_id: str):
    return _read(workspace_id, codebase_id, "doc_grounded_architecture_report", lambda service: service.read_reconstruction_report(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/verification")
async def read_doc_grounded_verification(workspace_id: str, codebase_id: str):
    return _read(workspace_id, codebase_id, "doc_grounded_verification", lambda service: service.read_verification(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/view")
async def read_doc_grounded_view(workspace_id: str, codebase_id: str, view: str = "html"):
    return _read(workspace_id, codebase_id, "doc_grounded_architecture_view", lambda service: service.read_report_view(codebase_id, view=view))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/brief")
async def create_doc_grounded_brief(workspace_id: str, codebase_id: str, request: DocGroundedBriefRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = DocGroundedArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.create_agent_brief(codebase_id, mode=request.mode, role=request.role, max_tokens=request.max_tokens)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    return _ok(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), "doc_grounded_architecture_brief", payload)


def _read(workspace_id: str, codebase_id: str, key: str, reader):
    workspace, meta = _workspace_for(workspace_id)
    service = DocGroundedArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = reader(service)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    return _ok(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), key, payload)


def _ok(workspace_id: str, codebase_id: str, snapshot_id: str | None, key: str, payload: dict[str, Any]):
    data = {key: payload}
    data["v2"] = v2_success_envelope(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        data={key: payload},
        artifact_refs=payload.get("artifact_refs", []),
        warnings=payload.get("warnings", []),
        unresolved=payload.get("unresolved", []),
        next_actions=payload.get("next_actions", []),
    )
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=data, warnings=payload.get("warnings", []))


def _error(status_code: int, workspace_id: str, codebase_id: str, snapshot_id: str | None, error: str):
    data = {
        "error": {"code": error, "message": error, "retryable": False},
        "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=error, message=error),
    }
    return JSONResponse(status_code=status_code, content={"workspace_id": workspace_id, "status": "blocked", "data": data, "warnings": [error]})
