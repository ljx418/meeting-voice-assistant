"""V5.8B minimal distributed run coordination slice.

This module is intentionally in-memory and staging-scoped. It models the
coordination semantics needed before a production distributed multi-agent
runtime can be built. It does not register routes, start worker processes,
call connectors, call external LLMs, or grant Agent-originated durable
mutation authority.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext
from core.policies.production_controlled_executor_runtime import ExecutionScope, HumanAuthorization


REPO_ROOT = Path(__file__).resolve().parents[2]
V4_MULTI_AGENT_EVIDENCE_ROOT = REPO_ROOT / "docs" / "design" / "V4.x" / "evidence" / "real-multi-agent"
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


class DistributedRuntimeCoordinationError(ValueError):
    """Stable denial for V5.8B coordination gates."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class DistributedWorkerDescriptor:
    """Tenant-bound worker descriptor for assignment only."""

    worker_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    station_id: str
    credential_decision_ref: str
    status: str = "available"

    @classmethod
    def from_context(cls, context: IdentityContext, *, worker_id: str, station_id: str, credential_decision_ref: str) -> "DistributedWorkerDescriptor":
        """Create a worker descriptor bound to one server-side identity scope."""
        return cls(
            worker_id=worker_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            station_id=station_id,
            credential_decision_ref=credential_decision_ref,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted worker DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class DistributedRunRequest:
    """Request to coordinate one distributed run."""

    workflow_instance_id: str
    source: str
    actor_type: str
    target_scope: ExecutionScope
    user_confirmed: bool
    human_authorization: HumanAuthorization
    station_ids: tuple[str, ...]
    evidence_source_refs: tuple[str, ...]
    idempotency_key: str
    correlation_id: str
    request_id: str
    incident_timeline_ref: str = "incident-timeline://v5-8b/default"
    audit_export_ref: str = "audit-export://v5-8b/default"


@dataclass(frozen=True)
class DistributedStationAttempt:
    """One distributed station attempt."""

    attempt_id: str
    station_id: str
    worker_id: str
    attempt_number: int
    status: str
    producer_artifact_ref: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted attempt DTO."""
        return mask_value(asdict(self))


@dataclass
class DistributedRunState:
    """In-memory distributed run state."""

    distributed_run_id: str
    workflow_instance_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    status: str
    source: str
    user_confirmed: bool
    evidence_source_refs: list[str]
    station_attempts: dict[str, list[DistributedStationAttempt]]
    assignments: dict[str, str]
    artifact_lineage: dict[str, dict[str, str]]
    downstream_stale: list[str] = field(default_factory=list)
    incident_timeline: list[dict[str, str]] = field(default_factory=list)
    recovered_after_restart: bool = False
    staging_only: bool = True
    production_ready: bool = False
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted run state."""
        return mask_value(
            {
                "distributed_run_id": self.distributed_run_id,
                "workflow_instance_id": self.workflow_instance_id,
                "tenant_id": self.tenant_id,
                "workspace_id": self.workspace_id,
                "project_id": self.project_id,
                "app_id": self.app_id,
                "status": self.status,
                "source": self.source,
                "user_confirmed": self.user_confirmed,
                "evidence_source_refs": self.evidence_source_refs,
                "station_attempts": {station_id: [attempt.to_dict() for attempt in attempts] for station_id, attempts in self.station_attempts.items()},
                "assignments": self.assignments,
                "artifact_lineage": self.artifact_lineage,
                "downstream_stale": self.downstream_stale,
                "incident_timeline": self.incident_timeline,
                "recovered_after_restart": self.recovered_after_restart,
                "staging_only": self.staging_only,
                "production_ready": self.production_ready,
                "updated_at": self.updated_at,
            }
        )


@dataclass(frozen=True)
class DistributedCoordinationEvidence:
    """Read-only evidence for a coordination event."""

    evidence_id: str
    operation: str
    distributed_run_id: str
    workflow_instance_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    source: str
    actor_type: str
    user_confirmed: bool
    human_authorization_ref: str
    policy_decision: str
    credential_boundary_decision: str
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
class DistributedCoordinationResult:
    """Result of one coordination operation."""

    status: str
    distributed_run_id: str | None
    run_state: dict[str, Any] | None
    evidence: dict[str, Any] | None
    blocked_reason: str | None = None


@dataclass(frozen=True)
class AttemptHistoryRecord:
    """Append-only attempt history record."""

    attempt_id: str
    station_id: str
    worker_id: str
    attempt_number: int
    status: str
    producer_artifact_ref: str
    previous_attempt_id: str | None
    recovery_reason: str | None
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return redacted attempt history record."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class ArtifactLineageRecord:
    """Artifact lineage record with producer attempt reference."""

    artifact_ref: str
    station_id: str
    producer_attempt_id: str
    producer_worker_id: str
    previous_attempt_id: str | None = None
    lineage_status: str = "active"

    def to_dict(self) -> dict[str, Any]:
        """Return redacted lineage record."""
        return mask_value(asdict(self))


class AttemptHistoryStore:
    """Append-only attempt history projection."""

    def __init__(self) -> None:
        self.records: dict[str, list[AttemptHistoryRecord]] = {}

    def ingest_state(self, state: DistributedRunState) -> None:
        """Ingest attempts from one run state without overwriting prior records."""
        for station_id, attempts in state.station_attempts.items():
            existing = self.records.setdefault(station_id, [])
            known_attempt_ids = {record.attempt_id for record in existing}
            previous_attempt_id: str | None = existing[-1].attempt_id if existing else None
            for attempt in attempts:
                if attempt.attempt_id in known_attempt_ids:
                    continue
                existing.append(
                    AttemptHistoryRecord(
                        attempt_id=attempt.attempt_id,
                        station_id=attempt.station_id,
                        worker_id=attempt.worker_id,
                        attempt_number=attempt.attempt_number,
                        status=attempt.status,
                        producer_artifact_ref=attempt.producer_artifact_ref,
                        previous_attempt_id=previous_attempt_id if attempt.attempt_number > 1 else None,
                        recovery_reason="worker_recovery" if attempt.attempt_number > 1 else None,
                        created_at=attempt.created_at,
                    )
                )
                previous_attempt_id = attempt.attempt_id

    def to_dict(self) -> dict[str, Any]:
        """Return redacted append-only attempt history."""
        return mask_value({station_id: [record.to_dict() for record in records] for station_id, records in self.records.items()})


class ArtifactLineageService:
    """Build read-only artifact lineage from distributed attempts."""

    def __init__(self) -> None:
        self.records: dict[str, ArtifactLineageRecord] = {}

    def ingest_state(self, state: DistributedRunState) -> None:
        """Ingest lineage from one run state."""
        for attempts in state.station_attempts.values():
            previous_attempt_id: str | None = None
            for attempt in attempts:
                existing = state.artifact_lineage.get(attempt.producer_artifact_ref, {})
                self.records[attempt.producer_artifact_ref] = ArtifactLineageRecord(
                    artifact_ref=attempt.producer_artifact_ref,
                    station_id=attempt.station_id,
                    producer_attempt_id=attempt.attempt_id,
                    producer_worker_id=attempt.worker_id,
                    previous_attempt_id=existing.get("previous_attempt_id") or previous_attempt_id,
                    lineage_status="recovered" if attempt.attempt_number > 1 else "active",
                )
                previous_attempt_id = attempt.attempt_id

    def to_dict(self) -> dict[str, Any]:
        """Return redacted artifact lineage records."""
        return mask_value({artifact_ref: record.to_dict() for artifact_ref, record in self.records.items()})


def build_runtime_report_projection(state: DistributedRunState, attempts: AttemptHistoryStore, lineage: ArtifactLineageService) -> dict[str, Any]:
    """Build a read-only runtime report projection for V5.8C."""
    report = {
        "report_id": f"runtime-report://v5-8c/{state.distributed_run_id}",
        "distributed_run_id": state.distributed_run_id,
        "workflow_instance_id": state.workflow_instance_id,
        "status": state.status,
        "source_refs": list(state.evidence_source_refs),
        "attempt_history": attempts.to_dict(),
        "artifact_lineage": lineage.to_dict(),
        "downstream_stale": list(state.downstream_stale),
        "incident_timeline": list(state.incident_timeline),
        "readonly": True,
        "report_actions": ["view", "export"],
        "redaction_status": "redacted",
        "staging_only": True,
        "production_ready": False,
    }
    _assert_no_sensitive_payload(report)
    return mask_value(report)


@dataclass(frozen=True)
class DistributedPolicyCredentialDecision:
    """Policy and credential decision for a distributed run projection."""

    decision_id: str
    distributed_run_id: str
    tenant_id: str
    workspace_id: str
    policy_decision: str
    credential_boundary_decision: str
    worker_credential_refs: dict[str, str]
    source_agent_can_mutate: bool
    unrestricted_connector_call_allowed: bool
    unrestricted_external_llm_call_allowed: bool
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        """Return redacted policy/credential decision."""
        return mask_value(asdict(self))


def build_policy_credential_decision(state: DistributedRunState, registry: AgentWorkerRegistry) -> DistributedPolicyCredentialDecision:
    """Build a read-only policy and credential boundary decision."""
    worker_credential_refs: dict[str, str] = {}
    for station_id, worker_id in state.assignments.items():
        worker = registry.workers.get(worker_id)
        if worker is None or not worker.credential_decision_ref:
            raise DistributedRuntimeCoordinationError("missing_worker_credential_decision", f"Missing credential decision for {station_id}.")
        if worker.tenant_id != state.tenant_id or worker.workspace_id != state.workspace_id:
            raise DistributedRuntimeCoordinationError("worker_scope_mismatch", f"Worker scope mismatch for {station_id}.")
        worker_credential_refs[worker_id] = worker.credential_decision_ref
    decision = DistributedPolicyCredentialDecision(
        decision_id=f"policy-credential://v5-8d/{state.distributed_run_id}",
        distributed_run_id=state.distributed_run_id,
        tenant_id=state.tenant_id,
        workspace_id=state.workspace_id,
        policy_decision="allow_distributed_projection_only",
        credential_boundary_decision="all_assigned_workers_have_credential_decision_refs",
        worker_credential_refs=worker_credential_refs,
        source_agent_can_mutate=False,
        unrestricted_connector_call_allowed=False,
        unrestricted_external_llm_call_allowed=False,
    )
    _assert_no_sensitive_payload(decision.to_dict())
    return decision


def build_distributed_observability_package(
    state: DistributedRunState,
    report: dict[str, Any],
    decision: DistributedPolicyCredentialDecision,
) -> dict[str, Any]:
    """Build read-only observability and audit export projection."""
    audit_events = [
        {
            "event_id": f"audit-event://v5-8d/{state.distributed_run_id}/start",
            "event_type": "distributed.run.coordinated",
            "distributed_run_id": state.distributed_run_id,
            "workflow_instance_id": state.workflow_instance_id,
            "tenant_id": state.tenant_id,
            "workspace_id": state.workspace_id,
            "policy_decision_ref": decision.decision_id,
            "source": state.source,
            "user_confirmed": state.user_confirmed,
            "redaction_status": "redacted",
        },
        {
            "event_id": f"audit-event://v5-8d/{state.distributed_run_id}/lineage",
            "event_type": "artifact.lineage.projected",
            "distributed_run_id": state.distributed_run_id,
            "artifact_lineage_count": str(len(report.get("artifact_lineage", {}))),
            "attempt_station_count": str(len(report.get("attempt_history", {}))),
            "redaction_status": "redacted",
        },
    ]
    package = {
        "audit_export_package_id": f"audit-export://v5-8d/{state.distributed_run_id}",
        "distributed_run_id": state.distributed_run_id,
        "tenant_id": state.tenant_id,
        "workspace_id": state.workspace_id,
        "policy_credential_decision": decision.to_dict(),
        "audit_events": audit_events,
        "incident_timeline": list(state.incident_timeline),
        "metrics": {
            "assigned_worker_count": len(state.assignments),
            "artifact_lineage_count": len(report.get("artifact_lineage", {})),
            "downstream_stale_count": len(state.downstream_stale),
        },
        "readonly": True,
        "report_actions": ["view", "export"],
        "redaction_status": "redacted",
        "staging_only": True,
        "production_ready": False,
    }
    _assert_no_sensitive_payload(package)
    return mask_value(package)


class InMemoryDistributedStateStore:
    """Small in-memory store for V5.8B coordination tests."""

    def __init__(self) -> None:
        self.states: dict[str, DistributedRunState] = {}

    def save(self, state: DistributedRunState) -> None:
        """Persist one run state in memory."""
        self.states[state.distributed_run_id] = state

    def load(self, distributed_run_id: str) -> DistributedRunState:
        """Load one run state."""
        return self.states[distributed_run_id]


class AgentWorkerRegistry:
    """Tenant-scoped worker registry for assignment decisions."""

    def __init__(self) -> None:
        self.workers: dict[str, DistributedWorkerDescriptor] = {}

    def register(self, worker: DistributedWorkerDescriptor) -> None:
        """Register one worker descriptor."""
        _assert_no_sensitive_payload(worker.to_dict())
        self.workers[worker.worker_id] = worker

    def worker_for(self, context: IdentityContext, station_id: str) -> DistributedWorkerDescriptor | None:
        """Return one available worker matching station and tenant scope."""
        for worker in self.workers.values():
            if (
                worker.station_id == station_id
                and worker.status == "available"
                and worker.tenant_id == context.tenant_id
                and worker.workspace_id == context.workspace_id
                and worker.project_id == context.project_id
                and worker.app_id == context.app_id
                and worker.credential_decision_ref
            ):
                return worker
        return None


class DistributedRunCoordinator:
    """Minimal distributed run coordinator for V5.8B."""

    def __init__(self, *, registry: AgentWorkerRegistry | None = None, store: InMemoryDistributedStateStore | None = None) -> None:
        self.registry = registry or AgentWorkerRegistry()
        self.store = store or InMemoryDistributedStateStore()
        self.evidence: list[DistributedCoordinationEvidence] = []

    def start_run(self, context: IdentityContext, request: DistributedRunRequest) -> DistributedCoordinationResult:
        """Coordinate worker assignment and initial run state."""
        try:
            self._validate_request(context, request)
            state = self._build_running_state(context, request)
        except DistributedRuntimeCoordinationError as exc:
            return DistributedCoordinationResult(status="blocked", distributed_run_id=None, run_state=None, evidence=None, blocked_reason=exc.reason)
        self.store.save(state)
        evidence = self._record_evidence(context, request, state, "distributed.run.start")
        return DistributedCoordinationResult(status="coordinated", distributed_run_id=state.distributed_run_id, run_state=state.to_dict(), evidence=evidence.to_dict())

    def recover_after_restart(self, distributed_run_id: str) -> DistributedCoordinationResult:
        """Recover one persisted run after coordinator restart."""
        state = self.store.load(distributed_run_id)
        state.recovered_after_restart = True
        state.status = "running_recovered"
        state.updated_at = _now()
        state.incident_timeline.append({"event_type": "coordinator.restart.recovered", "created_at": _now()})
        self.store.save(state)
        return DistributedCoordinationResult(status="recovered", distributed_run_id=distributed_run_id, run_state=state.to_dict(), evidence=None)

    def recover_lost_worker(self, distributed_run_id: str, *, station_id: str, replacement_worker_id: str) -> DistributedCoordinationResult:
        """Append a new attempt for one lost worker while retaining old attempts."""
        state = self.store.load(distributed_run_id)
        attempts = state.station_attempts[station_id]
        old_attempt = attempts[-1]
        replacement = self.registry.workers.get(replacement_worker_id)
        if replacement is None or replacement.station_id != station_id:
            return DistributedCoordinationResult(status="blocked", distributed_run_id=distributed_run_id, run_state=state.to_dict(), evidence=None, blocked_reason="replacement_worker_not_available")
        old_attempt_dict = old_attempt.to_dict()
        attempts.append(
            DistributedStationAttempt(
                attempt_id=f"v5_8b_attempt_{uuid4().hex[:12]}",
                station_id=station_id,
                worker_id=replacement.worker_id,
                attempt_number=len(attempts) + 1,
                status="completed_after_worker_recovery",
                producer_artifact_ref=f"artifact://v5-8b/{station_id}/attempt-{len(attempts) + 1}",
            )
        )
        state.assignments[station_id] = replacement.worker_id
        state.downstream_stale = sorted(set(state.downstream_stale) | {f"downstream-of:{station_id}"})
        state.artifact_lineage[attempts[-1].producer_artifact_ref] = {
            "station_id": station_id,
            "producer_attempt_id": attempts[-1].attempt_id,
            "previous_attempt_id": old_attempt_dict["attempt_id"],
        }
        state.incident_timeline.append({"event_type": "worker.lost.recovered", "station_id": station_id, "created_at": _now()})
        state.updated_at = _now()
        self.store.save(state)
        return DistributedCoordinationResult(status="worker_recovered", distributed_run_id=distributed_run_id, run_state=state.to_dict(), evidence=None)

    def _validate_request(self, context: IdentityContext, request: DistributedRunRequest) -> None:
        _assert_no_sensitive_payload(asdict(request))
        if request.source == "agent" or request.actor_type == "agent" or context.actor_type == "agent":
            raise DistributedRuntimeCoordinationError("source_agent_durable_mutation_denied", "source=agent cannot start distributed durable coordination.")
        if request.source not in ALLOWED_SOURCES:
            raise DistributedRuntimeCoordinationError("source_not_allowed", "Only product_console and approved_api are allowed.")
        if not request.user_confirmed:
            raise DistributedRuntimeCoordinationError("missing_user_confirmation", "Distributed coordination requires user_confirmed=true.")
        if request.actor_type != context.actor_type:
            raise DistributedRuntimeCoordinationError("actor_mismatch", "Request actor_type must match server identity context.")
        if request.target_scope != ExecutionScope.from_context(context):
            raise DistributedRuntimeCoordinationError("scope_mismatch", "Target scope must match server identity context.")
        now = _now()
        if not request.human_authorization.allows(context, "workflow.instance.start", now):
            raise DistributedRuntimeCoordinationError("human_authorization_invalid", "Human authorization must allow workflow.instance.start.")
        if not request.station_ids:
            raise DistributedRuntimeCoordinationError("missing_station_ids", "At least one station is required.")
        if not request.evidence_source_refs:
            raise DistributedRuntimeCoordinationError("missing_real_data_evidence", "V5.8B requires existing real-data evidence refs.")
        for station_id in request.station_ids:
            if self.registry.worker_for(context, station_id) is None:
                raise DistributedRuntimeCoordinationError("worker_not_available_or_scope_denied", f"No scoped worker for {station_id}.")

    def _build_running_state(self, context: IdentityContext, request: DistributedRunRequest) -> DistributedRunState:
        distributed_run_id = f"v5_8b_run_{uuid4().hex[:12]}"
        station_attempts: dict[str, list[DistributedStationAttempt]] = {}
        assignments: dict[str, str] = {}
        artifact_lineage: dict[str, dict[str, str]] = {}
        for station_id in request.station_ids:
            worker = self.registry.worker_for(context, station_id)
            if worker is None:
                raise DistributedRuntimeCoordinationError("worker_not_available_or_scope_denied", f"No scoped worker for {station_id}.")
            artifact_ref = f"artifact://v5-8b/{station_id}/attempt-1"
            attempt = DistributedStationAttempt(
                attempt_id=f"v5_8b_attempt_{uuid4().hex[:12]}",
                station_id=station_id,
                worker_id=worker.worker_id,
                attempt_number=1,
                status="assigned",
                producer_artifact_ref=artifact_ref,
            )
            station_attempts[station_id] = [attempt]
            assignments[station_id] = worker.worker_id
            artifact_lineage[artifact_ref] = {"station_id": station_id, "producer_attempt_id": attempt.attempt_id}
        return DistributedRunState(
            distributed_run_id=distributed_run_id,
            workflow_instance_id=request.workflow_instance_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            status="running",
            source=request.source,
            user_confirmed=request.user_confirmed,
            evidence_source_refs=list(request.evidence_source_refs),
            station_attempts=station_attempts,
            assignments=assignments,
            artifact_lineage=artifact_lineage,
            incident_timeline=[{"event_type": "distributed.run.started", "created_at": _now()}],
        )

    def _record_evidence(self, context: IdentityContext, request: DistributedRunRequest, state: DistributedRunState, operation: str) -> DistributedCoordinationEvidence:
        evidence = DistributedCoordinationEvidence(
            evidence_id=f"v5_8b_evidence_{uuid4().hex[:12]}",
            operation=operation,
            distributed_run_id=state.distributed_run_id,
            workflow_instance_id=state.workflow_instance_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            source=request.source,
            actor_type=context.actor_type,
            user_confirmed=request.user_confirmed,
            human_authorization_ref=request.human_authorization.human_authorization_ref,
            policy_decision="allow_minimal_coordination_slice",
            credential_boundary_decision="worker_credential_decision_refs_required",
            incident_timeline_ref=request.incident_timeline_ref,
            audit_export_ref=request.audit_export_ref,
            correlation_id=request.correlation_id,
            request_id=request.request_id,
            redaction_status="redacted",
        )
        _assert_no_sensitive_payload(evidence.to_dict())
        self.evidence.append(evidence)
        return evidence


def read_v4_multi_agent_evidence_summary(scenario: str) -> dict[str, Any]:
    """Read an existing V4 provider-backed multi-agent evidence summary."""
    result_path = V4_MULTI_AGENT_EVIDENCE_ROOT / scenario / "runtime-result.json"
    summary_path = V4_MULTI_AGENT_EVIDENCE_ROOT / scenario / "result-summary.md"
    if not result_path.exists() or not summary_path.exists():
        raise FileNotFoundError(f"Missing V4 multi-agent evidence for {scenario}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    station_ids = tuple(node["station_id"] for node in result.get("nodes", []))
    provider = result.get("provider", {})
    return {
        "scenario": scenario,
        "result_path": result_path.relative_to(REPO_ROOT).as_posix(),
        "summary_path": summary_path.relative_to(REPO_ROOT).as_posix(),
        "workflow_instance_id": result["workflow_instance_id"],
        "station_ids": station_ids,
        "provider": provider.get("provider"),
        "model_ref": provider.get("model_ref"),
        "provider_invocation_count": result.get("provider_invocation_count", 0),
        "runtime_backed": result.get("runtime_backed") is True,
        "real_provider_backed": result.get("real_provider_backed") is True,
    }


def seed_workers_for_stations(context: IdentityContext, registry: AgentWorkerRegistry, station_ids: tuple[str, ...]) -> None:
    """Register one scoped worker per station."""
    for station_id in station_ids:
        registry.register(
            DistributedWorkerDescriptor.from_context(
                context,
                worker_id=f"worker_{station_id}",
                station_id=station_id,
                credential_decision_ref=f"credential-decision://v5-8b/{station_id}",
            )
        )


def _assert_no_sensitive_payload(data: Mapping[str, Any]) -> None:
    dumped = json.dumps(data, ensure_ascii=False).lower()
    for term in SENSITIVE_TEXT:
        if term in dumped:
            raise DistributedRuntimeCoordinationError("redaction_failed", f"Sensitive text is not allowed: {term}")


def _now() -> str:
    return datetime.now(UTC).isoformat()
