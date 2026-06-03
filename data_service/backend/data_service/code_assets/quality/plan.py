"""Plan builder for V2.1 code quality governance."""

from __future__ import annotations

from typing import Any

from data_service.mcp_common import now

from .model import QUALITY_SCHEMA_VERSION, stable_id
from .persistence import plan_artifact_ref


def build_plan(*, workspace_id: str, codebase_id: str, rules: list[dict[str, Any]]) -> dict[str, Any]:
    approved = [dict(rule) for rule in rules if rule.get("status") == "approved"]
    generated_at = now()
    identity = {"workspace_id": workspace_id, "codebase_id": codebase_id, "rules": [rule["rule_id"] for rule in approved]}
    plan_id = stable_id("cqplan", identity)
    impacted_targets = [
        {
            "target_type": rule["target_type"],
            "target_id": rule["target_id"],
            "rule_id": rule["rule_id"],
            "rule_type": rule["rule_type"],
            "action": rule["action"],
            "suggested_value": rule.get("suggested_value", ""),
        }
        for rule in approved
    ]
    overlays = [
        {
            "target_type": item["target_type"],
            "target_id": item["target_id"],
            "applied_rules": [item["rule_id"]],
            "governed_by": [plan_id],
        }
        for item in impacted_targets
    ]
    return {
        "schema_version": QUALITY_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "plan_id": plan_id,
        "generated_at": generated_at,
        "approved_rule_ids": [rule["rule_id"] for rule in approved],
        "impacted_targets": impacted_targets,
        "read_time_overlays": overlays,
        "warnings": [],
        "artifact_ref": plan_artifact_ref(plan_id),
    }
