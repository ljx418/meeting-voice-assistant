"""V5.5 external app onboarding boundary primitives.

This module implements an in-memory production-boundary core slice for external
app onboarding validation. It does not create public onboarding routes, issue
raw credentials, or provide production-grade external app support.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping
from urllib.parse import urlparse
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext


FORBIDDEN_KEYS = {
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

FORBIDDEN_TEXT = (
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

BROWSER_FORBIDDEN_PATHS = ("/v1/rpc", "/v1/events/subscribe")
REGISTRATION_STATUSES = {"draft", "active", "suspended", "revoked"}
VERIFICATION_STATUSES = {"pending", "verified", "failed", "revoked"}
ORIGIN_STATUSES = {"allowed", "denied", "revoked"}


class ExternalAppOnboardingError(ValueError):
    """Stable V5.5 external app onboarding denial."""

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
class ExternalAppRegistration:
    """Tenant-bound external app registration."""

    app_registration_id: str
    tenant_id: str
    workspace_id: str
    app_id: str
    owner_actor_id: str
    display_name: str
    allowed_capabilities: tuple[str, ...]
    status: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted registration DTO."""
        data = asdict(self)
        data["allowed_capabilities"] = list(self.allowed_capabilities)
        data["redaction_status"] = "redacted"
        return mask_value(data)


@dataclass(frozen=True)
class DomainVerification:
    """External app domain verification record."""

    domain_verification_id: str
    tenant_id: str
    app_registration_id: str
    domain: str
    verification_method: str
    verification_status: str
    evidence_ref: str | None
    verified_at: str | None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted domain verification DTO."""
        data = asdict(self)
        data["redaction_status"] = "redacted"
        return mask_value(data)


@dataclass(frozen=True)
class OriginAllowlistEntry:
    """Origin allowlist decision record."""

    origin_entry_id: str
    tenant_id: str
    app_registration_id: str
    origin: str
    verified_domain_ref: str
    status: str
    policy_decision: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted origin DTO."""
        data = asdict(self)
        data["redaction_status"] = "redacted"
        return mask_value(data)


@dataclass(frozen=True)
class QuotaPolicy:
    """Tenant/app-bound quota policy."""

    quota_policy_id: str
    tenant_id: str
    app_registration_id: str
    limit_type: str
    limit_value: int
    window_seconds: int
    enforcement_status: str


