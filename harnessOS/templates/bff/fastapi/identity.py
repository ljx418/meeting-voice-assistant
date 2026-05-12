"""Identity provider extension points for the V3.5-F BFF template."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from harnessos_client import Scope


@dataclass(frozen=True)
class Identity:
    user_id: str
    tenant_id: str
    scope: Scope
    capabilities: frozenset[str]


class IdentityProvider(Protocol):
    def resolve(self, headers: Any) -> Identity:
        ...


class DemoIdentityProvider:
    """Demo-only identity provider. Replace this in real products."""

    def __init__(self, *, default_scope: Scope, capabilities: frozenset[str]) -> None:
        self.default_scope = default_scope
        self.capabilities = capabilities

    def resolve(self, headers: Any) -> Identity:
        scope = Scope(
            app_id=str(headers.get("x-demo-app-id") or self.default_scope.app_id),
            project_id=_optional_text(headers.get("x-demo-project-id")) or self.default_scope.project_id,
            workspace_id=_optional_text(headers.get("x-demo-workspace-id")) or self.default_scope.workspace_id,
        )
        self.default_scope.ensure_compatible(scope)
        requested_caps = _capabilities(headers.get("x-demo-capabilities"))
        return Identity(
            user_id=str(headers.get("x-demo-user-id") or "demo_user"),
            tenant_id=str(headers.get("x-demo-tenant-id") or "demo_tenant"),
            scope=scope,
            capabilities=frozenset(capability for capability in requested_caps if capability in self.capabilities) if requested_caps else self.capabilities,
        )


def _capabilities(value: Any) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
