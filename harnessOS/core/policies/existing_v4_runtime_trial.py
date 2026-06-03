"""V5.4C bridge for an existing V4 dev/local workflow runtime trial.

This module gates calls into an already-governed V4 BFF runtime entrypoint. It
does not add public routes, grant Agent mutation authority, or write workflow
runtime truth directly.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext
from core.policies.executor_safety import CapabilityDecision, CapabilityDecisionService, RequestedAction


FORBIDDEN_RUNTIME_TEXT = (
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed URL",
)


class ExistingV4RuntimeTrialError(ValueError):
    """Stable V5.4C existing-runtime trial denial."""

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


class ExistingV4RuntimeAdapter(Protocol):
    """Adapter for the existing V4 BFF runtime entrypoint."""

    entrypoint_id: str

    def start_local_folder_summary(self, *, folder_path: str, source: str, user_confirmed: bool) -> dict[str, Any]:
        """Start the existing V4 local folder summary runtime path."""

    def rerun_station(self, *, workflow_instance_id: str, station_id: str, source: str, user_confirmed: bool) -> dict[str, Any]:
        """Rerun one station through the existing V4 local runtime path."""

    def continue_downstream(self, *, workflow_instance_id: str, source: str, user_confirmed: bool) -> dict[str, Any]:
        """Continue downstream stations through the existing V4 local runtime path."""

    def list_evidence(self, *, workflow_instance_id: str) -> list[dict[str, Any]]:
        """Return existing runtime operation evidence."""


@dataclass(frozen=True)
class ExistingV4RuntimeEvidence:
    """Evidence for one V5.4C bridge call into the V4 dev/local runtime."""

    evidence_id: str
    operation: str
    source: str
    actor_type: str
    user_confirmed: bool
    policy_decision: str
    capability_decision: str
    bridge_policy_decision: str
    runtime_result_ref: dict[str, Any]
    v4_runtime_entrypoint: str
    correlation_id: str
    request_id: str
    risk_flags: tuple[str, ...]
    devlocal_only: bool
    runtime_backed: bool
    redaction_status: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted evidence DTO."""
        data = asdict(self)
        data["risk_flags"] = list(self.risk_flags)
        return mask_value(data)


