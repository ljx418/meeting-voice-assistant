"""V5.7B limited production controlled executor runtime slice.

This module models a staging-only runtime slice for production controlled
executor semantics. It does not register routes, start workers, grant Agent
mutation authority, call connectors, call external LLMs, or write
WorkflowDraft / WorkflowVersion / WorkflowStore directly.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext


INITIAL_ACTION_SET = {
    "workflow.instance.start",
    "station.rerun",
    "artifact.write",
    "quality.evaluation.create",
}

EXCLUDED_ACTIONS = {
    "business.event.emit",
    "context.update",
    "workflow.template.publish",
    "approval.respond",
    "connector.call",
    "external_llm.call",
}

MUTATION_ACTIONS = INITIAL_ACTION_SET | EXCLUDED_ACTIONS
MEDIUM_RISK_ACTIONS = {"artifact.write", "quality.evaluation.create"}
ALLOWED_SOURCES = {"product_console", "approved_api"}
ALLOWED_ACTOR_TYPES = {"human_user", "service_account"}
SENSITIVE_TEXT = (
    "capability_token",
    "subscription_token",
    "authorization:",
    "bearer ",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed url",
    "api_key",
    "sk-",
)


class ProductionControlledExecutorError(ValueError):
    """Stable V5.7B staging runtime denial."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        """Return a redacted error shape."""
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class ExecutionScope:
    """Tenant-bound execution target scope."""

    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str

    @classmethod
    def from_context(cls, context: IdentityContext) -> "ExecutionScope":
        """Create a scope matching one server-bound identity context."""
        return cls(
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
        )


@dataclass(frozen=True)
class HumanAuthorization:
    """Human authorization reference for controlled execution."""

    human_authorization_ref: str
    authorization_subject_actor_id: str
    authorization_created_at: str
    authorization_expires_at: str
    allowed_operations: tuple[str, ...]
    tenant_id: str
    workspace_id: str
    audit_ref: str

    def allows(self, context: IdentityContext, operation: str, now: str) -> bool:
        """Return whether this authorization can approve the operation."""
        return (
            self.tenant_id == context.tenant_id
            and self.workspace_id == context.workspace_id
            and self.authorization_subject_actor_id == context.actor_id
            and operation in self.allowed_operations
            and self.authorization_expires_at > now
        )

    def to_dict(self) -> dict[str, Any]:
        """Return redacted authorization metadata."""
        data = asdict(self)
        data["allowed_operations"] = list(self.allowed_operations)
        return data


@dataclass(frozen=True)
class ApprovedApiClient:
    """Tenant-bound approved API source boundary."""

    api_client_id: str
    tenant_id: str
    workspace_id: str
    service_account_id: str
    human_authorization_ref: str
    allowed_operations: tuple[str, ...]
    rate_limit_policy_ref: str
    quota_policy_ref: str
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        """Return redacted approved API client metadata."""
        data = asdict(self)
        data["allowed_operations"] = list(self.allowed_operations)
        return data


@dataclass(frozen=True)
class ExecutionAttempt:
    """One station attempt."""

    attempt_id: str
    station_id: str
    station_run_id: str
    attempt_number: int
    status: str
    error_ref: str | None = None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return attempt DTO."""
        return asdict(self)


