"""Conversation compaction service."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Literal

from core.engine.api.usage import UsageSnapshot
from core.engine.messages import ConversationMessage


@dataclass
class AutoCompactState:
    """State tracking for auto-compaction."""

    last_compacted_at: float = 0
    compaction_count: int = 0


async def auto_compact_if_needed(
    messages: list[ConversationMessage],
    api_client: Any,
    model: str,
    system_prompt: str,
    state: AutoCompactState,
    progress_callback: Callable[[Any], None],
    force: bool = False,
    trigger: str = "auto",
    hook_executor: Any = None,
    carryover_metadata: dict[str, Any] | None = None,
    context_window_tokens: int | None = None,
    auto_compact_threshold_tokens: int | None = None,
) -> tuple[list[ConversationMessage], bool]:
    """Perform auto-compaction if needed.

    This is a stub implementation - full compaction logic is not yet migrated.
    """
    # Return unchanged messages and False (was_compacted=False)
    return messages, False


CompactProgressEvent = Any  # Placeholder - full type defined in stream_events