@dataclass(frozen=True)
class ExistingV4RuntimeTrialResult:
    """Result of one V5.4C bridge operation."""

    result_id: str
    operation: str
    status: str
    decision: CapabilityDecision
    runtime_result: dict[str, Any] | None
    bridge_evidence: ExistingV4RuntimeEvidence | None
    blocked_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return redacted result DTO."""
        return mask_value(
            {
                "result_id": self.result_id,
                "operation": self.operation,
                "status": self.status,
                "decision": self.decision.to_dict(),
                "runtime_result": self.runtime_result,
                "bridge_evidence": self.bridge_evidence.to_dict() if self.bridge_evidence else None,
                "blocked_reason": self.blocked_reason,
                "devlocal_only": True,
                "production_ready": False,
            }
        )


class ExistingV4RuntimeTrialBridge:
    """Gated bridge into existing V4 dev/local runtime behavior."""

    def __init__(self, adapter: ExistingV4RuntimeAdapter, *, decision_service: CapabilityDecisionService | None = None) -> None:
        self.adapter = adapter
        self.decision_service = decision_service or CapabilityDecisionService()
        self.bridge_evidence: list[ExistingV4RuntimeEvidence] = []

    def start_local_folder_summary(
        self,
        context: IdentityContext,
        *,
        folder_path: str,
        source: str,
        actor_type: str,
        user_confirmed: bool,
    ) -> ExistingV4RuntimeTrialResult:
        """Start the existing V4 local folder workflow after V5.4C gates pass."""
        target_refs = {"folder_path_ref": _safe_folder_ref(folder_path)}
        decision = self._evaluate(context, "workflow.instance.start", source, actor_type, target_refs, user_confirmed, ("local_file_read", "existing_v4_runtime"))
        if not decision.allowed:
            return self._blocked("workflow.instance.start", decision)
        runtime_result = self.adapter.start_local_folder_summary(folder_path=folder_path, source=source, user_confirmed=True)
        return self._applied(context, "workflow.instance.start", decision, runtime_result, source=source, actor_type=actor_type, user_confirmed=True)

    def rerun_station(
        self,
        context: IdentityContext,
        *,
        workflow_instance_id: str,
        station_id: str,
        source: str,
        actor_type: str,
        user_confirmed: bool,
    ) -> ExistingV4RuntimeTrialResult:
        """Rerun one station through the existing V4 local runtime after gates pass."""
        target_refs = {"workflow_instance_id": workflow_instance_id, "station_id": station_id}
        decision = self._evaluate(context, "station.rerun", source, actor_type, target_refs, user_confirmed, ("station_rerun", "existing_v4_runtime"))
        if not decision.allowed:
            return self._blocked("station.rerun", decision)
        runtime_result = self.adapter.rerun_station(workflow_instance_id=workflow_instance_id, station_id=station_id, source=source, user_confirmed=True)
        return self._applied(context, "station.rerun", decision, runtime_result, source=source, actor_type=actor_type, user_confirmed=True)

    def continue_downstream(
        self,
        context: IdentityContext,
        *,
        workflow_instance_id: str,
        source: str,
        actor_type: str,
        user_confirmed: bool,
    ) -> ExistingV4RuntimeTrialResult:
        """Continue downstream stations through the existing V4 local runtime after gates pass."""
        target_refs = {"workflow_instance_id": workflow_instance_id}
        decision = self._evaluate(context, "workflow.instance.start", source, actor_type, target_refs, user_confirmed, ("downstream_continue", "existing_v4_runtime"))
        if not decision.allowed:
            return self._blocked("workflow.instance.continue_downstream", decision)
        runtime_result = self.adapter.continue_downstream(workflow_instance_id=workflow_instance_id, source=source, user_confirmed=True)
        return self._applied(context, "workflow.instance.continue_downstream", decision, runtime_result, source=source, actor_type=actor_type, user_confirmed=True)

    def _evaluate(
        self,
        context: IdentityContext,
        operation: str,
        source: str,
        actor_type: str,
        target_refs: dict[str, str],
        user_confirmed: bool,
        risk_flags: tuple[str, ...],
    ) -> CapabilityDecision:
        action = RequestedAction(
            operation=operation,
            source=source,
            actor_type=actor_type,
            target_refs=target_refs,
            user_confirmed=user_confirmed,
            risk_flags=risk_flags,
        )
        return self.decision_service.evaluate(context, action)

    def _blocked(self, operation: str, decision: CapabilityDecision) -> ExistingV4RuntimeTrialResult:
        return ExistingV4RuntimeTrialResult(
            result_id=f"v5_4c_result_{uuid4().hex[:12]}",
            operation=operation,
            status="blocked",
            decision=decision,
            runtime_result=None,
            bridge_evidence=None,
            blocked_reason=decision.reason,
        )

    def _applied(
        self,
        context: IdentityContext,
        operation: str,
        decision: CapabilityDecision,
        runtime_result: dict[str, Any],
        *,
        source: str,
        actor_type: str,
        user_confirmed: bool,
    ) -> ExistingV4RuntimeTrialResult:
        _assert_redacted(runtime_result)
        workflow_instance_id = str(runtime_result.get("workflow_instance_id") or decision.target_refs.get("workflow_instance_id") or "")
        runtime_ref = {
            "type": "existing_v4_local_runtime_result",
            "workflow_instance_id": workflow_instance_id,
            "operation": operation,
            "status": str(runtime_result.get("status") or "unknown"),
            "backed_by": str(runtime_result.get("backed_by") or "existing_v4_local_runtime"),
        }
        evidence = ExistingV4RuntimeEvidence(
            evidence_id=f"v5_4c_evidence_{uuid4().hex[:12]}",
            operation=operation,
            source=source,
            actor_type=actor_type,
            user_confirmed=user_confirmed,
            policy_decision=decision.policy_decision,
            capability_decision=decision.capability_decision,
            bridge_policy_decision="v5_4c_devlocal_runtime_bridge_allowed",
            runtime_result_ref=runtime_ref,
            v4_runtime_entrypoint=self.adapter.entrypoint_id,
            correlation_id=context.correlation_id,
            request_id=context.request_id,
            risk_flags=tuple(sorted(set(decision.risk_flags) | {"devlocal_only", "existing_v4_runtime"})),
            devlocal_only=True,
            runtime_backed=True,
            redaction_status="redacted",
        )
        self.bridge_evidence.append(evidence)
        return ExistingV4RuntimeTrialResult(
            result_id=f"v5_4c_result_{uuid4().hex[:12]}",
            operation=operation,
            status="applied_existing_v4_runtime",
            decision=decision,
            runtime_result=mask_value(runtime_result),
            bridge_evidence=evidence,
        )


def _assert_redacted(data: dict[str, Any]) -> None:
    dumped = json.dumps(data, ensure_ascii=False)
    for term in FORBIDDEN_RUNTIME_TEXT:
        if term in dumped:
            raise ExistingV4RuntimeTrialError("V5_4C_REDACTION_FAILED", "Existing V4 runtime result contains forbidden sensitive text.", reason="redaction_failed", resource=term)


def _safe_folder_ref(folder_path: str) -> str:
    if not folder_path.strip():
        return "folder://empty"
    return f"folder://{folder_path.strip().split('/')[-1]}"


def _now() -> str:
    return datetime.now(UTC).isoformat()
