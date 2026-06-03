"""V6.2 production pilot credential/provider lifecycle helpers.

This module adds an operation-bound credential lease layer on top of the V5.2
credential provider registry. It does not implement a production secret store,
external app onboarding, Agent executor authority, or unrestricted provider
invocation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from core.auth.credential_provider import CredentialProviderError, CredentialProviderRegistry
from core.auth.tenant_boundary import IdentityContext


@dataclass(frozen=True)
class CredentialLease:
    """Tenant/app/audience/operation-bound credential lease."""

    credential_lease_id: str
    credential_ref_id: str
    provider_profile_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    audience: str
    operation: str
    capability_ref: str
    model_ref: str
    issued_at: str
    expires_at: str
    lease_status: str
    request_id: str
    correlation_id: str
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["secret_configured"] = False
        return data


@dataclass(frozen=True)
class V6ProviderInvocationEvidence:
    """V6.2 provider invocation evidence with lease refs."""

    provider_invocation_evidence_id: str
    provider_profile_id: str
    credential_ref_id: str
    credential_lease_id: str
    provider: str
    model_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    audience: str
    operation: str
    capability_ref: str
    provider_config_source: str
    input_artifact_refs: tuple[str, ...]
    output_artifact_refs: tuple[str, ...]
    prompt_template_ref: str
    redacted_input_summary_ref: str
    redacted_output_summary_ref: str
    policy_decision: str
    credential_decision: str
    lease_decision: str
    runtime_result_ref: str
    request_id: str
    correlation_id: str
    redaction_status: str
    created_by: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["input_artifact_refs"] = list(self.input_artifact_refs)
        data["output_artifact_refs"] = list(self.output_artifact_refs)
        return data


class ProductionCredentialProviderLifecycle:
    """V6.2 in-memory lifecycle for pilot validation."""

    def __init__(self, registry: CredentialProviderRegistry | None = None) -> None:
        self.registry = registry or CredentialProviderRegistry()
        self.leases: dict[str, CredentialLease] = {}
        self.invocations: list[V6ProviderInvocationEvidence] = []

    def issue_lease(
        self,
        context: IdentityContext,
        *,
        provider_profile_id: str,
        audience: str,
        operation: str,
        capability_ref: str,
        model_ref: str,
        expires_at: str,
    ) -> CredentialLease:
        """Issue a V6.2 credential lease bound to identity, audience, and operation."""
        profile = self.registry.provider_profiles[provider_profile_id]
        credential = self.registry.credentials[profile.credential_ref_id]
        _require_profile_scope(context, profile)
        if credential.status != "active":
            raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Credential is not active.", reason="credential_not_active")
        if capability_ref not in profile.capability_refs:
            raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Capability is outside provider profile.", reason="capability_not_allowed")
        if model_ref not in profile.model_refs:
            raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Model is outside provider profile.", reason="model_not_allowed")
        lease = CredentialLease(
            credential_lease_id=f"credential_lease_{uuid4().hex}",
            credential_ref_id=credential.credential_ref_id,
            provider_profile_id=profile.provider_profile_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            audience=_required_text(audience, "audience"),
            operation=_required_text(operation, "operation"),
            capability_ref=capability_ref,
            model_ref=model_ref,
            issued_at=datetime.now(UTC).isoformat(),
            expires_at=_required_text(expires_at, "expires_at"),
            lease_status="active",
            request_id=context.request_id,
            correlation_id=context.correlation_id,
        )
        self.leases[lease.credential_lease_id] = lease
        return lease

    def validate_provider_invocation(
        self,
        context: IdentityContext,
        *,
        credential_lease_id: str,
        audience: str,
        operation: str,
        capability_ref: str,
        model_ref: str,
        provider_config_source: str,
        input_artifact_refs: list[str],
        output_artifact_refs: list[str],
        prompt_template_ref: str,
        redacted_input_summary_ref: str,
        redacted_output_summary_ref: str,
        runtime_result_ref: str,
    ) -> V6ProviderInvocationEvidence:
        """Validate a lease-bound provider invocation and record redacted evidence."""
        lease = self._get_lease(credential_lease_id)
        profile = self.registry.provider_profiles[lease.provider_profile_id]
        credential = self.registry.credentials[lease.credential_ref_id]
        _require_lease_scope(context, lease)
        _require_not_expired(lease)
        if lease.lease_status != "active":
            raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Credential lease is not active.", reason="lease_not_active")
        if credential.status != "active":
            raise CredentialProviderError("PROVIDER_CAPABILITY_DENIED", "Credential is not active.", reason="credential_not_active")
        if audience != lease.audience:
            raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Invocation audience does not match lease.", reason="audience_mismatch")
        if operation != lease.operation:
            raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Invocation operation does not match lease.", reason="operation_mismatch")
        if capability_ref != lease.capability_ref or capability_ref not in profile.capability_refs:
            raise CredentialProviderError("PROVIDER_CAPABILITY_DENIED", "Capability is not allowed.", reason="capability_not_allowed")
        if model_ref != lease.model_ref or model_ref not in profile.model_refs:
            raise CredentialProviderError("PROVIDER_CAPABILITY_DENIED", "Model is not allowed.", reason="model_not_allowed")
        _reject_raw_ref(provider_config_source, "provider_config_source")
        _reject_raw_ref(prompt_template_ref, "prompt_template_ref")
        _reject_raw_ref(redacted_input_summary_ref, "redacted_input_summary_ref")
        _reject_raw_ref(redacted_output_summary_ref, "redacted_output_summary_ref")
        evidence = V6ProviderInvocationEvidence(
            provider_invocation_evidence_id=f"provider_invocation_{uuid4().hex}",
            provider_profile_id=profile.provider_profile_id,
            credential_ref_id=credential.credential_ref_id,
            credential_lease_id=lease.credential_lease_id,
            provider=profile.provider,
            model_ref=model_ref,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            audience=audience,
            operation=operation,
            capability_ref=capability_ref,
            provider_config_source=provider_config_source,
            input_artifact_refs=tuple(input_artifact_refs),
            output_artifact_refs=tuple(output_artifact_refs),
            prompt_template_ref=prompt_template_ref,
            redacted_input_summary_ref=redacted_input_summary_ref,
            redacted_output_summary_ref=redacted_output_summary_ref,
            policy_decision="allow",
            credential_decision="allow",
            lease_decision="allow",
            runtime_result_ref=runtime_result_ref,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            redaction_status="redacted",
            created_by=context.actor_id,
        )
        self.invocations.append(evidence)
        return evidence

    def _get_lease(self, credential_lease_id: str) -> CredentialLease:
        try:
            return self.leases[credential_lease_id]
        except KeyError as exc:
            raise CredentialProviderError("CREDENTIAL_LEASE_NOT_FOUND", "Credential lease was not found.", reason="lease_not_found") from exc


def _require_profile_scope(context: IdentityContext, profile: Any) -> None:
    if profile.tenant_id != context.tenant_id:
        raise CredentialProviderError("CREDENTIAL_SCOPE_DENIED", "Provider profile tenant mismatch.", reason="tenant_mismatch")
    if profile.workspace_id != context.workspace_id:
        raise CredentialProviderError("CREDENTIAL_SCOPE_DENIED", "Provider profile workspace mismatch.", reason="workspace_mismatch")
    if profile.project_id != context.project_id:
        raise CredentialProviderError("CREDENTIAL_SCOPE_DENIED", "Provider profile project mismatch.", reason="project_mismatch")
    if profile.app_id != context.app_id:
        raise CredentialProviderError("CREDENTIAL_SCOPE_DENIED", "Provider profile app mismatch.", reason="app_mismatch")


def _require_lease_scope(context: IdentityContext, lease: CredentialLease) -> None:
    if lease.tenant_id != context.tenant_id:
        raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Lease tenant mismatch.", reason="tenant_mismatch")
    if lease.workspace_id != context.workspace_id:
        raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Lease workspace mismatch.", reason="workspace_mismatch")
    if lease.project_id != context.project_id:
        raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Lease project mismatch.", reason="project_mismatch")
    if lease.app_id != context.app_id:
        raise CredentialProviderError("CREDENTIAL_LEASE_DENIED", "Lease app mismatch.", reason="app_mismatch")


def _require_not_expired(lease: CredentialLease) -> None:
    expires_at = datetime.fromisoformat(lease.expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= datetime.now(UTC):
        raise CredentialProviderError("CREDENTIAL_LEASE_EXPIRED", "Credential lease has expired.", reason="lease_expired")


def _required_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CredentialProviderError("CREDENTIAL_LEASE_INVALID", f"{field} is required.", reason=f"missing_{field}")
    return value.strip()


def _reject_raw_ref(value: str, field: str) -> None:
    lowered = _required_text(value, field).lower()
    if "raw" in lowered or "prompt:" in lowered or "secret" in lowered or "bearer" in lowered or "authorization" in lowered or "sk-" in lowered:
        raise CredentialProviderError("PROVIDER_EVIDENCE_REDACTION_DENIED", f"{field} must be a redacted reference.", reason=f"{field}_raw_ref_denied")
