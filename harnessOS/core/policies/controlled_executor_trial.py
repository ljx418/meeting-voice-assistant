"""V5.4B synthetic controlled executor trial.

This module provides an in-memory dev/local trial runner for executor control
semantics. It does not call production connectors, create routes, run Agents,
or mutate WorkflowDraft / WorkflowVersion / WorkflowStore runtime truth.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext
from core.policies.executor_safety import CapabilityDecision, CapabilityDecisionService, RequestedAction


class ControlledExecutorTrialError(ValueError):
    """Stable V5.4B synthetic trial denial."""

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
class TrialAttempt:
    """Synthetic station attempt record."""

    attempt_id: str
    attempt_number: int
    station_id: str
    status: str
    input_refs: tuple[str, ...]
    output_refs: tuple[str, ...]
    error_ref: str | None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted attempt DTO."""
        data = asdict(self)
        data["input_refs"] = list(self.input_refs)
        data["output_refs"] = list(self.output_refs)
        return mask_value(data)


@dataclass
class SyntheticStationState:
    """In-memory station state for a synthetic workflow trial."""

    station_id: str
    status: str
    attempts: list[TrialAttempt] = field(default_factory=list)
    downstream_stale: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return redacted station state DTO."""
        return {
            "station_id": self.station_id,
            "status": self.status,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "attempt_count": len(self.attempts),
            "downstream_stale": self.downstream_stale,
        }


@dataclass
class SyntheticWorkflowState:
    """In-memory workflow state for V5.4B synthetic validation."""

    workflow_instance_id: str
    status: str
    station_states: dict[str, SyntheticStationState]
    revision: int = 0
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted workflow state DTO."""
        return {
            "workflow_instance_id": self.workflow_instance_id,
            "status": self.status,
            "revision": self.revision,
            "updated_at": self.updated_at,
            "station_states": {station_id: station.to_dict() for station_id, station in self.station_states.items()},
            "synthetic_only": True,
            "runtime_backed": False,
        }


@dataclass(frozen=True)
class TrialRuntimeEvidence:
    """Synthetic trial runtime evidence."""

    runtime_evidence_id: str
    operation: str
    source: str
    actor_type: str
    user_confirmed: bool
    capability_decision_ref: str
    policy_decision: str
    runtime_result_ref: str
    correlation_id: str
    request_id: str
    risk_flags: tuple[str, ...]
    redaction_status: str
    synthetic_only: bool
    runtime_backed: bool
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted evidence DTO."""
        data = asdict(self)
        data["risk_flags"] = list(self.risk_flags)
        return mask_value(data)


@dataclass(frozen=True)
class TrialActionResult:
    """Result of one synthetic controlled executor trial action."""

    result_id: str
    operation: str
    status: str
    decision: CapabilityDecision
    runtime_evidence: TrialRuntimeEvidence | None
    workflow_state: dict[str, Any] | None
    blocked_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return redacted action result DTO."""
        return mask_value(
            {
                "result_id": self.result_id,
                "operation": self.operation,
                "status": self.status,
                "decision": self.decision.to_dict(),
                "runtime_evidence": self.runtime_evidence.to_dict() if self.runtime_evidence else None,
                "workflow_state": self.workflow_state,
                "blocked_reason": self.blocked_reason,
            }
        )


