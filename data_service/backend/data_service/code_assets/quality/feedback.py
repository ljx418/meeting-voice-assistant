"""Feedback record helpers for V2.1 code quality governance."""

from __future__ import annotations

from typing import Any

from data_service.mcp_common import now

from .model import QUALITY_SCHEMA_VERSION, stable_id
from .persistence import feedback_artifact_ref


def make_feedback(
    *,
    workspace_id: str,
    codebase_id: str,
    target_type: str,
    target_id: str,
    action: str,
    rule_type: str,
    severity: str,
    reason: str,
    suggested_value: str,
    metadata: dict[str, Any] | None,
    resolved_target: dict[str, Any],
) -> dict[str, Any]:
    created_at = now()
    identity = {
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "target_type": target_type,
        "target_id": target_id,
        "action": action,
        "rule_type": rule_type,
        "suggested_value": suggested_value,
    }
    feedback_id = stable_id("cqfb", identity)
    return {
        "schema_version": QUALITY_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "feedback_id": feedback_id,
        "target_type": target_type,
        "target_id": target_id,
        "action": action,
        "rule_type": rule_type,
        "severity": severity or "medium",
        "reason": reason,
        "suggested_value": suggested_value,
        "metadata": metadata or {},
        "resolved_target": resolved_target,
        "status": "recorded",
        "created_at": created_at,
        "artifact_ref": feedback_artifact_ref(feedback_id),
    }
