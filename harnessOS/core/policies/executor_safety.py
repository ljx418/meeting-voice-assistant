"""V5.4A Agent executor safety gate primitives.

This module implements safety decisions for future executor trials. It does not
execute actions, add routes, grant Agent mutation authority, or write workflow
runtime truth.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext


CLASSIFICATIONS = {
    "forbidden",
    "proposal_only",
    "handoff_only",
    "user_confirmed_only",
    "approval_gated_future",
    "never_executor",
}

CANDIDATE_POLICY_MATRIX: dict[str, str] = {
    "workflow.patch.apply": "user_confirmed_only",
    "workflow.template.publish": "approval_gated_future",
    "workflow.instance.start": "user_confirmed_only",
    "station.rerun": "user_confirmed_only",
    "approval.respond": "user_confirmed_only",
    "context.update": "approval_gated_future",
    "business.event.emit": "approval_gated_future",
    "connector.call": "never_executor",
    "external_llm.call": "never_executor",
    "artifact.write": "approval_gated_future",
    "quality.evaluation.create": "approval_gated_future",
}

ACTIVE_AGENT_CAPABILITIES = {"agent.propose", "agent.handoff", "agent.explain", "agent.navigate"}
INACTIVE_EXECUTOR_CAPABILITIES = {
    "executor.dry_run",
    "executor.user_confirmed_execute",
    "executor.approval_gated_execute",
    "executor.admin_override",
}

HIGH_RISK_FLAGS = {
    "requires_approval",
    "high_risk",
    "external_side_effect",
    "connector_mutation",
    "publish_workflow",
    "context_mutation",
    "business_event_emit",
    "artifact_write",
    "quality_score_mutation",
}

SENSITIVE_KEYS = {
    "authorization",
    "bearer",
    "capability_token",
    "subscription_token",
    "secret",
    "api_key",
    "apikey",
    "raw prompt",
    "raw_prompt",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "upstream signed url",
    "upstream_signed_url",
}

SENSITIVE_TEXT = (
    "authorization:",
    "bearer ",
    "capability_token",
    "subscription_token",
    "raw prompt",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "upstream signed url",
    "sk-",
    "api_key=",
    "secret=",
)


class ExecutorSafetyError(ValueError):
    """Stable V5.4A safety-gate denial."""

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
class PolicyMatrixItem:
    """One executor candidate operation policy classification."""

    operation: str
    classification: str
    agent_executable: bool
    requires_user_confirmation: bool
    requires_approval_gate: bool
    runtime_execution_allowed: bool
    owner_stage: str = "V5-4A"

    def to_dict(self) -> dict[str, Any]:
        """Return policy matrix item DTO."""
        return asdict(self)


@dataclass(frozen=True)
class RequestedAction:
    """Action candidate submitted to the V5.4A safety gate."""

    operation: str
    source: str
    actor_type: str
    target_refs: dict[str, str]
    user_confirmed: bool
    risk_flags: tuple[str, ...] = ()
    capability_refs: tuple[str, ...] = ()
    payload_refs: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ApprovalGatePlan:
    """Future approval gate descriptor; V5.4A does not create approvals."""

    approval_required: bool
    approval_policy_id: str
    risk_flags: tuple[str, ...]
    human_approver_ref: str
    approval_evidence_ref: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return approval gate DTO."""
        data = asdict(self)
        data["risk_flags"] = list(self.risk_flags)
        return mask_value(data)


