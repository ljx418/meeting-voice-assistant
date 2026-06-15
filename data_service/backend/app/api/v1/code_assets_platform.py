"""HTTP routes for V2.18 Platform Product Console."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.platform.ci import PlatformCIReadinessService, public_ci_readiness_payload, public_release_report_payload
from data_service.code_assets.platform.contracts import ArtifactContractService, public_contract_payload
from data_service.code_assets.platform.console import (
    PlatformConsoleService,
    public_platform_console_payload,
    public_platform_console_view_payload,
)
from data_service.code_assets.platform.governance import PlatformGovernanceService, public_governance_payload
from data_service.code_assets.platform.incremental import PlatformIncrementalService, public_incremental_payload
from data_service.code_assets.platform.providers import PlatformProviderService, public_provider_payload
from data_service.code_assets.platform.tool_catalog import ToolCatalogService, public_tool_catalog_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Intelligence Platform"], dependencies=[Depends(verify_knowledge_access)])


class PlatformConsoleBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class PlatformIncrementalBuildRequest(BaseModel):
    from_snapshot_id: str
    to_snapshot_id: str


class PlatformProvidersBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class PlatformGovernanceFeedbackRequest(BaseModel):
    target_type: str
    target_id: str
    action: str
    rule_type: str = Field(default="read_time_overlay")
    severity: str = Field(default="medium")
    reason: str = Field(default="")
    suggested_value: str = Field(default="")


class PlatformGovernanceRuleReviewRequest(BaseModel):
    status: str
    reviewer: str = Field(default="")
    note: str = Field(default="")


class PlatformCIReadinessBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)
    command_evidence: dict[str, Any] = Field(default_factory=dict)
    warning_budget: int = Field(default=700)


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/console/build")
async def build_platform_console(workspace_id: str, codebase_id: str, request: PlatformConsoleBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformConsoleService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_console(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"platform_console": public_platform_console_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_console_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", []), next_actions=payload.get("next_actions", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/console")
async def read_platform_console(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformConsoleService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_console(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"platform_console": public_platform_console_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", []), next_actions=payload.get("next_actions", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/console/views/{view_id}")
async def read_platform_console_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformConsoleService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_console_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"platform_console_view": public_platform_console_view_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/contracts/build")
async def build_platform_contracts(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArtifactContractService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_contracts(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"artifact_contracts": public_contract_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_contracts_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/contracts")
async def read_platform_contracts(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArtifactContractService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_contracts(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"artifact_contracts": public_contract_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog/build")
async def build_platform_tool_catalog(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ToolCatalogService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        from data_service.mcp_tool_registry import all_tool_specs

        payload = service.build_tool_catalog(codebase_id, all_tool_specs())
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"tool_catalog": public_tool_catalog_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_tool_catalog_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/tool-catalog")
async def read_platform_tool_catalog(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ToolCatalogService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_tool_catalog(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"tool_catalog": public_tool_catalog_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/incremental/build")
async def build_platform_incremental(workspace_id: str, codebase_id: str, request: PlatformIncrementalBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformIncrementalService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_incremental_plan(codebase_id, from_snapshot_id=request.from_snapshot_id, to_snapshot_id=request.to_snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.to_snapshot_id, str(exc))
    data = {"incremental_build": public_incremental_payload(payload)}
    plan = payload.get("plan", {})
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_incremental_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, plan.get("to_snapshot_id"), data, payload.get("artifact_refs", []), warnings=plan.get("warnings", []), next_actions=["knowledge_code_platform_incremental_read"]))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/incremental")
async def read_platform_incremental(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformIncrementalService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_incremental_plan(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"incremental_build": public_incremental_payload(payload)}
    plan = payload.get("plan", {})
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, plan.get("to_snapshot_id"), data, payload.get("artifact_refs", []), warnings=plan.get("warnings", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/providers/build")
async def build_platform_providers(workspace_id: str, codebase_id: str, request: PlatformProvidersBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformProviderService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_provider_artifacts(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"provider_plugins": public_provider_payload(payload)}
    capabilities = payload.get("provider_capabilities", {})
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_providers_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, capabilities.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=capabilities.get("warnings", []), next_actions=["knowledge_code_platform_providers_read"]))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/providers")
async def read_platform_providers(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformProviderService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_provider_artifacts(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"provider_plugins": public_provider_payload(payload)}
    capabilities = payload.get("provider_capabilities", {})
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, capabilities.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=capabilities.get("warnings", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/governance/feedback")
async def record_platform_governance_feedback(workspace_id: str, codebase_id: str, request: PlatformGovernanceFeedbackRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformGovernanceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.record_feedback(
            codebase_id,
            target_type=request.target_type,
            target_id=request.target_id,
            action=request.action,
            rule_type=request.rule_type,
            severity=request.severity,
            reason=request.reason,
            suggested_value=request.suggested_value,
        )
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"platform_governance": public_governance_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_governance_rules_build"], data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_governance_rules_build"]))


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/build")
async def build_platform_governance_rules(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformGovernanceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_rules(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"platform_governance": public_governance_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_governance_overlay"], data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_governance_overlay"]))


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/governance/rules/{rule_id}/review")
async def review_platform_governance_rule(workspace_id: str, codebase_id: str, rule_id: str, request: PlatformGovernanceRuleReviewRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformGovernanceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.review_rule(codebase_id, rule_id, status=request.status, reviewer=request.reviewer, note=request.note)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"platform_governance": public_governance_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/governance/overlay")
async def read_platform_governance_overlay(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformGovernanceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        report = service.read_overlay_report(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    payload = {"overlay_report": report, "artifact_refs": report.get("artifact_refs", [])}
    data = {"platform_governance": public_governance_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", []), warnings=report.get("warnings", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/platform/ci/readiness/build")
async def build_platform_ci_readiness(workspace_id: str, codebase_id: str, request: PlatformCIReadinessBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformCIReadinessService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_readiness(codebase_id, snapshot_id=request.snapshot_id, command_evidence=request.command_evidence, warning_budget=request.warning_budget)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"ci_readiness": public_ci_readiness_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_platform_ci_readiness_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/ci/readiness")
async def read_platform_ci_readiness(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformCIReadinessService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_readiness(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"ci_readiness": public_ci_readiness_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", []), warnings=payload.get("warnings", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/platform/ci/release-report")
async def read_platform_ci_release_report(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = PlatformCIReadinessService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_release_report(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"ci_release_report": public_release_report_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


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
