"""ResearchNotebook target HTTP routes layered over the core data service."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from data_service.agent_workflow_contract import AgentWorkflowValidationError, create_agent_workflow_draft
from data_service.ai_provider_contract import AIProviderContractError, ai_provider_health_payload
from data_service.folder_collection_contract import FolderCollectionValidationError, scan_folder_collection
from data_service.folder_summary_workflow_contract import FolderSummaryWorkflowValidationError, run_folder_summary_workflow
from data_service.research_notebook_artifacts import (
    artifact_status,
    capability_flags,
    create_audio_artifact,
    create_compare_artifact,
    create_mindmap_artifact,
    create_ocr_artifact,
    create_slides_artifact,
    delete_artifact,
    download_descriptor,
    export_slides,
    list_artifacts,
    ocr_status,
    provider_execution_status,
    provider_health,
    read_artifact,
)

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
provider_router = APIRouter(tags=["ResearchNotebook Providers"], dependencies=[Depends(verify_knowledge_access)])


class AudioArtifactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_ids: list[str] = Field(default_factory=list)
    language: str | None = Field(default=None, max_length=32)
    voice_id: str | None = Field(default=None, max_length=128)


class SlideArtifactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_ids: list[str] = Field(default_factory=list)
    topic: str | None = Field(default=None, max_length=256)
    slide_count: int = Field(default=10, ge=1, le=30)


class SlideExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(..., min_length=1, max_length=256)


class MindmapArtifactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_ids: list[str] = Field(default_factory=list)
    topic: str | None = Field(default=None, max_length=256)
    max_depth: int = Field(default=3, ge=1, le=5)


class CompareArtifactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_ids: list[str] = Field(default_factory=list, min_length=2)


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


@provider_router.post("/ocr/provider/health")
async def read_ocr_provider_health() -> dict:
    return provider_health("ocr")


@provider_router.post("/ocr/provider/execution")
async def read_ocr_provider_execution() -> dict:
    return provider_execution_status("ocr")


@provider_router.post("/tts/provider/health")
async def read_tts_provider_health() -> dict:
    return provider_health("tts")


@provider_router.post("/tts/provider/execution")
async def read_tts_provider_execution() -> dict:
    return provider_execution_status("tts")


@provider_router.post("/pptx/provider/health")
async def read_pptx_provider_health() -> dict:
    return provider_health("pptx_export")


@provider_router.post("/pptx/provider/execution")
async def read_pptx_provider_execution() -> dict:
    return provider_execution_status("pptx_export")


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


@router.get("/{workspace_id}/artifacts")
async def list_target_artifacts(workspace_id: str, type: str | None = Query(default=None)) -> dict:  # noqa: A002
    workspace, meta = _target_workspace_or_404(workspace_id)
    items = list_artifacts(workspace, workspace_id=meta["workspace_id"], artifact_type=type)
    return _target_envelope(workspace_id=meta["workspace_id"], data={"items": items, "count": len(items)})


@router.get("/{workspace_id}/artifacts/{artifact_id}")
async def read_target_artifact(workspace_id: str, artifact_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    artifact = read_artifact(workspace, workspace_id=meta["workspace_id"], artifact_id=artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="not_found: artifact not found")
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        artifact_refs=[{"type": "artifact", "artifact_id": artifact_id, "artifact_ref": artifact.get("artifact_ref")}],
        data={"artifact": artifact},
    )


@router.delete("/{workspace_id}/artifacts/{artifact_id}")
async def delete_target_artifact(workspace_id: str, artifact_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    deleted = delete_artifact(workspace, artifact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="not_found: artifact not found")
    return _target_envelope(workspace_id=meta["workspace_id"], data={"deleted": True, "artifact_id": artifact_id})


@router.get("/{workspace_id}/artifacts/{artifact_id}/status")
async def read_target_artifact_status(workspace_id: str, artifact_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    status = artifact_status(workspace, artifact_id)
    if not status:
        raise HTTPException(status_code=404, detail="not_found: artifact not found")
    return _target_envelope(workspace_id=meta["workspace_id"], data=status)


@router.get("/{workspace_id}/artifacts/{artifact_id}/download")
async def download_target_artifact(workspace_id: str, artifact_id: str, format: str | None = Query(default=None)) -> dict:  # noqa: A002
    workspace, meta = _target_workspace_or_404(workspace_id)
    descriptor = download_descriptor(workspace, workspace_id=meta["workspace_id"], artifact_id=artifact_id, fmt=format)
    if not descriptor:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Artifact not found."}})
    return descriptor


@router.post("/{workspace_id}/artifacts/audio")
async def create_target_audio_artifact(workspace_id: str, request: AudioArtifactRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    artifact = create_audio_artifact(workspace, workspace_id=meta["workspace_id"], source_ids=list(request.source_ids), language=request.language, voice_id=request.voice_id)
    return _artifact_envelope(meta["workspace_id"], artifact)


@router.post("/{workspace_id}/artifacts/slides")
async def create_target_slides_artifact(workspace_id: str, request: SlideArtifactRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    artifact = create_slides_artifact(workspace, workspace_id=meta["workspace_id"], source_ids=list(request.source_ids), topic=request.topic, slide_count=request.slide_count)
    return _artifact_envelope(meta["workspace_id"], artifact)


@router.post("/{workspace_id}/artifacts/slides/export")
async def export_target_slides_artifact(workspace_id: str, request: SlideExportRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    return export_slides(workspace, workspace_id=meta["workspace_id"], artifact_id=request.artifact_id)


@router.post("/{workspace_id}/artifacts/mindmap")
async def create_target_mindmap_artifact(workspace_id: str, request: MindmapArtifactRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    artifact = create_mindmap_artifact(workspace, workspace_id=meta["workspace_id"], source_ids=list(request.source_ids), topic=request.topic, max_depth=request.max_depth)
    return _artifact_envelope(meta["workspace_id"], artifact)


@router.post("/{workspace_id}/artifacts/compare")
async def create_target_compare_artifact(workspace_id: str, request: CompareArtifactRequest) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    artifact = create_compare_artifact(workspace, workspace_id=meta["workspace_id"], source_ids=list(request.source_ids))
    return _artifact_envelope(meta["workspace_id"], artifact)


@router.post("/{workspace_id}/sources/{source_id}/ocr")
async def create_target_source_ocr(workspace_id: str, source_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    health = provider_health("ocr")
    if not health.get("available"):
        data = {
            "source_id": source_id,
            "status": "error",
            "error": {"code": "OCR_REQUIRED", "message": "OCR provider is not configured."},
        }
        payload = _target_envelope(
            workspace_id=meta["workspace_id"],
            status="blocked",
            warnings=["OCR_REQUIRED"],
            data=data,
        )
        payload["data"] = data
        return payload
    artifact = create_ocr_artifact(workspace, workspace_id=meta["workspace_id"], source_id=source_id)
    status = "ok" if artifact.get("status") == "ready" else "blocked"
    return _target_envelope(
        workspace_id=meta["workspace_id"],
        status=status,
        warnings=[artifact.get("unsupported_reason")] if artifact.get("unsupported_reason") else [],
        artifact_refs=[{"type": "artifact", "artifact_id": artifact.get("artifact_id"), "artifact_ref": artifact.get("artifact_ref")}]
        if artifact.get("artifact_id")
        else [],
        data={"source_id": source_id, "status": artifact.get("status"), "artifact": artifact, "progress": 100 if artifact.get("status") == "ready" else 0},
    )


@router.get("/{workspace_id}/sources/{source_id}/ocr/status")
async def read_target_source_ocr_status(workspace_id: str, source_id: str) -> dict:
    workspace, meta = _target_workspace_or_404(workspace_id)
    if provider_health("ocr").get("available"):
        payload = ocr_status(workspace, workspace_id=meta["workspace_id"], source_id=source_id)
    else:
        payload = {"source_id": source_id, "status": "error", "progress": None}
        payload["error"] = {"code": "OCR_REQUIRED", "message": "OCR provider is not configured."}
    return _target_envelope(workspace_id=meta["workspace_id"], data=payload)


def _artifact_envelope(workspace_id: str, artifact: dict[str, Any]) -> dict:
    payload = _target_envelope(
        workspace_id=workspace_id,
        artifact_refs=[{"type": "artifact", "artifact_id": artifact.get("artifact_id"), "artifact_ref": artifact.get("artifact_ref")}]
        if artifact.get("artifact_id")
        else [],
        next_actions=["review_artifact", "knowledge_source_list"],
        data={"artifact": artifact},
    )
    payload["data"]["artifact"] = artifact
    return payload


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
