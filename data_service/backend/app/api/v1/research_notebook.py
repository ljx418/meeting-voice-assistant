"""ResearchNotebook target HTTP routes layered over the core data service."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from data_service.agent_workflow_contract import AgentWorkflowValidationError, create_agent_workflow_draft
from data_service.ai_provider_contract import AIProviderContractError, ai_provider_health_payload
from data_service.folder_collection_contract import FolderCollectionValidationError, scan_folder_collection
from data_service.folder_summary_workflow_contract import FolderSummaryWorkflowValidationError, run_folder_summary_workflow

from .data_service import (
    TargetAgentWorkflowDraftRequest,
    TargetFolderScanRequest,
    TargetFolderSummaryWorkflowRunRequest,
    TargetResearchRequest,
    TargetStudioArtifactRequest,
    _ai_provider_error_response,
    _notebook_guide_payload,
    _source_grounded_research_payload,
    _studio_artifact_payload,
    _target_envelope,
    _target_workspace_or_404,
    normalize_query_top_k,
    verify_knowledge_access,
)


router = APIRouter(prefix="/workspaces", tags=["ResearchNotebook"], dependencies=[Depends(verify_knowledge_access)])


@router.get("/-/ai-provider/health")
async def read_target_ai_provider_health() -> dict:
    try:
        provider_health = ai_provider_health_payload()
    except AIProviderContractError as exc:
        return _ai_provider_error_response(exc)
    return _target_envelope(
        workspace_id="provider-health",
        next_actions=["ai_guide_generate", "ai_studio_generate", "source_grounded_query"],
        data={"provider_health": provider_health},
    )


@router.get("/{workspace_id}/guide")
async def read_target_notebook_guide(workspace_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        next_actions=["knowledge_query", "knowledge_source_list"],
        data={"guide": _notebook_guide_payload(workspace, workspace_id=meta["workspace_id"])},
    )


@router.post("/{workspace_id}/studio/artifacts")
async def create_target_studio_artifact(workspace_id: str, request: TargetStudioArtifactRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    artifact = _studio_artifact_payload(workspace, workspace_id=meta["workspace_id"], artifact_type=request.artifact_type)
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[{"type": "studio_artifact", "artifact_id": artifact["artifact_id"]}]
        if artifact.get("artifact_available")
        else [],
        next_actions=["knowledge_query", "knowledge_source_list"],
        data={"artifact": artifact},
    )


@router.post("/{workspace_id}/research")
async def create_target_research_report(workspace_id: str, request: TargetResearchRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    report = _source_grounded_research_payload(
        workspace,
        workspace_id=meta["workspace_id"],
        question=request.question,
        top_k=normalize_query_top_k(request.top_k),
    )
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[{"type": "research_report", "question": report["question"]}] if report.get("research_available") else [],
        next_actions=["knowledge_source_list", "knowledge_query"],
        data={"research": report},
    )


@router.post("/{workspace_id}/folder-collections/scan")
async def scan_target_folder_collection(workspace_id: str, request: TargetFolderScanRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        result = scan_folder_collection(
            workspace_id=meta["workspace_id"],
            workspace=workspace,
            authorized_root=request.authorized_root,
            permission_grant_id=request.permission_grant_id,
            dry_run=request.dry_run,
            recursive=request.recursive,
            include_extensions=list(request.include_extensions),
            exclude_globs=list(request.exclude_globs),
            max_depth=request.max_depth,
            max_file_size_bytes=request.max_file_size_bytes,
            follow_symlinks=request.follow_symlinks,
        )
    except FolderCollectionValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: folder scan authorization failed.") from exc
    return {
        "workspace_id": meta["workspace_id"],
        "operation_id": None,
        "status": "ok",
        "warnings": [],
        "artifact_refs": [],
        "next_actions": ["review_folder_manifest", "confirm_folder_permission_before_extract"],
        "data": result,
    }


@router.post("/{workspace_id}/workflows/folder-summary/runs")
async def run_target_folder_summary_workflow(workspace_id: str, request: TargetFolderSummaryWorkflowRunRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        result = run_folder_summary_workflow(
            workspace_id=meta["workspace_id"],
            workspace=workspace,
            authorized_root=request.authorized_root,
            permission_grant_id=request.permission_grant_id,
            dry_run=request.dry_run,
            recursive=request.recursive,
            include_extensions=list(request.include_extensions),
            exclude_globs=list(request.exclude_globs),
            max_depth=request.max_depth,
            max_file_size_bytes=request.max_file_size_bytes,
            follow_symlinks=request.follow_symlinks,
            confirm_extract=request.confirm_extract,
        )
    except (FolderCollectionValidationError, FolderSummaryWorkflowValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="VALIDATION_ERROR: folder summary workflow authorization failed.") from exc
    return {
        "workspace_id": meta["workspace_id"],
        "operation_id": result["run"]["run_id"],
        "status": "ok",
        "warnings": [],
        "artifact_refs": [],
        "next_actions": ["review_workflow_run_report", "confirm_extract_before_summary_generation"],
        "data": result,
    }


@router.post("/{workspace_id}/agent-workflows/draft")
async def create_target_agent_workflow_draft(workspace_id: str, request: TargetAgentWorkflowDraftRequest) -> dict:
    _workspace, meta = _target_workspace_or_404(workspace_id)
    try:
        result = create_agent_workflow_draft(workspace_id=meta["workspace_id"], user_goal=request.user_goal)
    except AgentWorkflowValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "workspace_id": meta["workspace_id"],
        "operation_id": result["task"]["task_id"],
        "status": "ok",
        "warnings": [],
        "artifact_refs": [],
        "next_actions": ["review_workflow_draft", "confirm_folder_permission_before_run"],
        "data": result,
    }
