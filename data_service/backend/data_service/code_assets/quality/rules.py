"""Rule builder for V2.1 code quality governance."""

from __future__ import annotations

from typing import Any

from data_service.mcp_common import now

from .model import QUALITY_SCHEMA_VERSION, stable_id
from .persistence import rule_artifact_ref


def build_rules_from_feedback(
    *,
    workspace_id: str,
    codebase_id: str,
    feedback: list[dict[str, Any]],
    existing_rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    existing_by_id = {row["rule_id"]: dict(row) for row in existing_rules}
    created_at = now()
    for item in feedback:
        identity = {
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "target_type": item["target_type"],
            "target_id": item["target_id"],
            "rule_type": item["rule_type"],
            "suggested_value": item.get("suggested_value", ""),
        }
        rule_id = stable_id("cqrule", identity)
        if rule_id in existing_by_id:
            rule = existing_by_id[rule_id]
            source_ids = set(rule.get("source_feedback_ids", []))
            source_ids.add(item["feedback_id"])
            rule["source_feedback_ids"] = sorted(source_ids)
            continue
        existing_by_id[rule_id] = {
            "schema_version": QUALITY_SCHEMA_VERSION,
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "rule_id": rule_id,
            "rule_type": item["rule_type"],
            "target_type": item["target_type"],
            "target_id": item["target_id"],
            "status": "draft",
            "source_feedback_ids": [item["feedback_id"]],
            "action": item["action"],
            "suggested_value": item.get("suggested_value", ""),
            "confidence": 0.8,
            "created_at": created_at,
            "reviewed_at": None,
            "reviewer": None,
            "artifact_ref": rule_artifact_ref(rule_id),
            "resolved_target": item.get("resolved_target", {}),
        }
    return sorted(existing_by_id.values(), key=lambda row: row["rule_id"])
