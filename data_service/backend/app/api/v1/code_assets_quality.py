"""HTTP routes for V2.1 code quality governance."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.quality.persistence import quality_artifact_refs
from data_service.code_assets.quality.service import CodeQualityService, public_quality_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Intelligence Quality"], dependencies=[Depends(verify_knowledge_access)])


class QualityFeedbackRequest(BaseModel):
    target_type: str
    target_id: str
    action: str
    rule_type: str
    severity: str = Field(default="medium")
    reason: str = Field(default="")
    suggested_value: str = Field(default="")
    metadata: dict[str, Any] = Field(default_factory=dict)


class QualityRuleReviewRequest(BaseModel):
    status: str
    reviewer: str = Field(default="")
    note: str = Field(default="")


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


def _with_v2(*, workspace_id: str, codebase_id: str, data: dict[str, Any], artifact_refs: list[dict[str, Any]] | None = None, warnings: list[Any] | None = None, unresolved: list[Any] | None = None, next_actions: list[str] | None = None) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=artifact_refs, warnings=warnings, unresolved=unresolved, next_actions=next_actions)
    return payload


def _error(*, status_code: int, workspace_id: str, codebase_id: str, error: str, next_actions: list[str] | None = None) -> JSONResponse:
    code = _quality_error_code(error)
    message = _quality_error_message(error)
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": message,
            "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=code, message=message, next_actions=next_actions),
        },
    )


@router.post("/{workspace_id}/codebases/{codebase_id}/quality/feedback")
async def record_code_quality_feedback(workspace_id: str, codebase_id: str, request: QualityFeedbackRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeQualityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.record_feedback(
            codebase_id,
            target_type=request.target_type,
            target_id=request.target_id,
            action=request.action,
            rule_type=request.rule_type,
            severity=request.severity,
            reason=request.reason,
            suggested_value=request.suggested_value,
            metadata=request.metadata,
        )
    except (FileNotFoundError, ValueError) as exc:
        return _error(status_code=400 if isinstance(exc, ValueError) else 404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, error=str(exc))
    data = public_quality_payload(result)
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result["artifact_refs"], next_actions=["knowledge_code_quality_rules_build"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, data=data, artifact_refs=result["artifact_refs"], next_actions=["knowledge_code_quality_rules_build"]))


@router.get("/{workspace_id}/codebases/{codebase_id}/quality/summary")
async def read_code_quality_summary(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeQualityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.summary(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, error=str(exc))
    data = public_quality_payload(result)
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result["artifact_refs"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, data=data, artifact_refs=result["artifact_refs"]))


@router.post("/{workspace_id}/codebases/{codebase_id}/quality/rules/build")
async def build_code_quality_rules(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeQualityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_rules(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, error=str(exc))
    data = public_quality_payload(result)
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result["artifact_refs"], next_actions=["knowledge_code_quality_rule_review"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, data=data, artifact_refs=result["artifact_refs"], next_actions=["knowledge_code_quality_rule_review"]))


@router.post("/{workspace_id}/codebases/{codebase_id}/quality/rules/{rule_id}/review")
async def review_code_quality_rule(workspace_id: str, codebase_id: str, rule_id: str, request: QualityRuleReviewRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeQualityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.review_rule(codebase_id, rule_id, status=request.status, reviewer=request.reviewer, note=request.note)
    except (FileNotFoundError, ValueError) as exc:
        return _error(status_code=400 if isinstance(exc, ValueError) else 404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, error=str(exc))
    data = public_quality_payload(result)
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result["artifact_refs"], next_actions=["knowledge_code_quality_plan"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, data=data, artifact_refs=result["artifact_refs"], next_actions=["knowledge_code_quality_plan"]))


@router.post("/{workspace_id}/codebases/{codebase_id}/quality/plan")
async def build_code_quality_plan(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodeQualityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_plan(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, error=str(exc))
    data = public_quality_payload(result)
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result["artifact_refs"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, data=data, artifact_refs=result["artifact_refs"]))


def _quality_error_code(error: str) -> str:
    for code in ["UNSUPPORTED_TARGET_TYPE", "UNSUPPORTED_RULE_TYPE", "UNSUPPORTED_REVIEW_STATUS", "QUALITY_RULE_NOT_FOUND", "QUALITY_TARGET_NOT_FOUND", "QUALITY_FEEDBACK_NOT_FOUND", "SNAPSHOT_NOT_FOUND"]:
        if code in error:
            return code
    return "CODE_QUALITY_ERROR"


def _quality_error_message(error: str) -> str:
    code = _quality_error_code(error)
    if code == "QUALITY_TARGET_NOT_FOUND":
        return "Quality target was not found in persisted V2 project intelligence artifacts"
    if code == "QUALITY_FEEDBACK_NOT_FOUND":
        return "No quality feedback records exist for this codebase"
    return code if code != "CODE_QUALITY_ERROR" else (error or "Code quality request failed")
