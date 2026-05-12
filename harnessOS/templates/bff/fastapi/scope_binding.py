"""Scope resolution for the V3.5-F BFF template."""

from __future__ import annotations

from typing import Any

from harnessos_client import Scope, ScopeMismatchError

from .errors import BffError
from .identity import Identity


class ScopeResolver:
    def resolve(
        self,
        *,
        identity: Identity,
        route_scope: dict[str, Any] | None = None,
        body_scope: dict[str, Any] | None = None,
        scope_mode: Any = None,
    ) -> Scope:
        if scope_mode == "all":
            raise BffError("METHOD_FORBIDDEN", "scope_mode=all is not allowed through the BFF.", status_code=403)
        resolved = _merge_scope(identity.scope, route_scope)
        try:
            identity.scope.ensure_compatible(resolved)
            if body_scope:
                body = Scope.from_value(body_scope)
                if body is not None:
                    identity.scope.ensure_compatible(body)
                    resolved.ensure_compatible(body)
        except ScopeMismatchError as exc:
            raise BffError("SCOPE_MISMATCH", str(exc), data=getattr(exc, "data", {}), status_code=403) from exc
        return resolved


def query_scope(query_params: Any) -> dict[str, Any]:
    return {
        key: value
        for key, value in {
            "app_id": query_params.get("app_id"),
            "project_id": query_params.get("project_id"),
            "workspace_id": query_params.get("workspace_id"),
        }.items()
        if value is not None
    }


def _merge_scope(base: Scope, value: dict[str, Any] | None) -> Scope:
    if not value:
        return base
    return Scope(
        app_id=str(value.get("app_id") or base.app_id),
        project_id=_optional_text(value.get("project_id")) or base.project_id,
        workspace_id=_optional_text(value.get("workspace_id")) or base.workspace_id,
    )


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
