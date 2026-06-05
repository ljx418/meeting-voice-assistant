"""V9-2 limited controlled Agent executor runtime slice.

This module implements only the approved V9-2 local runtime slice. It does not
register routes, start workers, call connectors, call external LLMs, perform git
operations, deploy, grant source=agent durable mutation, or claim Agent executor
readiness.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4

from core.policies.v9_agent_executor_safety import (
    APPROVAL_GATED_OPERATIONS,
    DURABLE_OPERATIONS,
    V9AgentExecutorSafetyGate,
    V9SafetyGateError,
)


EXCLUDED_ACTIONS = {
    "connector.call",
    "external_llm.call",
    "business.event.emit",
    "context.update",
    "workflow.template.publish",
    "approval.respond",
    "git.commit",
    "git.push",
    "production.deploy",
}
FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "bearer ",
    "bearer_token",
    "signed_url",
    "signed url",
    "credential_raw_secret",
    "credential raw secret",
)


class V9ControlledExecutorRuntimeError(ValueError):
    """Stable V9-2 controlled executor runtime error."""

    def __init__(self, code: str, message: str, *, reason: str, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.field = field

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"code": self.code, "message": str(self), "reason": self.reason}
        if self.field:
            data["field"] = self.field
        return data


@dataclass(frozen=True)
class V9RuntimeAttempt:
    """Append-only station attempt record."""

    attempt_id: str
    station_id: str
    station_run_id: str
    attempt_number: int
    status: str
    error_ref: str | None = None
    producer_runtime_result_ref: str | None = None
    previous_attempt_id: str | None = None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class V9ControlledRuntimeState:
    """In-memory V9-2 controlled runtime state."""

    workflow_instance_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    status: str = "created"
    station_attempts: dict[str, list[V9RuntimeAttempt]] = field(default_factory=dict)
    downstream_stale: list[str] = field(default_factory=list)
    artifact_versions: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    quality_evaluations: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    runtime_result_refs: list[str] = field(default_factory=list)
    incident_timeline_events: list[dict[str, Any]] = field(default_factory=list)
    revision: int = 0
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(
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
                "incident_timeline_events": list(self.incident_timeline_events),
                "revision": self.revision,
                "updated_at": self.updated_at,
                "v9_2_limited_runtime_slice": True,
                "agent_executor_ready": False,
                "controlled_executor_ready": False,
                "production_controlled_executor_ready": False,
            }
        )


@dataclass(frozen=True)
class V9ControlledExecutionResult:
    """Result of one V9-2 controlled action."""

    result_id: str
    operation: str
    status: str
    policy_decision: str
    capability_decision: str
    runtime_result_ref: str | None
    execution_evidence: dict[str, Any] | None
    workflow_state: dict[str, Any] | None
    blocked_reason: str | None = None
    idempotent_replay: bool = False
    incident_timeline_ref: str | None = None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(asdict(self) | {"agent_executor_ready": False, "controlled_executor_ready": False, "production_controlled_executor_ready": False})


class V9LimitedControlledExecutorRuntime:
    """Local V9-2 runtime slice for four allowlisted actions only."""

    def __init__(self, safety_gate: V9AgentExecutorSafetyGate | None = None) -> None:
        self.safety_gate = safety_gate or V9AgentExecutorSafetyGate()
        self.workflow_states: dict[str, V9ControlledRuntimeState] = {}
        self.idempotency_results: dict[str, V9ControlledExecutionResult] = {}
        self.idempotency_fingerprints: dict[str, tuple[str, str, str, str, str, str]] = {}
        self.execution_evidence: list[dict[str, Any]] = []
        self.runtime_results: list[dict[str, Any]] = []
        self.incident_timeline_events: list[dict[str, Any]] = []
        self.disabled_workspaces: set[str] = set()

    def seed_workflow(
        self,
        *,
        workflow_instance_id: str,
        tenant_id: str = "tenant-v9",
        workspace_id: str = "workspace-v9",
        project_id: str = "project-v9",
        app_id: str = "app-v9",
        station_id: str = "station-v9",
        station_run_id: str = "station-run-v9",
        failed: bool = False,
    ) -> V9ControlledRuntimeState:
        attempt = V9RuntimeAttempt(
            attempt_id=f"attempt-v9-2-{uuid4().hex[:12]}",
            station_id=station_id,
            station_run_id=station_run_id,
            attempt_number=1,
            status="failed" if failed else "completed",
            error_ref="error://v9-2/seeded-failure" if failed else None,
        )
        state = V9ControlledRuntimeState(
            workflow_instance_id=workflow_instance_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            project_id=project_id,
            app_id=app_id,
            status="failed" if failed else "created",
            station_attempts={station_id: [attempt]},
        )
        self.workflow_states[workflow_instance_id] = state
        return state

    def disable_workspace(self, workspace_id: str) -> None:
        self.disabled_workspaces.add(workspace_id)

    def execute(
        self,
        *,
        envelope: Mapping[str, Any],
        human_authorization: Mapping[str, Any] | None = None,
        approval_gate: Mapping[str, Any] | None = None,
        kill_switch: Mapping[str, Any] | None = None,
        timeout_policy: Mapping[str, Any] | None = None,
        rollback_descriptor: Mapping[str, Any] | None = None,
    ) -> V9ControlledExecutionResult:
        try:
            safe_envelope = dict(envelope)
            self._preflight(safe_envelope)
            safety_decision = self.safety_gate.evaluate(
                envelope=safe_envelope,
                human_authorization=human_authorization,
                approval_gate=approval_gate,
                kill_switch=kill_switch,
                timeout_policy=timeout_policy,
                rollback_descriptor=rollback_descriptor,
            ).to_dict()
            if safety_decision["decision"] != "allow":
                return self._blocked(safe_envelope, safety_decision["denial_reason"], safety_decision=safety_decision)
            if safe_envelope["workspace_id"] in self.disabled_workspaces:
                return self._blocked(safe_envelope, "kill_switch_denied", safety_decision=safety_decision)
            fingerprint = _idempotency_fingerprint(safe_envelope)
            idempotency_key = str(safe_envelope["idempotency_key"])
            if idempotency_key in self.idempotency_results:
                if self.idempotency_fingerprints[idempotency_key] != fingerprint:
                    return self._blocked(safe_envelope, "idempotency_key_conflict", safety_decision=safety_decision)
                prior = self.idempotency_results[idempotency_key]
                return V9ControlledExecutionResult(
                    result_id=f"v9_2_result_{uuid4().hex[:12]}",
                    operation=prior.operation,
                    status="idempotent_replay",
                    policy_decision=prior.policy_decision,
                    capability_decision=prior.capability_decision,
                    runtime_result_ref=prior.runtime_result_ref,
                    execution_evidence=prior.execution_evidence,
                    workflow_state=prior.workflow_state,
                    idempotent_replay=True,
                    incident_timeline_ref=prior.incident_timeline_ref,
                )
            state = self._state_for(safe_envelope)
            operation = str(safe_envelope["operation"])
            if operation == "workflow.instance.start":
                result = self._start_workflow(safe_envelope, state, safety_decision)
            elif operation == "station.rerun":
                result = self._rerun_station(safe_envelope, state, safety_decision)
            elif operation == "artifact.write":
                result = self._write_artifact(safe_envelope, state, safety_decision)
            elif operation == "quality.evaluation.create":
                result = self._create_quality_evaluation(safe_envelope, state, safety_decision)
            else:
                result = self._blocked(safe_envelope, "operation_not_allowed", safety_decision=safety_decision)
            if result.status == "applied_v9_2_limited_runtime_slice":
                self.idempotency_results[idempotency_key] = result
                self.idempotency_fingerprints[idempotency_key] = fingerprint
            return result
        except (V9SafetyGateError, V9ControlledExecutorRuntimeError) as exc:
            reason = getattr(exc, "reason", "validation_error")
            operation = str(envelope.get("operation", "unknown")) if isinstance(envelope, Mapping) else "unknown"
            return V9ControlledExecutionResult(
                result_id=f"v9_2_result_{uuid4().hex[:12]}",
                operation=operation,
                status="blocked",
                policy_decision="deny",
                capability_decision="deny",
                runtime_result_ref=None,
                execution_evidence=None,
                workflow_state=None,
                blocked_reason=reason,
                incident_timeline_ref=self._record_incident(dict(envelope), reason),
            )

    def _preflight(self, envelope: dict[str, Any]) -> None:
        _assert_no_forbidden_raw_content(envelope)
        operation = envelope.get("operation")
        if operation in EXCLUDED_ACTIONS or operation not in DURABLE_OPERATIONS:
            raise V9ControlledExecutorRuntimeError("V9_2_OPERATION_DENIED", "Operation is outside the V9-2 allowlist.", reason="operation_not_allowed", field="operation")
        if envelope.get("source") == "agent" or envelope.get("actor_type") == "agent":
            raise V9ControlledExecutorRuntimeError("V9_2_SOURCE_AGENT_DENIED", "source=agent cannot execute durable mutation.", reason="source_agent_durable_mutation_denied", field="source")

    def _state_for(self, envelope: dict[str, Any]) -> V9ControlledRuntimeState:
        refs = dict(envelope["target_refs"])
        workflow_instance_id = refs.get("workflow_instance_id") or str(envelope["workflow_instance_id"])
        state = self.workflow_states.get(workflow_instance_id)
        if state is None:
            state = V9ControlledRuntimeState(
                workflow_instance_id=workflow_instance_id,
                tenant_id=str(envelope["tenant_id"]),
                workspace_id=str(envelope["workspace_id"]),
                project_id=str(envelope["project_id"]),
                app_id=str(envelope["app_id"]),
            )
            self.workflow_states[workflow_instance_id] = state
        return state

    def _start_workflow(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any]) -> V9ControlledExecutionResult:
        state.status = "running"
        return self._applied(envelope, state, safety_decision, runtime_result_ref=f"runtime-result://v9-2/{state.workflow_instance_id}/start")

    def _rerun_station(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any]) -> V9ControlledExecutionResult:
        refs = dict(envelope["target_refs"])
        station_id = refs["station_id"]
        previous_station_run_id = refs["station_run_id"]
        attempts = state.station_attempts.setdefault(station_id, [])
        previous_attempt = attempts[-1] if attempts else None
        runtime_result_ref = f"runtime-result://v9-2/{state.workflow_instance_id}/rerun/{station_id}/{len(attempts) + 1}"
        attempts.append(
            V9RuntimeAttempt(
                attempt_id=f"attempt-v9-2-{uuid4().hex[:12]}",
                station_id=station_id,
                station_run_id=f"{previous_station_run_id}-retry-{len(attempts) + 1}",
                attempt_number=len(attempts) + 1,
                status="completed",
                producer_runtime_result_ref=runtime_result_ref,
                previous_attempt_id=previous_attempt.attempt_id if previous_attempt else None,
            )
        )
        state.status = "running"
        state.downstream_stale = sorted(set(state.downstream_stale) | {f"downstream-of:{station_id}"})
        return self._applied(envelope, state, safety_decision, runtime_result_ref=runtime_result_ref)

    def _write_artifact(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any]) -> V9ControlledExecutionResult:
        refs = dict(envelope["target_refs"])
        artifact_id = refs["artifact_id"]
        versions = state.artifact_versions.setdefault(artifact_id, [])
        runtime_result_ref = f"runtime-result://v9-2/{state.workflow_instance_id}/artifact/{artifact_id}/{len(versions) + 1}"
        versions.append(
            {
                "artifact_version_id": f"artifact-version-v9-2-{len(versions) + 1}",
                "artifact_id": artifact_id,
                "operation": "append_version",
                "content_ref": _payload_ref(envelope, "content_ref", f"artifact-content-ref://v9-2/{artifact_id}/{len(versions) + 1}"),
                "producer_station_id": refs.get("station_id") or envelope.get("station_id"),
                "producer_attempt_id": refs.get("attempt_id"),
                "producer_runtime_result_ref": runtime_result_ref,
                "created_at": _now(),
                "redaction_status": "PASS",
            }
        )
        return self._applied(envelope, state, safety_decision, runtime_result_ref=runtime_result_ref)

    def _create_quality_evaluation(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any]) -> V9ControlledExecutionResult:
        refs = dict(envelope["target_refs"])
        evaluation_id = refs["quality_evaluation_id"]
        evaluations = state.quality_evaluations.setdefault(evaluation_id, [])
        runtime_result_ref = f"runtime-result://v9-2/{state.workflow_instance_id}/quality/{evaluation_id}/{len(evaluations) + 1}"
        evaluations.append(
            {
                "quality_evaluation_id": evaluation_id,
                "operation": "append_evaluation",
                "quality_rule_ref": _payload_ref(envelope, "quality_rule_ref", "quality-rule-ref://v9-2/default"),
                "target_ref": refs.get("artifact_id") or refs.get("station_id") or evaluation_id,
                "score_ref": _payload_ref(envelope, "score_ref", f"quality-score-ref://v9-2/{evaluation_id}/{len(evaluations) + 1}"),
                "producer_runtime_result_ref": runtime_result_ref,
                "created_at": _now(),
                "redaction_status": "PASS",
            }
        )
        return self._applied(envelope, state, safety_decision, runtime_result_ref=runtime_result_ref)

    def _applied(self, envelope: dict[str, Any], state: V9ControlledRuntimeState, safety_decision: dict[str, Any], *, runtime_result_ref: str) -> V9ControlledExecutionResult:
        state.runtime_result_refs.append(runtime_result_ref)
        state.revision += 1
        state.updated_at = _now()
        incident_ref = self._record_incident(envelope, "runtime_action_completed", runtime_result_ref=runtime_result_ref)
        runtime_result = {
            "runtime_result_ref": runtime_result_ref,
            "operation": envelope["operation"],
            "status": "completed",
            "correlation_id": envelope["correlation_id"],
            "request_id": envelope["request_id"],
            "created_at": _now(),
        }
        self.runtime_results.append(runtime_result)
        evidence = self._execution_evidence(envelope, safety_decision, runtime_result_ref=runtime_result_ref, incident_timeline_ref=incident_ref)
        self.execution_evidence.append(evidence)
        _assert_no_forbidden_raw_content(evidence)
        return V9ControlledExecutionResult(
            result_id=f"v9_2_result_{uuid4().hex[:12]}",
            operation=str(envelope["operation"]),
            status="applied_v9_2_limited_runtime_slice",
            policy_decision="allow",
            capability_decision="allow_v9_2_limited_runtime_slice",
            runtime_result_ref=runtime_result_ref,
            execution_evidence=evidence,
            workflow_state=state.to_dict(),
            incident_timeline_ref=incident_ref,
        )

    def _blocked(self, envelope: dict[str, Any], reason: str, *, safety_decision: dict[str, Any] | None = None) -> V9ControlledExecutionResult:
        incident_ref = self._record_incident(envelope, reason)
        return V9ControlledExecutionResult(
            result_id=f"v9_2_result_{uuid4().hex[:12]}",
            operation=str(envelope.get("operation", "unknown")),
            status="blocked",
            policy_decision="deny",
            capability_decision="deny",
            runtime_result_ref=None,
            execution_evidence=None,
            workflow_state=None,
            blocked_reason=reason,
            incident_timeline_ref=incident_ref,
        )

    def _execution_evidence(self, envelope: dict[str, Any], safety_decision: dict[str, Any], *, runtime_result_ref: str, incident_timeline_ref: str) -> dict[str, Any]:
        evidence = {
            "schema_version": "v9.0",
            "execution_evidence_ref": f"execution-evidence://v9-2/{uuid4().hex}",
            "execution_envelope_id": envelope["execution_envelope_id"],
            "operation": envelope["operation"],
            "source": envelope["source"],
            "actor_type": envelope["actor_type"],
            "agent_id": envelope["agent_id"],
            "station_id": envelope["station_id"],
            "target_refs": dict(envelope["target_refs"]),
            "capability_decision_ref": safety_decision["capability_decision_ref"],
            "approval_gate_ref": envelope.get("approval_gate_ref"),
            "human_authorization_ref": envelope.get("human_authorization_ref"),
            "runtime_result_ref": runtime_result_ref,
            "rollback_descriptor_ref": envelope.get("rollback_descriptor_ref"),
            "redaction_status": "PASS",
            "correlation_id": envelope["correlation_id"],
            "request_id": envelope["request_id"],
            "audit_ref": envelope["audit_ref"],
            "created_at": _now(),
            "decision_chain_refs": {
                "policy_ref": safety_decision["policy_ref"],
                "capability_decision_ref": safety_decision["capability_decision_ref"],
                "kill_switch_policy_ref": envelope.get("kill_switch_policy_ref"),
                "timeout_policy_ref": envelope.get("timeout_policy_ref"),
                "rollback_descriptor_ref": envelope.get("rollback_descriptor_ref"),
                "incident_timeline_ref": incident_timeline_ref,
            },
            "agent_executor_ready": False,
            "controlled_executor_ready": False,
            "production_controlled_executor_ready": False,
        }
        return _redact(evidence)

    def _record_incident(self, envelope: Mapping[str, Any], event_type: str, *, runtime_result_ref: str | None = None) -> str:
        ref = f"incident-timeline://v9-2/{uuid4().hex}"
        event = {
            "incident_timeline_ref": ref,
            "event_type": event_type,
            "operation": envelope.get("operation", "unknown"),
            "target_refs": dict(envelope.get("target_refs", {})),
            "runtime_result_ref": runtime_result_ref,
            "correlation_id": envelope.get("correlation_id", f"corr-v9-2-{uuid4().hex[:8]}"),
            "request_id": envelope.get("request_id", f"req-v9-2-{uuid4().hex[:8]}"),
            "audit_ref": envelope.get("audit_ref", f"audit://v9-2/{uuid4().hex}"),
            "created_at": _now(),
        }
        self.incident_timeline_events.append(_redact(event))
        workflow_id = dict(envelope.get("target_refs", {})).get("workflow_instance_id") or envelope.get("workflow_instance_id")
        if workflow_id in self.workflow_states:
            self.workflow_states[str(workflow_id)].incident_timeline_events.append(_redact(event))
        return ref


def _payload_ref(envelope: Mapping[str, Any], key: str, default: str) -> str:
    payload_refs = envelope.get("payload_refs", [])
    if isinstance(payload_refs, Mapping) and payload_refs.get(key):
        return str(payload_refs[key])
    if isinstance(payload_refs, list) and payload_refs:
        for item in payload_refs:
            text = str(item)
            if text.startswith(f"{key}:"):
                return text
    return default


def _idempotency_fingerprint(envelope: Mapping[str, Any]) -> tuple[str, str, str, str, str, str]:
    target_hash = json.dumps(envelope.get("target_refs", {}), sort_keys=True, separators=(",", ":"))
    return (
        str(envelope["tenant_id"]),
        str(envelope["workspace_id"]),
        str(envelope["project_id"]),
        str(envelope["operation"]),
        str(envelope["source"]),
        target_hash,
    )


def _redact(value: Any) -> Any:
    text = json.dumps(value, ensure_ascii=False)
    lowered = text.lower()
    for term in FORBIDDEN_RAW_TERMS:
        if term in lowered:
            raise V9ControlledExecutorRuntimeError("V9_2_REDACTION_DENIED", "Forbidden raw content appears in runtime DTO.", reason="forbidden_raw_content")
    return value


def _assert_no_forbidden_raw_content(value: Any) -> None:
    _redact(value)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
