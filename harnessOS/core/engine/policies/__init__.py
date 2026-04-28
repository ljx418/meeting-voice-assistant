"""Permission helpers for engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PermissionDecision:
    """Result of checking whether a tool invocation may run."""

    allowed: bool
    requires_confirmation: bool = False
    reason: str = ""


class PermissionChecker:
    """Evaluate tool usage against the configured permission mode and rules."""

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        tool_name: str,
        *,
        is_read_only: bool,
        file_path: str | None = None,
        command: str | None = None,
    ) -> PermissionDecision:
        """Return whether the tool may run immediately."""
        # Default implementation - allow all in this minimal migration
        return PermissionDecision(allowed=True, reason="Default allow")


__all__ = ["PermissionChecker", "PermissionDecision"]
