"""HTTP API for the shared data_service layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from data_service import DataService, GraphExecutionOwner, QueryMode


router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


class IngestRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    paths: List[str] = Field(..., description="Source file or directory paths to ingest")
    graphrag_execution_owner: GraphExecutionOwner = Field(
        default=GraphExecutionOwner.APP_GRAPHRAG,
        description="Who executes GraphRAG indexing: data_service or app.graphrag",
    )


class QueryRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    query: str = Field(..., description="Query text")
    mode: QueryMode = Field(default=QueryMode.HYBRID, description="Query mode: llmwiki, graphrag, hybrid")
    top_k: int = Field(default=8, ge=1, le=50)


class SummaryRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")


class GraphRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    max_nodes: int = Field(default=120, ge=10, le=500)


class DistillRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    source_id: Optional[str] = Field(default=None, description="Optional source_id to inspect")
    limit: int = Field(default=20, ge=1, le=200)
    kind: Optional[str] = Field(default=None, description="Optional unit kind filter")
    min_importance: float = Field(default=0.0, ge=0.0, description="Minimum unit importance")
    llm_enriched_only: bool = Field(default=False, description="Only return llm-enriched units")
    authority: Optional[str] = Field(default=None, description="Optional authority filter")
    min_source_weight: float = Field(default=0.0, ge=0.0, description="Minimum source_weight")
    min_source_density: float = Field(default=0.0, ge=0.0, description="Minimum source_density_score")


class PageRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    slug: str = Field(..., description="LLMWiki page slug")


class ResetRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    confirmation: str = Field(..., description="Must equal 'Delete' to confirm reset")


class GraphRAGExecuteRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")


class QualityFeedbackRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    target_type: str = Field(..., min_length=1, max_length=64, description="Target class, for example page/source/entity/query")
    target_id: str = Field(..., min_length=1, max_length=512, description="Stable target id or slug")
    action: str = Field(..., min_length=1, max_length=64, description="Feedback action, for example needs_review/rename_suggest/mark_noise")
    label: str = Field(default="", max_length=256, description="Human-readable target label")
    suggested_value: str = Field(default="", max_length=1024, description="Optional correction or replacement value")
    reason: str = Field(default="", max_length=4096, description="Operator note")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional context copied from the UI")


class QualityFeedbackListRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    limit: int = Field(default=100, ge=1, le=500)
    target_type: Optional[str] = Field(default=None, description="Optional target type filter")
    target_id: Optional[str] = Field(default=None, description="Optional target id filter")


class QualityCorrectionRulesRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")
    limit: int = Field(default=100, ge=1, le=500)
    status: Optional[str] = Field(default=None, description="Optional rule status filter")


class QualityCorrectionRulesBuildRequest(BaseModel):
    workspace: str = Field(..., description="Target workspace directory")


@router.post("/ingest")
async def ingest_knowledge(request: IngestRequest) -> dict:
    service = DataService(Path(request.workspace))
    plan = service.build_ingest_plan(
        request.paths,
        graphrag_execution_owner=request.graphrag_execution_owner,
    )
    service.write_summary_files(plan)
    results = service.run_default_pipeline_and_refresh_summary(plan)
    return {
        "workspace": str(service.workspace),
        "summary": str(service.layout.summary_md),
        "results": [
            {"engine": result.engine, "status": result.status, "meta": result.meta}
            for result in results
        ],
    }


@router.post("/query")
async def query_knowledge(request: QueryRequest) -> dict:
    service = DataService(Path(request.workspace))
    response = service.query(request.query, mode=request.mode, top_k=request.top_k)
    return {
        "mode": response.mode.value,
        "query": response.query,
        "answer": response.answer,
        "hits": [
            {
                "title": hit.title,
                "snippet": hit.snippet,
                "source": hit.source,
                "score": hit.score,
                "meta": hit.meta,
            }
            for hit in response.hits
        ],
        "engine_payloads": response.engine_payloads,
    }


@router.post("/summary")
async def read_summary(request: SummaryRequest) -> dict:
    service = DataService(Path(request.workspace))
    return service.read_summary_bundle()


@router.post("/graph")
async def read_graph(request: GraphRequest) -> dict:
    service = DataService(Path(request.workspace))
    return service.get_graph_snapshot(max_nodes=request.max_nodes)


@router.post("/distill")
async def read_distill(request: DistillRequest) -> dict:
    service = DataService(Path(request.workspace))
    payload = service.read_distill_bundle(
        source_id=request.source_id,
        limit=request.limit,
        kind=request.kind,
        min_importance=request.min_importance,
        llm_enriched_only=request.llm_enriched_only,
        authority=request.authority,
        min_source_weight=request.min_source_weight,
        min_source_density=request.min_source_density,
    )
    if request.source_id and payload["source"] is None:
        raise HTTPException(status_code=404, detail=f"Unknown source_id: {request.source_id}")
    return payload


@router.post("/boundary")
async def read_boundary(request: SummaryRequest) -> dict:
    service = DataService(Path(request.workspace))
    return service.read_boundary_audit()


@router.post("/graphrag/execute")
async def execute_graphrag(request: GraphRAGExecuteRequest) -> dict:
    service = DataService(Path(request.workspace))
    return service.run_graphrag_execution_request()


@router.post("/quality/feedback")
async def record_quality_feedback(request: QualityFeedbackRequest) -> dict:
    service = DataService(Path(request.workspace))
    try:
        record = service.record_quality_feedback(
            target_type=request.target_type,
            target_id=request.target_id,
            action=request.action,
            label=request.label,
            suggested_value=request.suggested_value,
            reason=request.reason,
            metadata=request.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "workspace": str(service.workspace),
        "feedback": record,
        "summary": service.read_quality_feedback(limit=20)["summary"],
    }


@router.post("/quality/feedback/list")
async def list_quality_feedback(request: QualityFeedbackListRequest) -> dict:
    service = DataService(Path(request.workspace))
    return service.read_quality_feedback(
        limit=request.limit,
        target_type=request.target_type,
        target_id=request.target_id,
    )


@router.post("/quality/corrections")
async def list_quality_corrections(request: QualityCorrectionRulesRequest) -> dict:
    service = DataService(Path(request.workspace))
    return service.read_quality_correction_rules(limit=request.limit, status=request.status)


@router.post("/quality/corrections/build")
async def build_quality_corrections(request: QualityCorrectionRulesBuildRequest) -> dict:
    service = DataService(Path(request.workspace))
    return service.build_quality_correction_rules()


@router.post("/page")
async def read_page(request: PageRequest) -> dict:
    service = DataService(Path(request.workspace))
    return service.read_llmwiki_page(request.slug)


@router.post("/reset")
async def reset_workspace(request: ResetRequest) -> dict:
    service = DataService(Path(request.workspace))
    try:
        return service.reset_workspace(request.confirmation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
