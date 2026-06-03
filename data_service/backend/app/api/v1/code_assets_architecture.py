"""HTTP routes for V2.3 Architecture Abstraction code assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.architecture.persistence import architecture_artifact_refs, code_architecture_artifact_refs
from data_service.code_assets.architecture.service import ArchitectureService, public_architecture_payload, public_code_architecture_payload
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Intelligence Architecture"], dependencies=[Depends(verify_knowledge_access)])


class ArchitectureBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/sources/scan")
@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/build")
async def build_architecture_model(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        bundle = service.build_architecture(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = architecture_artifact_refs(codebase_id)
    data = {"architecture": {"summary": bundle["summary"]}}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_architecture_model_read", "knowledge_architecture_findings"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(bundle["summary"]["snapshot_id"]), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/code/build")
async def build_code_architecture_roles(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_code_architecture(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = code_architecture_artifact_refs(codebase_id)
    data = {"code_architecture": {"summary": payload["summary"]}}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_roles"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload["snapshot_id"]), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/code/roles")
async def read_code_architecture_roles(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = public_code_architecture_payload(service.read_code_architecture(codebase_id))
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = code_architecture_artifact_refs(codebase_id)
    data = {"code_architecture": payload}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/code/patterns")
async def read_code_architecture_patterns(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = public_code_architecture_payload(service.read_code_architecture(codebase_id))
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = code_architecture_artifact_refs(codebase_id)
    data = {"patterns": payload.get("patterns", []), "boundaries": payload.get("boundaries", []), "summary": payload.get("summary", {})}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/code/views/{view_id}")
async def read_code_architecture_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        view = service.read_code_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = code_architecture_artifact_refs(codebase_id)
    data = {"view": view}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(view["snapshot_id"]), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/model")
async def read_architecture_model(workspace_id: str, codebase_id: str):
    return _read_architecture(workspace_id, codebase_id, "architecture")


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/alignment")
async def read_architecture_alignment(workspace_id: str, codebase_id: str):
    return _read_architecture(workspace_id, codebase_id, "alignment")


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/findings")
async def read_architecture_findings(workspace_id: str, codebase_id: str):
    return _read_architecture(workspace_id, codebase_id, "findings")


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/views/{view_id}")
async def read_architecture_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        view = service.read_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_artifact_refs(codebase_id)
    data = {"view": view}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(view["snapshot_id"]), data=data, artifact_refs=refs))


def _read_architecture(workspace_id: str, codebase_id: str, payload_kind: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        bundle = service.read_architecture(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    payload = public_architecture_payload(bundle)
    data: dict[str, Any] = {"architecture": payload}
    if payload_kind == "alignment":
        data = {"alignment": payload["alignment"]}
    if payload_kind == "findings":
        data = {"findings": payload["findings"], "summary": payload["summary"]}
    refs = architecture_artifact_refs(codebase_id)
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(bundle["model"]["snapshot_id"]), data=data, artifact_refs=refs))


def _with_v2(*, workspace_id: str, data: dict[str, Any], codebase_id: str, snapshot_id: str | None, artifact_refs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=artifact_refs)
    return payload


def _error(*, status_code: int, workspace_id: str, codebase_id: str, snapshot_id: str | None, error: str) -> JSONResponse:
    code = _architecture_error_code(error)
    message = _architecture_error_message(error)
    return JSONResponse(status_code=status_code, content={"detail": message, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=code, message=message, next_actions=["knowledge_codebase_snapshot", "knowledge_code_graph_build", "knowledge_architecture_model_build"])})


def _architecture_error_code(error: str) -> str:
    if "ARCHITECTURE_SOURCE_NOT_FOUND" in error:
        return "ARCHITECTURE_SOURCE_NOT_FOUND"
    if "ARCHITECTURE_MODEL_NOT_BUILT" in error:
        return "ARCHITECTURE_MODEL_NOT_BUILT"
    if "CODE_ARCHITECTURE_NOT_BUILT" in error:
        return "CODE_ARCHITECTURE_NOT_BUILT"
    if "INVENTORY_NOT_FOUND" in error:
        return "INVENTORY_NOT_FOUND"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return "SYMBOL_INDEX_NOT_FOUND"
    if "DRAWIO_PARSE_FAILED" in error:
        return "DRAWIO_PARSE_FAILED"
    if "SNAPSHOT_NOT_FOUND" in error:
        return "SNAPSHOT_NOT_FOUND"
    return "ARCHITECTURE_ERROR"


def _architecture_error_message(error: str) -> str:
    if "ARCHITECTURE_SOURCE_NOT_FOUND" in error:
        return "No architecture source was found in the codebase snapshot"
    if "ARCHITECTURE_MODEL_NOT_BUILT" in error:
        return "Architecture Model has not been built"
    if "CODE_ARCHITECTURE_NOT_BUILT" in error:
        return "Code-derived Architecture Model has not been built"
    if "INVENTORY_NOT_FOUND" in error:
        return "Public surface inventory has not been built"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return "Python symbol index has not been built"
    return error or "Architecture request failed"
