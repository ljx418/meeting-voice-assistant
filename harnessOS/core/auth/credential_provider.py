"""V5.2 credential and provider lifecycle primitives.

This module implements a core credential/provider lifecycle slice. It does not
add production auth, external app onboarding, Agent executor authority, or BFF
routes.
"""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from dotenv import dotenv_values

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext, TenantBoundaryError


REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "capability_token",
    "subscription_token",
    "secret",
    "raw prompt",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "upstream signed url",
}

PROVIDER_PROFILE_FIELDS = {
    "provider_profile_id",
    "tenant_id",
    "workspace_id",
    "project_id",
    "app_id",
    "provider",
    "provider_kind",
    "base_url_ref",
    "model_refs",
    "credential_ref_id",
    "capability_refs",
    "status",
    "created_at",
    "created_by",
    "updated_at",
}

PROFILE_STATUSES = {"draft", "active", "suspended", "revoked", "rotation_required", "validation_failed"}
CREDENTIAL_STATUSES = {"active", "rotating", "revoked", "suspended", "expired"}
AGENT_DENIED_OPERATIONS = {
    "provider_profile.create",
    "provider_profile.update",
    "credential.issue",
    "credential.rotate",
    "credential.revoke",
    "credential.emergency_revoke",
    "provider.smoke.validate",
}


