"""V9 Agent executor safety gate.

This module validates V9 execution intent contracts and returns policy
decisions. It does not execute runtime actions, create executor routes, start
workers, write workflow runtime truth, or grant source=agent durable mutation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4


DURABLE_OPERATIONS = {
    "workflow.instance.start",
    "station.rerun",
    "artifact.write",
    "quality.evaluation.create",
}
APPROVAL_GATED_OPERATIONS = {"artifact.write", "quality.evaluation.create"}
VALID_SOURCES = {"product_console", "approved_api", "mission_tui", "agent"}
VALID_ACTOR_TYPES = {"human_user", "service_account_with_human_authorization", "agent"}
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


class V9SafetyGateError(ValueError):
    """Stable V9 safety gate validation error."""

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
class V9SafetyGateDecision:
    """V9 capability decision with evidence refs."""

    capability_decision_ref: str
    operation: str
    decision: str
    risk_level: str
    requires_user_confirmation: bool
    requires_human_authorization_ref: bool
    requires_approval_gate: bool
    denial_reason: str | None
    policy_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    correlation_id: str
    request_id: str
    audit_ref: str
    created_at: str
    runtime_execution_allowed: bool
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class V9AgentExecutorSafetyGate:
    """Evaluate V9 Agent execution intents without executing them."""

    def evaluate(
        self,
        *,
        envelope: Mapping[str, Any],
        human_authorization: Mapping[str, Any] | None = None,
        approval_gate: Mapping[str, Any] | None = None,
        kill_switch: Mapping[str, Any] | None = None,
        timeout_policy: Mapping[str, Any] | None = None,
        rollback_descriptor: Mapping[str, Any] | None = None,
    ) -> V9SafetyGateDecision:
        safe_envelope = dict(envelope)
        self._validate_no_raw_content(safe_envelope, field="envelope")
        self._validate_envelope_shape(safe_envelope)

        operation = str(safe_envelope["operation"])
        risk_level = self._risk_level(operation)
        requires_approval = operation in APPROVAL_GATED_OPERATIONS
        denial = self._first_denial(
            envelope=safe_envelope,
            human_authorization=human_authorization,
            approval_gate=approval_gate,
            kill_switch=kill_switch,
            timeout_policy=timeout_policy,
            rollback_descriptor=rollback_descriptor,
            requires_approval=requires_approval,
        )
        decision = "deny" if denial else "allow"
        now = _now()
        capability_ref = f"capability-decision://v9-1/{uuid4().hex}"
        evidence = {
            "schema_version": "v9.0",
            "execution_envelope_id": safe_envelope["execution_envelope_id"],
            "operation": operation,
            "source": safe_envelope["source"],
            "actor_type": safe_envelope["actor_type"],
            "agent_id": safe_envelope["agent_id"],
            "station_id": safe_envelope["station_id"],
            "target_refs": dict(safe_envelope["target_refs"]),
            "payload_refs": list(safe_envelope.get("payload_refs", [])),
            "user_confirmed": safe_envelope["user_confirmed"],
            "human_authorization_ref": safe_envelope.get("human_authorization_ref"),
            "capability_decision_ref": capability_ref,
            "approval_gate_ref": safe_envelope.get("approval_gate_ref"),
            "kill_switch_policy_ref": safe_envelope.get("kill_switch_policy_ref"),
            "timeout_policy_ref": safe_envelope.get("timeout_policy_ref"),
            "rollback_descriptor_ref": safe_envelope.get("rollback_descriptor_ref"),
            "policy_decision": decision,
            "denial_reason": denial,
            "runtime_execution_allowed": False,
            "redaction_status": "PASS",
            "correlation_id": safe_envelope["correlation_id"],
            "request_id": safe_envelope["request_id"],
            "audit_ref": safe_envelope["audit_ref"],
            "created_at": now,
        }
        return V9SafetyGateDecision(
            capability_decision_ref=capability_ref,
            operation=operation,
            decision=decision,
            risk_level=risk_level,
            requires_user_confirmation=True,
            requires_human_authorization_ref=not bool(safe_envelope["user_confirmed"]),
            requires_approval_gate=requires_approval,
            denial_reason=denial,
            policy_ref=f"policy://v9-1/agent-executor-safety/{operation}",
            tenant_id=safe_envelope["tenant_id"],
            workspace_id=safe_envelope["workspace_id"],
            project_id=safe_envelope["project_id"],
            app_id=safe_envelope["app_id"],
            correlation_id=safe_envelope["correlation_id"],
            request_id=safe_envelope["request_id"],
            audit_ref=safe_envelope["audit_ref"],
            created_at=now,
            runtime_execution_allowed=False,
            evidence=evidence,
        )

    def _first_denial(
        self,
        *,
        envelope: dict[str, Any],
        human_authorization: Mapping[str, Any] | None,
        approval_gate: Mapping[str, Any] | None,
        kill_switch: Mapping[str, Any] | None,
        timeout_policy: Mapping[str, Any] | None,
        rollback_descriptor: Mapping[str, Any] | None,
        requires_approval: bool,
    ) -> str | None:
        if envelope["source"] == "agent" or envelope["actor_type"] == "agent":
            return "source_agent_durable_mutation_denied"
        if not self._has_user_confirmation_or_valid_authorization(envelope, human_authorization):
            return "missing_user_confirmation_or_valid_human_authorization_ref"
        kill_denial = self._validate_kill_switch(envelope, kill_switch)
        if kill_denial:
            return kill_denial
        if requires_approval:
            approval_denial = self._validate_approval_gate(envelope, approval_gate)
            if approval_denial:
                return approval_denial
        timeout_denial = self._validate_timeout_policy(envelope, timeout_policy)
        if timeout_denial:
            return timeout_denial
        rollback_denial = self._validate_rollback_descriptor(envelope, rollback_descriptor)
        if rollback_denial:
            return rollback_denial
        return None

    def _has_user_confirmation_or_valid_authorization(self, envelope: dict[str, Any], authorization: Mapping[str, Any] | None) -> bool:
        if envelope.get("user_confirmed") is True:
            return True
        if not isinstance(envelope.get("human_authorization_ref"), str):
            return False
        return self.validate_human_authorization(envelope, authorization)

    def validate_human_authorization(self, envelope: Mapping[str, Any], authorization: Mapping[str, Any] | None) -> bool:
        if authorization is None:
            return False
        self._validate_no_raw_content(dict(authorization), field="human_authorization")
        if authorization.get("human_authorization_ref") != envelope.get("human_authorization_ref"):
            return False
        if authorization.get("revoked") is True:
            return False
        if _parse_time(str(authorization.get("expires_at"))) <= _now_dt():
            return False
        if authorization.get("operation") != envelope.get("operation"):
            return False
        for field in ("tenant_id", "workspace_id", "project_id", "app_id"):
            if authorization.get(field) != envelope.get(field):
                return False
        if envelope.get("source") not in set(authorization.get("allowed_sources", [])):
            return False
        if envelope.get("actor_type") not in set(authorization.get("allowed_actor_types", [])):
            return False
        if not _target_refs_match(dict(envelope.get("target_refs", {})), dict(authorization.get("target_refs", {}))):
            return False
        expected_hash = operation_hash(str(envelope["operation"]), dict(envelope["target_refs"]))
        return authorization.get("operation_hash") == expected_hash

    def _validate_envelope_shape(self, envelope: dict[str, Any]) -> None:
        required = {
            "schema_version",
            "execution_envelope_id",
            "operation",
            "source",
            "actor_type",
            "actor_id",
            "agent_id",
            "station_id",
            "tenant_id",
            "workspace_id",
            "project_id",
            "app_id",
            "workflow_instance_id",
            "station_run_id",
            "target_refs",
            "payload_refs",
            "user_confirmed",
            "human_authorization_ref",
            "correlation_id",
            "request_id",
            "audit_ref",
        }
        missing = sorted(required - set(envelope))
        if missing:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "AgentExecutionEnvelope is missing required fields.", reason="missing_required_field", field=missing[0])
        if envelope["schema_version"] != "v9.0":
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "Unsupported schema_version.", reason="unsupported_schema_version", field="schema_version")
        if envelope["operation"] not in DURABLE_OPERATIONS:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "Operation is not in V9-1 candidate action set.", reason="unknown_operation", field="operation")
        if envelope["source"] not in VALID_SOURCES:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "Source is not allowed.", reason="unknown_source", field="source")
        if envelope["actor_type"] not in VALID_ACTOR_TYPES:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "Actor type is not allowed.", reason="unknown_actor_type", field="actor_type")
        target_refs = envelope.get("target_refs")
        if not isinstance(target_refs, dict) or not target_refs:
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "target_refs must be a non-empty object.", reason="empty_target_refs", field="target_refs")
        _validate_operation_target_refs(str(envelope["operation"]), target_refs)
        payload_refs = envelope.get("payload_refs")
        if not isinstance(payload_refs, list):
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "payload_refs must be a list of redacted references.", reason="invalid_payload_refs", field="payload_refs")

    def _validate_kill_switch(self, envelope: dict[str, Any], kill_switch: Mapping[str, Any] | None) -> str | None:
        if kill_switch is None:
            return "missing_kill_switch_decision"
        self._validate_no_raw_content(dict(kill_switch), field="kill_switch")
        if kill_switch.get("operation") != envelope["operation"]:
            return "kill_switch_operation_mismatch"
        if kill_switch.get("allowed") is not True:
            return "kill_switch_denied"
        return None

    def _validate_approval_gate(self, envelope: dict[str, Any], approval_gate: Mapping[str, Any] | None) -> str | None:
        if approval_gate is None:
            return "approval_gate_required"
        self._validate_no_raw_content(dict(approval_gate), field="approval_gate")
        if approval_gate.get("operation") != envelope["operation"]:
            return "approval_gate_operation_mismatch"
        if approval_gate.get("approved") is not True:
            return "approval_gate_denied"
        if not approval_gate.get("approved_by") or not approval_gate.get("approved_at"):
            return "approval_gate_missing_human_approval_evidence"
        return None

    def _validate_timeout_policy(self, envelope: dict[str, Any], timeout_policy: Mapping[str, Any] | None) -> str | None:
        if timeout_policy is None:
            return "missing_timeout_policy"
        self._validate_no_raw_content(dict(timeout_policy), field="timeout_policy")
        if timeout_policy.get("operation") != envelope["operation"]:
            return "timeout_policy_operation_mismatch"
        if timeout_policy.get("incident_timeline_required") is not True:
            return "timeout_policy_requires_incident_timeline"
        max_runtime = timeout_policy.get("max_runtime_seconds")
        if not isinstance(max_runtime, int) or max_runtime < 1:
            return "timeout_policy_invalid"
        return None

    def _validate_rollback_descriptor(self, envelope: dict[str, Any], rollback_descriptor: Mapping[str, Any] | None) -> str | None:
        if rollback_descriptor is None:
            return "missing_rollback_descriptor"
        self._validate_no_raw_content(dict(rollback_descriptor), field="rollback_descriptor")
        if rollback_descriptor.get("operation") != envelope["operation"]:
            return "rollback_descriptor_operation_mismatch"
        if not rollback_descriptor.get("rollback_strategy"):
            return "rollback_descriptor_missing_strategy"
        return None

    def _validate_no_raw_content(self, value: Any, *, field: str) -> None:
        text = json.dumps(value, ensure_ascii=False).lower()
        for term in FORBIDDEN_RAW_TERMS:
            if term.lower() in text:
                raise V9SafetyGateError("V9_REDACTION_DENIED", "Raw or sensitive content is not allowed in V9 safety gate inputs.", reason="forbidden_raw_content", field=field)

    def _risk_level(self, operation: str) -> str:
        if operation in {"artifact.write", "quality.evaluation.create"}:
            return "medium"
        return "low"


def operation_hash(operation: str, target_refs: Mapping[str, str]) -> str:
    payload = {"operation": operation, "target_refs": dict(sorted(target_refs.items()))}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:32]


def build_human_authorization_ref(
    *,
    ref: str,
    envelope: Mapping[str, Any],
    expires_at: str = "2999-01-01T00:00:00Z",
) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "human_authorization_ref": ref,
        "issuer_type": "human_user",
        "issuer_id": str(envelope["actor_id"]),
        "authorization_subject_actor_id": str(envelope["actor_id"]),
        "tenant_id": str(envelope["tenant_id"]),
        "workspace_id": str(envelope["workspace_id"]),
        "project_id": str(envelope["project_id"]),
        "app_id": str(envelope["app_id"]),
        "operation": str(envelope["operation"]),
        "operation_hash": operation_hash(str(envelope["operation"]), dict(envelope["target_refs"])),
        "target_refs": dict(envelope["target_refs"]),
        "allowed_sources": [str(envelope["source"])],
        "allowed_actor_types": [str(envelope["actor_type"])],
        "scope": "single_operation",
        "created_at": "2026-06-05T00:00:00Z",
        "expires_at": expires_at,
        "revoked": False,
        "revoked_at": None,
        "revocation_reason": None,
        "correlation_id": str(envelope["correlation_id"]),
        "request_id": str(envelope["request_id"]),
        "audit_ref": f"audit://v9-1/human-authorization/{ref}",
    }


def build_kill_switch_decision(envelope: Mapping[str, Any], *, allowed: bool = True) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "kill_switch_policy_ref": str(envelope.get("kill_switch_policy_ref") or "kill-switch://v9-1/default"),
        "operation": str(envelope["operation"]),
        "checked_at": _now(),
        "checked_by": "v9_agent_executor_safety_gate",
        "allowed": allowed,
        "denial_reason": None if allowed else "kill_switch_active",
        "correlation_id": str(envelope["correlation_id"]),
        "audit_ref": f"audit://v9-1/kill-switch/{uuid4().hex}",
    }


def build_timeout_policy(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "timeout_policy_ref": str(envelope.get("timeout_policy_ref") or "timeout://v9-1/default"),
        "operation": str(envelope["operation"]),
        "max_runtime_seconds": 300,
        "on_timeout": "mark_failed",
        "incident_timeline_required": True,
    }


def build_rollback_descriptor(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "rollback_descriptor_ref": str(envelope.get("rollback_descriptor_ref") or f"rollback://v9-1/{uuid4().hex}"),
        "operation": str(envelope["operation"]),
        "rollback_strategy": "append_correction" if envelope["operation"] in APPROVAL_GATED_OPERATIONS else "mark_failed",
        "correction_artifact_required": envelope["operation"] in APPROVAL_GATED_OPERATIONS,
        "previous_state_ref": None,
        "created_at": _now(),
    }


def build_approval_gate_decision(envelope: Mapping[str, Any], *, approved: bool = True) -> dict[str, Any]:
    return {
        "schema_version": "v9.0",
        "approval_gate_ref": str(envelope.get("approval_gate_ref") or f"approval://v9-1/{uuid4().hex}"),
        "operation": str(envelope["operation"]),
        "risk_level": "medium",
        "requires_human_approval": True,
        "approved": approved,
        "approved_by": str(envelope["actor_id"]) if approved else None,
        "approved_at": _now() if approved else None,
        "denial_reason": None if approved else "not_approved",
        "correlation_id": str(envelope["correlation_id"]),
        "audit_ref": f"audit://v9-1/approval/{uuid4().hex}",
    }


def _validate_operation_target_refs(operation: str, target_refs: Mapping[str, Any]) -> None:
    required_by_operation = {
        "workflow.instance.start": ("workflow_instance_id",),
        "station.rerun": ("station_id", "station_run_id"),
        "artifact.write": ("artifact_id",),
        "quality.evaluation.create": ("quality_evaluation_id",),
    }
    for field in required_by_operation[operation]:
        if not target_refs.get(field):
            raise V9SafetyGateError("V9_ENVELOPE_INVALID", "target_refs are missing required operation-specific fields.", reason="missing_target_ref", field=f"target_refs.{field}")


def _target_refs_match(envelope_refs: Mapping[str, Any], authorization_refs: Mapping[str, Any]) -> bool:
    for key, value in authorization_refs.items():
        if envelope_refs.get(key) != value:
            return False
    return True


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _now_dt() -> datetime:
    return datetime.now(UTC)


def _now() -> str:
    return _now_dt().replace(microsecond=0).isoformat().replace("+00:00", "Z")

