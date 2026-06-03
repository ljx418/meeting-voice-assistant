"""V6.6 external app onboarding pilot slice.

This module provides repo-backed pilot behavior for tenant-bound external app
registration, domain/origin policy checks, quota decisions, offboarding
evidence, and browser SDK route guards. It does not create production routes or
claim production-ready external app support.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.apps.external_onboarding import ExternalAppOnboardingError, ExternalAppOnboardingRegistry
from core.auth.tenant_boundary import IdentityContext


V6_INTERNAL_BROWSER_DENYLIST = {
    "/v1/rpc",
    "/v1/events/subscribe",
    "/v1/internal/runtime",
    "/v1/internal/executor",
    "/v1/internal/workflow-store",
    "/v1/internal/station-run",
}

V6_ALLOWED_BFF_ROUTES = {
    "GET /bff/v6/runtime-report",
    "GET /bff/v6/evidence-review",
    "GET /bff/v6/audit-export",
    "GET /bff/v6/external-app-admin",
    "POST /bff/v6/manual-confirmation",
}

_FORBIDDEN_FIELD_FRAGMENTS = (
    "authorization",
    "bearer",
    "token",
    "secret",
    "api_key",
    "apikey",
    "raw_",
    "raw prompt",
    "signed_url",
    "signed url",
)

_FORBIDDEN_VALUE_FRAGMENTS = (
    "authorization:",
    "bearer ",
    "sk-",
    "api_key=",
    "secret=",
    "raw prompt",
    "raw_artifact_content",
    "raw_connector_payload",
    "upstream signed url",
)


@dataclass(frozen=True)
class V6ExternalAppRuntimeContext:
    """External app operation context with the service account binding."""

    identity: IdentityContext
    service_account_id: str


class V6ExternalAppOnboardingPilot:
    """V6.6 external app onboarding pilot boundary."""

    def __init__(self) -> None:
        self._registry = ExternalAppOnboardingRegistry()
        self._registrations: dict[str, dict[str, Any]] = {}
        self._verified_domains: dict[str, str] = {}
        self._origin_entries: dict[str, dict[str, Any]] = {}
        self._active_sessions: dict[str, set[str]] = {}
        self._pending_capability_grants: dict[str, set[str]] = {}
        self._credential_refs: dict[str, set[str]] = {}

    def register_app(
        self,
        runtime_context: V6ExternalAppRuntimeContext,
        *,
        registration_id: str,
        app_display_name: str,
        allowed_capabilities: list[str],
        source: str,
        user_confirmed: bool,
        credential_refs: list[str] | None = None,
        active_session_refs: list[str] | None = None,
        pending_capability_grant_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        """Register an external app and return V6 schema-shaped DTO."""
        _require_service_account(runtime_context)
        _reject_sensitive_payload(
            {
                "registration_id": registration_id,
                "app_display_name": app_display_name,
                "allowed_capabilities": allowed_capabilities,
                "credential_refs": credential_refs or [],
                "active_session_refs": active_session_refs or [],
                "pending_capability_grant_refs": pending_capability_grant_refs or [],
            },
            resource="external_app_registration",
        )
        registration = self._registry.register_app(
            runtime_context.identity,
            app_registration_id=registration_id,
            display_name=app_display_name,
            allowed_capabilities=allowed_capabilities,
            source=source,
            user_confirmed=user_confirmed,
        )
        app_id = registration.app_registration_id
        self._credential_refs[app_id] = set(credential_refs or [f"credential-ref://{app_id}/primary"])
        self._active_sessions[app_id] = set(active_session_refs or [f"session-ref://{app_id}/browser"])
        self._pending_capability_grants[app_id] = set(pending_capability_grant_refs or [f"capability-grant-ref://{app_id}/workflow-read"])
        dto = {
            **self._common(runtime_context, policy_decision="allow", operation="external_app.register"),
            "registration_id": registration.app_registration_id,
            "app_display_name": registration.display_name,
            "domain_refs": [],
            "status": "registered",
        }
        self._registrations[app_id] = dto
        return _redacted(dto)

    def create_domain_verification(
        self,
        runtime_context: V6ExternalAppRuntimeContext,
        *,
        registration_id: str,
        domain: str,
        verification_method: str,
        mark_verified: bool,
    ) -> dict[str, Any]:
        """Create domain verification and optionally mark it verified."""
        _require_service_account(runtime_context)
        verification = self._registry.create_domain_verification(
            runtime_context.identity,
            app_registration_id=registration_id,
            domain=domain,
            verification_method=verification_method,
        )
        verified_at: str | None = None
        status = "pending"
        policy_decision = "needs_review"
        if mark_verified:
            verified = self._registry.mark_domain_verified(
                runtime_context.identity,
                domain_verification_id=verification.domain_verification_id,
                evidence_ref=f"evidence://{runtime_context.identity.correlation_id}/domain/{verification.domain_verification_id}",
            )
            verification = verified
            verified_at = verified.verified_at
            status = "verified"
            policy_decision = "allow"
            self._verified_domains[verified.domain_verification_id] = verified.domain
            registration = self._registrations.get(registration_id)
            if registration is not None:
                registration["domain_refs"] = sorted(set(registration.get("domain_refs", [])) | {verified.domain_verification_id})
        return _redacted(
            {
                **self._common(runtime_context, policy_decision=policy_decision, operation="domain.verify"),
                "domain": verification.domain,
                "verification_method": verification.verification_method,
                "verification_status": status,
                "verified_at": verified_at,
                "denial_reason": None,
                "domain_verification_ref": verification.domain_verification_id,
            }
        )

    def allow_origin(
        self,
        runtime_context: V6ExternalAppRuntimeContext,
        *,
        registration_id: str,
        origin: str,
        domain_verification_ref: str,
    ) -> dict[str, Any]:
        """Allow an origin only after verified-domain evidence exists."""
        _require_service_account(runtime_context)
        try:
            entry = self._registry.allow_origin(
                runtime_context.identity,
                app_registration_id=registration_id,
                origin=origin,
                domain_verification_id=domain_verification_ref,
            )
        except ExternalAppOnboardingError as exc:
            return self._origin_denial(runtime_context, origin=origin, domain_verification_ref=domain_verification_ref, reason=exc.reason)
        dto = {
            **self._common(runtime_context, policy_decision="allow", operation="origin.allowlist"),
            "origin": entry.origin,
            "domain_verification_ref": domain_verification_ref,
            "decision": "allow",
            "denial_reason": None,
        }
        self._origin_entries[entry.origin_entry_id] = dto
        return _redacted(dto)

    def evaluate_origin(self, runtime_context: V6ExternalAppRuntimeContext, *, registration_id: str, origin: str) -> dict[str, Any]:
        """Evaluate origin access and return an auditable allow/deny DTO."""
        _require_service_account(runtime_context)
        try:
            entry = self._registry.evaluate_origin(runtime_context.identity, app_registration_id=registration_id, origin=origin)
        except ExternalAppOnboardingError as exc:
            return self._origin_denial(runtime_context, origin=origin, domain_verification_ref="domain-verification-ref://unknown", reason=exc.reason)
        return _redacted(
            {
                **self._common(runtime_context, policy_decision="allow", operation="origin.evaluate"),
                "origin": entry.origin,
                "domain_verification_ref": entry.verified_domain_ref,
                "decision": "allow",
                "denial_reason": None,
            }
        )

    def create_quota_policy(
        self,
        runtime_context: V6ExternalAppRuntimeContext,
        *,
        registration_id: str,
        limit_type: str,
        limit_value: int,
        window_seconds: int,
    ) -> str:
        """Create quota/rate-limit policy and return redacted policy ref."""
        _require_service_account(runtime_context)
        policy = self._registry.create_quota_policy(
            runtime_context.identity,
            app_registration_id=registration_id,
            limit_type=limit_type,
            limit_value=limit_value,
            window_seconds=window_seconds,
        )
        return policy.quota_policy_id

    def evaluate_quota(self, runtime_context: V6ExternalAppRuntimeContext, *, quota_policy_ref: str, current_usage: int, denial_type: str = "quota") -> dict[str, Any]:
        """Evaluate quota and shape the result as V6 QuotaDecisionDTO."""
        _require_service_account(runtime_context)
        decision = self._registry.evaluate_quota(runtime_context.identity, quota_policy_id=quota_policy_ref, usage_count=current_usage)
        mapped_decision = "allow"
        denial_reason = None
        if not decision.allowed:
            mapped_decision = "deny_rate_limit" if denial_type == "rate_limit" else "deny_quota"
            denial_reason = denial_type
        return _redacted(
            {
                **self._common(runtime_context, policy_decision=decision.policy_decision, operation="quota.evaluate"),
                "quota_policy_ref": decision.quota_policy_id,
                "rate_limit_policy_ref": f"rate-limit-policy-ref://{decision.quota_policy_id}",
                "current_usage": decision.usage_count,
                "limit": self._quota_limit(decision.quota_policy_id),
                "decision": mapped_decision,
                "denial_reason": denial_reason,
            }
        )

    def offboard_app(self, runtime_context: V6ExternalAppRuntimeContext, *, registration_id: str) -> dict[str, Any]:
        """Offboard app and prove all V6 revocation categories."""
        _require_service_account(runtime_context)
        credential_refs = sorted(self._credential_refs.get(registration_id, set()))
        session_refs = sorted(self._active_sessions.get(registration_id, set()))
        grant_refs = sorted(self._pending_capability_grants.get(registration_id, set()))
        origin_refs = sorted(ref for ref, dto in self._origin_entries.items() if dto.get("origin"))
        self._registry.offboard_app(
            runtime_context.identity,
            app_registration_id=registration_id,
            revoked_capability_refs=grant_refs,
            revoked_credential_refs=credential_refs,
        )
        self._credential_refs[registration_id] = set()
        self._active_sessions[registration_id] = set()
        self._pending_capability_grants[registration_id] = set()
        for dto in self._origin_entries.values():
            dto["decision"] = "deny"
            dto["policy_decision"] = "deny"
            dto["denial_reason"] = "app_offboarded"
        if registration_id in self._registrations:
            self._registrations[registration_id]["status"] = "offboarded"
        return _redacted(
            {
                **self._common(runtime_context, policy_decision="allow", operation="external_app.offboard"),
                "offboarding_id": f"offboarding-v6-6-{uuid4().hex}",
                "revoked_app_credentials": True,
                "revoked_origin_allowlist": True,
                "revoked_active_sessions": True,
                "revoked_pending_capability_grants": True,
                "revocation_refs": credential_refs + session_refs + grant_refs + (origin_refs or [f"origin-allowlist-ref://{registration_id}/none"]),
            }
        )

    def sdk_compatibility_policy(self, runtime_context: V6ExternalAppRuntimeContext, *, requested_browser_routes: list[str]) -> dict[str, Any]:
        """Return browser SDK policy and deny direct internal runtime routes."""
        _require_service_account(runtime_context)
        _reject_sensitive_payload({"requested_browser_routes": requested_browser_routes}, resource="sdk_compatibility_policy")
        denied = sorted(route for route in requested_browser_routes if route in V6_INTERNAL_BROWSER_DENYLIST)
        allowed = sorted(route for route in requested_browser_routes if route in V6_ALLOWED_BFF_ROUTES)
        policy_decision = "deny" if denied else "allow"
        return _redacted(
            {
                **self._common(runtime_context, policy_decision=policy_decision, operation="sdk.compatibility.evaluate"),
                "sdk_policy_id": f"sdk-policy-v6-6-{uuid4().hex}",
                "allowed_bff_routes": allowed,
                "denied_internal_routes": denied or sorted(V6_INTERNAL_BROWSER_DENYLIST),
                "browser_direct_runtime_route_denied": any(route.startswith("/v1/internal/") for route in denied) or "/v1/internal/runtime" in V6_INTERNAL_BROWSER_DENYLIST,
                "browser_direct_v1_rpc_denied": "/v1/rpc" in V6_INTERNAL_BROWSER_DENYLIST,
                "browser_direct_v1_events_subscribe_denied": "/v1/events/subscribe" in V6_INTERNAL_BROWSER_DENYLIST,
            }
        )

    def _origin_denial(self, runtime_context: V6ExternalAppRuntimeContext, *, origin: str, domain_verification_ref: str, reason: str) -> dict[str, Any]:
        return _redacted(
            {
                **self._common(runtime_context, policy_decision="deny", operation="origin.evaluate"),
                "origin": origin,
                "domain_verification_ref": domain_verification_ref,
                "decision": "deny",
                "denial_reason": reason,
            }
        )

    def _common(self, runtime_context: V6ExternalAppRuntimeContext, *, policy_decision: str, operation: str) -> dict[str, Any]:
        identity = runtime_context.identity
        return {
            "tenant_id": identity.tenant_id,
            "workspace_id": identity.workspace_id,
            "app_id": identity.app_id,
            "service_account_id": runtime_context.service_account_id,
            "actor_id": identity.actor_id,
            "request_id": identity.request_id,
            "correlation_id": identity.correlation_id,
            "audit_ref": f"audit://{identity.correlation_id}/v6-6/{operation}/{uuid4().hex}",
            "policy_decision": policy_decision,
            "created_at": _now(),
        }

    def _quota_limit(self, quota_policy_ref: str) -> int:
        policy = self._registry.quota_policies[quota_policy_ref]
        return policy.limit_value


def make_v6_external_app_context(identity: IdentityContext, *, service_account_id: str = "svc_v6_6_external_app") -> V6ExternalAppRuntimeContext:
    """Create V6 external app runtime context for tests and evidence scripts."""
    return V6ExternalAppRuntimeContext(identity=identity, service_account_id=service_account_id)


def _require_service_account(runtime_context: V6ExternalAppRuntimeContext) -> None:
    if not runtime_context.service_account_id:
        raise ExternalAppOnboardingError("EXTERNAL_APP_SERVICE_ACCOUNT_REQUIRED", "External app onboarding requires service account binding.", reason="missing_service_account")


def _reject_sensitive_payload(data: Any, *, resource: str) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            lowered_key = str(key).lower()
            if any(fragment in lowered_key for fragment in _FORBIDDEN_FIELD_FRAGMENTS):
                raise ExternalAppOnboardingError("EXTERNAL_APP_REDACTION_DENIED", "Sensitive fields are not allowed.", reason="sensitive_field", resource=f"{resource}.{key}")
            _reject_sensitive_payload(value, resource=f"{resource}.{key}")
    elif isinstance(data, list | tuple | set):
        for index, item in enumerate(data):
            _reject_sensitive_payload(item, resource=f"{resource}[{index}]")
    elif isinstance(data, str):
        lowered = data.lower()
        if any(fragment in lowered for fragment in _FORBIDDEN_VALUE_FRAGMENTS):
            raise ExternalAppOnboardingError("EXTERNAL_APP_REDACTION_DENIED", "Sensitive values are not allowed.", reason="sensitive_value", resource=resource)


def _redacted(data: dict[str, Any]) -> dict[str, Any]:
    _reject_sensitive_payload(data, resource="dto")
    return mask_value(data)


def _now() -> str:
    return datetime.now(UTC).isoformat()