class CredentialProviderError(ValueError):
    """Stable credential/provider lifecycle denial."""

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
class ProviderProfile:
    """Tenant-bound provider profile metadata without raw credentials."""

    provider_profile_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    provider: str
    provider_kind: str
    base_url_ref: str
    model_refs: tuple[str, ...]
    credential_ref_id: str
    capability_refs: tuple[str, ...]
    status: str
    created_at: str
    created_by: str
    updated_at: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ProviderProfile":
        """Create a strict provider profile DTO."""
        _reject_unknown_and_forbidden(data, PROVIDER_PROFILE_FIELDS, "PROVIDER_PROFILE_INVALID")
        required = PROVIDER_PROFILE_FIELDS - {"created_at", "updated_at"}
        values = {key: _required_text(data, key, "PROVIDER_PROFILE_INVALID") for key in required if key not in {"model_refs", "capability_refs"}}
        model_refs = _required_str_tuple(data, "model_refs", "PROVIDER_PROFILE_INVALID")
        capability_refs = _required_str_tuple(data, "capability_refs", "PROVIDER_PROFILE_INVALID")
        status = values["status"]
        if status not in PROFILE_STATUSES:
            raise CredentialProviderError("PROVIDER_PROFILE_INVALID", "Provider profile status is invalid.", reason="invalid_status")
        created_at = _optional_text(data.get("created_at")) or _now()
        updated_at = _optional_text(data.get("updated_at")) or created_at
        return cls(
            provider_profile_id=values["provider_profile_id"],
            tenant_id=values["tenant_id"],
            workspace_id=values["workspace_id"],
            project_id=values["project_id"],
            app_id=values["app_id"],
            provider=values["provider"],
            provider_kind=values["provider_kind"],
            base_url_ref=values["base_url_ref"],
            model_refs=model_refs,
            credential_ref_id=values["credential_ref_id"],
            capability_refs=capability_refs,
            status=status,
            created_at=created_at,
            created_by=values["created_by"],
            updated_at=updated_at,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return redacted provider profile DTO."""
        data = asdict(self)
        data["model_refs"] = list(self.model_refs)
        data["capability_refs"] = list(self.capability_refs)
        data["redaction_status"] = "redacted"
        return data


@dataclass(frozen=True)
class CredentialReference:
    """Credential reference metadata; never contains the raw secret value."""

    credential_ref_id: str
    tenant_id: str
    workspace_id: str
    app_id: str
    provider_profile_id: str
    secret_ref: str
    status: str
    issued_at: str
    expires_at: str | None
    last_rotated_at: str | None
    revoked_at: str | None
    created_by: str

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted credential reference DTO."""
        data = asdict(self)
        data["secret_ref"] = _safe_secret_ref(self.secret_ref)
        data["secret_configured"] = bool(self.secret_ref)
        data["redaction_status"] = "redacted"
        return data


@dataclass(frozen=True)
class CredentialLifecycleEvent:
    """Auditable credential lifecycle event."""

    credential_event_id: str
    credential_ref_id: str
    provider_profile_id: str
    operation: str
    source: str
    actor_type: str
    actor_id: str
    user_confirmed: bool
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    policy_decision: str
    risk_flags: tuple[str, ...]
    previous_status: str | None
    next_status: str
    request_id: str
    correlation_id: str
    redaction_status: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted event DTO."""
        data = asdict(self)
        data["risk_flags"] = list(self.risk_flags)
        return data


@dataclass(frozen=True)
class ProviderInvocationEvidence:
    """Redacted provider invocation evidence."""

    provider_invocation_evidence_id: str
    provider_profile_id: str
    provider: str
    model_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    operation: str
    capability_ref: str
    input_artifact_refs: tuple[str, ...]
    output_artifact_refs: tuple[str, ...]
    prompt_template_ref: str
    redacted_input_summary_ref: str
    redacted_output_summary_ref: str
    policy_decision: str
    credential_decision: str
    runtime_result_ref: str
    request_id: str
    correlation_id: str
    redaction_status: str
    created_by: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted provider invocation evidence."""
        data = asdict(self)
        data["input_artifact_refs"] = list(self.input_artifact_refs)
        data["output_artifact_refs"] = list(self.output_artifact_refs)
        return mask_value(data)


class CredentialProviderRegistry:
    """In-memory V5.2 registry for focused dev/local validation."""

    def __init__(self) -> None:
        self.provider_profiles: dict[str, ProviderProfile] = {}
        self.credentials: dict[str, CredentialReference] = {}
        self.lifecycle_events: list[CredentialLifecycleEvent] = []
        self.invocation_evidence: list[ProviderInvocationEvidence] = []

    def create_provider_profile(
        self,
        context: IdentityContext,
        data: Mapping[str, Any],
        *,
        source: str,
        user_confirmed: bool,
    ) -> ProviderProfile:
        """Create a tenant-bound provider profile."""
        _guard_operation(context, "provider_profile.create", source=source, user_confirmed=user_confirmed)
        profile = ProviderProfile.from_mapping(data)
        _require_same_scope(context, profile)
        if profile.provider_profile_id in self.provider_profiles:
            raise CredentialProviderError("PROVIDER_PROFILE_INVALID", "Provider profile already exists.", reason="duplicate_profile")
        self.provider_profiles[profile.provider_profile_id] = profile
        return profile

    def issue_credential(
        self,
        context: IdentityContext,
        *,
        provider_profile_id: str,
        credential_ref_id: str,
        secret_ref: str,
        source: str,
        user_confirmed: bool,
        expires_at: str | None = None,
    ) -> tuple[CredentialReference, CredentialLifecycleEvent]:
        """Issue a redacted credential reference."""
        _guard_operation(context, "credential.issue", source=source, user_confirmed=user_confirmed)
        profile = self._get_profile(provider_profile_id)
        _require_same_scope(context, profile)
        _validate_secret_ref(secret_ref)
        if credential_ref_id in self.credentials:
            raise CredentialProviderError("CREDENTIAL_INVALID", "Credential reference already exists.", reason="duplicate_credential")
        credential = CredentialReference(
            credential_ref_id=credential_ref_id,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            app_id=context.app_id,
            provider_profile_id=provider_profile_id,
            secret_ref=secret_ref,
            status="active",
            issued_at=_now(),
            expires_at=expires_at,
            last_rotated_at=None,
            revoked_at=None,
            created_by=context.actor_id,
        )
        self.credentials[credential_ref_id] = credential
        event = self._record_lifecycle_event(context, credential, operation="credential.issue", source=source, user_confirmed=user_confirmed, previous_status=None)
        return credential, event

    def rotate_credential(
        self,
        context: IdentityContext,
        *,
        credential_ref_id: str,
        new_secret_ref: str,
        source: str,
        user_confirmed: bool,
    ) -> tuple[CredentialReference, CredentialLifecycleEvent]:
        """Rotate a credential reference without exposing raw secret."""
        _guard_operation(context, "credential.rotate", source=source, user_confirmed=user_confirmed)
        current = self._get_credential(credential_ref_id)
        _validate_secret_ref(new_secret_ref)
        profile = self._get_profile(current.provider_profile_id)
        _require_same_scope(context, profile)
        previous_status = current.status
        rotated = CredentialReference(
            credential_ref_id=current.credential_ref_id,
            tenant_id=current.tenant_id,
            workspace_id=current.workspace_id,
            app_id=current.app_id,
            provider_profile_id=current.provider_profile_id,
            secret_ref=new_secret_ref,
            status="active",
            issued_at=current.issued_at,
            expires_at=current.expires_at,
            last_rotated_at=_now(),
            revoked_at=None,
            created_by=current.created_by,
        )
        self.credentials[credential_ref_id] = rotated
        event = self._record_lifecycle_event(context, rotated, operation="credential.rotate.complete", source=source, user_confirmed=user_confirmed, previous_status=previous_status)
        return rotated, event

    def revoke_credential(
        self,
        context: IdentityContext,
        *,
        credential_ref_id: str,
        source: str,
        user_confirmed: bool,
        emergency: bool = False,
    ) -> tuple[CredentialReference, CredentialLifecycleEvent]:
        """Revoke a credential reference."""
        operation = "credential.emergency_revoke" if emergency else "credential.revoke"
        _guard_operation(context, operation, source=source, user_confirmed=user_confirmed)
        current = self._get_credential(credential_ref_id)
        profile = self._get_profile(current.provider_profile_id)
        _require_same_scope(context, profile)
        previous_status = current.status
        revoked = CredentialReference(
            credential_ref_id=current.credential_ref_id,
            tenant_id=current.tenant_id,
            workspace_id=current.workspace_id,
            app_id=current.app_id,
            provider_profile_id=current.provider_profile_id,
            secret_ref=current.secret_ref,
            status="revoked",
            issued_at=current.issued_at,
            expires_at=current.expires_at,
            last_rotated_at=current.last_rotated_at,
            revoked_at=_now(),
            created_by=current.created_by,
        )
        self.credentials[credential_ref_id] = revoked
        event = self._record_lifecycle_event(context, revoked, operation=operation, source=source, user_confirmed=user_confirmed, previous_status=previous_status)
        return revoked, event

    def validate_provider_smoke(
        self,
        context: IdentityContext,
        *,
        provider_profile_id: str,
        capability_ref: str,
        model_ref: str,
        input_artifact_refs: list[str],
        output_artifact_refs: list[str],
        prompt_template_ref: str,
        redacted_input_summary_ref: str,
        redacted_output_summary_ref: str,
        runtime_result_ref: str,
        source: str,
        user_confirmed: bool,
    ) -> ProviderInvocationEvidence:
        """Record redacted provider smoke validation evidence."""
        _guard_operation(context, "provider.smoke.validate", source=source, user_confirmed=user_confirmed)
        profile = self._get_profile(provider_profile_id)
        _require_same_scope(context, profile)
        if profile.status != "active":
            raise CredentialProviderError("PROVIDER_VALIDATION_FAILED", "Provider profile is not active.", reason="provider_not_active")
        credential = self._get_credential(profile.credential_ref_id)
        if credential.status != "active":
            raise CredentialProviderError("PROVIDER_CAPABILITY_DENIED", "Credential is not active.", reason="credential_not_active")
        if capability_ref not in profile.capability_refs:
            raise CredentialProviderError("PROVIDER_CAPABILITY_DENIED", "Capability is not allowed for provider profile.", reason="capability_not_allowed")
        if model_ref not in profile.model_refs:
            raise CredentialProviderError("PROVIDER_CAPABILITY_DENIED", "Model is not allowed for provider profile.", reason="model_not_allowed")
        evidence = ProviderInvocationEvidence(
            provider_invocation_evidence_id=f"provider_evidence_{uuid4().hex}",
            provider_profile_id=profile.provider_profile_id,
            provider=profile.provider,
            model_ref=model_ref,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            operation="provider.smoke.validate",
            capability_ref=capability_ref,
            input_artifact_refs=tuple(input_artifact_refs),
            output_artifact_refs=tuple(output_artifact_refs),
            prompt_template_ref=prompt_template_ref,
            redacted_input_summary_ref=_reject_raw_summary_ref(redacted_input_summary_ref),
            redacted_output_summary_ref=_reject_raw_summary_ref(redacted_output_summary_ref),
            policy_decision="allow",
            credential_decision="allow",
            runtime_result_ref=runtime_result_ref,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            redaction_status="redacted",
            created_by=context.actor_id,
        )
        self.invocation_evidence.append(evidence)
        return evidence

    def _record_lifecycle_event(
        self,
        context: IdentityContext,
        credential: CredentialReference,
        *,
        operation: str,
        source: str,
        user_confirmed: bool,
        previous_status: str | None,
    ) -> CredentialLifecycleEvent:
        event = CredentialLifecycleEvent(
            credential_event_id=f"credential_event_{uuid4().hex}",
            credential_ref_id=credential.credential_ref_id,
            provider_profile_id=credential.provider_profile_id,
            operation=operation,
            source=source,
            actor_type=context.actor_type,
            actor_id=context.actor_id,
            user_confirmed=user_confirmed,
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            policy_decision="allow",
            risk_flags=(),
            previous_status=previous_status,
            next_status=credential.status,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            redaction_status="redacted",
        )
        self.lifecycle_events.append(event)
        return event

    def _get_profile(self, provider_profile_id: str) -> ProviderProfile:
        try:
            return self.provider_profiles[provider_profile_id]
        except KeyError as exc:
            raise CredentialProviderError("PROVIDER_PROFILE_NOT_FOUND", "Provider profile was not found.", reason="profile_not_found") from exc

    def _get_credential(self, credential_ref_id: str) -> CredentialReference:
        try:
            return self.credentials[credential_ref_id]
        except KeyError as exc:
            raise CredentialProviderError("CREDENTIAL_NOT_FOUND", "Credential reference was not found.", reason="credential_not_found") from exc


def resolve_provider_profile_from_env(
    context: IdentityContext,
    *,
    env_files: tuple[str, ...] = (".env", ".env.local"),
) -> tuple[dict[str, Any], str, bool, str]:
    """Resolve provider profile data from dotenv/environment without exposing secrets."""
    merged: dict[str, str] = {}
    source = "environment"
    for env_file in env_files:
        path = REPO_ROOT / env_file
        if path.exists():
            values = {key: value for key, value in dotenv_values(path).items() if value is not None}
            if values:
                merged.update(values)
                source = env_file
    merged.update({key: value for key, value in os.environ.items() if key.startswith(("V5_", "V4_U5E_", "MINIMAX_", "OPENAI_", "LLM_"))})

    provider = (merged.get("V5_LLM_PROVIDER") or merged.get("V4_U5E_LLM_PROVIDER") or merged.get("LLM_PROVIDER") or "minimax").strip().lower()
    model_ref = (merged.get("V5_LLM_MODEL") or merged.get("V4_U5E_LLM_MODEL") or merged.get("LLM_MODEL") or "").strip()
    if not model_ref or model_ref.startswith("<") or model_ref.startswith("your-"):
        model_ref = "MiniMax-M2.1" if provider == "minimax" else "default"
    api_key_env = "MINIMAX_API_KEY" if provider == "minimax" else "OPENAI_API_KEY"
    secret_configured = bool((merged.get(api_key_env) or "").strip()) and not _looks_placeholder(merged.get(api_key_env) or "")
    base_url_ref = "env://MINIMAX_BASE_URL" if provider == "minimax" else "env://OPENAI_BASE_URL"
    credential_ref_id = f"credential_ref_{provider}_{context.app_id}"
    profile = {
        "provider_profile_id": f"provider_profile_{provider}_{context.app_id}",
        "tenant_id": context.tenant_id,
        "workspace_id": context.workspace_id,
        "project_id": context.project_id,
        "app_id": context.app_id,
        "provider": provider,
        "provider_kind": "llm",
        "base_url_ref": base_url_ref,
        "model_refs": [model_ref],
        "credential_ref_id": credential_ref_id,
        "capability_refs": ["llm.chat", "llm.summarize"],
        "status": "active",
        "created_by": context.actor_id,
    }
    return profile, f"env://{api_key_env}", secret_configured, source


def _guard_operation(context: IdentityContext, operation: str, *, source: str, user_confirmed: bool) -> None:
    if source == "agent" or context.actor_type == "agent":
        if operation in AGENT_DENIED_OPERATIONS:
            raise CredentialProviderError("CREDENTIAL_AGENT_MUTATION_DENIED", "Agent source cannot mutate credential/provider lifecycle.", reason="agent_mutation_denied")
    if not user_confirmed:
        raise CredentialProviderError("CREDENTIAL_USER_CONFIRMATION_REQUIRED", "Credential/provider operation requires user confirmation.", reason="missing_user_confirmation")


def _require_same_scope(context: IdentityContext, profile: ProviderProfile) -> None:
    if profile.tenant_id != context.tenant_id:
        raise CredentialProviderError("CREDENTIAL_SCOPE_DENIED", "Provider profile tenant does not match actor tenant.", reason="tenant_mismatch")
    if profile.workspace_id != context.workspace_id:
        raise CredentialProviderError("CREDENTIAL_SCOPE_DENIED", "Provider profile workspace does not match actor workspace.", reason="workspace_mismatch")
    if profile.project_id != context.project_id:
        raise CredentialProviderError("CREDENTIAL_SCOPE_DENIED", "Provider profile project does not match actor project.", reason="project_mismatch")
    if profile.app_id != context.app_id:
        raise CredentialProviderError("CREDENTIAL_SCOPE_DENIED", "Provider profile app does not match actor app.", reason="app_mismatch")


def _validate_secret_ref(secret_ref: str) -> None:
    value = _optional_text(secret_ref)
    if value is None:
        raise CredentialProviderError("CREDENTIAL_SECRET_REDACTED", "Credential secret reference is required.", reason="missing_secret_ref")
    if not value.startswith(("secret://", "env://", "vault://", "keychain://")):
        raise CredentialProviderError("CREDENTIAL_SECRET_REDACTED", "Credential must use a secret reference, not a raw secret.", reason="raw_secret_ref_denied")
    lowered = value.lower()
    if "sk-" in lowered or "bearer " in lowered or "api_key=" in lowered or "secret=" in lowered:
        raise CredentialProviderError("CREDENTIAL_SECRET_REDACTED", "Credential reference appears to contain a raw secret.", reason="raw_secret_ref_denied")


def _safe_secret_ref(secret_ref: str) -> str:
    if secret_ref.startswith("env://"):
        return secret_ref
    if secret_ref.startswith("secret://"):
        return "secret://[REDACTED]"
    if secret_ref.startswith("vault://"):
        return "vault://[REDACTED]"
    if secret_ref.startswith("keychain://"):
        return "keychain://[REDACTED]"
    return "[REDACTED]"


def _reject_unknown_and_forbidden(data: Mapping[str, Any], allowed: set[str], code: str) -> None:
    for key in data:
        lowered = str(key).lower()
        if lowered in FORBIDDEN_KEYS or "token" in lowered or lowered.endswith("_secret") or "raw_" in lowered:
            raise CredentialProviderError(code, "Sensitive fields are not allowed.", reason="sensitive_field", resource=str(key))
    unknown = set(data) - allowed
    if unknown:
        raise CredentialProviderError(code, "Unknown fields are not allowed.", reason="unknown_field", resource=sorted(unknown)[0])


def _required_text(data: Mapping[str, Any], key: str, code: str) -> str:
    value = _optional_text(data.get(key))
    if value is None:
        raise CredentialProviderError(code, f"{key} is required.", reason=f"missing_{key}", resource=key)
    return value


def _required_str_tuple(data: Mapping[str, Any], key: str, code: str) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise CredentialProviderError(code, f"{key} must be a non-empty list.", reason=f"invalid_{key}", resource=key)
    result: list[str] = []
    for item in value:
        text = _optional_text(item)
        if text is None:
            raise CredentialProviderError(code, f"{key} items must be non-empty strings.", reason=f"invalid_{key}", resource=key)
        result.append(text)
    return tuple(result)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise CredentialProviderError("CREDENTIAL_INVALID", "Expected string value.", reason="invalid_text_value")
    stripped = value.strip()
    return stripped or None


def _reject_raw_summary_ref(value: str) -> str:
    text = _optional_text(value)
    if text is None:
        raise CredentialProviderError("PROVIDER_PROFILE_INVALID", "Redacted summary ref is required.", reason="missing_summary_ref")
    lowered = text.lower()
    if "raw" in lowered or "prompt" in lowered or "secret" in lowered or "bearer" in lowered:
        raise CredentialProviderError("PROVIDER_PROFILE_INVALID", "Provider evidence requires redacted summary refs.", reason="raw_summary_ref_denied")
    return text


def _looks_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    return not lowered or lowered.startswith("<") or lowered.startswith("your-") or lowered in {"changeme", "placeholder"}


def _now() -> str:
    return datetime.now(UTC).isoformat()
