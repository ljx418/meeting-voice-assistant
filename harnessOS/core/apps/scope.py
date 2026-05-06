"""Scope context used to isolate multi-app Core records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from core.apps.profiles import AppRegistry


DEFAULT_APP_ID = "default"


@dataclass(frozen=True)
class ScopeContext:
    """App/project/workspace scope for Core records and RPC calls."""

    app_id: str = DEFAULT_APP_ID
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON view."""
        return {
            "app_id": self.app_id,
            "project_id": self.project_id,
            "workspace_id": self.workspace_id,
        }

    def apply(self, metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Return metadata with a scope payload attached."""
        payload = dict(metadata or {})
        payload["scope"] = self.to_dict()
        return payload


def resolve_scope_context(
    params: Optional[dict[str, Any]] = None,
    *,
    app_registry: Optional["AppRegistry"] = None,
    app_id: Optional[str] = None,
    project_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    default_app_id: str = DEFAULT_APP_ID,
) -> ScopeContext:
    """Resolve scope from explicit values plus an optional params mapping."""
    params = params or {}
    raw_scope = params.get("scope")
    if raw_scope is None:
        scope_params: dict[str, Any] = {}
    elif isinstance(raw_scope, dict):
        scope_params = raw_scope
    else:
        raise ValueError("scope must be an object when provided")

    resolved_app_id = (
        _optional_text(app_id)
        or _optional_text(scope_params.get("app_id"))
        or _optional_text(params.get("app_id"))
        or default_app_id
    )
    profile = None
    if app_registry is not None and resolved_app_id != DEFAULT_APP_ID:
        profile = app_registry.get(resolved_app_id)
    elif app_registry is not None:
        profile = app_registry.get_optional(resolved_app_id)
    return ScopeContext(
        app_id=resolved_app_id,
        project_id=(
            _optional_text(project_id)
            or _optional_text(scope_params.get("project_id"))
            or _optional_text(params.get("project_id"))
            or getattr(profile, "default_project_id", None)
        ),
        workspace_id=(
            _optional_text(workspace_id)
            or _optional_text(scope_params.get("workspace_id"))
            or _optional_text(params.get("workspace_id"))
            or getattr(profile, "default_workspace_id", None)
        ),
    )


def _optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("scope values must be strings when provided")
    stripped = value.strip()
    return stripped or None