@dataclass(frozen=True)
class CapabilityDecision:
    """Read-only safety decision for an action candidate."""

    decision_id: str
    operation: str
    classification: str
    source: str
    actor_type: str
    policy_decision: str
    capability_decision: str
    allowed: bool
    agent_executable: bool
    requires_user_confirmation: bool
    requires_approval: bool
    runtime_execution_allowed: bool
    reason: str
    risk_flags: tuple[str, ...]
    target_refs: dict[str, str]
    request_id: str
    correlation_id: str
    redaction_status: str
    created_at: str = field(default_factory=lambda: _now())
    allowed_actions: tuple[str, ...] = ("open_handoff", "record_evidence")
    approval_gate: ApprovalGatePlan | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return redacted decision DTO."""
        data = asdict(self)
        data["risk_flags"] = list(self.risk_flags)
        data["allowed_actions"] = list(self.allowed_actions)
        if self.approval_gate is not None:
            data["approval_gate"] = self.approval_gate.to_dict()
        return mask_value(data)


@dataclass(frozen=True)
class RuntimeEvidenceContract:
    """Future runtime evidence schema descriptor for executor trials."""

    evidence_schema_id: str
    required_fields: tuple[str, ...]
    readonly: bool = True
    runtime_execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return evidence schema DTO."""
        data = asdict(self)
        data["required_fields"] = list(self.required_fields)
        return data


class ExecutorPolicyMatrix:
    """Policy matrix for V5.4A executor candidate operations."""

    def __init__(self, matrix: Mapping[str, str] | None = None) -> None:
        self._matrix = dict(matrix or CANDIDATE_POLICY_MATRIX)
        self._validate()

    def items(self) -> list[PolicyMatrixItem]:
        """Return all policy matrix items."""
        return [self.item_for(operation) for operation in sorted(self._matrix)]

    def item_for(self, operation: str) -> PolicyMatrixItem:
        """Return policy matrix item for one operation."""
        classification = self._matrix.get(operation)
        if classification is None:
            raise ExecutorSafetyError("EXECUTOR_POLICY_UNKNOWN_OPERATION", "Operation is not in the executor safety matrix.", reason="unknown_operation", resource=operation)
        return PolicyMatrixItem(
            operation=operation,
            classification=classification,
            agent_executable=False,
            requires_user_confirmation=classification in {"user_confirmed_only", "approval_gated_future"},
            requires_approval_gate=classification == "approval_gated_future",
            runtime_execution_allowed=False,
        )

    def _validate(self) -> None:
        missing = set(CANDIDATE_POLICY_MATRIX) - set(self._matrix)
        if missing:
            raise ExecutorSafetyError("EXECUTOR_POLICY_MATRIX_INVALID", "Every candidate operation must have a classification.", reason="missing_operation", resource=sorted(missing)[0])
        for operation, classification in self._matrix.items():
            if classification not in CLASSIFICATIONS:
                raise ExecutorSafetyError("EXECUTOR_POLICY_MATRIX_INVALID", "Policy classification is invalid.", reason="invalid_classification", resource=operation)


class ExecutorSandboxBoundary:
    """Validate that safety-gate inputs contain only redacted references."""

    def validate(self, action: RequestedAction) -> None:
        """Reject raw payload, token, secret, or direct runtime-store write refs."""
        _reject_sensitive_mapping(action.target_refs, resource="target_refs")
        _reject_sensitive_mapping(action.payload_refs, resource="payload_refs")
        lowered_operation = action.operation.lower()
        if "workflowstore" in lowered_operation or "workflowdraft.write" in lowered_operation or "workflowversion.write" in lowered_operation or "stationrun.write" in lowered_operation:
            raise ExecutorSafetyError("EXECUTOR_SANDBOX_DENIED", "Direct runtime truth writes are not allowed.", reason="direct_runtime_truth_write", resource=action.operation)


class ApprovalGatePlanner:
    """Plan future approval gates without creating approval requests."""

    def plan(self, context: IdentityContext, action: RequestedAction, item: PolicyMatrixItem) -> ApprovalGatePlan | None:
        """Return an approval gate plan when policy or risk requires it."""
        risk_flags = tuple(sorted(set(action.risk_flags) | set(_operation_risk_flags(action.operation))))
        approval_required = item.requires_approval_gate or bool(set(risk_flags) & HIGH_RISK_FLAGS)
        if not approval_required:
            return None
        return ApprovalGatePlan(
            approval_required=True,
            approval_policy_id=f"approval_policy_v5_4a_{action.operation.replace('.', '_')}",
            risk_flags=risk_flags,
            human_approver_ref=f"human://{context.tenant_id}/{context.workspace_id}/approver",
            approval_evidence_ref=f"evidence://{context.correlation_id}/approval-gate/{uuid4().hex}",
        )


