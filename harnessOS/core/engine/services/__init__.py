"""Services module."""

from __future__ import annotations

from core.engine.services.compact import AutoCompactState, auto_compact_if_needed

__all__ = [
    "AutoCompactState",
    "auto_compact_if_needed",
]
