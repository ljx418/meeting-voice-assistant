"""HTTP routes for V2.11 Coding Agent actionability."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.coding_agent.persistence import actionability_artifact_refs
from data_service.code_assets.coding_agent.service import (
    CodingAgentActionabilityService,
    public_large_project_advisor_payload,
    public_actionability_payload,
    public_impact_payload,
    public_incremental_diff_payload,
    public_incremental_timeline_payload,
    public_patch_plan_payload,
    public_patch_preview_payload,
    public_provider_registry_payload,
    public_runtime_registry_payload,
    public_runtime_profile_run_payload,
    public_runtime_profiles_payload,
    public_runtime_run_payload,
    public_semantic_payload,
    public_task_plan_payload,
    public_workbench_context_export_payload,
    public_workbench_payload,
    public_workbench_v2_payload,
    public_workbench_view_payload,
)
from data_service.code_assets.coding_agent_navigation.service import (
    CodingAgentNavigationService,
    public_task_navigation_index_payload,
    public_task_navigation_query_payload,
    public_task_handoff_payload,
    public_task_impact_payload,
    public_task_reading_pack_payload,
    public_task_closure_payload,
    public_task_relationship_graph_payload,
    public_task_test_selection_payload,
    task_impact_refs,
    task_handoff_refs,
    task_closure_refs,
    task_navigation_refs,
    task_query_refs,
    task_reading_pack_refs,
    task_relationship_refs,
)
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Coding Agent Actionability"], dependencies=[Depends(verify_knowledge_access)])


class ActionabilityBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class ProviderRegistryBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class SemanticBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class ImpactRequest(BaseModel):
    task: str
    snapshot_id: Optional[str] = Field(default=None)
    focus_paths: list[str] = Field(default_factory=list)


class TaskPlanRequest(BaseModel):
    task: str
    snapshot_id: Optional[str] = Field(default=None)
    focus_paths: list[str] = Field(default_factory=list)
    max_items: int = Field(default=12, ge=1, le=50)


class PatchPlanRequest(BaseModel):
    task: str
    snapshot_id: Optional[str] = Field(default=None)
    task_plan_id: Optional[str] = Field(default=None)
    focus_paths: list[str] = Field(default_factory=list)
    max_options: int = Field(default=3, ge=1, le=5)


class PatchPreviewRequest(BaseModel):
    task: str = Field(default="")
    snapshot_id: Optional[str] = Field(default=None)
    patch_plan_id: Optional[str] = Field(default=None)


class RuntimeCommandsRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)
    patch_plan_id: Optional[str] = Field(default=None)


class RuntimeRunRequest(BaseModel):
    command_id: str
    snapshot_id: Optional[str] = Field(default=None)
    patch_plan_id: Optional[str] = Field(default=None)


class RuntimeProfilesRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)
    patch_plan_id: Optional[str] = Field(default=None)


class RuntimeProfileRunRequest(BaseModel):
    profile_id: str
    snapshot_id: Optional[str] = Field(default=None)
    patch_plan_id: Optional[str] = Field(default=None)


class IncrementalDiffRequest(BaseModel):
    from_snapshot_id: str
    to_snapshot_id: str
    task: Optional[str] = Field(default=None)


class WorkbenchBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class WorkbenchV2BuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class LargeProjectAdvisorBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class WorkbenchContextExportRequest(BaseModel):
    mode: str = Field(default="coding_agent")
    max_items: int = Field(default=25, ge=1, le=100)


class TaskNavigationBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)


class TaskNavigationPrepareRequest(BaseModel):
    task: str
    snapshot_id: Optional[str] = Field(default=None)
    limit: int = Field(default=25, ge=1, le=100)


class TaskImpactRequest(BaseModel):
    task: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
    snapshot_id: Optional[str] = Field(default=None)
    max_items: int = Field(default=50, ge=1, le=200)


class TaskReadingPackRequest(BaseModel):
    task: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
    snapshot_id: Optional[str] = Field(default=None)
    max_tokens: int = Field(default=12000, ge=100, le=64000)
    role: str = Field(default="coding_agent")
    max_items: int = Field(default=50, ge=1, le=200)


class AgentHandoffRequest(BaseModel):
    target_agent: str = Field(default="generic")
    pack_id: Optional[str] = Field(default=None)
    task: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
    snapshot_id: Optional[str] = Field(default=None)
    max_tokens: int = Field(default=12000, ge=100, le=64000)
    max_items: int = Field(default=50, ge=1, le=200)


class TaskClosureBuildRequest(BaseModel):
    handoff_id: Optional[str] = Field(default=None)
    task: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
    snapshot_id: Optional[str] = Field(default=None)
    max_tokens: int = Field(default=12000, ge=100, le=64000)
    max_items: int = Field(default=50, ge=1, le=200)


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/providers/build")
async def build_coding_agent_provider_registry(workspace_id: str, codebase_id: str, request: ProviderRegistryBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_provider_registry(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"provider_registry": public_provider_registry_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_provider_registry_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/providers")
async def read_coding_agent_provider_registry(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_provider_registry(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"provider_registry": public_provider_registry_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/semantic/build")
async def build_coding_agent_semantic_provider_index(workspace_id: str, codebase_id: str, request: SemanticBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_semantic_provider_index(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"semantic_provider_index": public_semantic_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_semantic_providers_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload["index"].get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/semantic")
async def read_coding_agent_semantic_provider_index(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_semantic_provider_index(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"semantic_provider_index": public_semantic_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload["index"].get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/actionability/build")
async def build_coding_agent_actionability(workspace_id: str, codebase_id: str, request: ActionabilityBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_actionability(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    refs = actionability_artifact_refs(codebase_id)
    data = {"actionability": public_actionability_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_actionability_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload["index"].get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/actionability")
async def read_coding_agent_actionability(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_actionability(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = actionability_artifact_refs(codebase_id)
    data = {"actionability": public_actionability_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, payload["index"].get("snapshot_id"), data, refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/impact")
async def analyze_coding_agent_impact(workspace_id: str, codebase_id: str, request: ImpactRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.analyze_impact(codebase_id, task=request.task, focus_paths=request.focus_paths, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"impact": public_impact_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_task_plan"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/task-plan")
async def create_coding_agent_task_plan(workspace_id: str, codebase_id: str, request: TaskPlanRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.create_task_plan(codebase_id, task=request.task, focus_paths=request.focus_paths, max_items=request.max_items, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"task_plan": public_task_plan_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans")
async def create_coding_agent_patch_plan(workspace_id: str, codebase_id: str, request: PatchPlanRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.create_patch_plan(codebase_id, task=request.task, focus_paths=request.focus_paths, max_options=request.max_options, snapshot_id=request.snapshot_id, task_plan_id=request.task_plan_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"patch_plan": public_patch_plan_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_patch_plan_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{patch_plan_id}")
async def read_coding_agent_patch_plan(workspace_id: str, codebase_id: str, patch_plan_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_patch_plan(codebase_id, patch_plan_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"patch_plan": public_patch_plan_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-sandbox/previews")
async def create_coding_agent_patch_preview(workspace_id: str, codebase_id: str, request: PatchPreviewRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.create_patch_preview(codebase_id, task=request.task, patch_plan_id=request.patch_plan_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"patch_preview": public_patch_preview_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_patch_preview_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-sandbox/previews/{preview_id}")
async def read_coding_agent_patch_preview(workspace_id: str, codebase_id: str, preview_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_patch_preview(codebase_id, preview_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"patch_preview": public_patch_preview_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-sandbox/previews/{preview_id}/apply")
async def apply_coding_agent_patch_preview(workspace_id: str, codebase_id: str, preview_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    payload = service.apply_patch_preview(codebase_id, preview_id)
    data = {"patch_apply": payload}
    return envelope(workspace_id=str(meta["workspace_id"]), status="blocked", artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/commands")
async def build_coding_agent_runtime_commands(workspace_id: str, codebase_id: str, request: RuntimeCommandsRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_runtime_registry(codebase_id, snapshot_id=request.snapshot_id, patch_plan_id=request.patch_plan_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"runtime_commands": public_runtime_registry_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/commands")
async def read_coding_agent_runtime_commands(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_runtime_registry(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"runtime_commands": public_runtime_registry_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/runs")
async def run_coding_agent_runtime_command(workspace_id: str, codebase_id: str, request: RuntimeRunRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.run_runtime_command(codebase_id, command_id=request.command_id, patch_plan_id=request.patch_plan_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"runtime_run": public_runtime_run_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), status=payload.get("status", "ok"), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/runs/{run_id}")
async def read_coding_agent_runtime_run(workspace_id: str, codebase_id: str, run_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_runtime_run(codebase_id, run_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"runtime_run": public_runtime_run_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profiles/build")
async def build_coding_agent_runtime_profiles(workspace_id: str, codebase_id: str, request: RuntimeProfilesRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_runtime_profiles(codebase_id, snapshot_id=request.snapshot_id, patch_plan_id=request.patch_plan_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"runtime_profiles": public_runtime_profiles_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_runtime_profiles_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profiles")
async def read_coding_agent_runtime_profiles(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_runtime_profiles_v2_16(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"runtime_profiles": public_runtime_profiles_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profile-runs")
async def run_coding_agent_runtime_profile(workspace_id: str, codebase_id: str, request: RuntimeProfileRunRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    payload = service.run_runtime_profile(codebase_id, profile_id=request.profile_id, patch_plan_id=request.patch_plan_id, snapshot_id=request.snapshot_id)
    data = {"runtime_profile_run": public_runtime_profile_run_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), status=payload.get("status", "ok"), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profile-runs/{profile_run_id}")
async def read_coding_agent_runtime_profile_run(workspace_id: str, codebase_id: str, profile_run_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_runtime_profile_run(codebase_id, profile_run_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"runtime_profile_run": public_runtime_profile_run_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/diff")
async def build_coding_agent_incremental_diff(workspace_id: str, codebase_id: str, request: IncrementalDiffRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_incremental_diff(codebase_id, from_snapshot_id=request.from_snapshot_id, to_snapshot_id=request.to_snapshot_id, task=request.task)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.to_snapshot_id, str(exc))
    data = {"incremental_diff": public_incremental_diff_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("to_snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/diffs/{diff_id}")
async def read_coding_agent_incremental_diff(workspace_id: str, codebase_id: str, diff_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_incremental_diff(codebase_id, diff_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"incremental_diff": public_incremental_diff_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("to_snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/timeline")
async def read_coding_agent_incremental_timeline(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    payload = service.read_incremental_timeline(codebase_id)
    data = {"drift_timeline": public_incremental_timeline_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/build")
async def build_coding_agent_workbench(workspace_id: str, codebase_id: str, request: WorkbenchBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_workbench(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"workbench": public_workbench_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench")
async def read_coding_agent_workbench(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_workbench(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"workbench": public_workbench_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/views/{view_id}")
async def read_coding_agent_workbench_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_workbench_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"workbench_view": public_workbench_view_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/context-export")
async def create_coding_agent_workbench_context_export(workspace_id: str, codebase_id: str, request: WorkbenchContextExportRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.create_workbench_context_export(codebase_id, mode=request.mode, max_items=request.max_items)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"context_export": public_workbench_context_export_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench-v2/build")
async def build_coding_agent_workbench_v2(workspace_id: str, codebase_id: str, request: WorkbenchV2BuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_workbench_v2(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"workbench_v2": public_workbench_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_workbench_v2_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench-v2")
async def read_coding_agent_workbench_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_workbench_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"workbench_v2": public_workbench_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench-v2/views/{view_id}")
async def read_coding_agent_workbench_v2_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_workbench_v2_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"workbench_v2_view": payload}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/large-project-advisor/build")
async def build_coding_agent_large_project_advisor(workspace_id: str, codebase_id: str, request: LargeProjectAdvisorBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_large_project_advisor(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    data = {"large_project_advisor": public_large_project_advisor_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_large_project_advisor_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/large-project-advisor")
async def read_coding_agent_large_project_advisor(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentActionabilityService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_large_project_advisor(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    data = {"large_project_advisor": public_large_project_advisor_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/build")
async def build_coding_agent_task_navigation_index(workspace_id: str, codebase_id: str, request: TaskNavigationBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_navigation_index(codebase_id, snapshot_id=request.snapshot_id)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    refs = task_navigation_refs(codebase_id)
    data = {"task_navigation_index": public_task_navigation_index_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_task_navigation_prepare"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation")
async def read_coding_agent_task_navigation_index(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_navigation_index(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = task_navigation_refs(codebase_id)
    data = {"task_navigation_index": public_task_navigation_index_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation")
async def prepare_coding_agent_task_navigation(workspace_id: str, codebase_id: str, request: TaskNavigationPrepareRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.prepare_task_navigation(codebase_id, task=request.task, snapshot_id=request.snapshot_id, limit=request.limit)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    refs = task_query_refs(codebase_id, str(payload.get("task_id")))
    data = {"task_navigation_query": public_task_navigation_query_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_task_navigation_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/{task_id}")
async def read_coding_agent_task_navigation_query(workspace_id: str, codebase_id: str, task_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_task_query(codebase_id, task_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = task_query_refs(codebase_id, task_id)
    data = {"task_navigation_query": public_task_navigation_query_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships/build")
async def build_coding_agent_relationship_graph(workspace_id: str, codebase_id: str, request: TaskNavigationBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_relationship_graph(codebase_id, snapshot_id=request.snapshot_id)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    refs = task_relationship_refs(codebase_id)
    data = {"relationship_graph": public_task_relationship_graph_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_task_relationships_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships")
async def read_coding_agent_relationship_graph(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_relationship_graph(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = task_relationship_refs(codebase_id)
    data = {"relationship_graph": public_task_relationship_graph_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2")
async def build_coding_agent_impact_analysis(workspace_id: str, codebase_id: str, request: TaskImpactRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        impact, test_selection = service.build_impact_analysis(
            codebase_id,
            task=request.task,
            task_id=request.task_id,
            snapshot_id=request.snapshot_id,
            max_items=request.max_items,
        )
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    refs = task_impact_refs(codebase_id, str(impact.get("task_id")))
    data = {"impact_analysis": public_task_impact_payload(impact), "test_selection": public_task_test_selection_payload(test_selection)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_task_impact_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, impact.get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2/{task_id}")
async def read_coding_agent_impact_analysis(workspace_id: str, codebase_id: str, task_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        impact, test_selection = service.read_impact_analysis(codebase_id, task_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = task_impact_refs(codebase_id, task_id)
    data = {"impact_analysis": public_task_impact_payload(impact), "test_selection": public_task_test_selection_payload(test_selection)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, impact.get("snapshot_id"), data, refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack")
async def build_coding_agent_module_reading_pack(workspace_id: str, codebase_id: str, request: TaskReadingPackRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack, markdown, ledger = service.build_reading_pack(
            codebase_id,
            task=request.task,
            task_id=request.task_id,
            snapshot_id=request.snapshot_id,
            max_tokens=request.max_tokens,
            role=request.role,
            max_items=request.max_items,
        )
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    refs = task_reading_pack_refs(codebase_id, str(pack.get("pack_id")))
    data = {"reading_pack": public_task_reading_pack_payload(pack), "markdown": markdown, "token_ledger": ledger}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_module_reading_pack_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, pack.get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack/{pack_id}")
async def read_coding_agent_module_reading_pack(workspace_id: str, codebase_id: str, pack_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack, markdown, ledger = service.read_reading_pack(codebase_id, pack_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = task_reading_pack_refs(codebase_id, pack_id)
    data = {"reading_pack": public_task_reading_pack_payload(pack), "markdown": markdown, "token_ledger": ledger}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, pack.get("snapshot_id"), data, refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff")
async def build_coding_agent_handoff(workspace_id: str, codebase_id: str, request: AgentHandoffRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_agent_handoff(
            codebase_id,
            target_agent=request.target_agent,
            pack_id=request.pack_id,
            task=request.task,
            task_id=request.task_id,
            snapshot_id=request.snapshot_id,
            max_tokens=request.max_tokens,
            max_items=request.max_items,
        )
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    refs = list(payload.get("artifact_refs") or task_handoff_refs(codebase_id, str(payload.get("handoff_id"))))
    data = {"agent_handoff": public_task_handoff_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_agent_handoff_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff/{handoff_id}")
async def read_coding_agent_handoff(workspace_id: str, codebase_id: str, handoff_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_agent_handoff(codebase_id, handoff_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = list(payload.get("artifact_refs") or task_handoff_refs(codebase_id, handoff_id))
    data = {"agent_handoff": public_task_handoff_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, payload.get("snapshot_id"), data, refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/build")
async def build_coding_agent_task_navigation_closure(workspace_id: str, codebase_id: str, request: TaskClosureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        report, html, mermaid, coverage, governance, audit = service.build_closure_report(
            codebase_id,
            handoff_id=request.handoff_id,
            task=request.task,
            task_id=request.task_id,
            snapshot_id=request.snapshot_id,
            max_tokens=request.max_tokens,
            max_items=request.max_items,
        )
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, request.snapshot_id, str(exc))
    refs = task_closure_refs(codebase_id)
    data = {"closure_report": public_task_closure_payload(report), "html": html, "mermaid": mermaid, "coverage_matrix": coverage, "governance_targets": governance, "closure_audit": audit}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_task_navigation_closure_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, report.get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/closure")
async def read_coding_agent_task_navigation_closure(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        report, html, mermaid, coverage, governance, audit = service.read_closure_report(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = task_closure_refs(codebase_id)
    data = {"closure_report": public_task_closure_payload(report), "html": html, "mermaid": mermaid, "coverage_matrix": coverage, "governance_targets": governance, "closure_audit": audit}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, report.get("snapshot_id"), data, refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/coding-agent/closure/views/{view_id}")
async def read_coding_agent_task_navigation_closure_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = CodingAgentNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_closure_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, None, str(exc))
    refs = task_closure_refs(codebase_id)
    data = {"closure_view": payload}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(str(meta["workspace_id"]), codebase_id, None, data, refs))


def _with_v2(workspace_id: str, codebase_id: str, snapshot_id: str | None, data: dict[str, Any], refs: list[dict[str, Any]]) -> dict[str, Any]:
    payload = dict(data)
    payload["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=refs)
    return payload


def _error(status_code: int, workspace_id: str, codebase_id: str, snapshot_id: str | None, error: str):
    data = {
        "error": {"code": error, "message": error, "retryable": False},
        "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, code=error, message=error),
    }
    return JSONResponse(status_code=status_code, content={"workspace_id": workspace_id, "status": "blocked", "data": data, "warnings": [error]})
