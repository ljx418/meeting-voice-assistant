"""V6.1 production pilot identity and tenant boundary helpers.

This module extends the V5.1 tenant guard with V6.1 review-scoped evidence:
staging IdP status, service-account scope audit, and workflow-head identity
projection. It does not implement enterprise auth, tenant admin routes, or
runtime mutation authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from core.auth.tenant_boundary import (
    IdentityContext,
    ResourceRef,
    TenantBoundaryError,
    build_denial_audit_event,
    resolve_identity_context,
    validate_resource_access,
)


DEFAULT_WORKFLOW_HEADS = (
    "mission_console",
    "workflow_blueprint",
    "runtime_report",
    "review_console",
    "evidence_chain",
    "workflow_spec_registry",
)


@dataclass(frozen=True)
class StagingIdentityProviderStatus:
    """Review-scoped identity provider status for V6.1."""

    provider: str
    status: str
    evidence_scope: str
    issuer_ref: str | None = None
    client_ref: str | None = None
    enterprise_auth_ready: bool = False

    def to_audit_fields(self) -> dict[str, Any]:
        return {
            "identity_provider": self.provider,
            "identity_provider_status": self.status,
            "identity_provider_evidence_scope": self.evidence_scope,
            "identity_provider_issuer_ref": self.issuer_ref,
            "identity_provider_client_ref": self.client_ref,
            "enterprise_auth_ready": self.enterprise_auth_ready,
        }


@dataclass(frozen=True)
class ServiceAccountScope:
    """Tenant-bound service account operation scope."""

    service_account_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    allowed_operations: tuple[str, ...]
    audit_ref: str

    def scope_key(self) -> tuple[str, str, str, str]:
        return (self.tenant_id, self.workspace_id, self.project_id, self.app_id)


def resolve_staging_identity_provider_status(env: Mapping[str, Any] | None = None) -> StagingIdentityProviderStatus:
    """Resolve V6.1 staging IdP status without reading secrets."""
    env = env or {}
    issuer = _optional_text(env.get("V6_1_OIDC_ISSUER"))
    client_id = _optional_text(env.get("V6_1_OIDC_CLIENT_ID"))
    provider = _optional_text(env.get("V6_1_IDENTITY_PROVIDER")) or "staging_oidc"
    if issuer and client_id:
        return StagingIdentityProviderStatus(
            provider=provider,
            status="staging_real",
            evidence_scope="staging_oidc_configured",
            issuer_ref=_redacted_ref("issuer", issuer),
            client_ref=_redacted_ref("client", client_id),
            enterprise_auth_ready=False,
        )
    return StagingIdentityProviderStatus(
        provider=provider,
        status="staging_only",
        evidence_scope="staging_fixture",
        enterprise_auth_ready=False,
    )


def validate_service_account_scope(context: IdentityContext, scope: ServiceAccountScope | None, *, operation: str) -> dict[str, Any]:
    """Validate service-account binding and operation scope."""
    if context.actor_type != "service_account":
        return {"service_account_scope_decision": "not_applicable"}
    if scope is None:
        raise TenantBoundaryError(
            "SERVICE_ACCOUNT_SCOPE_DENIED",
            "Service account requires an explicit V6.1 scope binding.",
            reason="missing_service_account_scope",
        )
    if context.service_account_id != scope.service_account_id:
        raise TenantBoundaryError(
            "SERVICE_ACCOUNT_SCOPE_DENIED",
            "Service account binding does not match actor.",
            reason="service_account_binding_mismatch",
        )
    if context.scope_key() != scope.scope_key():
        raise TenantBoundaryError(
            "SERVICE_ACCOUNT_SCOPE_DENIED",
            "Service account scope does not match identity context.",
            reason="service_account_scope_mismatch",
        )
    if operation not in scope.allowed_operations:
        raise TenantBoundaryError(
            "SERVICE_ACCOUNT_OPERATION_DENIED",
            "Service account operation is outside its allowed scope.",
            reason="service_account_operation_denied",
        )
    return {
        "service_account_scope_decision": "allow",
        "service_account_audit_ref": scope.audit_ref,
        "service_account_allowed_operations": list(scope.allowed_operations),
    }


def project_identity_to_workflow_heads(
    context: IdentityContext,
    provider_status: StagingIdentityProviderStatus,
    *,
    heads: Sequence[str] = DEFAULT_WORKFLOW_HEADS,
) -> dict[str, dict[str, Any]]:
    """Project identity source refs to shared V6 workflow heads."""
    refs: dict[str, dict[str, Any]] = {}
    for head in heads:
        refs[head] = {
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
            "request_id": context.request_id,
            "correlation_id": context.correlation_id,
            "identity_provider_status": provider_status.status,
            "source_ref": f"identity://{context.tenant_id}/{context.workspace_id}/{context.project_id}/{context.app_id}/{context.actor_id}",
        }
    return refs


def validate_v6_1_identity_tenant_access(
    server_context: Mapping[str, Any],
    resource: ResourceRef,
    *,
    operation: str,
    source: str = "user",
    user_confirmed: bool = False,
    client_selectors: Mapping[str, Any] | None = None,
    service_account_scope: ServiceAccountScope | None = None,
    identity_provider_env: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate one V6.1 identity/tenant access decision and return evidence."""
    context = resolve_identity_context(server_context, client_selectors)
    provider_status = resolve_staging_identity_provider_status(identity_provider_env)
    service_scope = validate_service_account_scope(context, service_account_scope, operation=operation)
    audit = validate_resource_access(
        context,
        resource,
        operation=operation,
        source=source,
        user_confirmed=user_confirmed,
    )
    audit.update(provider_status.to_audit_fields())
    audit.update(service_scope)
    audit["workflow_head_refs"] = project_identity_to_workflow_heads(context, provider_status)
    audit["metadata"] = {**audit.get("metadata", {}), "v6_1_metadata_ref": _safe_metadata_ref(metadata or {})}
    audit["v6_stage"] = "V6-1"
    audit["claim_scope"] = "production_identity_tenant_boundary_pilot_slice_ready_for_review"
    return audit


def build_v6_1_denial_evidence(
    server_context: Mapping[str, Any],
    resource: ResourceRef,
    *,
    operation: str,
    error: TenantBoundaryError,
    identity_provider_env: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build V6.1 redacted evidence for a denial."""
    context = resolve_identity_context(server_context)
    provider_status = resolve_staging_identity_provider_status(identity_provider_env)
    audit = build_denial_audit_event(context, operation=operation, target=resource, error=error)
    audit.update(provider_status.to_audit_fields())
    audit["workflow_head_refs"] = project_identity_to_workflow_heads(context, provider_status)
    audit["v6_stage"] = "V6-1"
    audit["claim_scope"] = "production_identity_tenant_boundary_pilot_slice_ready_for_review"
    return audit


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _redacted_ref(kind: str, value: str) -> str:
    return f"{kind}_ref:{len(value)}:{value[:2]}***"


def _safe_metadata_ref(metadata: Mapping[str, Any]) -> str:
    if not metadata:
        return "metadata://empty"
    keys = sorted(str(key) for key in metadata.keys())
    return "metadata://keys/" + ",".join(keys)