@dataclass
class WorkflowExecutionState:
    """In-memory staging runtime state."""

    workflow_instance_id: str
    status: str
    station_attempts: dict[str, list[ExecutionAttempt]]
    downstream_stale: list[str] = field(default_factory=list)
    artifact_versions: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    quality_evaluations: list[dict[str, Any]] = field(default_factory=list)
    revision: int = 0
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted state DTO."""
        return mask_value(
            {
                "workflow_instance_id": self.workflow_instance_id,
                "status": self.status,
                "station_attempts": {station_id: [attempt.to_dict() for attempt in attempts] for station_id, attempts in self.station_attempts.items()},
                "downstream_stale": list(self.downstream_stale),
                "artifact_versions": self.artifact_versions,
                "quality_evaluations": self.quality_evaluations,
                "revision": self.revision,
                "updated_at": self.updated_at,
                "staging_only": True,
                "production_ready": False,
            }
        )


@dataclass(frozen=True)
class ProductionExecutionRequest:
    """One V5.7B limited runtime action request."""

    operation: str
    source: str
    actor_type: str
    target_refs: dict[str, str]
    user_confirmed: bool
    human_authorization: HumanAuthorization | None
    target_scope: ExecutionScope
    idempotency_key: str
    correlation_id: str
    request_id: str
    approved_api_client: ApprovedApiClient | None = None
    approval_gate_decision_ref: str | None = None
    payload_refs: dict[str, str] = field(default_factory=dict)
    timeout_policy_ref: str = "timeout-policy://v5-7b/default"
    kill_switch_decision_ref: str = "kill-switch://v5-7b/checked"
    incident_timeline_ref: str = "incident-timeline://v5-7b/default"
    audit_export_ref: str = "audit-export://v5-7b/default"
    credential_decision_ref: str = "credential-decision://v5-7b/not-required"


@dataclass(frozen=True)
class ExecutionEvidence:
    """Execution evidence for one allowed staging runtime action."""

    execution_evidence_id: str
    operation: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    target_refs: dict[str, str]
    actor_type: str
    actor_id: str
    source: str
    user_confirmed: bool
    human_authorization_ref: str
    approval_gate_decision_ref: str | None
    policy_decision: str
    capability_decision: str
    credential_decision_ref: str
    runtime_result_ref: str
    idempotency_key: str
    rollback_descriptor_ref: str
    kill_switch_decision_ref: str
    timeout_policy_ref: str
    incident_timeline_ref: str
    audit_export_ref: str
    correlation_id: str
    request_id: str
    redaction_status: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted evidence DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class ProductionExecutionResult:
    """Result of one V5.7B staging runtime action."""

    result_id: str
    operation: str
    status: str
    policy_decision: str
    capability_decision: str
    runtime_result_ref: str | None
    evidence: ExecutionEvidence | None
    workflow_state: dict[str, Any] | None
    blocked_reason: str | None = None
    idempotent_replay: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return redacted result DTO."""
        return mask_value(
            {
                "result_id": self.result_id,
                "operation": self.operation,
                "status": self.status,
                "policy_decision": self.policy_decision,
                "capability_decision": self.capability_decision,
                "runtime_result_ref": self.runtime_result_ref,
                "evidence": self.evidence.to_dict() if self.evidence else None,
                "workflow_state": self.workflow_state,
                "blocked_reason": self.blocked_reason,
                "idempotent_replay": self.idempotent_replay,
                "staging_only": True,
                "production_ready": False,
            }
        )


