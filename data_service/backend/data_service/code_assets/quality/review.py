"""Rule review helpers for V2.1 code quality governance."""

from __future__ import annotations

from typing import Any

from data_service.mcp_common import now

from .model import QUALITY_SCHEMA_VERSION


def apply_review(
    *,
    workspace_id: str,
    codebase_id: str,
    rules: list[dict[str, Any]],
    rule_id: str,
    status: str,
    reviewer: str,
    note: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    reviewed_at = now()
    updated = []
    reviewed_rule = None
    for rule in rules:
        item = dict(rule)
        if item["rule_id"] == rule_id:
            item["status"] = status
            item["reviewed_at"] = reviewed_at
            item["reviewer"] = reviewer or "unknown"
            item["review_note"] = note
            reviewed_rule = item
        updated.append(item)
    if reviewed_rule is None:
        raise FileNotFoundError("QUALITY_RULE_NOT_FOUND")
    review_record = {
        "schema_version": QUALITY_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "rule_id": rule_id,
        "status": status,
        "reviewer": reviewer or "unknown",
        "note": note,
        "reviewed_at": reviewed_at,
    }
    return updated, reviewed_rule, review_record