class ControlledExecutorTrialRunner:
    """Synthetic in-memory controlled executor trial runner."""

    def __init__(self, *, decision_service: CapabilityDecisionService | None = None) -> None:
        self.decision_service = decision_service or CapabilityDecisionService()
        self.workflow_states: dict[str, SyntheticWorkflowState] = {}
        self.evidence: list[TrialRuntimeEvidence] = []

    def seed_workflow(self, *, workflow_instance_id: str, station_ids: list[str]) -> SyntheticWorkflowState:
        """Create or replace one synthetic workflow state."""
        if not workflow_instance_id.strip() or not station_ids:
            raise ControlledExecutorTrialError("TRIAL_WORKFLOW_INVALID", "Synthetic workflow requires an instance id and stations.", reason="invalid_workflow")
        state = SyntheticWorkflowState(
            workflow_instance_id=workflow_instance_id,
            status="draft",
            station_states={station_id: SyntheticStationState(station_id=station_id, status="pending") for station_id in station_ids},
        )
        self.workflow_states[workflow_instance_id] = state
        return state

    def start_workflow(
        self,
        context: IdentityContext,
        *,
        workflow_instance_id: str,
        source: str,
        actor_type: str,
        user_confirmed: bool,
    ) -> TrialActionResult:
        """Start a synthetic workflow after safety gate approval."""
        action = RequestedAction(
            operation="workflow.instance.start",
            source=source,
            actor_type=actor_type,
            target_refs={"workflow_instance_id": workflow_instance_id},
            user_confirmed=user_confirmed,
        )
        decision = self.decision_service.evaluate(context, action)
        if not decision.allowed:
            return self._blocked("workflow.instance.start", decision, decision.reason)
        state = self._require_state(workflow_instance_id)
        state.status = "running"
        state.revision += 1
        state.updated_at = _now()
        for station in state.station_states.values():
            if station.status == "pending":
                station.status = "waiting"
        evidence = self._record_evidence(context, decision, action)
        return self._result("workflow.instance.start", "applied_synthetic", decision, evidence, state)

    def rerun_station(
        self,
        context: IdentityContext,
        *,
        workflow_instance_id: str,
        station_id: str,
        source: str,
        actor_type: str,
        user_confirmed: bool,
        input_refs: list[str],
        output_refs: list[str],
    ) -> TrialActionResult:
        """Rerun a synthetic station and retain attempt history."""
        action = RequestedAction(
            operation="station.rerun",
            source=source,
            actor_type=actor_type,
            target_refs={"workflow_instance_id": workflow_instance_id, "station_id": station_id},
            user_confirmed=user_confirmed,
            payload_refs={"input_refs": ",".join(input_refs), "output_refs": ",".join(output_refs)},
        )
        decision = self.decision_service.evaluate(context, action)
        if not decision.allowed:
            return self._blocked("station.rerun", decision, decision.reason)
        state = self._require_state(workflow_instance_id)
        station = state.station_states.get(station_id)
        if station is None:
            raise ControlledExecutorTrialError("TRIAL_STATION_NOT_FOUND", "Synthetic station was not found.", reason="station_not_found", resource=station_id)
        attempt = TrialAttempt(
            attempt_id=f"trial_attempt_{uuid4().hex}",
            attempt_number=len(station.attempts) + 1,
            station_id=station_id,
            status="completed",
            input_refs=tuple(input_refs),
            output_refs=tuple(output_refs),
            error_ref=None,
        )
        station.attempts.append(attempt)
        station.status = "completed"
        for candidate in state.station_states.values():
            if candidate.station_id != station_id and candidate.status in {"waiting", "completed"}:
                candidate.downstream_stale = True
        state.status = "running"
        state.revision += 1
        state.updated_at = _now()
        evidence = self._record_evidence(context, decision, action)
        return self._result("station.rerun", "applied_synthetic", decision, evidence, state)

    def evaluate_high_risk_action(
        self,
        context: IdentityContext,
        *,
        operation: str,
        target_refs: dict[str, str],
        source: str,
        actor_type: str,
        user_confirmed: bool,
        risk_flags: tuple[str, ...],
    ) -> TrialActionResult:
        """Evaluate a high-risk action without executing it."""
        action = RequestedAction(
            operation=operation,
            source=source,
            actor_type=actor_type,
            target_refs=target_refs,
            user_confirmed=user_confirmed,
            risk_flags=risk_flags,
        )
        decision = self.decision_service.evaluate(context, action)
        return self._blocked(operation, decision, decision.reason)

    def _require_state(self, workflow_instance_id: str) -> SyntheticWorkflowState:
        try:
            return self.workflow_states[workflow_instance_id]
        except KeyError as exc:
            raise ControlledExecutorTrialError("TRIAL_WORKFLOW_NOT_FOUND", "Synthetic workflow was not found.", reason="workflow_not_found", resource=workflow_instance_id) from exc

    def _record_evidence(self, context: IdentityContext, decision: CapabilityDecision, action: RequestedAction) -> TrialRuntimeEvidence:
        evidence = TrialRuntimeEvidence(
            runtime_evidence_id=f"trial_evidence_{uuid4().hex}",
            operation=action.operation,
            source=action.source,
            actor_type=action.actor_type,
            user_confirmed=action.user_confirmed,
            capability_decision_ref=decision.decision_id,
            policy_decision=decision.policy_decision,
            runtime_result_ref=f"synthetic-runtime://{context.correlation_id}/{action.operation}/{uuid4().hex}",
            correlation_id=context.correlation_id,
            request_id=context.request_id,
            risk_flags=decision.risk_flags,
            redaction_status="redacted",
            synthetic_only=True,
            runtime_backed=False,
        )
        self.evidence.append(evidence)
        return evidence

    def _blocked(self, operation: str, decision: CapabilityDecision, reason: str) -> TrialActionResult:
        return TrialActionResult(
            result_id=f"trial_result_{uuid4().hex}",
            operation=operation,
            status="blocked",
            decision=decision,
            runtime_evidence=None,
            workflow_state=None,
            blocked_reason=reason,
        )

    def _result(
        self,
        operation: str,
        status: str,
        decision: CapabilityDecision,
        evidence: TrialRuntimeEvidence,
        state: SyntheticWorkflowState,
    ) -> TrialActionResult:
        return TrialActionResult(
            result_id=f"trial_result_{uuid4().hex}",
            operation=operation,
            status=status,
            decision=decision,
            runtime_evidence=evidence,
            workflow_state=state.to_dict(),
        )


def _now() -> str:
    return datetime.now(UTC).isoformat()
