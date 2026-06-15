"""HTTP routes for V2.25-V2.30 architecture intent public contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.architecture_intent.service import ArchitectureIntentService
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Architecture Intent"], dependencies=[Depends(verify_knowledge_access)])


class ArchitectureIntentBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)
    mode: str = Field(default="architecture_review")


class ArchitectureIntentGovernanceRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)
    target_type: str
    target_id: str
    note: str = Field(default="")
    reviewer: str = Field(default="local")


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/intent/build")
async def build_architecture_intent(workspace_id: str, codebase_id: str, request: ArchitectureIntentBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureIntentService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_pipeline(codebase_id, snapshot_id=request.snapshot_id, mode=request.mode)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"architecture_intent": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=payload.get("artifact_refs", []),
        next_actions=payload.get("next_actions", []),
        data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", []), next_actions=payload.get("next_actions", [])),
    )


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/intent/report")
async def read_architecture_intent_report(workspace_id: str, codebase_id: str):
    return _read_payload(workspace_id, codebase_id, "architecture_intent_report", lambda service: service.read_report(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/intent/context-pack")
async def read_architecture_context_pack_v4(workspace_id: str, codebase_id: str):
    return _read_payload(workspace_id, codebase_id, "architecture_context_pack_v4", lambda service: service.read_context_pack(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/intent/verification")
async def read_diagram_code_verification(workspace_id: str, codebase_id: str):
    return _read_payload(workspace_id, codebase_id, "diagram_code_verification", lambda service: service.read_verification(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/intent/proof-graph")
async def read_architecture_proof_graph(workspace_id: str, codebase_id: str):
    return _read_payload(workspace_id, codebase_id, "architecture_proof_graph", lambda service: service.read_proof_graph(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/intent/governance")
async def read_architecture_intent_governance(workspace_id: str, codebase_id: str):
    return _read_payload(workspace_id, codebase_id, "architecture_intent_governance", lambda service: service.read_governance(codebase_id))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/intent/confirm")
async def confirm_architecture_intent(workspace_id: str, codebase_id: str, request: ArchitectureIntentGovernanceRequest):
    return _governance_payload(workspace_id, codebase_id, request, action="confirm")


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/intent/revoke")
async def revoke_architecture_intent(workspace_id: str, codebase_id: str, request: ArchitectureIntentGovernanceRequest):
    return _governance_payload(workspace_id, codebase_id, request, action="revoke")


def _read_payload(workspace_id: str, codebase_id: str, key: str, reader):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureIntentService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = reader(service)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {key: payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=payload.get("artifact_refs", []),
        data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])),
    )


def _governance_payload(workspace_id: str, codebase_id: str, request: ArchitectureIntentGovernanceRequest, *, action: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureIntentService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        if action == "confirm":
            payload = service.confirm(
                codebase_id,
                snapshot_id=request.snapshot_id,
                target_type=request.target_type,
                target_id=request.target_id,
                note=request.note,
                reviewer=request.reviewer,
            )
        else:
            payload = service.revoke(
                codebase_id,
                snapshot_id=request.snapshot_id,
                target_type=request.target_type,
                target_id=request.target_id,
                note=request.note,
                reviewer=request.reviewer,
            )
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"architecture_intent_governance": payload}
    return envelope(
        workspace_id=str(meta["workspace_id"]),
        artifact_refs=payload.get("artifact_refs", []),
        data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])),
    )


def _with_v2(workspace_id: str, codebase_id: str, snapshot_id: str | None, data: dict[str, Any], refs: list[dict[str, Any]], *, warnings: list[Any] | None = None, next_actions: list[str] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=refs, warnings=warnings, next_actions=next_actions)
    return payload


def _error(status_code: int, workspace_id: str, codebase_id: str, snapshot_id: str | None, error: str):
    data = {
        "error": {"code": error, "message": error, "retryable": False},
        "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=error, message=error),
    }
    return JSONResponse(status_code=status_code, content={"workspace_id": workspace_id, "status": "blocked", "data": data, "warnings": [error]})
