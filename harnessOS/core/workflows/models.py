"""V3.6 workflow runtime contract models.

These models define protocol-facing workflow contracts only. They do not
register runtime handlers, access stores, or execute workflow logic.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class FrozenWorkflowBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, use_enum_values=True)


class WorkflowTemplateStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class WorkflowDraftStatus(str, Enum):
    EDITABLE = "editable"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class WorkflowInstanceStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StationRunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ArtifactDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class ArtifactCardinality(str, Enum):
    ONE = "one"
    MANY = "many"


class ArtifactKindMatchPolicy(str, Enum):
    EXACT = "exact"
    COMPATIBLE = "compatible"


class EvaluatorType(str, Enum):
    RULE = "rule"
    MANUAL = "manual"
    LLM_PLACEHOLDER = "llm_placeholder"


class WorkflowActionType(str, Enum):
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    RERUN = "rerun"
    UPDATE_CONTEXT = "update_context"
    ATTACH_ARTIFACT = "attach_artifact"


class WorkflowPatchTarget(str, Enum):
    DRAFT = "draft"


class WorkflowPatchOperation(str, Enum):
    ADD_STATION = "add_station"
    REMOVE_STATION = "remove_station"
    UPDATE_STATION_PROMPT = "update_station_prompt"
    UPDATE_CONNECTOR = "update_connector"
    UPDATE_ARTIFACT_CONTRACT = "update_artifact_contract"
    UPDATE_QUALITY_RULE = "update_quality_rule"
    UPDATE_APPROVAL_POINT = "update_approval_point"
    UPDATE_EDGE = "update_edge"


class WorkflowPatchStatus(str, Enum):
    PROPOSED = "proposed"
    APPLIED = "applied"
    REJECTED = "rejected"


class WorkflowPatchActorType(str, Enum):
    AGENT = "agent"
    USER = "user"
    SYSTEM = "system"


class ArtifactContract(WorkflowBaseModel):
    contract_id: str
    artifact_kind: str
    direction: ArtifactDirection
    required: bool = True
    cardinality: ArtifactCardinality = ArtifactCardinality.ONE
    kind_match_policy: ArtifactKindMatchPolicy = ArtifactKindMatchPolicy.EXACT
    schema_ref: str | None = None
    metadata_schema: dict[str, Any] = Field(default_factory=dict)
    preview_policy: dict[str, Any] = Field(default_factory=dict)
    large_file_policy_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QualityContract(WorkflowBaseModel):
    contract_id: str
    rubric_id: str
    evaluator_type: EvaluatorType = EvaluatorType.RULE
    required: bool = False
    blocking: bool = False
    threshold: float | None = None
    policy: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Station(WorkflowBaseModel):
    station_id: str
    name: str
    role: str = ""
    agent_ref: str | None = None
    skill_refs: list[str] = Field(default_factory=list)
    connector_refs: list[str] = Field(default_factory=list)
    input_contracts: list[ArtifactContract] = Field(default_factory=list)
    output_contracts: list[ArtifactContract] = Field(default_factory=list)
    approval_required: bool = False
    quality_policy: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_contract_ids(self) -> "Station":
        input_ids = [contract.contract_id for contract in self.input_contracts]
        output_ids = [contract.contract_id for contract in self.output_contracts]
        duplicate_ids = {
            contract_id
            for contract_id in input_ids + output_ids
            if (input_ids + output_ids).count(contract_id) > 1
        }
        if duplicate_ids:
            raise ValueError(f"station contains duplicate artifact contract ids: {', '.join(sorted(duplicate_ids))}")
        return self


class WorkflowEdge(WorkflowBaseModel):
    edge_id: str
    from_station_id: str
    to_station_id: str
    condition: dict[str, Any] = Field(default_factory=dict)
    order: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowTemplate(WorkflowBaseModel):
    workflow_template_id: str
    app_id: str
    project_id: str | None = None
    workspace_id: str | None = None
    name: str
    description: str = ""
    status: WorkflowTemplateStatus = WorkflowTemplateStatus.DRAFT
    version: str = "0.1.0"
    latest_draft_id: str | None = None
    latest_published_version_id: str | None = None
    stations: list[Station] = Field(default_factory=list)
    edges: list[WorkflowEdge] = Field(default_factory=list)
    artifact_contracts: list[ArtifactContract] = Field(default_factory=list)
    quality_contracts: list[QualityContract] = Field(default_factory=list)
    approval_points: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_station_graph(self) -> "WorkflowTemplate":
        station_ids = {station.station_id for station in self.stations}
        if len(station_ids) != len(self.stations):
            raise ValueError("workflow template contains duplicate station ids")
        missing: list[str] = []
        for edge in self.edges:
            if edge.from_station_id not in station_ids:
                missing.append(edge.from_station_id)
            if edge.to_station_id not in station_ids:
                missing.append(edge.to_station_id)
        if missing:
            missing_ids = ", ".join(sorted(set(missing)))
            raise ValueError(f"workflow edge references missing station ids: {missing_ids}")
        return self


class WorkflowDraft(WorkflowBaseModel):
    workflow_draft_id: str
    workflow_template_id: str
    base_version: str | None = None
    base_version_id: str | None = None
    status: WorkflowDraftStatus = WorkflowDraftStatus.EDITABLE
    revision: int = Field(default=1, ge=1)
    draft: dict[str, Any]
    updated_at: datetime = Field(default_factory=_now_utc)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowVersion(FrozenWorkflowBaseModel):
    workflow_version_id: str
    workflow_template_id: str
    version: str
    published_at: datetime = Field(default_factory=_now_utc)
    snapshot: dict[str, Any]
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowInstance(WorkflowBaseModel):
    workflow_instance_id: str
    workflow_template_id: str
    workflow_version: str
    workflow_version_id: str | None = None
    session_id: str | None = None
    thread_id: str | None = None
    app_id: str
    project_id: str | None = None
    workspace_id: str | None = None
    status: WorkflowInstanceStatus = WorkflowInstanceStatus.CREATED
    current_station_ids: list[str] = Field(default_factory=list)
    job_ids: list[str] = Field(default_factory=list)
    artifact_ids: list[str] = Field(default_factory=list)
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StationRun(WorkflowBaseModel):
    station_run_id: str
    workflow_instance_id: str
    station_id: str
    status: StationRunStatus = StationRunStatus.QUEUED
    attempt: int = Field(default=1, ge=1)
    rerun_of_station_run_id: str | None = None
    job_id: str | None = None
    input_artifact_ids: list[str] = Field(default_factory=list)
    output_artifact_ids: list[str] = Field(default_factory=list)
    input_bindings: dict[str, list[str]] = Field(default_factory=dict)
    output_bindings: dict[str, list[str]] = Field(default_factory=dict)
    quality_evaluation_ids: list[str] = Field(default_factory=list)
    failure_context: dict[str, Any] = Field(default_factory=dict)
    trace_id: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class QualityEvaluation(WorkflowBaseModel):
    evaluation_id: str
    workflow_instance_id: str
    station_run_id: str
    artifact_id: str | None = None
    rubric_id: str
    evaluator_type: EvaluatorType = EvaluatorType.RULE
    score: float | None = None
    status: str
    issues: list[dict[str, Any]] = Field(default_factory=list)
    suggestions: list[dict[str, Any]] = Field(default_factory=list)
    evaluator: str | None = None
    created_at: datetime = Field(default_factory=_now_utc)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowAction(WorkflowBaseModel):
    action_id: str
    workflow_instance_id: str
    action_type: WorkflowActionType
    station_run_id: str | None = None
    station_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowPatch(WorkflowBaseModel):
    workflow_patch_id: str
    workflow_template_id: str
    workflow_draft_id: str
    base_revision: int = Field(ge=1)
    base_version_id: str | None = None
    target: Literal["draft"] = "draft"
    operation: WorkflowPatchOperation
    payload: dict[str, Any] = Field(default_factory=dict)
    diff: dict[str, Any]
    proposed_by: str
    actor_type: WorkflowPatchActorType = WorkflowPatchActorType.USER
    actor_id: str | None = None
    status: WorkflowPatchStatus = WorkflowPatchStatus.PROPOSED
    applied_revision: int | None = None
    resulting_draft_revision: int | None = None
    rejected_reason: str | None = None
    risk_flags: list[str] = Field(default_factory=list)
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowContext(WorkflowBaseModel):
    workflow_instance_id: str
    app_id: str
    project_id: str | None = None
    workspace_id: str | None = None
    revision: int = Field(default=1, ge=1)
    system: dict[str, Any] = Field(default_factory=dict)
    business: dict[str, Any] = Field(default_factory=dict)
    runtime: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=_now_utc)
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BusinessEvent(WorkflowBaseModel):
    event_id: str | None = None
    idempotency_key: str | None = None
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    scope: dict[str, Any] = Field(default_factory=dict)
    workflow_instance_id: str | None = None
    trace_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def validate_business_namespace(cls, value: str) -> str:
        if not value.startswith("business.") or value == "business.*":
            raise ValueError("business event type must use a concrete business.* namespace")
        return value


class BusinessEventBinding(WorkflowBaseModel):
    binding_id: str
    workflow_instance_id: str
    event_type: str
    target_path: str
    payload_path: str
    mode: Literal["set"] = "set"
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        if not value.startswith("business.") or value == "business.*":
            raise ValueError("binding event_type must use a concrete business.* namespace")
        return value

    @field_validator("target_path")
    @classmethod
    def validate_target_path(cls, value: str) -> str:
        if not value.startswith("context.business."):
            raise ValueError("binding target_path must be under context.business.*")
        return value

    @field_validator("payload_path")
    @classmethod
    def validate_payload_path(cls, value: str) -> str:
        if not value.startswith("event.payload."):
            raise ValueError("binding payload_path must read from event.payload.*")
        return value


class PipelineBoard(WorkflowBaseModel):
    workflow_instance: dict[str, Any]
    stations: list[dict[str, Any]]
    current_station_ids: list[str] = Field(default_factory=list)
    jobs: list[dict[str, Any]] = Field(default_factory=list)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    approvals: list[dict[str, Any]] = Field(default_factory=list)
    quality_evaluations: list[dict[str, Any]] = Field(default_factory=list)
    trace_summary: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
