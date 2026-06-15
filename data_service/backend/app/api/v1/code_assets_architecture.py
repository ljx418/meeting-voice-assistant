"""HTTP routes for V2.3 Architecture Abstraction code assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from data_service.code_assets.architecture.persistence import architecture_artifact_refs, architecture_code_fact_chain_artifact_refs, architecture_context_pack_optimized_v244_artifact_refs, architecture_context_pack_v2_artifact_refs, architecture_context_pack_v3_artifact_refs, architecture_doc_claim_artifact_refs, architecture_doc_code_alignment_artifact_refs, architecture_doc_quality_artifact_refs, architecture_doc_registry_artifact_refs, architecture_document_semantics_v243_artifact_refs, architecture_graph_v28_artifact_refs, architecture_human_report_v29_artifact_refs, architecture_intent_evidence_artifact_refs, architecture_inventory_artifact_refs, architecture_pattern_evidence_v210_artifact_refs, architecture_public_surface_evidence_v29_artifact_refs, architecture_reading_dashboard_artifact_refs, architecture_reconstructed_artifact_refs, architecture_relationship_chains_v242_artifact_refs, architecture_relationships_v29_artifact_refs, architecture_scale_artifact_refs, architecture_signal_ranking_artifact_refs, architecture_signal_ranking_v29_artifact_refs, architecture_taxonomy_artifact_refs, code_architecture_artifact_refs
from data_service.code_assets.architecture.service import ArchitectureService, public_architecture_code_fact_chain_payload, public_architecture_code_relationships_v2_payload, public_architecture_context_pack_v2_payload, public_architecture_context_pack_v3_payload, public_architecture_document_claims_payload, public_architecture_document_code_alignment_payload, public_architecture_document_quality_payload, public_architecture_document_registry_payload, public_architecture_document_semantics_v3_payload, public_architecture_graph_summary_payload, public_architecture_human_review_report_v2_payload, public_architecture_human_review_report_view_v2_payload, public_architecture_intent_evidence_payload, public_architecture_inventory_list_payload, public_architecture_inventory_payload, public_architecture_optimized_context_pack_v244_payload, public_architecture_pattern_blockers_v2_payload, public_architecture_pattern_evidence_v2_payload, public_architecture_pattern_view_v2_payload, public_architecture_payload, public_architecture_profile_taxonomy_regression_v245_payload, public_architecture_public_surface_evidence_v2_payload, public_architecture_ranking_calibration_v2_payload, public_architecture_reading_payload, public_architecture_reconstructed_payload, public_architecture_relationship_chains_v3_payload, public_architecture_review_queue_payload, public_architecture_scale_profile_payload, public_architecture_signal_ranking_payload, public_architecture_taxonomy_payload, public_code_architecture_payload, public_language_provider_payload, public_workflow_runtime_payload
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Intelligence Architecture"], dependencies=[Depends(verify_knowledge_access)])


class ArchitectureBuildRequest(BaseModel):
    snapshot_id: Optional[str] = Field(default=None)
    max_files: Optional[int] = Field(default=None, ge=1)
    max_loc: Optional[int] = Field(default=None, ge=1)
    max_file_size_mb: Optional[int] = Field(default=None, ge=1)
    timeout_seconds: Optional[int] = Field(default=None, ge=1)
    shard_size: Optional[int] = Field(default=None, ge=1)


class ArchitectureContextPackRequest(BaseModel):
    mode: str = Field(default="project_brief")
    role: str = Field(default="maintainer")
    task: Optional[str] = Field(default=None)
    max_tokens: int = Field(default=12000, ge=200)


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


def _scale_budget_from_request(request: ArchitectureBuildRequest) -> dict[str, int] | None:
    budget = {
        "max_files": request.max_files,
        "max_loc": request.max_loc,
        "max_file_size_mb": request.max_file_size_mb,
        "timeout_seconds": request.timeout_seconds,
        "shard_size": request.shard_size,
    }
    return {key: int(value) for key, value in budget.items() if value is not None} or None


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


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/scale/build")
async def build_architecture_scale_profile(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        profile = service.build_scale_profile(codebase_id, snapshot_id=request.snapshot_id, budget=_scale_budget_from_request(request))
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = architecture_scale_artifact_refs(codebase_id)
    data = {"scale_profile": public_architecture_scale_profile_payload(profile)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_scale_profile"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(profile["snapshot_id"]), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/scale/profile")
async def read_architecture_scale_profile(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        profile = service.read_scale_profile(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_scale_artifact_refs(codebase_id)
    data = {"scale_profile": public_architecture_scale_profile_payload(profile)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(profile.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/scale/readback")
async def read_architecture_scale_readback(workspace_id: str, codebase_id: str, shard: str = "files", page: int = 1, page_size: int = 100):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_scale_shard(codebase_id, shard=shard, page=page, page_size=page_size)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_scale_artifact_refs(codebase_id)
    data = {"scale_readback": payload}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/inventory/build")
async def build_architecture_inventory(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_inventory(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = architecture_inventory_artifact_refs(codebase_id)
    data = {"architecture_inventory": public_architecture_inventory_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_config_inventory", "knowledge_code_architecture_deployment_inventory", "knowledge_code_architecture_schema_inventory"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/language-facts")
async def read_architecture_language_facts(workspace_id: str, codebase_id: str):
    return _read_architecture_inventory_list(workspace_id, codebase_id, "language_facts")


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/language-providers/build")
async def build_architecture_language_providers(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_language_provider_facts(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    data = {"language_providers": public_language_provider_payload(payload)}
    refs = payload.get("artifact_refs", [])
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_language_providers"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/language-providers")
async def read_architecture_language_providers(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_language_provider_facts(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    data = {"language_providers": public_language_provider_payload(payload)}
    refs = payload.get("artifact_refs", [])
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/workflow-runtime/build")
async def build_architecture_workflow_runtime(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_workflow_runtime_candidates(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    data = {"workflow_runtime": public_workflow_runtime_payload(payload)}
    refs = payload.get("artifact_refs", [])
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_workflow_runtime"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/workflow-runtime")
async def read_architecture_workflow_runtime(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_workflow_runtime_candidates(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    data = {"workflow_runtime": public_workflow_runtime_payload(payload)}
    refs = payload.get("artifact_refs", [])
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/config")
async def read_architecture_config_inventory(workspace_id: str, codebase_id: str):
    return _read_architecture_inventory_list(workspace_id, codebase_id, "config")


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/deployment")
async def read_architecture_deployment_inventory(workspace_id: str, codebase_id: str):
    return _read_architecture_inventory_list(workspace_id, codebase_id, "deployment")


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/schema")
async def read_architecture_schema_inventory(workspace_id: str, codebase_id: str):
    return _read_architecture_inventory_list(workspace_id, codebase_id, "schema")


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/taxonomy/build")
async def build_architecture_taxonomy(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        taxonomy = service.build_taxonomy(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_taxonomy_artifact_refs(codebase_id)
    data = {"taxonomy": public_architecture_taxonomy_payload(taxonomy)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_review_queue"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/taxonomy")
async def read_architecture_taxonomy(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        taxonomy = service.read_taxonomy(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_taxonomy_artifact_refs(codebase_id)
    data = {"taxonomy": public_architecture_taxonomy_payload(taxonomy)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/review-queue/build")
async def build_architecture_review_queue(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_review_queue(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_taxonomy_artifact_refs(codebase_id)
    data = {"review_queue": public_architecture_review_queue_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/review-queue")
async def read_architecture_review_queue(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_review_queue(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_taxonomy_artifact_refs(codebase_id)
    data = {"review_queue": public_architecture_review_queue_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/views/build")
async def build_architecture_large_project_views(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_large_project_views(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    data = {"views": payload}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_architecture_large_project_view"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=payload.get("artifact_refs", [])))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views/build")
async def build_architecture_reading_dashboard(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_architecture_reading_dashboard(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_reading_dashboard_artifact_refs(codebase_id)
    data = {"reading_dashboard": public_architecture_reading_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_views"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views")
async def read_architecture_reading_dashboard(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_architecture_reading_dashboard(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_reading_dashboard_artifact_refs(codebase_id)
    data = {"reading_dashboard": public_architecture_reading_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/views/{view_id}")
async def read_architecture_reading_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        view = service.read_architecture_reading_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_reading_dashboard_artifact_refs(codebase_id)
    data = {"view": view}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/build")
async def build_architecture_graph_summary(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_architecture_graph_summary(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_graph_v28_artifact_refs(codebase_id)
    data = {"graph_summary": public_architecture_graph_summary_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_graph_summary"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph")
async def read_architecture_graph_summary(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_architecture_graph_summary(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_graph_v28_artifact_refs(codebase_id)
    data = {"graph_summary": public_architecture_graph_summary_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/graph/views/{view_id}")
async def read_architecture_graph_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        view = service.read_architecture_graph_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_graph_v28_artifact_refs(codebase_id)
    data = {"graph_view": view}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains/build")
async def build_architecture_code_fact_chains(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_code_fact_chains(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_code_fact_chain_artifact_refs(codebase_id)
    data = {"code_fact_chains": public_architecture_code_fact_chain_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_code_fact_chains"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains")
async def read_architecture_code_fact_chains(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_code_fact_chains(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_code_fact_chain_artifact_refs(codebase_id)
    data = {"code_fact_chains": public_architecture_code_fact_chain_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking/build")
async def build_architecture_signal_ranking(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_signal_ranking(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_signal_ranking_artifact_refs(codebase_id)
    data = {"signal_ranking": public_architecture_signal_ranking_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_ranking"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("ranking", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking")
async def read_architecture_signal_ranking(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_signal_ranking(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_signal_ranking_artifact_refs(codebase_id)
    data = {"signal_ranking": public_architecture_signal_ranking_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("ranking", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/intent/build")
async def build_architecture_intent_evidence(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_intent_evidence(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_intent_evidence_artifact_refs(codebase_id)
    data = {"intent_evidence": public_architecture_intent_evidence_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_intent_evidence"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/intent")
async def read_architecture_intent_evidence(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_intent_evidence(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_intent_evidence_artifact_refs(codebase_id)
    data = {"intent_evidence": public_architecture_intent_evidence_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("summary", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/context-pack")
async def create_architecture_context_pack_v2(workspace_id: str, codebase_id: str, request: ArchitectureContextPackRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack = service.create_architecture_context_pack_v2(codebase_id, mode=request.mode, task=request.task, max_tokens=request.max_tokens)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_context_pack_v2_artifact_refs(codebase_id, str(pack.get("pack_id") or ""))
    data = {"architecture_context_pack": public_architecture_context_pack_v2_payload(pack)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_context_pack_read"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/context-pack/{pack_id}")
async def read_architecture_context_pack_v2(workspace_id: str, codebase_id: str, pack_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack = service.read_architecture_context_pack_v2(codebase_id, pack_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_context_pack_v2_artifact_refs(codebase_id, pack_id)
    data = {"architecture_context_pack": public_architecture_context_pack_v2_payload(pack)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence/build")
async def build_architecture_public_surface_evidence_v2(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_public_surface_evidence_v2(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = architecture_public_surface_evidence_v29_artifact_refs(codebase_id)
    data = {"public_surface_evidence_v2": public_architecture_public_surface_evidence_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_evidence_v2"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence")
async def read_architecture_public_surface_evidence_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_public_surface_evidence_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_public_surface_evidence_v29_artifact_refs(codebase_id)
    data = {"public_surface_evidence_v2": public_architecture_public_surface_evidence_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships/build")
async def build_architecture_relationships_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_code_relationships_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_relationships_v29_artifact_refs(codebase_id)
    data = {"code_relationships_v2": public_architecture_code_relationships_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_relationships_v2"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships")
async def read_architecture_relationships_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_code_relationships_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_relationships_v29_artifact_refs(codebase_id)
    data = {"code_relationships_v2": public_architecture_code_relationships_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains/build")
async def build_architecture_relationship_chains_v3(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_relationship_chains_v3(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = architecture_relationship_chains_v242_artifact_refs(codebase_id)
    data = {"relationship_chains_v3": public_architecture_relationship_chains_v3_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_relationship_chains_v3"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains")
async def read_architecture_relationship_chains_v3(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_relationship_chains_v3(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_relationship_chains_v242_artifact_refs(codebase_id)
    data = {"relationship_chains_v3": public_architecture_relationship_chains_v3_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking/build")
async def build_architecture_ranking_calibration_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_ranking_calibration_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_signal_ranking_v29_artifact_refs(codebase_id)
    data = {"ranking_calibration_v2": public_architecture_ranking_calibration_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_ranking_v2"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("ranking", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking")
async def read_architecture_ranking_calibration_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_ranking_calibration_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_signal_ranking_v29_artifact_refs(codebase_id)
    data = {"ranking_calibration_v2": public_architecture_ranking_calibration_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("ranking", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report/build")
async def build_architecture_human_review_report_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_human_review_report_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_human_report_v29_artifact_refs(codebase_id)
    data = {"human_review_report_v2": public_architecture_human_review_report_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_human_report_v2"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("report", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report")
async def read_architecture_human_review_report_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_human_review_report_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_human_report_v29_artifact_refs(codebase_id)
    data = {"human_review_report_v2": public_architecture_human_review_report_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("report", {}).get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report/views/{view_id}")
async def read_architecture_human_review_report_view_v2(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        view = service.read_human_review_report_view_v2(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_human_report_v29_artifact_refs(codebase_id)
    data = {"view": public_architecture_human_review_report_view_v2_payload(view)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack")
async def create_architecture_context_pack_v3(workspace_id: str, codebase_id: str, request: ArchitectureContextPackRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack = service.create_architecture_context_pack_v3(codebase_id, mode=request.mode, role=request.role, task=request.task, max_tokens=request.max_tokens)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_context_pack_v3_artifact_refs(codebase_id, str(pack.get("pack_id") or ""))
    data = {"architecture_context_pack_v3": public_architecture_context_pack_v3_payload(pack)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_context_pack_v3_read"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack/{pack_id}")
async def read_architecture_context_pack_v3(workspace_id: str, codebase_id: str, pack_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack = service.read_architecture_context_pack_v3(codebase_id, pack_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_context_pack_v3_artifact_refs(codebase_id, pack_id)
    data = {"architecture_context_pack_v3": public_architecture_context_pack_v3_payload(pack)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized")
async def create_architecture_optimized_context_pack_v244(workspace_id: str, codebase_id: str, request: ArchitectureContextPackRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack = service.create_optimized_context_pack_v244(codebase_id, mode=request.mode, role=request.role, task=request.task, max_tokens=request.max_tokens)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_context_pack_optimized_v244_artifact_refs(codebase_id, str(pack.get("pack_id") or ""))
    data = {"architecture_context_pack_optimized": public_architecture_optimized_context_pack_v244_payload(pack)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_context_pack_optimized_read"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized/{pack_id}")
async def read_architecture_optimized_context_pack_v244(workspace_id: str, codebase_id: str, pack_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        pack = service.read_optimized_context_pack_v244(codebase_id, pack_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_context_pack_optimized_v244_artifact_refs(codebase_id, pack_id)
    data = {"architecture_context_pack_optimized": public_architecture_optimized_context_pack_v244_payload(pack)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(pack.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression/build")
async def build_architecture_profile_taxonomy_regression_v245(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_profile_taxonomy_regression_v245(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = payload.get("artifact_refs") or []
    data = {"profile_taxonomy_regression": public_architecture_profile_taxonomy_regression_v245_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_profile_regression"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression")
async def read_architecture_profile_taxonomy_regression_v245(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_profile_taxonomy_regression_v245(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = payload.get("artifact_refs") or []
    data = {"profile_taxonomy_regression": public_architecture_profile_taxonomy_regression_v245_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/build")
async def build_architecture_pattern_evidence_v2(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_pattern_evidence_v2(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
    data = {"pattern_evidence_v2": public_architecture_pattern_evidence_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_patterns_v2"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns")
async def read_architecture_pattern_evidence_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_pattern_evidence_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
    data = {"pattern_evidence_v2": public_architecture_pattern_evidence_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/blockers")
async def read_architecture_pattern_blockers_v2(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_pattern_evidence_v2(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
    data = {"pattern_blockers": public_architecture_pattern_blockers_v2_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/views/{view_id}")
async def read_architecture_pattern_view_v2(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        view = service.read_pattern_evidence_view_v2(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_pattern_evidence_v210_artifact_refs(codebase_id)
    data = {"view": public_architecture_pattern_view_v2_payload(view)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/docs/build")
async def build_architecture_document_registry(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_document_registry(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = architecture_doc_registry_artifact_refs(codebase_id)
    data = {"document_registry": public_architecture_document_registry_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_docs_list"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/docs")
async def read_architecture_document_registry(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_document_registry(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_doc_registry_artifact_refs(codebase_id)
    data = {"document_registry": public_architecture_document_registry_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims/build")
async def build_architecture_document_claims(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_document_claims(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_doc_claim_artifact_refs(codebase_id)
    data = {"document_claims": public_architecture_document_claims_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_doc_claims"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims")
async def read_architecture_document_claims(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_document_claims(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_doc_claim_artifact_refs(codebase_id)
    data = {"document_claims": public_architecture_document_claims_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics/build")
async def build_architecture_document_semantics_v3(workspace_id: str, codebase_id: str, request: ArchitectureBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_document_semantics_v3(codebase_id, snapshot_id=request.snapshot_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=request.snapshot_id, error=str(exc))
    refs = architecture_document_semantics_v243_artifact_refs(codebase_id)
    data = {"document_semantics_v3": public_architecture_document_semantics_v3_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_document_semantics_v3"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics")
async def read_architecture_document_semantics_v3(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_document_semantics_v3(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_document_semantics_v243_artifact_refs(codebase_id)
    data = {"document_semantics_v3": public_architecture_document_semantics_v3_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality/build")
async def build_architecture_document_quality(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_document_quality(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_doc_quality_artifact_refs(codebase_id)
    data = {"document_quality": public_architecture_document_quality_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_doc_quality"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality")
async def read_architecture_document_quality(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_document_quality(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_doc_quality_artifact_refs(codebase_id)
    data = {"document_quality": public_architecture_document_quality_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment/build")
async def build_architecture_document_code_alignment(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_document_code_alignment(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_doc_code_alignment_artifact_refs(codebase_id)
    data = {"document_code_alignment": public_architecture_document_code_alignment_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_doc_code_alignment"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment")
async def read_architecture_document_code_alignment(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_document_code_alignment(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_doc_code_alignment_artifact_refs(codebase_id)
    data = {"document_code_alignment": public_architecture_document_code_alignment_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.post("/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed/build")
async def build_architecture_document_reconstructed(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_reconstructed_architecture(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_reconstructed_artifact_refs(codebase_id)
    data = {"reconstructed_architecture": public_architecture_reconstructed_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, next_actions=["knowledge_code_architecture_reconstructed", "knowledge_code_architecture_doc_view"], data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed")
async def read_architecture_document_reconstructed(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_reconstructed_architecture(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_reconstructed_artifact_refs(codebase_id)
    data = {"reconstructed_architecture": public_architecture_reconstructed_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(payload.get("snapshot_id") or ""), data=data, artifact_refs=refs))


@router.get("/{workspace_id}/codebases/{codebase_id}/architecture/docs/views/{view_id}")
async def read_architecture_document_view(workspace_id: str, codebase_id: str, view_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        view = service.read_document_architecture_view(codebase_id, view_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_reconstructed_artifact_refs(codebase_id)
    data = {"view": view}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=str(view.get("snapshot_id") or ""), data=data, artifact_refs=refs))


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
        if view_id in {"architecture_large_project_overview.html", "architecture_key_boundaries.mmd"}:
            view = service.read_large_project_view(codebase_id, view_id)
            refs = view.get("artifact_refs", [])
        else:
            view = service.read_view(codebase_id, view_id)
            refs = architecture_artifact_refs(codebase_id)
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
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


def _read_architecture_inventory_list(workspace_id: str, codebase_id: str, payload_kind: str):
    workspace, meta = _workspace_for(workspace_id)
    service = ArchitectureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        if payload_kind == "language_facts":
            items = service.read_language_facts(codebase_id)
            payload_key, item_key = "language_facts", "fact_type"
        elif payload_kind == "config":
            items = service.read_config_inventory(codebase_id)
            payload_key, item_key = "config_inventory", "item_type"
        elif payload_kind == "deployment":
            items = service.read_deployment_inventory(codebase_id)
            payload_key, item_key = "deployment_inventory", "deployment_type"
        else:
            items = service.read_schema_inventory(codebase_id)
            payload_key, item_key = "schema_inventory", "schema_type"
    except FileNotFoundError as exc:
        return _error(status_code=404, workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=None, error=str(exc))
    refs = architecture_inventory_artifact_refs(codebase_id)
    snapshot_id = str(items[0].get("snapshot_id") or "") if items else ""
    data = public_architecture_inventory_list_payload(items, payload_key=payload_key, item_key=item_key, codebase_id=codebase_id)
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=refs, data=_with_v2(workspace_id=str(meta["workspace_id"]), codebase_id=codebase_id, snapshot_id=snapshot_id, data=data, artifact_refs=refs))


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
    if "ARCHITECTURE_SCALE_PROFILE_NOT_BUILT" in error:
        return "ARCHITECTURE_SCALE_PROFILE_NOT_BUILT"
    if "SHARD_NOT_FOUND" in error:
        return "ARCHITECTURE_SCALE_SHARD_NOT_FOUND"
    if "ARCHITECTURE_INVENTORY_NOT_BUILT" in error:
        return "ARCHITECTURE_INVENTORY_NOT_BUILT"
    if "ARCHITECTURE_LANGUAGE_FACTS_NOT_BUILT" in error:
        return "ARCHITECTURE_LANGUAGE_FACTS_NOT_BUILT"
    if "ARCHITECTURE_LANGUAGE_PROVIDERS_NOT_BUILT" in error:
        return "ARCHITECTURE_LANGUAGE_PROVIDERS_NOT_BUILT"
    if "ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT" in error:
        return "ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT"
    if "ARCHITECTURE_CONFIG_INVENTORY_NOT_BUILT" in error:
        return "ARCHITECTURE_CONFIG_INVENTORY_NOT_BUILT"
    if "ARCHITECTURE_DEPLOYMENT_INVENTORY_NOT_BUILT" in error:
        return "ARCHITECTURE_DEPLOYMENT_INVENTORY_NOT_BUILT"
    if "ARCHITECTURE_SCHEMA_INVENTORY_NOT_BUILT" in error:
        return "ARCHITECTURE_SCHEMA_INVENTORY_NOT_BUILT"
    if "ARCHITECTURE_TAXONOMY_NOT_BUILT" in error:
        return "ARCHITECTURE_TAXONOMY_NOT_BUILT"
    if "ARCHITECTURE_REVIEW_QUEUE_NOT_BUILT" in error:
        return "ARCHITECTURE_REVIEW_QUEUE_NOT_BUILT"
    if "ARCHITECTURE_DOCS_NOT_BUILT" in error:
        return "ARCHITECTURE_DOCS_NOT_BUILT"
    if "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT" in error:
        return "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT"
    if "ARCHITECTURE_DOC_CLAIMS_NOT_FOUND" in error:
        return "ARCHITECTURE_DOC_CLAIMS_NOT_FOUND"
    if "ARCHITECTURE_DOC_QUALITY_NOT_BUILT" in error:
        return "ARCHITECTURE_DOC_QUALITY_NOT_BUILT"
    if "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT" in error:
        return "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT"
    if "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT" in error:
        return "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT"
    if "ARCHITECTURE_DOC_VIEW_NOT_FOUND" in error:
        return "ARCHITECTURE_DOC_VIEW_NOT_FOUND"
    if "ARCHITECTURE_READING_DASHBOARD_NOT_BUILT" in error:
        return "ARCHITECTURE_READING_DASHBOARD_NOT_BUILT"
    if "ARCHITECTURE_V28_VIEW_NOT_FOUND" in error:
        return "ARCHITECTURE_V28_VIEW_NOT_FOUND"
    if "ARCHITECTURE_GRAPH_SUMMARY_NOT_BUILT" in error:
        return "ARCHITECTURE_GRAPH_SUMMARY_NOT_BUILT"
    if "ARCHITECTURE_GRAPH_VIEW_NOT_FOUND" in error:
        return "ARCHITECTURE_GRAPH_VIEW_NOT_FOUND"
    if "ARCHITECTURE_CODE_FACT_CHAINS_NOT_BUILT" in error:
        return "ARCHITECTURE_CODE_FACT_CHAINS_NOT_BUILT"
    if "ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT" in error:
        return "ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT"
    if "ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT" in error:
        return "ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT"
    if "ARCHITECTURE_PROFILE_TAXONOMY_REGRESSION_NOT_BUILT" in error:
        return "ARCHITECTURE_PROFILE_TAXONOMY_REGRESSION_NOT_BUILT"
    if "ARCHITECTURE_DOC_SOURCE_NOT_FOUND" in error:
        return "ARCHITECTURE_DOC_SOURCE_NOT_FOUND"
    if "ARCHITECTURE_VIEW_NOT_BUILT" in error:
        return "ARCHITECTURE_VIEW_NOT_BUILT"
    if "SNAPSHOT_FILES_NOT_FOUND" in error:
        return "SNAPSHOT_FILES_NOT_FOUND"
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
    if "ARCHITECTURE_SCALE_PROFILE_NOT_BUILT" in error:
        return "Architecture Scale Profile has not been built"
    if "SHARD_NOT_FOUND" in error:
        return "Architecture scale shard was not found"
    if "ARCHITECTURE_LANGUAGE_PROVIDERS_NOT_BUILT" in error:
        return "Architecture language providers have not been built"
    if "ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT" in error:
        return "Architecture workflow/runtime candidates have not been built"
    if "ARCHITECTURE_DOCS_NOT_BUILT" in error:
        return "Architecture document registry has not been built"
    if "ARCHITECTURE_DOC_CLAIMS_NOT_BUILT" in error:
        return "Architecture document claims have not been built"
    if "ARCHITECTURE_DOC_CLAIMS_NOT_FOUND" in error:
        return "No architecture document claims were found"
    if "ARCHITECTURE_DOC_QUALITY_NOT_BUILT" in error:
        return "Architecture document quality has not been built"
    if "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT" in error:
        return "Architecture document-code alignment has not been built"
    if "ARCHITECTURE_RECONSTRUCTION_NOT_BUILT" in error:
        return "Architecture document-code reconstruction has not been built"
    if "ARCHITECTURE_DOC_VIEW_NOT_FOUND" in error:
        return "Architecture document-code view was not found"
    if "ARCHITECTURE_READING_DASHBOARD_NOT_BUILT" in error:
        return "Architecture reading dashboard has not been built"
    if "ARCHITECTURE_V28_VIEW_NOT_FOUND" in error:
        return "Architecture V2.8 reading view was not found"
    if "ARCHITECTURE_GRAPH_SUMMARY_NOT_BUILT" in error:
        return "Architecture graph summary has not been built"
    if "ARCHITECTURE_GRAPH_VIEW_NOT_FOUND" in error:
        return "Architecture graph view was not found"
    if "ARCHITECTURE_CODE_FACT_CHAINS_NOT_BUILT" in error:
        return "Architecture code fact chains have not been built"
    if "ARCHITECTURE_RELATIONSHIP_CHAINS_V3_NOT_BUILT" in error:
        return "Architecture relationship chains v3 have not been built"
    if "ARCHITECTURE_DOCUMENT_SEMANTICS_V3_NOT_BUILT" in error:
        return "Architecture document semantics v3 have not been built"
    if "ARCHITECTURE_PROFILE_TAXONOMY_REGRESSION_NOT_BUILT" in error:
        return "Architecture profile/taxonomy regression artifacts have not been built"
    if "ARCHITECTURE_DOC_SOURCE_NOT_FOUND" in error:
        return "No architecture document source was found in the codebase snapshot"
    if "SNAPSHOT_FILES_NOT_FOUND" in error:
        return "Snapshot file manifest has not been built"
    if "INVENTORY_NOT_FOUND" in error:
        return "Public surface inventory has not been built"
    if "SYMBOL_INDEX_NOT_FOUND" in error:
        return "Python symbol index has not been built"
    return error or "Architecture request failed"