class LimitedProductionControlledExecutorRuntime:
    """Staging-only runtime slice for limited production controlled actions."""

    def __init__(self) -> None:
        self.workflow_states: dict[str, WorkflowExecutionState] = {}
        self.idempotency_results: dict[str, ProductionExecutionResult] = {}
        self.evidence: list[ExecutionEvidence] = []
        self.workspace_kill_switches: set[str] = set()

    def seed_workflow(self, *, workflow_instance_id: str, station_id: str, station_run_id: str, failed: bool = False) -> WorkflowExecutionState:
        """Seed one staging fixture workflow."""
        status = "failed" if failed else "created"
        attempt = ExecutionAttempt(
            attempt_id=f"attempt_{uuid4().hex[:12]}",
            station_id=station_id,
            station_run_id=station_run_id,
            attempt_number=1,
            status=status,
            error_ref="error://v5-7b/seeded-parse-failure" if failed else None,
        )
        state = WorkflowExecutionState(
            workflow_instance_id=workflow_instance_id,
            status=status,
            station_attempts={station_id: [attempt]},
        )
        self.workflow_states[workflow_instance_id] = state
        return state

    def disable_workspace(self, workspace_id: str) -> None:
        """Enable a staging kill switch for one workspace."""
        self.workspace_kill_switches.add(workspace_id)

    def execute(self, context: IdentityContext, request: ProductionExecutionRequest) -> ProductionExecutionResult:
        """Execute one limited staging runtime action after all gates pass."""
        try:
            self._validate_request(context, request)
        except ProductionControlledExecutorError as exc:
            return self._blocked(request.operation, exc.reason)

        if request.idempotency_key in self.idempotency_results:
            prior = self.idempotency_results[request.idempotency_key]
            return ProductionExecutionResult(
                result_id=f"v5_7b_result_{uuid4().hex[:12]}",
                operation=request.operation,
                status="idempotent_replay",
                policy_decision=prior.policy_decision,
                capability_decision=prior.capability_decision,
                runtime_result_ref=prior.runtime_result_ref,
                evidence=prior.evidence,
                workflow_state=prior.workflow_state,
                idempotent_replay=True,
            )

        state = self._state_for(request)
        if request.operation == "workflow.instance.start":
            result = self._start_workflow(context, request, state)
        elif request.operation == "station.rerun":
            result = self._rerun_station(context, request, state)
        elif request.operation == "artifact.write":
            result = self._write_artifact(context, request, state)
        elif request.operation == "quality.evaluation.create":
            result = self._create_quality_evaluation(context, request, state)
        else:
            result = self._blocked(request.operation, "unsupported_operation")
        if result.status == "applied_limited_runtime_slice":
            self.idempotency_results[request.idempotency_key] = result
        return result

    def _validate_request(self, context: IdentityContext, request: ProductionExecutionRequest) -> None:
        _assert_no_sensitive_payload(asdict(request))
        if request.operation in EXCLUDED_ACTIONS or request.operation not in INITIAL_ACTION_SET:
            raise ProductionControlledExecutorError("V5_7B_ACTION_DENIED", "Operation is not in the V5-7B initial controlled action set.", reason="operation_not_allowed", resource=request.operation)
        if request.source == "agent" or request.actor_type == "agent" or context.actor_type == "agent":
            raise ProductionControlledExecutorError("V5_7B_AGENT_DENIED", "Agent source cannot execute durable mutation.", reason="source_agent_durable_mutation_denied")
        if request.source not in ALLOWED_SOURCES:
            raise ProductionControlledExecutorError("V5_7B_SOURCE_DENIED", "Source is not approved for V5-7B controlled runtime.", reason="source_not_allowed", resource=request.source)
        if request.actor_type not in ALLOWED_ACTOR_TYPES or request.actor_type != context.actor_type:
            raise ProductionControlledExecutorError("V5_7B_ACTOR_DENIED", "Actor type is not approved for V5-7B controlled runtime.", reason="actor_not_allowed", resource=request.actor_type)
        if not request.user_confirmed:
            raise ProductionControlledExecutorError("V5_7B_USER_CONFIRMATION_REQUIRED", "Controlled runtime action requires user_confirmed=true.", reason="missing_user_confirmation")
        if context.workspace_id in self.workspace_kill_switches:
            raise ProductionControlledExecutorError("V5_7B_KILL_SWITCH_DENIED", "Workspace kill switch is active.", reason="workspace_kill_switch_active")
        self._validate_scope(context, request.target_scope)
        self._validate_human_authorization(context, request)
        self._validate_approved_api(context, request)
        self._validate_target_refs(request)
        if request.operation in MEDIUM_RISK_ACTIONS and not request.approval_gate_decision_ref:
            raise ProductionControlledExecutorError("V5_7B_APPROVAL_GATE_REQUIRED", "Medium-risk action requires an approval gate decision.", reason="approval_gate_required", resource=request.operation)

    def _validate_scope(self, context: IdentityContext, target_scope: ExecutionScope) -> None:
        if target_scope.tenant_id != context.tenant_id:
            raise ProductionControlledExecutorError("V5_7B_TENANT_SCOPE_DENIED", "Target tenant does not match actor tenant.", reason="tenant_mismatch")
        if target_scope.workspace_id != context.workspace_id:
            raise ProductionControlledExecutorError("V5_7B_WORKSPACE_SCOPE_DENIED", "Target workspace does not match actor workspace.", reason="workspace_mismatch")
        if target_scope.project_id != context.project_id:
            raise ProductionControlledExecutorError("V5_7B_PROJECT_SCOPE_DENIED", "Target project does not match actor project.", reason="project_mismatch")
        if target_scope.app_id != context.app_id:
            raise ProductionControlledExecutorError("V5_7B_APP_SCOPE_DENIED", "Target app does not match actor app.", reason="app_mismatch")

    def _validate_human_authorization(self, context: IdentityContext, request: ProductionExecutionRequest) -> None:
        now = _now()
        authorization = request.human_authorization
        if authorization is None:
            raise ProductionControlledExecutorError("V5_7B_HUMAN_AUTHORIZATION_REQUIRED", "Controlled runtime action requires a human_authorization_ref.", reason="missing_human_authorization")
        if not authorization.allows(context, request.operation, now):
            raise ProductionControlledExecutorError("V5_7B_HUMAN_AUTHORIZATION_DENIED", "Human authorization is expired, out of scope, or does not allow the operation.", reason="human_authorization_invalid", resource=request.operation)

    def _validate_approved_api(self, context: IdentityContext, request: ProductionExecutionRequest) -> None:
        if request.source != "approved_api":
            return
        client = request.approved_api_client
        if client is None:
            raise ProductionControlledExecutorError("V5_7B_APPROVED_API_DENIED", "approved_api source requires an API client boundary.", reason="missing_api_client")
        if client.status != "active":
            raise ProductionControlledExecutorError("V5_7B_APPROVED_API_DENIED", "approved_api client is not active.", reason="api_client_not_active")
        if client.tenant_id != context.tenant_id:
            raise ProductionControlledExecutorError("V5_7B_APPROVED_API_DENIED", "approved_api client tenant mismatch.", reason="approved_api_wrong_tenant")
        if client.workspace_id != context.workspace_id:
            raise ProductionControlledExecutorError("V5_7B_APPROVED_API_DENIED", "approved_api client workspace mismatch.", reason="approved_api_wrong_workspace")
        if context.service_account_id != client.service_account_id:
            raise ProductionControlledExecutorError("V5_7B_APPROVED_API_DENIED", "approved_api client service account mismatch.", reason="approved_api_service_account_mismatch")
        if request.operation not in client.allowed_operations:
            raise ProductionControlledExecutorError("V5_7B_APPROVED_API_DENIED", "approved_api client is not allowed for this operation.", reason="approved_api_wrong_operation")
        if request.human_authorization is None or client.human_authorization_ref != request.human_authorization.human_authorization_ref:
            raise ProductionControlledExecutorError("V5_7B_APPROVED_API_DENIED", "approved_api requires a matching human_authorization_ref.", reason="approved_api_missing_human_authorization")

    def _validate_target_refs(self, request: ProductionExecutionRequest) -> None:
        refs = request.target_refs
        if request.operation == "workflow.instance.start" and not refs.get("workflow_instance_id"):
            raise ProductionControlledExecutorError("V5_7B_TARGET_REF_REQUIRED", "workflow.instance.start requires workflow_instance_id.", reason="missing_workflow_instance_id")
        if request.operation == "station.rerun" and (not refs.get("station_id") or not refs.get("station_run_id") or not refs.get("workflow_instance_id")):
            raise ProductionControlledExecutorError("V5_7B_TARGET_REF_REQUIRED", "station.rerun requires workflow_instance_id, station_id, and station_run_id.", reason="missing_station_rerun_target")
        if request.operation == "artifact.write" and not (refs.get("artifact_id") or refs.get("output_artifact_target_id")):
            raise ProductionControlledExecutorError("V5_7B_TARGET_REF_REQUIRED", "artifact.write requires artifact_id or output_artifact_target_id.", reason="missing_artifact_target")
        if request.operation == "quality.evaluation.create" and not (refs.get("quality_evaluation_id") or refs.get("station_id") or refs.get("artifact_id")):
            raise ProductionControlledExecutorError("V5_7B_TARGET_REF_REQUIRED", "quality.evaluation.create requires quality_evaluation_id, station_id, or artifact_id.", reason="missing_quality_target")

    def _state_for(self, request: ProductionExecutionRequest) -> WorkflowExecutionState:
        workflow_instance_id = request.target_refs.get("workflow_instance_id") or "workflow_v5_7b_staging_default"
        state = self.workflow_states.get(workflow_instance_id)
        if state is None:
            state = WorkflowExecutionState(workflow_instance_id=workflow_instance_id, status="created", station_attempts={})
            self.workflow_states[workflow_instance_id] = state
        return state

    def _start_workflow(self, context: IdentityContext, request: ProductionExecutionRequest, state: WorkflowExecutionState) -> ProductionExecutionResult:
        state.status = "running"
        state.revision += 1
        state.updated_at = _now()
        return self._applied(context, request, state, runtime_result_ref=f"runtime://v5-7b/{state.workflow_instance_id}/start")

    def _rerun_station(self, context: IdentityContext, request: ProductionExecutionRequest, state: WorkflowExecutionState) -> ProductionExecutionResult:
        station_id = request.target_refs["station_id"]
        station_run_id = request.target_refs["station_run_id"]
        attempts = state.station_attempts.setdefault(station_id, [])
        attempts.append(
            ExecutionAttempt(
                attempt_id=f"attempt_{uuid4().hex[:12]}",
                station_id=station_id,
                station_run_id=f"{station_run_id}_retry_{len(attempts) + 1}",
                attempt_number=len(attempts) + 1,
                status="completed",
            )
        )
        state.status = "running"
        state.downstream_stale = sorted(set(state.downstream_stale) | {f"downstream-of:{station_id}"})
        state.revision += 1
        state.updated_at = _now()
        return self._applied(context, request, state, runtime_result_ref=f"runtime://v5-7b/{state.workflow_instance_id}/rerun/{station_id}")

    def _write_artifact(self, context: IdentityContext, request: ProductionExecutionRequest, state: WorkflowExecutionState) -> ProductionExecutionResult:
        artifact_id = request.target_refs.get("artifact_id") or request.target_refs["output_artifact_target_id"]
        versions = state.artifact_versions.setdefault(artifact_id, [])
        versions.append(
            {
                "artifact_version_id": f"artifact-version-{len(versions) + 1}",
                "artifact_id": artifact_id,
                "operation": "append_version",
                "content_ref": request.payload_refs.get("content_ref", f"artifact-content-ref://{artifact_id}/{len(versions) + 1}"),
                "created_at": _now(),
            }
        )
        state.revision += 1
        state.updated_at = _now()
        return self._applied(context, request, state, runtime_result_ref=f"runtime://v5-7b/{state.workflow_instance_id}/artifact/{artifact_id}")

    def _create_quality_evaluation(self, context: IdentityContext, request: ProductionExecutionRequest, state: WorkflowExecutionState) -> ProductionExecutionResult:
        evaluation_id = request.target_refs.get("quality_evaluation_id") or f"quality-evaluation-{len(state.quality_evaluations) + 1}"
        state.quality_evaluations.append(
            {
                "quality_evaluation_id": evaluation_id,
                "quality_rule_ref": request.payload_refs.get("quality_rule_ref", "quality-rule://v5-7b/default"),
                "target_ref": request.target_refs.get("artifact_id") or request.target_refs.get("station_id"),
                "score_ref": request.payload_refs.get("score_ref", f"quality-score-ref://{evaluation_id}"),
                "operation": "append_evaluation",
                "created_at": _now(),
            }
        )
        state.revision += 1
        state.updated_at = _now()
        return self._applied(context, request, state, runtime_result_ref=f"runtime://v5-7b/{state.workflow_instance_id}/quality/{evaluation_id}")

    def _applied(self, context: IdentityContext, request: ProductionExecutionRequest, state: WorkflowExecutionState, *, runtime_result_ref: str) -> ProductionExecutionResult:
        evidence = ExecutionEvidence(
            execution_evidence_id=f"v5_7b_evidence_{uuid4().hex[:12]}",
            operation=request.operation,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            target_refs=dict(request.target_refs),
            actor_type=context.actor_type,
            actor_id=context.actor_id,
            source=request.source,
            user_confirmed=request.user_confirmed,
            human_authorization_ref=request.human_authorization.human_authorization_ref if request.human_authorization else "",
            approval_gate_decision_ref=request.approval_gate_decision_ref,
            policy_decision="allow",
            capability_decision="allow_limited_runtime_slice",
            credential_decision_ref=request.credential_decision_ref,
            runtime_result_ref=runtime_result_ref,
            idempotency_key=request.idempotency_key,
            rollback_descriptor_ref=f"rollback://v5-7b/{request.operation}/{request.idempotency_key}",
            kill_switch_decision_ref=request.kill_switch_decision_ref,
            timeout_policy_ref=request.timeout_policy_ref,
            incident_timeline_ref=request.incident_timeline_ref,
            audit_export_ref=request.audit_export_ref,
            correlation_id=request.correlation_id,
            request_id=request.request_id,
            redaction_status="redacted",
        )
        _assert_no_sensitive_payload(evidence.to_dict())
        self.evidence.append(evidence)
        return ProductionExecutionResult(
            result_id=f"v5_7b_result_{uuid4().hex[:12]}",
            operation=request.operation,
            status="applied_limited_runtime_slice",
            policy_decision="allow",
            capability_decision="allow_limited_runtime_slice",
            runtime_result_ref=runtime_result_ref,
            evidence=evidence,
            workflow_state=state.to_dict(),
        )

    def _blocked(self, operation: str, reason: str) -> ProductionExecutionResult:
        return ProductionExecutionResult(
            result_id=f"v5_7b_result_{uuid4().hex[:12]}",
            operation=operation,
            status="blocked",
            policy_decision="deny",
            capability_decision="deny",
            runtime_result_ref=None,
            evidence=None,
            workflow_state=None,
            blocked_reason=reason,
        )


def _assert_no_sensitive_payload(data: Mapping[str, Any]) -> None:
    dumped = json.dumps(data, ensure_ascii=False).lower()
    for term in SENSITIVE_TEXT:
        if term in dumped:
            raise ProductionControlledExecutorError("V5_7B_REDACTION_FAILED", "Sensitive text is not allowed in V5-7B runtime DTOs.", reason="redaction_failed", resource=term)


def _now() -> str:
    return datetime.now(UTC).isoformat()
