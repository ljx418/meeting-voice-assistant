"""V6-7 distributed runtime productization pilot slice.

This module implements a bounded in-memory production pilot runtime slice for
V6-7. It does not register production routes, start distributed worker
processes, grant Agent durable mutation authority, call connectors, call
external LLMs, or claim full multi-agent orchestration readiness.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext
from core.policies.v6_controlled_executor_runtime import V6ExecutionScope, V6HumanAuthorization


ALLOWED_SOURCES = {"product_console", "approved_api"}
FORBIDDEN_SOURCES = {"agent"}
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


class V67DistributedRuntimeError(ValueError):
    """Stable denial for V6-7 distributed runtime pilot gates."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class V67DistributedRunRequest:
    """Request to start one V6-7 distributed runtime pilot run."""

    workflow_instance_id: str
    source: str
    actor_type: str
    target_scope: V6ExecutionScope
    user_confirmed: bool
    human_authorization: V6HumanAuthorization
    branch_station_ids: dict[str, tuple[str, ...]]
    evidence_source_refs: tuple[str, ...]
    idempotency_key: str
    correlation_id: str
    request_id: str
    completed_station_ids: tuple[str, ...] = ()
    station_dependencies: dict[str, tuple[str, ...]] = field(default_factory=dict)
    policy_decision_ref: str = "policy-decision://v6-7/distributed-run/start"
    credential_decision_ref: str = "credential-decision://v6-7/distributed-run/start"
    audit_ref: str = "audit://v6-7/distributed-run/start"


