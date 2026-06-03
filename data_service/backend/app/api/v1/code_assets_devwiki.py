"""HTTP routes for V2.1 DevWiki code assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.devwiki.persistence import devwiki_artifact_refs
from data_service.code_assets.devwiki.service import (
    CodebaseDevWikiService,
    public_devwiki_index_payload,
    public_devwiki_page_payload,
)
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Intelligence DevWiki"], dependencies=[Depends(verify_knowledge_access)])


class DevWikiBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None, description="Optional snapshot identifier; defaults to latest")


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


def _with_v2(
    *,
    workspace_id: str,
    data: dict[str, Any],
    codebase_id: str | None = None,
    snapshot_id: str | None = None,
    artifact_refs: list[dict[str, Any]] | None = None,
    warnings: list[Any] | None = None,
    unresolved: list[Any] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        data=data,
        artifact_refs=artifact_refs,
        warnings=warnings,
        unresolved=unresolved,
        next_actions=next_actions,
    )
    return payload


def _http_v2_error(
    *,
    status_code: int,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str | None,
    code: str,
    message: str,
    next_actions: list[str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": message,
            "v2": v2_error_envelope(
                workspace_id=workspace_id,
                codebase_id=codebase_id,
                snapshot_id=snapshot_id,
                code=code,
                message=message,
                next_actions=next_actions,
            ),
        },
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/devwiki/build")
async def build_codebase_devwiki(workspace_id: str, codebase_id: str, request: DevWikiBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodebaseDevWikiService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_devwiki(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=request.snapshot_id,
            code=_devwiki_error_code(str(exc)),
            message=_devwiki_error_message(str(exc)),
            next_actions=["knowledge_project_overview", "knowledge_project_inventory", "knowledge_code_symbol_search", "knowledge_public_surface_trace"],
        )
    except ValueError as exc:
        return _http_v2_error(
            status_code=400,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=request.snapshot_id,
            code=str(exc),
            message=str(exc),
            next_actions=["knowledge_codebase_describe"],
        )
    index = public_devwiki_index_payload(result["index"])
    refs = index.get("artifact_refs", devwiki_artifact_refs(codebase_id))
    data = {"devwiki": index}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        next_actions=["knowledge_devwiki_read"],
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(index["snapshot_id"]),
            data=data,
            artifact_refs=refs,
            next_actions=["knowledge_devwiki_read"],
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/devwiki/pages")
async def list_codebase_devwiki_pages(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodebaseDevWikiService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        index = service.list_pages(codebase_id)
    except FileNotFoundError as exc:
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=None,
            code=_devwiki_error_code(str(exc)),
            message=_devwiki_error_message(str(exc)),
            next_actions=["knowledge_devwiki_build"],
        )
    refs = index.get("artifact_refs", devwiki_artifact_refs(codebase_id))
    data = {"devwiki": public_devwiki_index_payload(index)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(index["snapshot_id"]),
            data=data,
            artifact_refs=refs,
        ),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/devwiki/pages/{page_slug}")
async def read_codebase_devwiki_page(workspace_id: str, codebase_id: str, page_slug: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodebaseDevWikiService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        page = service.read_page(codebase_id, page_slug)
    except FileNotFoundError as exc:
        return _http_v2_error(
            status_code=404,
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=None,
            code=_devwiki_error_code(str(exc)),
            message=_devwiki_error_message(str(exc)),
            next_actions=["knowledge_devwiki_build"],
        )
    refs = page.get("artifact_refs", devwiki_artifact_refs(codebase_id, page_slug))
    data = {"page": public_devwiki_page_payload(page)}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=refs,
        data=_with_v2(
            workspace_id=str(meta["workspace_id"]),
            codebase_id=codebase_id,
            snapshot_id=str(page["snapshot_id"]),
            data=data,
            artifact_refs=refs,
            unresolved=page.get("needs_review", []),
        ),
    )


def _devwiki_error_code(error: str) -> str:
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    if "V20_ARTIFACT_MISSING" in error:
        return "V20_ARTIFACT_MISSING"
    if "DEVWIKI_PAGE_NOT_FOUND" in error:
        return "DEVWIKI_PAGE_NOT_FOUND"
    if "DEVWIKI_NOT_FOUND" in error:
        return "DEVWIKI_NOT_FOUND"
    if "codebase" in error.lower():
        return "CODEBASE_NOT_FOUND"
    return "DEVWIKI_ERROR"


def _devwiki_error_message(error: str) -> str:
    code = _devwiki_error_code(error)
    if code == "SNAPSHOT_NOT_FOUND":
        return "No codebase snapshot exists; create one before building DevWiki"
    if code == "V20_ARTIFACT_MISSING":
        return "Required V2.0 artifact is missing; build V2.0 inventory, symbols, trace, and overview before DevWiki"
    if code == "DEVWIKI_PAGE_NOT_FOUND":
        return "DevWiki page not found"
    if code == "DEVWIKI_NOT_FOUND":
        return "DevWiki has not been built"
    return error or "DevWiki request failed"
