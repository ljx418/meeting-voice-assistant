"""V3.5 error inventory.

non-runtime contract metadata only; no handler registration; no behavior change
"""

from __future__ import annotations

from typing import Any, Dict, List

ErrorEntry = Dict[str, Any]


ERROR_INVENTORY: List[ErrorEntry] = [
    {"code": "INVALID_PARAMS", "status": "implemented", "category": "rpc", "retryable": False, "planned_phase": None},
    {"code": "METHOD_NOT_FOUND", "status": "implemented", "category": "rpc", "retryable": False, "planned_phase": None},
    {"code": "SESSION_NOT_FOUND", "status": "implemented", "category": "session", "retryable": False, "planned_phase": None},
    {
        "code": "ARTIFACT_READ_BLOCKED",
        "status": "implemented",
        "category": "artifact",
        "retryable": False,
        "planned_phase": None,
    },
    {"code": "AUTH_REQUIRED", "status": "planned", "category": "auth", "retryable": False, "planned_phase": "V3.5-B"},
    {"code": "AUTH_INVALID", "status": "planned", "category": "auth", "retryable": False, "planned_phase": "V3.5-B"},
    {"code": "AUTH_FORBIDDEN", "status": "planned", "category": "auth", "retryable": False, "planned_phase": "V3.5-B"},
    {
        "code": "CAPABILITY_DENIED",
        "status": "planned",
        "category": "auth",
        "retryable": False,
        "planned_phase": "V3.5-B",
    },
    {"code": "SCOPE_MISMATCH", "status": "planned", "category": "scope", "retryable": False, "planned_phase": "V3.5-B"},
    {"code": "SCOPE_REQUIRED", "status": "planned", "category": "scope", "retryable": False, "planned_phase": "V3.5-B"},
    {
        "code": "APP_PROFILE_NOT_FOUND",
        "status": "planned",
        "category": "scope",
        "retryable": False,
        "planned_phase": "V3.5-B",
    },
    {
        "code": "EVENT_CURSOR_INVALID",
        "status": "planned",
        "category": "event",
        "retryable": False,
        "planned_phase": "V3.5-C",
    },
    {
        "code": "SUBSCRIPTION_TOKEN_INVALID",
        "status": "planned",
        "category": "event",
        "retryable": False,
        "planned_phase": "V3.5-C",
    },
    {
        "code": "SUBSCRIPTION_TOKEN_EXPIRED",
        "status": "planned",
        "category": "event",
        "retryable": False,
        "planned_phase": "V3.5-C",
    },
    {
        "code": "SUBSCRIPTION_TOKEN_SCOPE_MISMATCH",
        "status": "planned",
        "category": "event",
        "retryable": False,
        "planned_phase": "V3.5-C",
    },
    {
        "code": "SUBSCRIPTION_TOKEN_CHANNEL_DENIED",
        "status": "planned",
        "category": "event",
        "retryable": False,
        "planned_phase": "V3.5-C",
    },
    {
        "code": "APPROVAL_CONFLICT",
        "status": "planned",
        "category": "approval",
        "retryable": False,
        "planned_phase": "V3.5-A",
    },
    {
        "code": "APPROVAL_NOT_FOUND",
        "status": "planned",
        "category": "approval",
        "retryable": False,
        "planned_phase": "V3.5-A",
    },
    {
        "code": "APPROVAL_RETRY_CONSUMED",
        "status": "planned",
        "category": "approval",
        "retryable": False,
        "planned_phase": "V3.5-A",
    },
    {
        "code": "APPROVAL_INVALID_DECISION",
        "status": "planned",
        "category": "approval",
        "retryable": False,
        "planned_phase": "V3.5-A",
    },
    {
        "code": "METHOD_FORBIDDEN",
        "status": "planned",
        "category": "rpc",
        "retryable": False,
        "planned_phase": "V3.5-A",
    },
    {
        "code": "METHOD_DEPRECATED",
        "status": "planned",
        "category": "rpc",
        "retryable": False,
        "planned_phase": "V3.5-A",
    },
    {"code": "PACK_NOT_FOUND", "status": "planned", "category": "pack", "retryable": False, "planned_phase": "V3.5-G"},
    {
        "code": "CONNECTOR_NOT_FOUND",
        "status": "planned",
        "category": "connector",
        "retryable": False,
        "planned_phase": "V3.5-G",
    },
    {"code": "RUNTIME_ERROR", "status": "implemented", "category": "runtime", "retryable": True, "planned_phase": None},
]
