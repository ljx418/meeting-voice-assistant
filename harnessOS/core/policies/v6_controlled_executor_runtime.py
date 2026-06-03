"""V6.4 limited production controlled executor pilot slice.

This module implements only the V6-4 pilot runtime slice. It does not expose
production executor routes, start runtime workers, grant Agent mutation
authority, call connectors, call external LLMs, or write WorkflowDraft /
WorkflowVersion / WorkflowStore directly.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext
from core.observability.production_audit import ProductionAuditService


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

MEDIUM_RISK_ACTIONS = {"artifact.write", "quality.evaluation.create"}
ALLOWED_SOURCES = {"product_console", "approved_api"}
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


class V6ControlledExecutorError(ValueError):
    """Stable V6-4 controlled executor denial."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class V6ExecutionScope:
    """Tenant-bound V6 execution target scope."""

    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str

    @classmethod
    def from_context(cls, context: IdentityContext) -> "V6ExecutionScope":
        return cls(
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
        )


@dataclass(frozen=True)
class V6HumanAuthorization:
    """Human authorization reference for V6-4 controlled execution."""

    human_authorization_ref: str
    authorization_subject_actor_id: str
    authorization_created_at: str
    authorization_expires_at: str
    allowed_operations: tuple[str, ...]
    tenant_id: str
    workspace_id: str
    authorizing_human_user_id: str
    audit_ref: str

    def allows(self, context: IdentityContext, operation: str, now: str) -> bool:
        return (
            self.tenant_id == context.tenant_id
            and self.workspace_id == context.workspace_id
            and operation in self.allowed_operations
            and self.authorization_expires_at > now
            and bool(self.authorizing_human_user_id)
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_operations"] = list(self.allowed_operations)
        return data


@dataclass(frozen=True)
class V6ApprovedApiClient:
    """Tenant-bound approved API source boundary."""

    api_client_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    service_account_id: str
    human_authorization_ref: str
    allowed_operations: tuple[str, ...]
    rate_limit_policy_ref: str
    quota_policy_ref: str
    status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_operations"] = list(self.allowed_operations)
        return data


@dataclass(frozen=True)
class V6ExecutionAttempt:
    """One V6-4 station attempt."""

    attempt_id: str
    station_id: str
    station_run_id: str
    attempt_number: int
    status: str
    error_ref: str | None = None
    producer_runtime_result_ref: str | None = None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class V6ControlledRuntimeState:
    """In-memory V6-4 pilot runtime state."""

    workflow_instance_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    status: str
    station_attempts: dict[str, list[V6ExecutionAttempt]]
    downstream_stale: list[str] = field(default_factory=list)
    artifact_versions: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    quality_evaluations: list[dict[str, Any]] = field(default_factory=list)
    runtime_result_refs: list[str] = field(default_factory=list)
    incident_timeline_refs: list[str] = field(default_factory=list)
    audit_event_refs: list[str] = field(default_factory=list)
    revision: int = 0
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return mask_value(
            {
                "workflow_instance_id": self.workflow_instance_id,
                "tenant_id": self.tenant_id,
                "workspace_id": self.workspace_id,
                "project_id": self.project_id,
                "app_id": self.app_id,
                "status": self.status,
                "station_attempts": {station_id: [attempt.to_dict() for attempt in attempts] for station_id, attempts in self.station_attempts.items()},
                "downstream_stale": list(self.downstream_stale),
                "artifact_versions": self.artifact_versions,
                "quality_evaluations": self.quality_evaluations,
                "runtime_result_refs": list(self.runtime_result_refs),
                "incident_timeline_refs": list(self.incident_timeline_refs),
                "audit_event_refs": list(self.audit_event_refs),
                "revision": self.revision,
                "updated_at": self.updated_at,
                "pilot_slice_ready_for_review": True,
                "production_ready": False,
            }
        )


@dataclass(frozen=True)
class V6ControlledExecutionRequest:
    """One V6-4 controlled action request."""

    operation: str
    source: str
    actor_type: str
    target_refs: dict[str, str]
    user_confirmed: bool
    human_authorization: V6HumanAuthorization | None
    target_scope: V6ExecutionScope
    idempotency_key: str
    correlation_id: str
    request_id: str
    approved_api_client: V6ApprovedApiClient | None = None
    approval_gate_decision_ref: str | None = None
    payload_refs: dict[str, str] = field(default_factory=dict)
    credential_decision_ref: str = "credential-decision://v6-4/not-required"
    credential_lease_id: str | None = None
    provider_profile_id: str | None = None
    timeout_policy_ref: str = "timeout-policy://v6-4/default"
    kill_switch_decision_ref: str = "kill-switch://v6-4/checked"
    incident_timeline_ref: str = "incident-timeline://v6-4/default"
    audit_export_ref: str = "audit-export://v6-4/default"


@dataclass(frozen=True)
class V6ExecutionEvidence:
    """Execution evidence for one allowed V6-4 pilot action."""

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
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V6ControlledExecutionResult:
    """Result of one V6-4 controlled action."""

    result_id: str
    operation: str
    status: str
    policy_decision: str
    capability_decision: str
    runtime_result_ref: str | None
    evidence: V6ExecutionEvidence | None
    workflow_state: dict[str, Any] | None
    blocked_reason: str | None = None
    idempotent_replay: bool = False
    audit_event_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
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
                "audit_event_ref": self.audit_event_ref,
                "pilot_slice_ready_for_review": True,
                "production_ready": False,
            }
        )


