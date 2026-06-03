"""JSON renderer for V2 agent context packs."""

from __future__ import annotations

from typing import Any


def render_json_pack(base: dict[str, Any], selected: dict[str, Any]) -> dict[str, Any]:
    payload = dict(base)
    payload.update(selected)
    payload["content"] = None
    return payload
