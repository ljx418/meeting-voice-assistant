"""Hook executor for the query engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.engine.hooks.events import HookEvent


class HookExecutor:
    """Execute hooks for lifecycle events."""

    def __init__(self) -> None:
        pass

    async def execute(self, event: HookEvent, payload: dict[str, Any]) -> "AggregatedHookResult":
        """Execute all matching hooks for an event."""
        from core.engine.hooks.types import AggregatedHookResult

        # Minimal implementation - hooks are not fully migrated yet
        return AggregatedHookResult(results=[])
