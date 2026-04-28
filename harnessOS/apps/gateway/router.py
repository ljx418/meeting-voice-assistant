"""Session routing helpers for harnessOS gateway."""

from __future__ import annotations

from typing import Any, Mapping


def session_key_for_payload(payload: Mapping[str, Any]) -> str:
    """Resolve a stable session key from a protocol payload."""
    explicit = payload.get("session_key") or payload.get("session_id")
    if explicit:
        return str(explicit)
    user_id = str(payload.get("user_id") or "anonymous")
    thread_id = str(payload.get("thread_id") or payload.get("conversation_id") or "default")
    return f"{thread_id}:{user_id}"