class KillSwitchRegistry:
    """In-memory kill switch and capability revocation registry."""

    def __init__(self) -> None:
        self.disabled_agents: set[str] = set()
        self.disabled_workspaces: set[str] = set()
        self.revoked_capabilities: set[str] = set()

    def disable_agent(self, agent_id: str) -> None:
        """Disable one Agent identity for future executor trials."""
        self.disabled_agents.add(agent_id)

    def disable_workspace(self, workspace_id: str) -> None:
        """Disable future executor trials in one workspace."""
        self.disabled_workspaces.add(workspace_id)

    def revoke_capability(self, capability_ref: str) -> None:
        """Revoke one capability reference."""
        self.revoked_capabilities.add(capability_ref)

    def denial_reason(self, context: IdentityContext, action: RequestedAction) -> str | None:
        """Return kill-switch denial reason, if any."""
        if context.agent_id and context.agent_id in self.disabled_agents:
            return "agent_kill_switch_active"
        if context.workspace_id in self.disabled_workspaces:
            return "workspace_kill_switch_active"
        if set(action.capability_refs) & self.revoked_capabilities:
            return "capability_revoked"
        return None


class CapabilityDecisionService:
    """Evaluate V5.4A safety decisions without executing actions."""

    def __init__(
        self,
        *,
        policy_matrix: ExecutorPolicyMatrix | None = None,
        sandbox: ExecutorSandboxBoundary | None = None,
        approval_planner: ApprovalGatePlanner | None = None,
        kill_switches: KillSwitchRegistry | None = None,
    ) -> None:
        self.policy_matrix = policy_matrix or ExecutorPolicyMatrix()
        self.sandbox = sandbox or ExecutorSandboxBoundary()
        self.approval_planner = approval_planner or ApprovalGatePlanner()
        self.kill_switches = kill_switches or KillSwitchRegistry()

    def evaluate(self, context: IdentityContext, action: RequestedAction) -> CapabilityDecision:
        """Return a redacted safety decision for an action candidate."""
        self.sandbox.validate(action)
        item = self.policy_matrix.item_for(action.operation)
        kill_reason = self.kill_switches.denial_reason(context, action)
        approval_gate = self.approval_planner.plan(context, action, item)
        risk_flags = tuple(sorted(set(action.risk_flags) | set(_operation_risk_flags(action.operation))))

        if kill_reason is not None:
            return self._decision(context, action, item, "deny", "deny", False, f"kill_switch:{kill_reason}", risk_flags, approval_gate)
        if action.source == "agent" or action.actor_type == "agent" or context.actor_type == "agent":
            if item.classification in {"user_confirmed_only", "approval_gated_future", "never_executor"}:
                return self._decision(context, action, item, "deny", "deny", False, "source_agent_cannot_execute_mutation", risk_flags, approval_gate)
        if item.classification == "never_executor":
            return self._decision(context, action, item, "deny", "deny", False, "never_executor", risk_flags, approval_gate)
        if item.classification == "approval_gated_future":
            return self._decision(context, action, item, "approval_required", "deny", False, "approval_gated_future_not_executable_in_v5_4a", risk_flags, approval_gate)
        if item.requires_user_confirmation and not action.user_confirmed:
            return self._decision(context, action, item, "deny", "deny", False, "missing_user_confirmation", risk_flags, approval_gate)

        return self._decision(context, action, item, "allow", "allow_for_handoff_only", True, "user_confirmed_handoff_allowed_no_runtime_execution", risk_flags, approval_gate)

    def evidence_contract(self) -> RuntimeEvidenceContract:
        """Return future runtime evidence schema descriptor."""
        return RuntimeEvidenceContract(
            evidence_schema_id="runtime_evidence_contract_v5_4a",
            required_fields=(
                "operation",
                "source",
                "actor_type",
                "user_confirmed",
                "capability_decision",
                "policy_decision",
                "risk_flags",
                "runtime_result_ref",
                "correlation_id",
                "redaction_status",
            ),
        )

    def _decision(
        self,
        context: IdentityContext,
        action: RequestedAction,
        item: PolicyMatrixItem,
        policy_decision: str,
        capability_decision: str,
        allowed: bool,
        reason: str,
        risk_flags: tuple[str, ...],
        approval_gate: ApprovalGatePlan | None,
    ) -> CapabilityDecision:
        return CapabilityDecision(
            decision_id=f"capability_decision_{uuid4().hex}",
            operation=action.operation,
            classification=item.classification,
            source=action.source,
            actor_type=action.actor_type,
            policy_decision=policy_decision,
            capability_decision=capability_decision,
            allowed=allowed,
            agent_executable=False,
            requires_user_confirmation=item.requires_user_confirmation,
            requires_approval=approval_gate is not None,
            runtime_execution_allowed=False,
            reason=reason,
            risk_flags=risk_flags,
            target_refs=dict(action.target_refs),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            redaction_status="redacted",
            approval_gate=approval_gate,
        )


