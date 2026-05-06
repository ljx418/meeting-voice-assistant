"""Multi-app profile and scope primitives."""

from core.apps.profiles import AppProfile, AppRegistry, build_default_app_registry
from core.apps.scope import ScopeContext, resolve_scope_context

__all__ = [
    "AppProfile",
    "AppRegistry",
    "ScopeContext",
    "build_default_app_registry",
    "resolve_scope_context",
]
