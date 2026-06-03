"""Models and stable identifiers for V2 agent context packs."""

from __future__ import annotations

import hashlib
import json
from typing import Any


CONTEXT_SCHEMA_VERSION = "v2.0"
ALLOWED_CONTEXT_MODES = {"project_brief", "task_context"}
ALLOWED_CONTEXT_FORMATS = {"json", "markdown"}


def stable_pack_id(
    *,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    mode: str,
    task: str | None,
    output_format: str,
    focus: dict[str, Any] | None,
    include: list[str] | None,
    max_tokens: int,
) -> str:
    payload = {
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "mode": mode,
        "task": task or "",
        "format": output_format,
        "focus": focus or {},
        "include": include or [],
        "max_tokens": max_tokens,
    }
    return "acp_" + hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:20]


def normalize_mode(mode: str | None, task: str | None) -> str:
    value = (mode or "").strip() or ("task_context" if task else "project_brief")
    if value not in ALLOWED_CONTEXT_MODES:
        raise ValueError("INVALID_CONTEXT_MODE")
    if value == "task_context" and not (task or "").strip():
        raise ValueError("TASK_REQUIRED")
    return value


def normalize_format(output_format: str | None) -> str:
    value = (output_format or "json").strip().lower()
    if value not in ALLOWED_CONTEXT_FORMATS:
        raise ValueError("INVALID_CONTEXT_FORMAT")
    return value


def token_estimate(value: Any) -> int:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return max(1, len(text) // 4)