@dataclass(frozen=True)
class QuotaDecision:
    """Auditable quota/rate-limit decision."""

    quota_decision_id: str
    tenant_id: str
    app_registration_id: str
    quota_policy_id: str
    usage_count: int
    allowed: bool
    policy_decision: str
    evidence_ref: str
    request_id: str
    correlation_id: str
    redaction_status: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted quota decision DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class OffboardingRecord:
    """Customer offboarding record."""

    offboarding_id: str
    tenant_id: str
    app_registration_id: str
    revoked_capability_refs: tuple[str, ...]
    revoked_credential_refs: tuple[str, ...]
    data_export_status: str
    deletion_status: str
    evidence_ref: str
    redaction_status: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return redacted offboarding DTO."""
        data = asdict(self)
        data["revoked_capability_refs"] = list(self.revoked_capability_refs)
        data["revoked_credential_refs"] = list(self.revoked_credential_refs)
        return mask_value(data)


@dataclass(frozen=True)
class SDKCompatibilityPolicy:
    """SDK compatibility policy and browser-surface guard."""

    sdk_name: str
    sdk_version: str
    api_version: str
    compatibility_status: str
    deprecated_at: str | None
    sunset_at: str | None
    migration_guide_ref: str | None
    browser_allowed_paths: tuple[str, ...]
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        """Return redacted SDK compatibility DTO."""
        data = asdict(self)
        data["browser_allowed_paths"] = list(self.browser_allowed_paths)
        return mask_value(data)


class ExternalAppOnboardingRegistry:
    """In-memory registry for V5.5 focused validation."""

    def __init__(self) -> None:
        self.registrations: dict[str, ExternalAppRegistration] = {}
        self.domain_verifications: dict[str, DomainVerification] = {}
        self.origins: dict[str, OriginAllowlistEntry] = {}
        self.quota_policies: dict[str, QuotaPolicy] = {}
        self.quota_decisions: list[QuotaDecision] = []
        self.offboarding_records: list[OffboardingRecord] = []

    def register_app(
        self,
        context: IdentityContext,
        *,
        app_registration_id: str,
        display_name: str,
        allowed_capabilities: list[str],
        source: str,
        user_confirmed: bool,
    ) -> ExternalAppRegistration:
        """Register a tenant-bound external app without issuing credentials."""
        _guard_user_confirmed(source, user_confirmed, "external_app.register")
        _reject_sensitive_mapping({"display_name": display_name, "allowed_capabilities": allowed_capabilities}, resource="registration")
        if app_registration_id in self.registrations:
            raise ExternalAppOnboardingError("EXTERNAL_APP_INVALID", "App registration already exists.", reason="duplicate_registration", resource=app_registration_id)
        registration = ExternalAppRegistration(
            app_registration_id=_required_text(app_registration_id, "app_registration_id"),
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            app_id=context.app_id,
            owner_actor_id=context.actor_id,
            display_name=_required_text(display_name, "display_name"),
            allowed_capabilities=tuple(allowed_capabilities),
            status="active",
        )
        self.registrations[registration.app_registration_id] = registration
        return registration

    def create_domain_verification(
        self,
        context: IdentityContext,
        *,
        app_registration_id: str,
        domain: str,
        verification_method: str,
    ) -> DomainVerification:
        """Create a pending domain verification record."""
        registration = self._get_registration(context, app_registration_id)
        normalized_domain = _normalize_domain(domain)
        verification = DomainVerification(
            domain_verification_id=f"domain_verification_{uuid4().hex}",
            tenant_id=registration.tenant_id,
            app_registration_id=registration.app_registration_id,
            domain=normalized_domain,
            verification_method=_required_text(verification_method, "verification_method"),
            verification_status="pending",
            evidence_ref=None,
            verified_at=None,
        )
        self.domain_verifications[verification.domain_verification_id] = verification
        return verification

    def mark_domain_verified(self, context: IdentityContext, *, domain_verification_id: str, evidence_ref: str) -> DomainVerification:
        """Mark a domain verification as verified using redacted evidence refs."""
        current = self._get_domain_verification(context, domain_verification_id)
        _reject_sensitive_mapping({"evidence_ref": evidence_ref}, resource="domain_verification")
        verified = DomainVerification(
            domain_verification_id=current.domain_verification_id,
            tenant_id=current.tenant_id,
            app_registration_id=current.app_registration_id,
            domain=current.domain,
            verification_method=current.verification_method,
            verification_status="verified",
            evidence_ref=_required_text(evidence_ref, "evidence_ref"),
            verified_at=_now(),
            created_at=current.created_at,
        )
        self.domain_verifications[verified.domain_verification_id] = verified
        return verified

    def allow_origin(self, context: IdentityContext, *, app_registration_id: str, origin: str, domain_verification_id: str) -> OriginAllowlistEntry:
        """Allow one origin only after matching domain verification succeeds."""
        registration = self._get_registration(context, app_registration_id)
        verification = self._get_domain_verification(context, domain_verification_id)
        normalized_origin = _normalize_origin(origin)
        if verification.app_registration_id != registration.app_registration_id:
            raise ExternalAppOnboardingError("ORIGIN_SCOPE_DENIED", "Domain verification does not belong to app registration.", reason="verification_app_mismatch")
        if verification.verification_status != "verified":
            raise ExternalAppOnboardingError("ORIGIN_VERIFICATION_REQUIRED", "Origin requires verified domain.", reason="domain_not_verified", resource=normalized_origin)
        if not _origin_matches_domain(normalized_origin, verification.domain):
            raise ExternalAppOnboardingError("ORIGIN_SCOPE_DENIED", "Origin does not match verified domain.", reason="origin_domain_mismatch", resource=normalized_origin)
        entry = OriginAllowlistEntry(
            origin_entry_id=f"origin_entry_{uuid4().hex}",
            tenant_id=context.tenant_id,
            app_registration_id=app_registration_id,
            origin=normalized_origin,
            verified_domain_ref=domain_verification_id,
            status="allowed",
            policy_decision="allow",
        )
        self.origins[entry.origin_entry_id] = entry
        return entry

    def evaluate_origin(self, context: IdentityContext, *, app_registration_id: str, origin: str) -> OriginAllowlistEntry:
        """Return allowlist entry or a stable denial for unknown origin."""
        self._get_registration(context, app_registration_id)
        normalized_origin = _normalize_origin(origin)
        for entry in self.origins.values():
            if entry.app_registration_id == app_registration_id and entry.origin == normalized_origin and entry.status == "allowed":
                return entry
        raise ExternalAppOnboardingError("ORIGIN_ALLOWLIST_DENIED", "Origin is not allowlisted.", reason="unknown_origin", resource=normalized_origin)

    def create_quota_policy(
        self,
        context: IdentityContext,
        *,
        app_registration_id: str,
        limit_type: str,
        limit_value: int,
        window_seconds: int,
    ) -> QuotaPolicy:
        """Create an app-bound quota policy."""
        self._get_registration(context, app_registration_id)
        if limit_value <= 0 or window_seconds <= 0:
            raise ExternalAppOnboardingError("QUOTA_POLICY_INVALID", "Quota limits must be positive.", reason="invalid_quota")
        policy = QuotaPolicy(
            quota_policy_id=f"quota_policy_{uuid4().hex}",
            tenant_id=context.tenant_id,
            app_registration_id=app_registration_id,
            limit_type=_required_text(limit_type, "limit_type"),
            limit_value=limit_value,
            window_seconds=window_seconds,
            enforcement_status="active",
        )
        self.quota_policies[policy.quota_policy_id] = policy
        return policy

    def evaluate_quota(self, context: IdentityContext, *, quota_policy_id: str, usage_count: int) -> QuotaDecision:
        """Evaluate quota and record auditable denial/allow decision."""
        policy = self._get_quota_policy(context, quota_policy_id)
        allowed = usage_count < policy.limit_value
        decision = QuotaDecision(
            quota_decision_id=f"quota_decision_{uuid4().hex}",
            tenant_id=context.tenant_id,
            app_registration_id=policy.app_registration_id,
            quota_policy_id=policy.quota_policy_id,
            usage_count=usage_count,
            allowed=allowed,
            policy_decision="allow" if allowed else "deny",
            evidence_ref=f"evidence://{context.correlation_id}/quota/{uuid4().hex}",
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            redaction_status="redacted",
        )
        self.quota_decisions.append(decision)
        return decision

    def offboard_app(
        self,
        context: IdentityContext,
        *,
        app_registration_id: str,
        revoked_capability_refs: list[str],
        revoked_credential_refs: list[str],
    ) -> OffboardingRecord:
        """Offboard an app and revoke access refs."""
        registration = self._get_registration(context, app_registration_id)
        _reject_sensitive_mapping({"revoked_capability_refs": revoked_capability_refs, "revoked_credential_refs": revoked_credential_refs}, resource="offboarding")
        revoked = ExternalAppRegistration(
            app_registration_id=registration.app_registration_id,
            tenant_id=registration.tenant_id,
            workspace_id=registration.workspace_id,
            app_id=registration.app_id,
            owner_actor_id=registration.owner_actor_id,
            display_name=registration.display_name,
            allowed_capabilities=(),
            status="revoked",
            created_at=registration.created_at,
        )
        self.registrations[app_registration_id] = revoked
        record = OffboardingRecord(
            offboarding_id=f"offboarding_{uuid4().hex}",
            tenant_id=context.tenant_id,
            app_registration_id=app_registration_id,
            revoked_capability_refs=tuple(revoked_capability_refs),
            revoked_credential_refs=tuple(revoked_credential_refs),
            data_export_status="completed",
            deletion_status="scheduled",
            evidence_ref=f"evidence://{context.correlation_id}/offboarding/{uuid4().hex}",
            redaction_status="redacted",
        )
        self.offboarding_records.append(record)
        return record

    def _get_registration(self, context: IdentityContext, app_registration_id: str) -> ExternalAppRegistration:
        try:
            registration = self.registrations[app_registration_id]
        except KeyError as exc:
            raise ExternalAppOnboardingError("EXTERNAL_APP_NOT_FOUND", "App registration was not found.", reason="registration_not_found", resource=app_registration_id) from exc
        if registration.tenant_id != context.tenant_id or registration.workspace_id != context.workspace_id or registration.app_id != context.app_id:
            raise ExternalAppOnboardingError("EXTERNAL_APP_SCOPE_DENIED", "App registration is outside actor scope.", reason="scope_mismatch", resource=app_registration_id)
        if registration.status == "revoked":
            raise ExternalAppOnboardingError("EXTERNAL_APP_REVOKED", "App registration is revoked.", reason="app_revoked", resource=app_registration_id)
        return registration

    def _get_domain_verification(self, context: IdentityContext, domain_verification_id: str) -> DomainVerification:
        try:
            verification = self.domain_verifications[domain_verification_id]
        except KeyError as exc:
            raise ExternalAppOnboardingError("DOMAIN_VERIFICATION_NOT_FOUND", "Domain verification was not found.", reason="verification_not_found", resource=domain_verification_id) from exc
        registration = self._get_registration(context, verification.app_registration_id)
        if registration.tenant_id != verification.tenant_id:
            raise ExternalAppOnboardingError("DOMAIN_VERIFICATION_SCOPE_DENIED", "Domain verification is outside actor scope.", reason="scope_mismatch", resource=domain_verification_id)
        return verification

    def _get_quota_policy(self, context: IdentityContext, quota_policy_id: str) -> QuotaPolicy:
        try:
            policy = self.quota_policies[quota_policy_id]
        except KeyError as exc:
            raise ExternalAppOnboardingError("QUOTA_POLICY_NOT_FOUND", "Quota policy was not found.", reason="quota_not_found", resource=quota_policy_id) from exc
        self._get_registration(context, policy.app_registration_id)
        return policy


def validate_sdk_compatibility(policy: SDKCompatibilityPolicy) -> dict[str, Any]:
    """Validate SDK compatibility policy and browser route restrictions."""
    _reject_sensitive_mapping(policy.to_dict(), resource="sdk_policy")
    for path in policy.browser_allowed_paths:
        if path in BROWSER_FORBIDDEN_PATHS:
            raise ExternalAppOnboardingError("SDK_BROWSER_ROUTE_DENIED", "Browser SDK cannot call direct internal routes.", reason="direct_browser_route", resource=path)
    return policy.to_dict()


def _guard_user_confirmed(source: str, user_confirmed: bool, operation: str) -> None:
    if source == "agent":
        raise ExternalAppOnboardingError("EXTERNAL_APP_AGENT_DENIED", "Agent source cannot perform external app onboarding.", reason="agent_mutation_denied", resource=operation)
    if not user_confirmed:
        raise ExternalAppOnboardingError("EXTERNAL_APP_CONFIRMATION_REQUIRED", "External app onboarding requires user_confirmed=true.", reason="missing_user_confirmation", resource=operation)


def _normalize_domain(domain: str) -> str:
    value = _required_text(domain, "domain").lower()
    if "://" in value or "/" in value:
        raise ExternalAppOnboardingError("DOMAIN_INVALID", "Domain must not include protocol or path.", reason="invalid_domain", resource=domain)
    return value


def _normalize_origin(origin: str) -> str:
    value = _required_text(origin, "origin")
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.path not in {"", "/"}:
        raise ExternalAppOnboardingError("ORIGIN_INVALID", "Origin must be scheme plus host only.", reason="invalid_origin", resource=origin)
    return f"{parsed.scheme}://{parsed.netloc.lower()}"


def _origin_matches_domain(origin: str, domain: str) -> bool:
    host = urlparse(origin).hostname or ""
    return host == domain or host.endswith(f".{domain}")


def _required_text(value: str, resource: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExternalAppOnboardingError("EXTERNAL_APP_FIELD_REQUIRED", f"{resource} is required.", reason="missing_field", resource=resource)
    return value.strip()


def _reject_sensitive_mapping(data: Mapping[str, Any], *, resource: str) -> None:
    for key, value in data.items():
        lowered_key = str(key).strip().lower()
        normalized_key = lowered_key.replace("-", "_")
        if lowered_key in FORBIDDEN_KEYS or normalized_key in FORBIDDEN_KEYS or "token" in lowered_key or "secret" in lowered_key or "raw_" in lowered_key:
            raise ExternalAppOnboardingError("EXTERNAL_APP_REDACTION_DENIED", "Sensitive fields are not allowed.", reason="sensitive_field", resource=f"{resource}.{key}")
        if isinstance(value, Mapping):
            _reject_sensitive_mapping(value, resource=f"{resource}.{key}")
        elif isinstance(value, str):
            lowered_value = value.lower()
            if any(token in lowered_value for token in FORBIDDEN_TEXT):
                raise ExternalAppOnboardingError("EXTERNAL_APP_REDACTION_DENIED", "Sensitive values are not allowed.", reason="sensitive_value", resource=f"{resource}.{key}")
        elif isinstance(value, list | tuple):
            for index, item in enumerate(value):
                if isinstance(item, Mapping):
                    _reject_sensitive_mapping(item, resource=f"{resource}.{key}[{index}]")
                elif isinstance(item, str):
                    lowered_item = item.lower()
                    if any(token in lowered_item for token in FORBIDDEN_TEXT):
                        raise ExternalAppOnboardingError("EXTERNAL_APP_REDACTION_DENIED", "Sensitive values are not allowed.", reason="sensitive_value", resource=f"{resource}.{key}[{index}]")


def _now() -> str:
    return datetime.now(UTC).isoformat()
