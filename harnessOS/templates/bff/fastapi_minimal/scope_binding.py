"""Platform-neutral scope binding sample for V3.5-D2 Minimal BFF Smoke."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from harnessos_client import Scope, ScopeMismatchError


@dataclass(frozen=True)
class DemoIdentity:
    """Demo identity context supplied by a business app."""

    user_id: str
    tenant_id: str
    scope: Scope


def identity_from_headers(headers: Any, *, default_scope: Scope) -> DemoIdentity:
    """Resolve a smoke identity from sample headers.

    This is not a user system. It is only a deterministic binding sample.
    """
    scope = Scope(
        app_id=str(headers.get("x-demo-app-id") or default_scope.app_id),
        project_id=_optional_text(headers.get("x-demo-project-id")) or default_scope.project_id,
        workspace_id=_optional_text(headers.get("x-demo-workspace-id")) or default_scope.workspace_id,
    )
    default_scope.ensure_compatible(scope)
    return DemoIdentity(
        user_id=str(headers.get("x-demo-user-id") or "demo_user"),
        tenant_id=str(headers.get("x-demo-tenant-id") or "demo_tenant"),
        scope=scope,
    )


def resolve_request_scope(
    *,
    identity_scope: Scope,
    route_scope: Optional[dict[str, Any]] = None,
    body_scope: Optional[dict[str, Any]] = None,
) -> Scope:
    """Resolve route/body scope under an identity upper bound."""
    resolved = _merge_scope(identity_scope, route_scope)
    identity_scope.ensure_compatible(resolved)
    if body_scope:
        body = Scope.from_value(body_scope)
        if body is not None:
            identity_scope.ensure_compatible(body)
            resolved.ensure_compatible(body)
    return resolved


def scope_error(message: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "SCOPE_MISMATCH",
            "message": message,
            "data": {},
        }
    }


def _merge_scope(base: Scope, value: Optional[dict[str, Any]]) -> Scope:
    if not value:
        return base
    return Scope(
        app_id=str(value.get("app_id") or base.app_id),
        project_id=_optional_text(value.get("project_id")) or base.project_id,
        workspace_id=_optional_text(value.get("workspace_id")) or base.workspace_id,
    )


def _optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