def _operation_risk_flags(operation: str) -> tuple[str, ...]:
    return {
        "workflow.template.publish": ("publish_workflow", "requires_approval"),
        "context.update": ("context_mutation", "requires_approval"),
        "business.event.emit": ("business_event_emit", "external_side_effect", "requires_approval"),
        "connector.call": ("connector_mutation", "external_side_effect", "requires_approval"),
        "external_llm.call": ("external_side_effect", "requires_approval"),
        "artifact.write": ("artifact_write", "requires_approval"),
        "quality.evaluation.create": ("quality_score_mutation", "requires_approval"),
    }.get(operation, ())


def _reject_sensitive_mapping(data: Mapping[str, Any], *, resource: str) -> None:
    for key, value in data.items():
        lowered_key = str(key).strip().lower()
        normalized_key = lowered_key.replace("-", "_")
        if lowered_key in SENSITIVE_KEYS or normalized_key in SENSITIVE_KEYS or "token" in lowered_key or "secret" in lowered_key or "raw_" in lowered_key:
            raise ExecutorSafetyError("EXECUTOR_SANDBOX_DENIED", "Sensitive fields are not allowed in executor safety inputs.", reason="sensitive_field", resource=f"{resource}.{key}")
        if lowered_key in {"workflow_store_write", "workflowdraft_write", "workflowversion_write", "stationrun_write", "direct_workflowstore_write"}:
            raise ExecutorSafetyError("EXECUTOR_SANDBOX_DENIED", "Direct runtime truth writes are not allowed.", reason="direct_runtime_truth_write", resource=f"{resource}.{key}")
        if isinstance(value, Mapping):
            _reject_sensitive_mapping(value, resource=f"{resource}.{key}")
        elif isinstance(value, str):
            lowered_value = value.lower()
            if any(token in lowered_value for token in SENSITIVE_TEXT):
                raise ExecutorSafetyError("EXECUTOR_SANDBOX_DENIED", "Sensitive values are not allowed in executor safety inputs.", reason="sensitive_value", resource=f"{resource}.{key}")
            if "workflowstore.write" in lowered_value or "workflowdraft.write" in lowered_value or "workflowversion.write" in lowered_value or "stationrun.write" in lowered_value:
                raise ExecutorSafetyError("EXECUTOR_SANDBOX_DENIED", "Direct runtime truth writes are not allowed.", reason="direct_runtime_truth_write", resource=f"{resource}.{key}")
        elif isinstance(value, list | tuple):
            for index, item in enumerate(value):
                if isinstance(item, Mapping):
                    _reject_sensitive_mapping(item, resource=f"{resource}.{key}[{index}]")


def _now() -> str:
    return datetime.now(UTC).isoformat()
