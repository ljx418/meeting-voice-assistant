"""V5.1 tenant boundary primitives.

This module implements the production auth / tenant boundary slice without
adding OAuth, SSO, tenant admin routes, or Agent executor authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Mapping
from uuid import uuid4


SENSITIVE_KEYS = {
    "capability_token",
    "subscription_token",
    "authorization",
    "bearer",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed url",
}

DURABLE_MUTATIONS = {
    "workflow.patch.apply",
    "workflow.template.publish",
    "workflow.instance.start",
    "station.rerun",
    "approval.respond",
    "context.update",
    "business.event.emit",
}


class TenantBoundaryError(ValueError):
    """Stable tenant-boundary denial."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        """Return a redacted API-compatible error shape."""
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class IdentityContext:
    """Server-bound identity context for production route guards."""

    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    actor_type: str
    actor_id: str
    request_id: str
    correlation_id: str
    user_id: str | None = None
    service_account_id: str | None = None
    agent_id: str | None = None
    session_id: str | None = None

    def scope_key(self) -> tuple[str, str, str, str]:
        """Return the tenant/workspace/project/app scope tuple."""
        return (self.tenant_id, self.workspace_id, self.project_id, self.app_id)


@dataclass(frozen=True)
class ResourceRef:
    """Tenant-bound target resource reference."""

    resource_type: str
    resource_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    owner_ref: str
    workflow_instance_id: str | None = None
    agent_session_id: str | None = None

    def scope_key(self) -> tuple[str, str, str, str]:
        """Return the tenant/workspace/project/app scope tuple."""
        return (self.tenant_id, self.workspace_id, self.project_id, self.app_id)


def resolve_identity_context(server_context: Mapping[str, Any], client_selectors: Mapping[str, Any] | None = None) -> IdentityContext:
    """Resolve a server-bound identity context and reject client conflicts."""
    client_selectors = client_selectors or {}
    required = ("tenant_id", "workspace_id", "project_id", "app_id", "actor_type", "actor_id", "request_id", "correlation_id")
    values = {key: _required_text(server_context, key) for key in required}
    for key in ("tenant_id", "workspace_id", "project_id", "app_id", "actor_id"):
        requested = _optional_text(client_selectors.get(key))
        if requested is not None and requested != values[key]:
            raise TenantBoundaryError(_scope_error_code(key), "Client selector does not match server-bound identity.", reason=f"{key}_mismatch", resource=key)

    actor_type = values["actor_type"]
    user_id = _optional_text(server_context.get("user_id"))
    service_account_id = _optional_text(server_context.get("service_account_id"))
    agent_id = _optional_text(server_context.get("agent_id"))
    session_id = _optional_text(server_context.get("session_id"))
    if actor_type == "human_user" and user_id is None:
        raise TenantBoundaryError("ACTOR_BINDING_DENIED", "Human actor requires user_id.", reason="missing_user_id")
    if actor_type == "service_account" and service_account_id is None:
        raise TenantBoundaryError("SERVICE_ACCOUNT_SCOPE_DENIED", "Service account actor requires service_account_id.", reason="missing_service_account_id")
    if actor_type == "agent" and (agent_id is None or session_id is None):
        raise TenantBoundaryError("ACTOR_BINDING_DENIED", "Agent actor requires agent_id and session_id.", reason="missing_agent_binding")
    if actor_type not in {"human_user", "service_account", "agent", "system_service"}:
        raise TenantBoundaryError("ACTOR_BINDING_DENIED", "Actor type is not supported.", reason="unsupported_actor_type")

    return IdentityContext(
        tenant_id=values["tenant_id"],
        workspace_id=values["workspace_id"],
        project_id=values["project_id"],
        app_id=values["app_id"],
        actor_type=actor_type,
        actor_id=values["actor_id"],
        request_id=values["request_id"],
        correlation_id=values["correlation_id"],
        user_id=user_id,
        service_account_id=service_account_id,
        agent_id=agent_id,
        session_id=session_id,
    )


def validate_resource_access(
    context: IdentityContext,
    resource: ResourceRef,
    *,
    operation: str,
    source: str = "user",
    user_confirmed: bool = False,
) -> dict[str, Any]:
    """Validate scope and operation policy for one target resource."""
    if resource.tenant_id != context.tenant_id:
        raise TenantBoundaryError("TENANT_SCOPE_DENIED", "Resource tenant does not match actor tenant.", reason="tenant_mismatch", resource=resource.resource_type)
    if resource.workspace_id != context.workspace_id:
        raise TenantBoundaryError("WORKSPACE_SCOPE_DENIED", "Resource workspace does not match actor workspace.", reason="workspace_mismatch", resource=resource.resource_type)
    if resource.project_id != context.project_id:
        raise TenantBoundaryError("PROJECT_SCOPE_DENIED", "Resource project does not match actor project.", reason="project_mismatch", resource=resource.resource_type)
    if resource.app_id != context.app_id:
        raise TenantBoundaryError("APP_SCOPE_DENIED", "Resource app does not match actor app.", reason="app_mismatch", resource=resource.resource_type)
    if context.actor_type == "agent" and resource.agent_session_id is not None and resource.agent_session_id != context.session_id:
        raise TenantBoundaryError("ACTOR_BINDING_DENIED", "Agent session does not match target resource.", reason="agent_session_mismatch", resource=resource.resource_type)
    if context.actor_type == "agent" and source == "agent" and operation in DURABLE_MUTATIONS:
        raise TenantBoundaryError("AGENT_EXECUTION_DENIED", "Agent source cannot execute durable mutation.", reason="agent_mutation_denied", resource=resource.resource_type)
    if operation in DURABLE_MUTATIONS and not user_confirmed:
        raise TenantBoundaryError("USER_CONFIRMATION_REQUIRED", "Durable mutation requires user_confirmed=true.", reason="missing_user_confirmation", resource=resource.resource_type)
    return build_audit_event(
        context,
        operation=operation,
        target=resource,
        policy_decision="allow",
        scope_decision="allow",
        risk_flags=[],
    )


def build_denial_audit_event(context: IdentityContext, *, operation: str, target: ResourceRef, error: TenantBoundaryError) -> dict[str, Any]:
    """Build a redacted audit event for a denied boundary decision."""
    return build_audit_event(
        context,
        operation=operation,
        target=target,
        policy_decision="deny",
        scope_decision="deny",
        risk_flags=[error.reason],
        denial_reason=error.reason,
    )


def build_audit_event(
    context: IdentityContext,
    *,
    operation: str,
    target: ResourceRef,
    policy_decision: str,
    scope_decision: str,
    risk_flags: list[str],
    denial_reason: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the V5.1 tenant-bound audit event shape."""
    event = {
        "audit_event_id": f"audit_{uuid4().hex}",
        "created_at": datetime.now(UTC).isoformat(),
        "request_id": context.request_id,
        "correlation_id": context.correlation_id,
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "project_id": context.project_id,
        "app_id": context.app_id,
        "actor_type": context.actor_type,
        "actor_id": context.actor_id,
        "user_id": context.user_id,
        "service_account_id": context.service_account_id,
        "agent_id": context.agent_id,
        "session_id": context.session_id,
        "operation": operation,
        "target_resource_type": target.resource_type,
        "target_resource_id": target.resource_id,
        "workflow_instance_id": target.workflow_instance_id,
        "policy_decision": policy_decision,
        "scope_decision": scope_decision,
        "risk_flags": list(risk_flags),
        "denial_reason": denial_reason,
        "redaction_status": "redacted",
        "evidence_ref": f"evidence://{context.correlation_id}/{target.resource_type}/{target.resource_id}",
        "metadata": _redact_mapping(metadata or {}),
    }
    return {key: value for key, value in event.items() if value is not None}


def _required_text(data: Mapping[str, Any], key: str) -> str:
    value = _optional_text(data.get(key))
    if value is None:
        raise TenantBoundaryError("AUDIT_CONTEXT_REQUIRED", f"{key} is required.", reason=f"missing_{key}", resource=key)
    return value


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TenantBoundaryError("AUDIT_CONTEXT_REQUIRED", "Identity and scope values must be strings.", reason="invalid_text_value")
    stripped = value.strip()
    return stripped or None


def _scope_error_code(key: str) -> str:
    return {
        "tenant_id": "TENANT_SCOPE_DENIED",
        "workspace_id": "WORKSPACE_SCOPE_DENIED",
        "project_id": "PROJECT_SCOPE_DENIED",
        "app_id": "APP_SCOPE_DENIED",
    }.get(key, "ACTOR_BINDING_DENIED")


def _redact_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in data.items():
        lowered = str(key).lower()
        if lowered in SENSITIVE_KEYS or "token" in lowered or "secret" in lowered:
            redacted[str(key)] = "[REDACTED]"
        elif isinstance(value, Mapping):
            redacted[str(key)] = _redact_mapping(value)
        else:
            redacted[str(key)] = value
    return redacted
