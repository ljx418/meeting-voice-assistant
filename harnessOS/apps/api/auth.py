"""External transport auth guard for V3.5 local capability tokens."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from apps.gateway.protocol import RpcError, RpcResponse
from apps.gateway.service import GatewayService
from core.apps.scope import ScopeContext
from core.protocol.auth import CapabilityTokenClaims, get_method_capability, is_forbidden_method, verify_capability_token
from core.protocol.schemas.errors import ProtocolError


ADMIN_CAPABILITIES = {"admin", "debug", "internal"}
LOCAL_ORIGINS = {
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
}


@dataclass(frozen=True)
class ExternalAuthContext:
    """External request auth context."""

    scope: ScopeContext
    claims: Optional[CapabilityTokenClaims] = None
    dev_mode: bool = False
    warning: Optional[str] = None


async def authorize_rpc_request(
    request: Request,
    *,
    gateway: GatewayService,
    method: str,
    params: dict[str, Any],
) -> ExternalAuthContext:
    """Authorize and normalize one external JSON-RPC request."""
    if params.get("scope_mode") == "all":
        raise ProtocolError("METHOD_FORBIDDEN", "scope_mode=all is not allowed on external transports.", {"reason": "scope_mode_all_forbidden"})
    _ensure_no_scope_conflict(params)
    if is_forbidden_method(method):
        raise ProtocolError("METHOD_FORBIDDEN", "Method is forbidden for external default auth.", {"method": method})
    if method == "method.list" and params.get("include_forbidden"):
        context = _authenticate(request, gateway=gateway, params=params)
        _require_admin(context)
        return context
    capability = get_method_capability(method)
    context = _authenticate(request, gateway=gateway, params=params)
    if capability:
        _require_capability(context, capability)
    _inject_token_scope(params, context.scope)
    _inject_auth_metadata(params, context)
    _ensure_resource_scope(gateway, params, context.scope, context=context)
    return context


async def authorize_http_request(
    request: Request,
    *,
    gateway: GatewayService,
    params: dict[str, Any],
    capability: str,
    admin_only: bool = False,
) -> ExternalAuthContext:
    """Authorize a non-RPC external HTTP request."""
    if params.get("scope_mode") == "all":
        raise ProtocolError("METHOD_FORBIDDEN", "scope_mode=all is not allowed on external transports.", {"reason": "scope_mode_all_forbidden"})
    _ensure_no_scope_conflict(params)
    context = _authenticate(request, gateway=gateway, params=params)
    if admin_only:
        _require_admin(context)
    else:
        _require_capability(context, capability)
    _inject_token_scope(params, context.scope)
    _inject_auth_metadata(params, context)
    _ensure_resource_scope(gateway, params, context.scope, context=context)
    return context


def protocol_error_response(exc: ProtocolError, *, request_id: Optional[str] = None) -> dict[str, Any]:
    """Return a JSON-RPC style error payload."""
    return RpcResponse(
        id=request_id,
        error=RpcError(code=exc.code, message=str(exc), data=_redact(exc.data)),
    ).model_dump(mode="json")


def http_error_response(exc: ProtocolError) -> JSONResponse:
    """Return a non-streaming HTTP auth error."""
    return JSONResponse(
        status_code=_http_status(exc.code),
        content={"error": {"code": exc.code, "message": str(exc), "data": _redact(exc.data)}},
    )


def add_dev_warning(response: Any, context: ExternalAuthContext) -> None:
    """Attach dev-mode warning metadata to a FastAPI response."""
    if context.warning and hasattr(response, "headers"):
        response.headers["X-HarnessOS-Auth-Warning"] = context.warning


def _authenticate(request: Request, *, gateway: GatewayService, params: dict[str, Any]) -> ExternalAuthContext:
    token = _bearer_token(request)
    origin = request.headers.get("origin")
    if token is None:
        if not _dev_mode_enabled():
            raise ProtocolError("AUTH_REQUIRED", "Authentication is required.", {"reason": "missing_token"})
        if origin and not _is_local_origin(origin):
            raise ProtocolError("AUTH_FORBIDDEN", "Dev mode only allows local origins.", {"reason": "dev_mode_non_local_origin"})
        scope = _scope_from_params(params) or ScopeContext()
        return ExternalAuthContext(scope=scope, dev_mode=True, warning="dev-mode-no-token")
    claims = verify_capability_token(token)
    profile = _profile_for_claims(gateway, claims)
    profile_origins = set(profile.allowed_origins)
    token_origins = set(claims.allowed_origins)
    if not token_origins <= profile_origins:
        raise ProtocolError("AUTH_FORBIDDEN", "Token origin exceeds app profile bounds.", {"reason": "origin_exceeds_app_profile"})
    if not set(claims.capabilities) <= set(profile.default_capabilities):
        raise ProtocolError("CAPABILITY_DENIED", "Token capability exceeds app profile bounds.", {"reason": "capability_exceeds_app_profile"})
    if origin and origin not in (profile_origins & token_origins):
        raise ProtocolError("AUTH_FORBIDDEN", "Origin is not allowed.", {"reason": "origin_mismatch"})
    token_scope = ScopeContext(
        app_id=claims.app_id,
        project_id=claims.project_id,
        workspace_id=claims.workspace_id,
    )
    requested_scope = _scope_from_params(params)
    if requested_scope is not None and requested_scope != token_scope:
        raise ProtocolError("SCOPE_MISMATCH", "Requested scope does not match token scope.", {"reason": "token_scope_mismatch"})
    return ExternalAuthContext(scope=token_scope, claims=claims)


def _profile_for_claims(gateway: GatewayService, claims: CapabilityTokenClaims):
    try:
        return gateway.app_registry.get(claims.app_id)
    except KeyError as exc:
        raise ProtocolError("APP_PROFILE_NOT_FOUND", f"App profile not found: {claims.app_id}", {"app_id": claims.app_id}) from exc


def _require_capability(context: ExternalAuthContext, capability: str) -> None:
    if context.dev_mode:
        return
    if context.claims is None or capability not in context.claims.capabilities:
        raise ProtocolError("CAPABILITY_DENIED", "Capability is denied.", {"capability": capability})


def _require_admin(context: ExternalAuthContext) -> None:
    if context.dev_mode:
        return
    if context.claims is None or not (set(context.claims.capabilities) & ADMIN_CAPABILITIES):
        raise ProtocolError("METHOD_FORBIDDEN", "Method requires admin/debug/internal capability.", {"reason": "admin_capability_required"})


def _context_has_admin(context: ExternalAuthContext) -> bool:
    if context.dev_mode:
        return True
    return context.claims is not None and bool(set(context.claims.capabilities) & ADMIN_CAPABILITIES)


def _bearer_token(request: Request) -> Optional[str]:
    value = request.headers.get("authorization")
    if not value:
        return None
    scheme, _, token = value.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise ProtocolError("AUTH_INVALID", "Invalid Authorization header.", {"reason": "invalid_authorization_header"})
    return token.strip()


def _dev_mode_enabled() -> bool:
    return os.getenv("HARNESS_V3_5_DEV_MODE", "").strip().lower() in {"1", "true", "yes", "on"}


def _is_local_origin(origin: str) -> bool:
    return origin in LOCAL_ORIGINS


def _scope_from_params(params: dict[str, Any]) -> Optional[ScopeContext]:
    raw_scope = params.get("scope")
    has_top_level = any(key in params for key in ("app_id", "project_id", "workspace_id"))
    if raw_scope is None and not has_top_level:
        return None
    scope = raw_scope if isinstance(raw_scope, dict) else {}
    return ScopeContext(
        app_id=_text(scope.get("app_id") or params.get("app_id") or "default") or "default",
        project_id=_text(scope.get("project_id") or params.get("project_id")),
        workspace_id=_text(scope.get("workspace_id") or params.get("workspace_id")),
    )


def _ensure_no_scope_conflict(params: dict[str, Any]) -> None:
    raw_scope = params.get("scope")
    if raw_scope is None:
        return
    if not isinstance(raw_scope, dict):
        raise ProtocolError("INVALID_PARAMS", "scope must be an object when provided.", {"field": "scope"})
    for key in ("app_id", "project_id", "workspace_id"):
        nested = _text(raw_scope.get(key))
        top_level = _text(params.get(key))
        if nested is not None and top_level is not None and nested != top_level:
            raise ProtocolError("SCOPE_MISMATCH", "Top-level scope conflicts with nested scope.", {"field": key})


def _inject_token_scope(params: dict[str, Any], scope: ScopeContext) -> None:
    params.setdefault("scope", scope.to_dict())


def _inject_auth_metadata(params: dict[str, Any], context: ExternalAuthContext) -> None:
    if context.claims is not None:
        params["_auth_capabilities"] = list(context.claims.capabilities)
        params["_auth_allowed_origins"] = list(context.claims.allowed_origins)
    elif context.dev_mode:
        params["_auth_capabilities"] = [
            "events",
            "turns",
            "jobs",
            "jobs.read",
            "artifacts",
            "artifacts.read",
            "approvals",
            "approvals.read",
            "memory",
            "connectors.read",
            "packs.read",
            "workflows.read",
            "workflows.write",
            "workflows.execute",
            "stations.read",
            "stations.execute",
            "quality.read",
            "quality.write",
            "board.read",
            "business_events.read",
            "business_events.write",
            "workflow_context.read",
            "workflow_context.write",
            "workflow_patches.read",
            "workflow_patches.write",
            "workflow_versions.publish",
        ]
        params["_auth_allowed_origins"] = sorted(LOCAL_ORIGINS)
    params["_auth_external"] = True


def _ensure_resource_scope(gateway: GatewayService, params: dict[str, Any], scope: ScopeContext, *, context: ExternalAuthContext) -> None:
    session_id = _text(params.get("session_id"))
    if session_id:
        try:
            session = gateway.runtime_pool.read_session(session_id)
        except Exception:
            session = None
        if isinstance(session, dict) and not _record_matches(session, scope):
            raise ProtocolError("SCOPE_MISMATCH", "Session does not match token scope.", {"resource": "session_id"})
    approval_id = _text(params.get("approval_id"))
    if approval_id:
        try:
            approval = gateway.approval_store.get_approval(approval_id)
        except Exception:
            approval = None
        if isinstance(approval, dict) and not _record_matches(approval, scope):
            raise ProtocolError("SCOPE_MISMATCH", "Approval does not match token scope.", {"resource": "approval_id"})
    job_id = _text(params.get("job_id"))
    if job_id:
        try:
            job = gateway.core_service.get_job(job_id).model_dump(mode="json")
        except Exception:
            job = None
        if isinstance(job, dict) and not _record_matches(job, scope):
            raise ProtocolError("SCOPE_MISMATCH", "Job does not match token scope.", {"resource": "job_id"})
    artifact_id = _text(params.get("artifact_id"))
    if artifact_id:
        try:
            artifact = gateway.artifact_registry.get_artifact(artifact_id)
        except Exception:
            artifact = None
        if isinstance(artifact, dict) and not _record_matches(artifact, scope):
            raise ProtocolError("SCOPE_MISMATCH", "Artifact does not match token scope.", {"resource": "artifact_id"})
    trace_id = _text(params.get("trace_id"))
    if trace_id:
        try:
            records = gateway.core_service.list_trace_records(trace_id=trace_id)
        except Exception:
            records = []
        for record in records:
            raw = record.model_dump(mode="json") if hasattr(record, "model_dump") else dict(record)
            if not _record_matches(raw, scope):
                raise ProtocolError("SCOPE_MISMATCH", "Trace does not match token scope.", {"resource": "trace_id"})
    memory_id = _text(params.get("memory_id"))
    if memory_id:
        try:
            memory = gateway.core_service.get_memory(memory_id).model_dump(mode="json")
        except Exception:
            memory = None
        if isinstance(memory, dict):
            if _text(memory.get("app_id")) is None and not _context_has_admin(context):
                raise ProtocolError("SCOPE_REQUIRED", "Memory record does not include scope.", {"resource": "memory_id", "reason": "legacy_memory_scope_required"})
            if not _record_matches(memory, scope):
                raise ProtocolError("SCOPE_MISMATCH", "Memory does not match token scope.", {"resource": "memory_id"})


def _record_matches(record: dict[str, Any], scope: ScopeContext) -> bool:
    return (
        _text(record.get("app_id")) == scope.app_id
        and _text(record.get("project_id")) == scope.project_id
        and _text(record.get("workspace_id")) == scope.workspace_id
    )


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ProtocolError("INVALID_PARAMS", "scope values must be strings.", {"reason": "invalid_scope_value"})
    stripped = value.strip()
    return stripped or None


def _redact(data: dict[str, Any]) -> dict[str, Any]:
    redacted = {}
    for key, value in (data or {}).items():
        lower = str(key).lower()
        if "token" in lower or lower == "authorization":
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


def _http_status(code: str) -> int:
    if code in {"AUTH_REQUIRED", "AUTH_INVALID"}:
        return 401
    if code in {"AUTH_FORBIDDEN", "CAPABILITY_DENIED", "SCOPE_MISMATCH", "METHOD_FORBIDDEN", "SUBSCRIPTION_TOKEN_SCOPE_MISMATCH", "SUBSCRIPTION_TOKEN_CHANNEL_DENIED"}:
        return 403
    if code in {"SUBSCRIPTION_TOKEN_INVALID", "SUBSCRIPTION_TOKEN_EXPIRED"}:
        return 401
    if code == "APP_PROFILE_NOT_FOUND":
        return 404
    return 400