@dataclass(frozen=True)
class V67WorkerDescriptor:
    """Tenant-bound worker descriptor."""

    worker_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    worker_type: str
    explicit_tenant_binding: bool
    credential_decision_ref: str
    policy_decision_ref: str
    created_at: str = field(default_factory=lambda: _now())
    audit_ref: str = field(default_factory=lambda: f"audit://v6-7/worker/{uuid4().hex[:12]}")
    status: str = "available"

    @classmethod
    def from_context(
        cls,
        context: IdentityContext,
        *,
        worker_id: str,
        worker_type: str = "station_worker",
        credential_decision_ref: str,
        policy_decision_ref: str,
    ) -> "V67WorkerDescriptor":
        """Create a tenant-bound worker from the server-bound context."""
        return cls(
            worker_id=worker_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            worker_type=worker_type,
            explicit_tenant_binding=True,
            credential_decision_ref=credential_decision_ref,
            policy_decision_ref=policy_decision_ref,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted worker DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V67WorkerAssignment:
    """One worker assignment record."""

    assignment_id: str
    worker_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    workflow_instance_id: str
    station_id: str
    station_run_id: str
    attempt_id: str
    source: str
    credential_decision_ref: str
    policy_decision_ref: str
    checkpoint_ref: str
    correlation_id: str
    request_id: str
    audit_ref: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted assignment DTO."""
        return mask_value(asdict(self))


@dataclass
class V67AttemptRecord:
    """Append-only station attempt record."""

    attempt_id: str
    tenant_id: str
    workspace_id: str
    station_id: str
    station_run_id: str
    attempt_number: int
    status: str
    old_attempt_retained: bool
    previous_attempt_id: str | None
    error_ref: str | None
    worker_id: str
    branch_id: str
    producer_artifact_ref: str
    created_at: str = field(default_factory=lambda: _now())
    audit_ref: str = field(default_factory=lambda: f"audit://v6-7/attempt/{uuid4().hex[:12]}")

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted attempt DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V67DistributedStateCheckpoint:
    """One distributed state checkpoint."""

    checkpoint_id: str
    tenant_id: str
    workspace_id: str
    run_id: str
    workflow_instance_id: str
    station_id: str
    station_run_id: str
    attempt_id: str
    branch_id: str
    branch_state: str
    checkpoint_state: str
    created_at: str
    correlation_id: str
    audit_ref: str

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted checkpoint DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V67ArtifactLineageRecord:
    """Artifact lineage with producer attempt ref."""

    artifact_id: str
    tenant_id: str
    workspace_id: str
    workflow_instance_id: str
    station_id: str
    station_run_id: str
    producer_attempt_id: str
    producer_worker_id: str
    input_artifact_refs: tuple[str, ...]
    output_artifact_refs: tuple[str, ...]
    previous_attempt_id: str | None
    lineage_status: str
    created_at: str = field(default_factory=lambda: _now())
    audit_ref: str = field(default_factory=lambda: f"audit://v6-7/lineage/{uuid4().hex[:12]}")

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted lineage DTO."""
        data = asdict(self)
        data["input_artifact_refs"] = list(self.input_artifact_refs)
        data["output_artifact_refs"] = list(self.output_artifact_refs)
        return mask_value(data)


@dataclass(frozen=True)
class V67IncidentTimelineEvent:
    """One incident timeline event."""

    tenant_id: str
    workspace_id: str
    run_id: str
    workflow_instance_id: str
    station_id: str
    station_run_id: str
    attempt_id: str
    worker_id: str
    event_type: str
    correlation_id: str
    request_id: str
    audit_ref: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted timeline event."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V67WorkerRecoveryDecision:
    """One recovery decision record."""

    recovery_decision_id: str
    distributed_run_id: str
    tenant_id: str
    workspace_id: str
    worker_id: str
    replacement_worker_id: str
    station_id: str
    station_run_id: str
    attempt_id: str
    failed_attempt_id: str
    failure_type: str
    decision: str
    recovery_strategy: str
    previous_checkpoint_ref: str
    policy_decision_ref: str
    credential_decision_ref: str
    old_attempt_retained: bool
    created_at: str
    correlation_id: str
    request_id: str
    incident_timeline_ref: str
    audit_ref: str

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted recovery decision DTO."""
        return mask_value(asdict(self))


@dataclass
class V67DistributedRunState:
    """In-memory distributed runtime state."""

    distributed_run_id: str
    workflow_instance_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    status: str
    source: str
    actor_type: str
    user_confirmed: bool
    evidence_source_refs: list[str]
    branch_states: dict[str, str]
    assignments: dict[str, V67WorkerAssignment]
    station_attempts: dict[str, list[V67AttemptRecord]]
    checkpoints: list[V67DistributedStateCheckpoint]
    artifact_lineage: dict[str, V67ArtifactLineageRecord]
    incident_timeline: list[V67IncidentTimelineEvent]
    recovery_decisions: dict[str, V67WorkerRecoveryDecision] = field(default_factory=dict)
    recovery_idempotency: dict[str, str] = field(default_factory=dict)
    downstream_stale: list[str] = field(default_factory=list)
    pilot_slice_ready_for_review: bool = True
    production_ready: bool = False
    distributed_multi_agent_runtime_ready: bool = False
    full_multi_agent_orchestration_ready: bool = False
    agent_executor_ready: bool = False
    production_controlled_executor_ready: bool = False
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted state."""
        data = {
            "distributed_run_id": self.distributed_run_id,
            "workflow_instance_id": self.workflow_instance_id,
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "app_id": self.app_id,
            "status": self.status,
            "source": self.source,
            "actor_type": self.actor_type,
            "user_confirmed": self.user_confirmed,
            "evidence_source_refs": list(self.evidence_source_refs),
            "branch_states": dict(self.branch_states),
            "assignments": {station_id: assignment.to_dict() for station_id, assignment in self.assignments.items()},
            "station_attempts": {station_id: [attempt.to_dict() for attempt in attempts] for station_id, attempts in self.station_attempts.items()},
            "checkpoints": [checkpoint.to_dict() for checkpoint in self.checkpoints],
            "artifact_lineage": {artifact_id: lineage.to_dict() for artifact_id, lineage in self.artifact_lineage.items()},
            "incident_timeline": [event.to_dict() for event in self.incident_timeline],
            "recovery_decisions": {key: decision.to_dict() for key, decision in self.recovery_decisions.items()},
            "downstream_stale": list(self.downstream_stale),
            "pilot_slice_ready_for_review": self.pilot_slice_ready_for_review,
            "production_ready": self.production_ready,
            "distributed_multi_agent_runtime_ready": self.distributed_multi_agent_runtime_ready,
            "full_multi_agent_orchestration_ready": self.full_multi_agent_orchestration_ready,
            "agent_executor_ready": self.agent_executor_ready,
            "production_controlled_executor_ready": self.production_controlled_executor_ready,
            "updated_at": self.updated_at,
        }
        _assert_no_sensitive_payload(data)
        return mask_value(data)


@dataclass(frozen=True)
class V67DistributedRunResult:
    """Result of one V6-7 runtime operation."""

    status: str
    distributed_run_id: str | None
    run_state: dict[str, Any] | None
    evidence: dict[str, Any] | None = None
    blocked_reason: str | None = None


class V67AgentWorkerRegistry:
    """Tenant-scoped V6-7 worker registry."""

    def __init__(self) -> None:
        self.workers: dict[str, V67WorkerDescriptor] = {}

    def register(self, worker: V67WorkerDescriptor) -> None:
        """Register one tenant-bound worker descriptor."""
        if not worker.explicit_tenant_binding:
            raise V67DistributedRuntimeError("missing_explicit_tenant_binding", "Worker requires explicit_tenant_binding=true.")
        if not worker.credential_decision_ref:
            raise V67DistributedRuntimeError("missing_worker_credential_decision", "Worker requires credential_decision_ref.")
        if not worker.policy_decision_ref:
            raise V67DistributedRuntimeError("missing_worker_policy_decision", "Worker requires policy_decision_ref.")
        _assert_no_sensitive_payload(worker.to_dict())
        self.workers[worker.worker_id] = worker

    def worker_for(self, context: IdentityContext, station_id: str, used_worker_ids: set[str]) -> V67WorkerDescriptor | None:
        """Return an available worker matching the current identity scope."""
        del station_id
        for worker in self.workers.values():
            if worker.worker_id in used_worker_ids:
                continue
            if (
                worker.status == "available"
                and worker.explicit_tenant_binding is True
                and worker.tenant_id == context.tenant_id
                and worker.workspace_id == context.workspace_id
                and worker.project_id == context.project_id
                and worker.app_id == context.app_id
                and worker.credential_decision_ref
                and worker.policy_decision_ref
            ):
                return worker
        return None

    def get_scoped(self, context: IdentityContext, worker_id: str) -> V67WorkerDescriptor | None:
        """Return one worker only when full scope and decisions match."""
        worker = self.workers.get(worker_id)
        if worker is None:
            return None
        if (
            worker.tenant_id != context.tenant_id
            or worker.workspace_id != context.workspace_id
            or worker.project_id != context.project_id
            or worker.app_id != context.app_id
            or not worker.explicit_tenant_binding
            or not worker.credential_decision_ref
            or not worker.policy_decision_ref
        ):
            return None
        return worker


class V67DistributedStateStore:
    """In-memory V6-7 runtime state store."""

    def __init__(self) -> None:
        self.states: dict[str, V67DistributedRunState] = {}

    def save(self, state: V67DistributedRunState) -> None:
        """Save one state."""
        self.states[state.distributed_run_id] = state

    def load(self, distributed_run_id: str) -> V67DistributedRunState:
        """Load one state."""
        return self.states[distributed_run_id]


class V67DistributedRunCoordinator:
    """V6-7 distributed run coordinator pilot."""

    def __init__(self, *, registry: V67AgentWorkerRegistry | None = None, store: V67DistributedStateStore | None = None) -> None:
        self.registry = registry or V67AgentWorkerRegistry()
        self.store = store or V67DistributedStateStore()
        self.start_idempotency: dict[str, str] = {}

    def start_run(self, context: IdentityContext, request: V67DistributedRunRequest) -> V67DistributedRunResult:
        """Start a distributed run pilot slice."""
        try:
            self._validate_start(context, request)
            if request.idempotency_key in self.start_idempotency:
                state = self.store.load(self.start_idempotency[request.idempotency_key])
                return V67DistributedRunResult(status="idempotent_replay", distributed_run_id=state.distributed_run_id, run_state=state.to_dict(), evidence=None)
            state = self._build_state(context, request)
        except V67DistributedRuntimeError as exc:
            return V67DistributedRunResult(status="blocked", distributed_run_id=None, run_state=None, evidence=None, blocked_reason=exc.reason)
        self.store.save(state)
        self.start_idempotency[request.idempotency_key] = state.distributed_run_id
        evidence = _runtime_evidence(context, request, state)
        return V67DistributedRunResult(status="started", distributed_run_id=state.distributed_run_id, run_state=state.to_dict(), evidence=evidence)

    def recover_worker(
        self,
        context: IdentityContext,
        distributed_run_id: str,
        *,
        station_id: str,
        failure_type: str,
        replacement_worker_id: str,
        recovery_strategy: str,
        idempotency_key: str,
    ) -> V67DistributedRunResult:
        """Recover one failed worker while preserving old attempts."""
        state = self.store.load(distributed_run_id)
        try:
            if context.scope_key() != (state.tenant_id, state.workspace_id, state.project_id, state.app_id):
                raise V67DistributedRuntimeError("scope_mismatch", "Recovery context scope must match run state.")
            if context.actor_type == "agent":
                raise V67DistributedRuntimeError("source_agent_durable_mutation_denied", "Agent source cannot recover workers.")
            if failure_type not in {"worker_lost", "timeout", "policy_denied", "credential_denied"}:
                raise V67DistributedRuntimeError("unsupported_failure_type", "Unsupported failure type.")
            if recovery_strategy not in {"retry_same_worker", "retry_replacement_worker", "recover_from_checkpoint", "mark_failed"}:
                raise V67DistributedRuntimeError("unsupported_recovery_strategy", "Unsupported recovery strategy.")
            if idempotency_key in state.recovery_idempotency:
                decision = state.recovery_decisions[state.recovery_idempotency[idempotency_key]]
                return V67DistributedRunResult(status="idempotent_recovery_replay", distributed_run_id=distributed_run_id, run_state=state.to_dict(), evidence=decision.to_dict())
            replacement = self.registry.get_scoped(context, replacement_worker_id)
            if replacement is None:
                raise V67DistributedRuntimeError("replacement_worker_not_available_or_scope_denied", "Replacement worker is not scoped.")
            if station_id not in state.station_attempts:
                raise V67DistributedRuntimeError("station_not_found", "Station not found.")
            old_attempt = state.station_attempts[station_id][-1]
            old_attempt.status = "failed"
            old_attempt.error_ref = f"error-ref://v6-7/{failure_type}/{old_attempt.attempt_id}"
            previous_checkpoint = _last_checkpoint_for_station(state, station_id)
            new_attempt = self._append_recovery_attempt(state, replacement, old_attempt, recovery_strategy)
            decision = self._record_recovery_decision(
                state,
                replacement,
                old_attempt,
                new_attempt,
                failure_type=failure_type,
                recovery_strategy=recovery_strategy,
                previous_checkpoint_ref=previous_checkpoint.checkpoint_id,
                idempotency_key=idempotency_key,
                context=context,
            )
        except V67DistributedRuntimeError as exc:
            return V67DistributedRunResult(status="blocked", distributed_run_id=distributed_run_id, run_state=state.to_dict(), evidence=None, blocked_reason=exc.reason)
        self.store.save(state)
        return V67DistributedRunResult(status="worker_recovered", distributed_run_id=distributed_run_id, run_state=state.to_dict(), evidence=decision.to_dict())

    def _validate_start(self, context: IdentityContext, request: V67DistributedRunRequest) -> None:
        _assert_no_sensitive_payload(_request_dict(request))
        if request.source in FORBIDDEN_SOURCES or request.actor_type == "agent" or context.actor_type == "agent":
            raise V67DistributedRuntimeError("source_agent_durable_mutation_denied", "source=agent cannot start distributed runtime.")
        if request.source not in ALLOWED_SOURCES:
            raise V67DistributedRuntimeError("source_not_allowed", "Only product_console and approved_api are allowed.")
        if not request.user_confirmed:
            raise V67DistributedRuntimeError("missing_user_confirmation", "Distributed runtime start requires user confirmation.")
        if request.actor_type != context.actor_type:
            raise V67DistributedRuntimeError("actor_mismatch", "Request actor_type must match context.")
        if request.target_scope != V6ExecutionScope.from_context(context):
            raise V67DistributedRuntimeError("scope_mismatch", "Target scope must match context.")
        if not request.human_authorization.allows(context, "workflow.instance.start", _now()):
            raise V67DistributedRuntimeError("human_authorization_invalid", "Human authorization must allow workflow.instance.start.")
        if not request.branch_station_ids:
            raise V67DistributedRuntimeError("missing_branch_station_ids", "At least one branch is required.")
        if not request.evidence_source_refs:
            raise V67DistributedRuntimeError("missing_evidence_source_refs", "V6-7 requires evidence source refs.")

    def _build_state(self, context: IdentityContext, request: V67DistributedRunRequest) -> V67DistributedRunState:
        distributed_run_id = f"v6_7_run_{uuid4().hex[:12]}"
        branch_states: dict[str, str] = {}
        assignments: dict[str, V67WorkerAssignment] = {}
        attempts: dict[str, list[V67AttemptRecord]] = {}
        checkpoints: list[V67DistributedStateCheckpoint] = []
        lineage: dict[str, V67ArtifactLineageRecord] = {}
        timeline: list[V67IncidentTimelineEvent] = []
        used_workers: set[str] = set()
        completed = set(request.completed_station_ids)
        _append_timeline(timeline, context, distributed_run_id, request.workflow_instance_id, "_run", "_run", "_run", "_run", "distributed_run_created")

        for branch_id, station_ids in request.branch_station_ids.items():
            branch_state = "running"
            for station_id in station_ids:
                dependencies = set(request.station_dependencies.get(station_id, ()))
                if dependencies and not dependencies.issubset(completed):
                    branch_state = "waiting_dependency"
                    checkpoints.append(
                        _checkpoint(
                            context,
                            run_id=distributed_run_id,
                            workflow_instance_id=request.workflow_instance_id,
                            station_id=station_id,
                            station_run_id=f"station-run://v6-7/{station_id}",
                            attempt_id="not-assigned",
                            branch_id=branch_id,
                            branch_state=branch_state,
                            checkpoint_state="assigned",
                        )
                    )
                    continue
                worker = self.registry.worker_for(context, station_id, used_workers)
                if worker is None:
                    raise V67DistributedRuntimeError("worker_not_available_or_scope_denied", f"No scoped worker for {station_id}.")
                used_workers.add(worker.worker_id)
                station_run_id = f"station-run://v6-7/{station_id}"
                attempt = V67AttemptRecord(
                    attempt_id=f"v6_7_attempt_{uuid4().hex[:12]}",
                    tenant_id=context.tenant_id,
                    workspace_id=context.workspace_id,
                    station_id=station_id,
                    station_run_id=station_run_id,
                    attempt_number=1,
                    status="running",
                    old_attempt_retained=True,
                    previous_attempt_id=None,
                    error_ref=None,
                    worker_id=worker.worker_id,
                    branch_id=branch_id,
                    producer_artifact_ref=f"artifact://v6-7/{station_id}/attempt-1",
                )
                checkpoint = _checkpoint(
                    context,
                    run_id=distributed_run_id,
                    workflow_instance_id=request.workflow_instance_id,
                    station_id=station_id,
                    station_run_id=station_run_id,
                    attempt_id=attempt.attempt_id,
                    branch_id=branch_id,
                    branch_state="running",
                    checkpoint_state="running",
                )
                assignment = V67WorkerAssignment(
                    assignment_id=f"assignment://v6-7/{uuid4().hex[:12]}",
                    worker_id=worker.worker_id,
                    tenant_id=context.tenant_id,
                    workspace_id=context.workspace_id,
                    project_id=context.project_id,
                    app_id=context.app_id,
                    workflow_instance_id=request.workflow_instance_id,
                    station_id=station_id,
                    station_run_id=station_run_id,
                    attempt_id=attempt.attempt_id,
                    source=request.source,
                    credential_decision_ref=worker.credential_decision_ref,
                    policy_decision_ref=worker.policy_decision_ref,
                    checkpoint_ref=checkpoint.checkpoint_id,
                    correlation_id=request.correlation_id,
                    request_id=request.request_id,
                    audit_ref=f"audit://v6-7/assignment/{uuid4().hex[:12]}",
                )
                attempts[station_id] = [attempt]
                assignments[station_id] = assignment
                checkpoints.append(checkpoint)
                lineage[attempt.producer_artifact_ref] = _lineage(context, request.workflow_instance_id, attempt, worker, previous_attempt_id=None, status="active")
                for event_type in ("worker_assignment_created", "worker_started", "checkpoint_written", "attempt_created", "artifact_lineage_recorded"):
                    _append_timeline(timeline, context, distributed_run_id, request.workflow_instance_id, station_id, station_run_id, attempt.attempt_id, worker.worker_id, event_type)
            branch_states[branch_id] = branch_state
        return V67DistributedRunState(
            distributed_run_id=distributed_run_id,
            workflow_instance_id=request.workflow_instance_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            status="running",
            source=request.source,
            actor_type=context.actor_type,
            user_confirmed=request.user_confirmed,
            evidence_source_refs=list(request.evidence_source_refs),
            branch_states=branch_states,
            assignments=assignments,
            station_attempts=attempts,
            checkpoints=checkpoints,
            artifact_lineage=lineage,
            incident_timeline=timeline,
        )

    def _append_recovery_attempt(
        self,
        state: V67DistributedRunState,
        replacement: V67WorkerDescriptor,
        old_attempt: V67AttemptRecord,
        recovery_strategy: str,
    ) -> V67AttemptRecord:
        attempt_number = len(state.station_attempts[old_attempt.station_id]) + 1
        station_run_id = old_attempt.station_run_id
        new_attempt = V67AttemptRecord(
            attempt_id=f"v6_7_attempt_{uuid4().hex[:12]}",
            tenant_id=state.tenant_id,
            workspace_id=state.workspace_id,
            station_id=old_attempt.station_id,
            station_run_id=station_run_id,
            attempt_number=attempt_number,
            status="recovered" if recovery_strategy != "mark_failed" else "failed",
            old_attempt_retained=True,
            previous_attempt_id=old_attempt.attempt_id,
            error_ref=None,
            worker_id=replacement.worker_id,
            branch_id=old_attempt.branch_id,
            producer_artifact_ref=f"artifact://v6-7/{old_attempt.station_id}/attempt-{attempt_number}",
        )
        checkpoint = _checkpoint(
            _context_from_state(state),
            run_id=state.distributed_run_id,
            workflow_instance_id=state.workflow_instance_id,
            station_id=old_attempt.station_id,
            station_run_id=station_run_id,
            attempt_id=new_attempt.attempt_id,
            branch_id=old_attempt.branch_id,
            branch_state="recovered" if recovery_strategy != "mark_failed" else "failed",
            checkpoint_state="recovered" if recovery_strategy != "mark_failed" else "failed",
        )
        state.station_attempts[old_attempt.station_id].append(new_attempt)
        state.assignments[old_attempt.station_id] = V67WorkerAssignment(
            assignment_id=f"assignment://v6-7/{uuid4().hex[:12]}",
            worker_id=replacement.worker_id,
            tenant_id=state.tenant_id,
            workspace_id=state.workspace_id,
            project_id=state.project_id,
            app_id=state.app_id,
            workflow_instance_id=state.workflow_instance_id,
            station_id=old_attempt.station_id,
            station_run_id=station_run_id,
            attempt_id=new_attempt.attempt_id,
            source="product_console",
            credential_decision_ref=replacement.credential_decision_ref,
            policy_decision_ref=replacement.policy_decision_ref,
            checkpoint_ref=checkpoint.checkpoint_id,
            correlation_id=checkpoint.correlation_id,
            request_id=_context_from_state(state).request_id,
            audit_ref=f"audit://v6-7/assignment/{uuid4().hex[:12]}",
        )
        state.checkpoints.append(checkpoint)
        state.artifact_lineage[new_attempt.producer_artifact_ref] = _lineage(_context_from_state(state), state.workflow_instance_id, new_attempt, replacement, old_attempt.attempt_id, "recovered")
        state.branch_states[old_attempt.branch_id] = checkpoint.branch_state
        state.downstream_stale = sorted(set(state.downstream_stale) | {f"downstream-of:{old_attempt.station_id}"})
        state.updated_at = _now()
        return new_attempt

    def _record_recovery_decision(
        self,
        state: V67DistributedRunState,
        replacement: V67WorkerDescriptor,
        old_attempt: V67AttemptRecord,
        new_attempt: V67AttemptRecord,
        *,
        failure_type: str,
        recovery_strategy: str,
        previous_checkpoint_ref: str,
        idempotency_key: str,
        context: IdentityContext,
    ) -> V67WorkerRecoveryDecision:
        for event_type in ("worker_lost" if failure_type == "worker_lost" else "worker_timeout", "attempt_failed", "retry_scheduled", "attempt_recovered", "checkpoint_written", "artifact_lineage_recorded"):
            _append_timeline(
                state.incident_timeline,
                context,
                state.distributed_run_id,
                state.workflow_instance_id,
                old_attempt.station_id,
                old_attempt.station_run_id,
                new_attempt.attempt_id,
                replacement.worker_id,
                event_type,
            )
        decision = V67WorkerRecoveryDecision(
            recovery_decision_id=f"recovery://v6-7/{uuid4().hex[:12]}",
            distributed_run_id=state.distributed_run_id,
            tenant_id=state.tenant_id,
            workspace_id=state.workspace_id,
            worker_id=old_attempt.worker_id,
            replacement_worker_id=replacement.worker_id,
            station_id=old_attempt.station_id,
            station_run_id=old_attempt.station_run_id,
            attempt_id=new_attempt.attempt_id,
            failed_attempt_id=old_attempt.attempt_id,
            failure_type=failure_type,
            decision="mark_failed" if recovery_strategy == "mark_failed" else "recover",
            recovery_strategy=recovery_strategy,
            previous_checkpoint_ref=previous_checkpoint_ref,
            policy_decision_ref=replacement.policy_decision_ref,
            credential_decision_ref=replacement.credential_decision_ref,
            old_attempt_retained=True,
            created_at=_now(),
            correlation_id=context.correlation_id,
            request_id=context.request_id,
            incident_timeline_ref=f"incident-timeline://v6-7/{state.distributed_run_id}",
            audit_ref=f"audit://v6-7/recovery/{uuid4().hex[:12]}",
        )
        state.recovery_decisions[decision.recovery_decision_id] = decision
        state.recovery_idempotency[idempotency_key] = decision.recovery_decision_id
        _assert_no_sensitive_payload(decision.to_dict())
        return decision


def seed_v67_workers(context: IdentityContext, registry: V67AgentWorkerRegistry, count: int) -> None:
    """Seed tenant-bound workers for tests and evidence scripts."""
    for index in range(count):
        registry.register(
            V67WorkerDescriptor.from_context(
                context,
                worker_id=f"worker_v6_7_{index + 1}",
                credential_decision_ref=f"credential-decision://v6-7/worker/{index + 1}",
                policy_decision_ref=f"policy-decision://v6-7/worker/{index + 1}",
            )
        )


def build_v67_runtime_report(state: V67DistributedRunState) -> dict[str, Any]:
    """Build a read-only runtime report projection."""
    report = {
        "report_id": f"runtime-report://v6-7/{state.distributed_run_id}",
        "distributed_run_id": state.distributed_run_id,
        "workflow_instance_id": state.workflow_instance_id,
        "status": state.status,
        "branch_states": dict(state.branch_states),
        "assignments": {station_id: assignment.to_dict() for station_id, assignment in state.assignments.items()},
        "attempt_history": {station_id: [attempt.to_dict() for attempt in attempts] for station_id, attempts in state.station_attempts.items()},
        "artifact_lineage": {artifact_id: lineage.to_dict() for artifact_id, lineage in state.artifact_lineage.items()},
        "checkpoints": [checkpoint.to_dict() for checkpoint in state.checkpoints],
        "incident_timeline": [event.to_dict() for event in state.incident_timeline],
        "recovery_decisions": {key: decision.to_dict() for key, decision in state.recovery_decisions.items()},
        "downstream_stale": list(state.downstream_stale),
        "readonly": True,
        "report_actions": ["view", "export"],
        "redaction_status": "redacted",
        "pilot_slice_ready_for_review": True,
        "production_ready": False,
        "distributed_multi_agent_runtime_ready": False,
        "full_multi_agent_orchestration_ready": False,
        "agent_executor_ready": False,
        "production_controlled_executor_ready": False,
    }
    _assert_no_sensitive_payload(report)
    return mask_value(report)


def build_v67_observability_package(state: V67DistributedRunState) -> dict[str, Any]:
    """Build read-only observability package for V6-7."""
    report = build_v67_runtime_report(state)
    package = {
        "audit_export_package_id": f"audit-export://v6-7/{state.distributed_run_id}",
        "distributed_run_id": state.distributed_run_id,
        "tenant_id": state.tenant_id,
        "workspace_id": state.workspace_id,
        "metrics": {
            "assigned_worker_count": len(state.assignments),
            "attempt_count": sum(len(attempts) for attempts in state.station_attempts.values()),
            "checkpoint_count": len(state.checkpoints),
            "artifact_lineage_count": len(state.artifact_lineage),
            "incident_timeline_event_count": len(state.incident_timeline),
        },
        "runtime_report": report,
        "readonly": True,
        "report_actions": ["view", "export"],
        "redaction_status": "redacted",
        "pilot_slice_ready_for_review": True,
        "production_ready": False,
    }
    _assert_no_sensitive_payload(package)
    return mask_value(package)


def _request_dict(request: V67DistributedRunRequest) -> dict[str, Any]:
    data = asdict(request)
    data["branch_station_ids"] = {branch_id: list(stations) for branch_id, stations in request.branch_station_ids.items()}
    data["completed_station_ids"] = list(request.completed_station_ids)
    data["station_dependencies"] = {station_id: list(deps) for station_id, deps in request.station_dependencies.items()}
    return data


def _runtime_evidence(context: IdentityContext, request: V67DistributedRunRequest, state: V67DistributedRunState) -> dict[str, Any]:
    evidence = {
        "evidence_id": f"evidence://v6-7/{uuid4().hex[:12]}",
        "operation": "distributed.run.start",
        "distributed_run_id": state.distributed_run_id,
        "workflow_instance_id": state.workflow_instance_id,
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "project_id": context.project_id,
        "app_id": context.app_id,
        "source": request.source,
        "actor_type": context.actor_type,
        "user_confirmed": request.user_confirmed,
        "human_authorization_ref": request.human_authorization.human_authorization_ref,
        "policy_decision_ref": request.policy_decision_ref,
        "credential_decision_ref": request.credential_decision_ref,
        "audit_ref": request.audit_ref,
        "correlation_id": request.correlation_id,
        "request_id": request.request_id,
        "redaction_status": "redacted",
        "created_at": _now(),
    }
    _assert_no_sensitive_payload(evidence)
    return mask_value(evidence)


def _checkpoint(
    context: IdentityContext,
    *,
    run_id: str,
    workflow_instance_id: str,
    station_id: str,
    station_run_id: str,
    attempt_id: str,
    branch_id: str,
    branch_state: str,
    checkpoint_state: str,
) -> V67DistributedStateCheckpoint:
    return V67DistributedStateCheckpoint(
        checkpoint_id=f"checkpoint://v6-7/{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        run_id=run_id,
        workflow_instance_id=workflow_instance_id,
        station_id=station_id,
        station_run_id=station_run_id,
        attempt_id=attempt_id,
        branch_id=branch_id,
        branch_state=branch_state,
        checkpoint_state=checkpoint_state,
        created_at=_now(),
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v6-7/checkpoint/{uuid4().hex[:12]}",
    )


def _lineage(
    context: IdentityContext,
    workflow_instance_id: str,
    attempt: V67AttemptRecord,
    worker: V67WorkerDescriptor,
    previous_attempt_id: str | None,
    status: str,
) -> V67ArtifactLineageRecord:
    return V67ArtifactLineageRecord(
        artifact_id=attempt.producer_artifact_ref,
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        workflow_instance_id=workflow_instance_id,
        station_id=attempt.station_id,
        station_run_id=attempt.station_run_id,
        producer_attempt_id=attempt.attempt_id,
        producer_worker_id=worker.worker_id,
        input_artifact_refs=(),
        output_artifact_refs=(attempt.producer_artifact_ref,),
        previous_attempt_id=previous_attempt_id,
        lineage_status=status,
    )


def _append_timeline(
    events: list[V67IncidentTimelineEvent],
    context: IdentityContext,
    run_id: str,
    workflow_instance_id: str,
    station_id: str,
    station_run_id: str,
    attempt_id: str,
    worker_id: str,
    event_type: str,
) -> None:
    events.append(
        V67IncidentTimelineEvent(
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            run_id=run_id,
            workflow_instance_id=workflow_instance_id,
            station_id=station_id,
            station_run_id=station_run_id,
            attempt_id=attempt_id,
            worker_id=worker_id,
            event_type=event_type,
            correlation_id=context.correlation_id,
            request_id=context.request_id,
            audit_ref=f"audit://v6-7/incident/{uuid4().hex[:12]}",
        )
    )


def _last_checkpoint_for_station(state: V67DistributedRunState, station_id: str) -> V67DistributedStateCheckpoint:
    for checkpoint in reversed(state.checkpoints):
        if checkpoint.station_id == station_id:
            return checkpoint
    raise V67DistributedRuntimeError("checkpoint_not_found", "Station checkpoint not found.")


def _context_from_state(state: V67DistributedRunState) -> IdentityContext:
    return IdentityContext(
        tenant_id=state.tenant_id,
        workspace_id=state.workspace_id,
        project_id=state.project_id,
        app_id=state.app_id,
        actor_type="human_user",
        actor_id="user_v6_7",
        user_id="user_v6_7",
        service_account_id=None,
        agent_id=None,
        session_id=None,
        request_id=f"request_{state.distributed_run_id}",
        correlation_id=f"correlation_{state.distributed_run_id}",
    )


def _assert_no_sensitive_payload(data: Mapping[str, Any]) -> None:
    dumped = json.dumps(data, ensure_ascii=False).lower()
    for term in SENSITIVE_TEXT:
        if term in dumped:
            raise V67DistributedRuntimeError("redaction_failed", f"Sensitive text is not allowed: {term}")


def _now() -> str:
    return datetime.now(UTC).isoformat()