class V6LimitedProductionControlledExecutorRuntime:
    """Limited V6-4 production pilot runtime slice."""

    def __init__(self, audit_service: ProductionAuditService | None = None) -> None:
        self.workflow_states: dict[str, V6ControlledRuntimeState] = {}
        self.idempotency_results: dict[str, V6ControlledExecutionResult] = {}
        self.idempotency_targets: dict[str, tuple[str, str, str, str, str]] = {}
        self.evidence: list[V6ExecutionEvidence] = []
        self.workspace_kill_switches: set[str] = set()
        self.audit_service = audit_service or ProductionAuditService()
        self.audit_events: list[dict[str, Any]] = []

    def seed_workflow(self, context: IdentityContext, *, workflow_instance_id: str, station_id: str, station_run_id: str, failed: bool = False) -> V6ControlledRuntimeState:
        status = "failed" if failed else "created"
        attempt = V6ExecutionAttempt(
            attempt_id=f"attempt_{uuid4().hex[:12]}",
            station_id=station_id,
            station_run_id=station_run_id,
            attempt_number=1,
            status=status,
            error_ref="error://v6-4/seeded-failure" if failed else None,
        )
        state = V6ControlledRuntimeState(
            workflow_instance_id=workflow_instance_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            status=status,
            station_attempts={station_id: [attempt]},
        )
        self.workflow_states[workflow_instance_id] = state
        return state

    def disable_workspace(self, workspace_id: str) -> None:
        self.workspace_kill_switches.add(workspace_id)

    def execute(self, context: IdentityContext, request: V6ControlledExecutionRequest) -> V6ControlledExecutionResult:
        try:
            self._validate_request(context, request)
        except V6ControlledExecutorError as exc:
            return self._blocked(context, request, exc.reason)

        fingerprint = _idempotency_fingerprint(context, request)
        if request.idempotency_key in self.idempotency_results:
            if self.idempotency_targets[request.idempotency_key] != fingerprint:
                return self._blocked(context, request, "idempotency_key_conflict")
            prior = self.idempotency_results[request.idempotency_key]
            return V6ControlledExecutionResult(
                result_id=f"v6_4_result_{uuid4().hex[:12]}",
                operation=request.operation,
                status="idempotent_replay",
                policy_decision=prior.policy_decision,
                capability_decision=prior.capability_decision,
                runtime_result_ref=prior.runtime_result_ref,
                evidence=prior.evidence,
                workflow_state=prior.workflow_state,
                idempotent_replay=True,
                audit_event_ref=prior.audit_event_ref,
            )

        state = self._state_for(context, request)
        if request.operation == "workflow.instance.start":
            result = self._start_workflow(context, request, state)
        elif request.operation == "station.rerun":
            result = self._rerun_station(context, request, state)
        elif request.operation == "artifact.write":
            result = self._write_artifact(context, request, state)
        elif request.operation == "quality.evaluation.create":
            result = self._create_quality_evaluation(context, request, state)
        else:
            result = self._blocked(context, request, "unsupported_operation")
        if result.status == "applied_limited_runtime_slice":
            self.idempotency_results[request.idempotency_key] = result
            self.idempotency_targets[request.idempotency_key] = fingerprint
        return result

    def _validate_request(self, context: IdentityContext, request: V6ControlledExecutionRequest) -> None:
        _assert_no_sensitive_payload(asdict(request))
        if request.operation in EXCLUDED_ACTIONS or request.operation not in INITIAL_ACTION_SET:
            raise V6ControlledExecutorError("V6_4_ACTION_DENIED", "Operation is not in the V6-4 action set.", reason="operation_not_allowed", resource=request.operation)
        if request.source == "agent" or request.actor_type == "agent" or context.actor_type == "agent":
            raise V6ControlledExecutorError("V6_4_AGENT_DENIED", "Agent source cannot execute durable mutation.", reason="source_agent_durable_mutation_denied")
        if request.source not in ALLOWED_SOURCES:
            raise V6ControlledExecutorError("V6_4_SOURCE_DENIED", "Source is not allowed.", reason="source_not_allowed", resource=request.source)
        self._validate_actor_binding(context, request)
        if not request.user_confirmed:
            raise V6ControlledExecutorError("V6_4_USER_CONFIRMATION_REQUIRED", "Controlled runtime action requires user_confirmed=true.", reason="missing_user_confirmation")
        if context.workspace_id in self.workspace_kill_switches:
            raise V6ControlledExecutorError("V6_4_KILL_SWITCH_DENIED", "Workspace kill switch is active.", reason="workspace_kill_switch_active")
        self._validate_scope(context, request.target_scope)
        self._validate_human_authorization(context, request)
        self._validate_approved_api(context, request)
        self._validate_target_refs(request)
        if request.operation in MEDIUM_RISK_ACTIONS and not request.approval_gate_decision_ref:
            raise V6ControlledExecutorError("V6_4_APPROVAL_GATE_REQUIRED", "Medium-risk action requires approval gate decision.", reason="approval_gate_required", resource=request.operation)

    def _validate_actor_binding(self, context: IdentityContext, request: V6ControlledExecutionRequest) -> None:
        if request.actor_type == "human_user":
            if context.actor_type != "human_user" or not context.user_id:
                raise V6ControlledExecutorError("V6_4_ACTOR_DENIED", "human_user envelope requires a human user context.", reason="missing_user_id")
        elif request.actor_type == "service_account_with_human_authorization":
            if context.actor_type != "service_account" or not context.service_account_id:
                raise V6ControlledExecutorError("V6_4_ACTOR_DENIED", "service account envelope requires service_account_id.", reason="missing_service_account_id")
            if request.human_authorization is None:
                raise V6ControlledExecutorError("V6_4_HUMAN_AUTHORIZATION_REQUIRED", "Service account execution requires human authorization.", reason="missing_human_authorization")
        else:
            raise V6ControlledExecutorError("V6_4_ACTOR_DENIED", "Actor type is not allowed for V6-4.", reason="actor_not_allowed", resource=request.actor_type)

    def _validate_scope(self, context: IdentityContext, target_scope: V6ExecutionScope) -> None:
        if target_scope.tenant_id != context.tenant_id:
            raise V6ControlledExecutorError("V6_4_TENANT_SCOPE_DENIED", "Target tenant does not match actor tenant.", reason="tenant_mismatch")
        if target_scope.workspace_id != context.workspace_id:
            raise V6ControlledExecutorError("V6_4_WORKSPACE_SCOPE_DENIED", "Target workspace does not match actor workspace.", reason="workspace_mismatch")
        if target_scope.project_id != context.project_id:
            raise V6ControlledExecutorError("V6_4_PROJECT_SCOPE_DENIED", "Target project does not match actor project.", reason="project_mismatch")
        if target_scope.app_id != context.app_id:
            raise V6ControlledExecutorError("V6_4_APP_SCOPE_DENIED", "Target app does not match actor app.", reason="app_mismatch")

    def _validate_human_authorization(self, context: IdentityContext, request: V6ControlledExecutionRequest) -> None:
        authorization = request.human_authorization
        if authorization is None:
            raise V6ControlledExecutorError("V6_4_HUMAN_AUTHORIZATION_REQUIRED", "Controlled runtime action requires human_authorization_ref.", reason="missing_human_authorization")
        if not authorization.allows(context, request.operation, _now()):
            raise V6ControlledExecutorError("V6_4_HUMAN_AUTHORIZATION_DENIED", "Human authorization is expired, out of scope, or does not allow the operation.", reason="human_authorization_invalid", resource=request.operation)

    def _validate_approved_api(self, context: IdentityContext, request: V6ControlledExecutionRequest) -> None:
        if request.source != "approved_api":
            return
        client = request.approved_api_client
        if client is None:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api requires an API client.", reason="missing_api_client")
        if client.status != "active":
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api client is not active.", reason="api_client_not_active")
        if client.tenant_id != context.tenant_id:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api client tenant mismatch.", reason="approved_api_wrong_tenant")
        if client.workspace_id != context.workspace_id:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api client workspace mismatch.", reason="approved_api_wrong_workspace")
        if client.project_id != context.project_id:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api client project mismatch.", reason="approved_api_wrong_project")
        if client.app_id != context.app_id:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api client app mismatch.", reason="approved_api_wrong_app")
        if context.service_account_id != client.service_account_id:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api client service account mismatch.", reason="approved_api_service_account_mismatch")
        if request.operation not in client.allowed_operations:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api client is not allowed for this operation.", reason="approved_api_wrong_operation")
        if request.human_authorization is None or client.human_authorization_ref != request.human_authorization.human_authorization_ref:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api requires matching human_authorization_ref.", reason="approved_api_missing_human_authorization")
        if not client.rate_limit_policy_ref or not client.quota_policy_ref:
            raise V6ControlledExecutorError("V6_4_APPROVED_API_DENIED", "approved_api requires quota and rate limit policy refs.", reason="approved_api_quota_rate_limit_missing")

    def _validate_target_refs(self, request: V6ControlledExecutionRequest) -> None:
        refs = request.target_refs
        if request.operation == "workflow.instance.start" and not refs.get("workflow_instance_id"):
            raise V6ControlledExecutorError("V6_4_TARGET_REF_REQUIRED", "workflow.instance.start requires workflow_instance_id.", reason="missing_workflow_instance_id")
        if request.operation == "station.rerun" and (not refs.get("workflow_instance_id") or not refs.get("station_id") or not refs.get("station_run_id")):
            raise V6ControlledExecutorError("V6_4_TARGET_REF_REQUIRED", "station.rerun requires workflow_instance_id, station_id, and station_run_id.", reason="missing_station_rerun_target")
        if request.operation == "artifact.write" and not (refs.get("artifact_id") or refs.get("output_artifact_target_id")):
            raise V6ControlledExecutorError("V6_4_TARGET_REF_REQUIRED", "artifact.write requires artifact_id or output_artifact_target_id.", reason="missing_artifact_target")
        if request.operation == "quality.evaluation.create" and not (refs.get("quality_evaluation_id") or refs.get("station_id") or refs.get("artifact_id")):
            raise V6ControlledExecutorError("V6_4_TARGET_REF_REQUIRED", "quality.evaluation.create requires quality_evaluation_id, station_id, or artifact_id.", reason="missing_quality_target")

    def _state_for(self, context: IdentityContext, request: V6ControlledExecutionRequest) -> V6ControlledRuntimeState:
        workflow_instance_id = request.target_refs.get("workflow_instance_id") or "workflow_v6_4_pilot_default"
        state = self.workflow_states.get(workflow_instance_id)
        if state is None:
            state = V6ControlledRuntimeState(
                workflow_instance_id=workflow_instance_id,
                tenant_id=context.tenant_id,
                workspace_id=context.workspace_id,
                project_id=context.project_id,
                app_id=context.app_id,
                status="created",
                station_attempts={},
            )
            self.workflow_states[workflow_instance_id] = state
        return state

    def _start_workflow(self, context: IdentityContext, request: V6ControlledExecutionRequest, state: V6ControlledRuntimeState) -> V6ControlledExecutionResult:
        state.status = "running"
        return self._applied(context, request, state, runtime_result_ref=f"runtime://v6-4/{state.workflow_instance_id}/start")

    def _rerun_station(self, context: IdentityContext, request: V6ControlledExecutionRequest, state: V6ControlledRuntimeState) -> V6ControlledExecutionResult:
        station_id = request.target_refs["station_id"]
        station_run_id = request.target_refs["station_run_id"]
        attempts = state.station_attempts.setdefault(station_id, [])
        runtime_result_ref = f"runtime://v6-4/{state.workflow_instance_id}/rerun/{station_id}"
        attempts.append(
            V6ExecutionAttempt(
                attempt_id=f"attempt_{uuid4().hex[:12]}",
                station_id=station_id,
                station_run_id=f"{station_run_id}_retry_{len(attempts) + 1}",
                attempt_number=len(attempts) + 1,
                status="completed",
                producer_runtime_result_ref=runtime_result_ref,
            )
        )
        state.status = "running"
        state.downstream_stale = sorted(set(state.downstream_stale) | {f"downstream-of:{station_id}"})
        return self._applied(context, request, state, runtime_result_ref=runtime_result_ref)

    def _write_artifact(self, context: IdentityContext, request: V6ControlledExecutionRequest, state: V6ControlledRuntimeState) -> V6ControlledExecutionResult:
        artifact_id = request.target_refs.get("artifact_id") or request.target_refs["output_artifact_target_id"]
        runtime_result_ref = f"runtime://v6-4/{state.workflow_instance_id}/artifact/{artifact_id}"
        versions = state.artifact_versions.setdefault(artifact_id, [])
        versions.append(
            {
                "artifact_version_id": f"artifact-version-{len(versions) + 1}",
                "artifact_id": artifact_id,
                "operation": "append_version",
                "content_ref": request.payload_refs.get("content_ref", f"artifact-content-ref://{artifact_id}/{len(versions) + 1}"),
                "producer_station_id": request.target_refs.get("station_id"),
                "producer_attempt_id": request.target_refs.get("attempt_id"),
                "producer_runtime_result_ref": runtime_result_ref,
                "created_at": _now(),
                "redaction_status": "redacted",
            }
        )
        return self._applied(context, request, state, runtime_result_ref=runtime_result_ref)

    def _create_quality_evaluation(self, context: IdentityContext, request: V6ControlledExecutionRequest, state: V6ControlledRuntimeState) -> V6ControlledExecutionResult:
        evaluation_id = request.target_refs.get("quality_evaluation_id") or f"quality-evaluation-{len(state.quality_evaluations) + 1}"
        runtime_result_ref = f"runtime://v6-4/{state.workflow_instance_id}/quality/{evaluation_id}"
        state.quality_evaluations.append(
            {
                "quality_evaluation_id": evaluation_id,
                "quality_rule_ref": request.payload_refs.get("quality_rule_ref", "quality-rule://v6-4/default"),
                "target_ref": request.target_refs.get("artifact_id") or request.target_refs.get("station_id"),
                "score_ref": request.payload_refs.get("score_ref", f"quality-score-ref://{evaluation_id}"),
                "operation": "append_evaluation",
                "producer_runtime_result_ref": runtime_result_ref,
                "created_at": _now(),
                "redaction_status": "redacted",
            }
        )
        return self._applied(context, request, state, runtime_result_ref=runtime_result_ref)

    def _applied(self, context: IdentityContext, request: V6ControlledExecutionRequest, state: V6ControlledRuntimeState, *, runtime_result_ref: str) -> V6ControlledExecutionResult:
        audit_event = self.audit_service.record_production_event(
            context,
            event_type="controlled_executor.action.allowed",
            operation=request.operation,
            target_refs=request.target_refs,
            policy_decision="allow",
            source_refs={"runtime_result_ref": runtime_result_ref, "audit_export_ref": request.audit_export_ref},
            metadata={"stage": "V6-4", "source": request.source},
            user_confirmed=request.user_confirmed,
        )
        audit_event_ref = f"audit-event://{audit_event.event_id}"
        self.audit_events.append(audit_event.to_dict())
        state.runtime_result_refs.append(runtime_result_ref)
        state.incident_timeline_refs.append(request.incident_timeline_ref)
        state.audit_event_refs.append(audit_event_ref)
        state.revision += 1
        state.updated_at = _now()
        evidence = V6ExecutionEvidence(
            execution_evidence_id=f"v6_4_evidence_{uuid4().hex[:12]}",
            operation=request.operation,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            target_refs=dict(request.target_refs),
            actor_type=request.actor_type,
            actor_id=context.actor_id,
            source=request.source,
            user_confirmed=request.user_confirmed,
            human_authorization_ref=request.human_authorization.human_authorization_ref if request.human_authorization else "",
            approval_gate_decision_ref=request.approval_gate_decision_ref,
            policy_decision="allow",
            capability_decision="allow_limited_production_pilot_slice",
            credential_decision_ref=request.credential_decision_ref,
            runtime_result_ref=runtime_result_ref,
            idempotency_key=request.idempotency_key,
            rollback_descriptor_ref=f"rollback://v6-4/{request.operation}/{request.idempotency_key}",
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
        return V6ControlledExecutionResult(
            result_id=f"v6_4_result_{uuid4().hex[:12]}",
            operation=request.operation,
            status="applied_limited_runtime_slice",
            policy_decision="allow",
            capability_decision="allow_limited_production_pilot_slice",
            runtime_result_ref=runtime_result_ref,
            evidence=evidence,
            workflow_state=state.to_dict(),
            audit_event_ref=audit_event_ref,
        )

    def _blocked(self, context: IdentityContext, request: V6ControlledExecutionRequest, reason: str) -> V6ControlledExecutionResult:
        try:
            audit_event = self.audit_service.record_production_event(
                context,
                event_type="controlled_executor.action.denied",
                operation=request.operation,
                target_refs=request.target_refs or {"operation": request.operation},
                policy_decision="deny",
                source_refs={"blocked_reason": reason},
                metadata={"stage": "V6-4", "source": request.source},
                user_confirmed=request.user_confirmed,
            )
            audit_event_ref = f"audit-event://{audit_event.event_id}"
            self.audit_events.append(audit_event.to_dict())
        except Exception:
            audit_event_ref = None
        return V6ControlledExecutionResult(
            result_id=f"v6_4_result_{uuid4().hex[:12]}",
            operation=request.operation,
            status="blocked",
            policy_decision="deny",
            capability_decision="deny",
            runtime_result_ref=None,
            evidence=None,
            workflow_state=None,
            blocked_reason=reason,
            audit_event_ref=audit_event_ref,
        )


def _idempotency_fingerprint(context: IdentityContext, request: V6ControlledExecutionRequest) -> tuple[str, str, str, str, str]:
    target_hash = json.dumps(request.target_refs, sort_keys=True)
    return (context.tenant_id, context.workspace_id, request.operation, request.source, target_hash)


def _assert_no_sensitive_payload(data: Mapping[str, Any]) -> None:
    dumped = json.dumps(data, ensure_ascii=False).lower()
    for term in SENSITIVE_TEXT:
        if term in dumped:
            raise V6ControlledExecutorError("V6_4_REDACTION_FAILED", "Sensitive text is not allowed in V6-4 runtime DTOs.", reason="redaction_failed", resource=term)


def _now() -> str:
    return datetime.now(UTC).isoformat()
