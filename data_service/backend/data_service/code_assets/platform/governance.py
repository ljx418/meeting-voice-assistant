"""V2.23 platform governance feedback loop."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    console_payload_path,
    governance_artifact_refs,
    read_cache_decisions,
    read_console,
    read_contract_registry,
    read_governance_feedback,
    read_governance_overlay_report,
    read_governance_rules,
    read_provider_capabilities,
    read_tool_catalog,
    read_workflow_guides,
    write_governance_feedback,
    write_governance_overlay_report,
    write_governance_rules,
)


GOVERNANCE_SCHEMA_VERSION = "v2.23"
RULE_STATUSES = {"draft", "approved", "rejected", "revoked"}
TARGET_TYPES = {"platform_panel", "artifact_contract", "tool_guidance", "workflow_guide_step", "incremental_decision", "provider_capability"}


class PlatformGovernanceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def record_feedback(
        self,
        codebase_id: str,
        *,
        target_type: str,
        target_id: str,
        action: str,
        rule_type: str,
        severity: str = "medium",
        reason: str = "",
        suggested_value: str = "",
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        resolved = self.resolve_target(codebase_id, target_type, target_id)
        feedback = {
            "schema_version": GOVERNANCE_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "feedback_id": _stable_id("feedback", codebase_id, target_type, target_id, action, rule_type, reason, suggested_value),
            "target_type": target_type,
            "target_id": target_id,
            "action": str(action or "").strip(),
            "rule_type": str(rule_type or "").strip() or "read_time_overlay",
            "severity": str(severity or "medium").strip(),
            "reason": str(reason or ""),
            "suggested_value": str(suggested_value or ""),
            "resolved_target": resolved,
            "status": "recorded",
            "artifact_refs": governance_artifact_refs(codebase_id),
            "created_at": now(),
        }
        if not feedback["action"]:
            raise ValueError("INVALID_ACTION")
        rows = [row for row in read_governance_feedback(self.workspace, codebase_id) if row.get("feedback_id") != feedback["feedback_id"]]
        rows.append(feedback)
        write_governance_feedback(self.workspace, codebase_id, sorted(rows, key=lambda row: str(row.get("feedback_id"))))
        overlay = self.build_overlay_report(codebase_id)
        return {"feedback": feedback, "overlay_report": overlay, "artifact_refs": governance_artifact_refs(codebase_id)}

    def build_rules(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        feedback_rows = read_governance_feedback(self.workspace, codebase_id)
        if not feedback_rows:
            raise FileNotFoundError("PLATFORM_GOVERNANCE_FEEDBACK_NOT_FOUND")
        existing = {str(row.get("rule_id")): row for row in read_governance_rules(self.workspace, codebase_id)}
        rules = []
        for feedback in feedback_rows:
            rule_id = _stable_id("rule", feedback.get("target_type"), feedback.get("target_id"), feedback.get("rule_type"), feedback.get("suggested_value"))
            current = dict(existing.get(rule_id) or {})
            status = current.get("status") or "draft"
            rule = {
                "schema_version": GOVERNANCE_SCHEMA_VERSION,
                "workspace_id": self.workspace_id,
                "codebase_id": codebase_id,
                "rule_id": rule_id,
                "feedback_ids": sorted(set([*list(current.get("feedback_ids") or []), str(feedback["feedback_id"])])),
                "target_type": feedback["target_type"],
                "target_id": feedback["target_id"],
                "rule_type": feedback["rule_type"],
                "severity": feedback["severity"],
                "effect": "read_time_overlay",
                "status": status,
                "suggested_value": feedback.get("suggested_value"),
                "reason": feedback.get("reason"),
                "resolved_target": feedback.get("resolved_target", {}),
                "created_at": current.get("created_at") or now(),
                "updated_at": now(),
                "artifact_refs": governance_artifact_refs(codebase_id),
            }
            rules.append(rule)
        write_governance_rules(self.workspace, codebase_id, sorted(rules, key=lambda row: str(row.get("rule_id"))))
        overlay = self.build_overlay_report(codebase_id)
        return {"rules": rules, "overlay_report": overlay, "artifact_refs": governance_artifact_refs(codebase_id)}

    def review_rule(self, codebase_id: str, rule_id: str, *, status: str, reviewer: str = "", note: str = "") -> dict[str, Any]:
        self.registry.describe(codebase_id)
        normalized = str(status or "").strip()
        if normalized not in RULE_STATUSES:
            raise ValueError("INVALID_RULE_STATUS")
        rows = read_governance_rules(self.workspace, codebase_id)
        updated = []
        reviewed = None
        for row in rows:
            item = dict(row)
            if item.get("rule_id") == rule_id:
                item["status"] = normalized
                item["reviewer"] = reviewer or "unknown"
                item["review_note"] = note
                item["reviewed_at"] = now()
                item["updated_at"] = item["reviewed_at"]
                reviewed = item
            updated.append(item)
        if reviewed is None:
            raise FileNotFoundError("PLATFORM_GOVERNANCE_RULE_NOT_FOUND")
        write_governance_rules(self.workspace, codebase_id, updated)
        overlay = self.build_overlay_report(codebase_id)
        return {"rule": reviewed, "overlay_report": overlay, "artifact_refs": governance_artifact_refs(codebase_id)}

    def build_overlay_report(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        feedback_rows = read_governance_feedback(self.workspace, codebase_id)
        rules = read_governance_rules(self.workspace, codebase_id)
        approved = [row for row in rules if row.get("status") == "approved"]
        revoked = [row for row in rules if row.get("status") == "revoked"]
        source_hashes_before = _source_hashes(self.workspace, codebase_id)
        applied_rules = []
        for rule in approved:
            resolved = self.resolve_target(codebase_id, str(rule.get("target_type") or ""), str(rule.get("target_id") or ""))
            applied_rules.append(
                {
                    "rule_id": rule.get("rule_id"),
                    "target_type": rule.get("target_type"),
                    "target_id": rule.get("target_id"),
                    "effect": "read_time_overlay",
                    "suggested_value": rule.get("suggested_value"),
                    "resolved_target": resolved,
                }
            )
        source_hashes_after = _source_hashes(self.workspace, codebase_id)
        report = {
            "schema_version": GOVERNANCE_SCHEMA_VERSION,
            "artifact_type": "platform_governance_overlay_report",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "summary": {
                "feedback_count": len(feedback_rows),
                "rule_count": len(rules),
                "approved_rule_count": len(approved),
                "revoked_rule_count": len(revoked),
                "applied_rule_count": len(applied_rules),
                "source_artifact_hash_unchanged": source_hashes_before == source_hashes_after,
            },
            "applied_rules": applied_rules,
            "revoked_rule_ids": [row.get("rule_id") for row in revoked],
            "source_artifact_hash_before": source_hashes_before,
            "source_artifact_hash_after": source_hashes_after,
            "warnings": [] if source_hashes_before == source_hashes_after else ["SOURCE_ARTIFACT_HASH_CHANGED"],
            "unresolved": [],
            "artifact_refs": governance_artifact_refs(codebase_id),
            "created_at": now(),
        }
        write_governance_overlay_report(self.workspace, codebase_id, report)
        return report

    def read_overlay_report(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        try:
            return read_governance_overlay_report(self.workspace, codebase_id)
        except FileNotFoundError:
            return self.build_overlay_report(codebase_id)

    def resolve_target(self, codebase_id: str, target_type: str, target_id: str) -> dict[str, Any]:
        if target_type not in TARGET_TYPES:
            raise FileNotFoundError("PLATFORM_GOVERNANCE_TARGET_NOT_FOUND")
        if not str(target_id or "").strip():
            raise FileNotFoundError("PLATFORM_GOVERNANCE_TARGET_NOT_FOUND")
        if target_type == "platform_panel":
            console = read_console(self.workspace, codebase_id)
            for panel in console.get("panels", []):
                if panel.get("panel_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "title": panel.get("title")}
        if target_type == "artifact_contract":
            registry = read_contract_registry(self.workspace, codebase_id)
            for row in registry.get("contracts", []):
                if row.get("artifact_family") == target_id or row.get("artifact_path") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "status": row.get("status")}
        if target_type == "tool_guidance":
            catalog = read_tool_catalog(self.workspace, codebase_id)
            for row in catalog.get("tools", []):
                if row.get("tool_name") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "group_id": row.get("group_id")}
        if target_type == "workflow_guide_step":
            guides = read_workflow_guides(self.workspace, codebase_id)
            for guide in guides.get("guides", []):
                for step in guide.get("steps", []):
                    step_id = f"{guide.get('goal_id')}:{step.get('step_index')}:{step.get('tool_name')}"
                    if step_id == target_id:
                        return {"target_type": target_type, "target_id": target_id, "goal_id": guide.get("goal_id"), "tool_name": step.get("tool_name")}
        if target_type == "incremental_decision":
            for row in read_cache_decisions(self.workspace, codebase_id):
                if row.get("artifact_family") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "decision": row.get("decision")}
        if target_type == "provider_capability":
            capabilities = read_provider_capabilities(self.workspace, codebase_id)
            for row in capabilities.get("providers", []):
                if row.get("provider_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "status": row.get("status")}
        raise FileNotFoundError("PLATFORM_GOVERNANCE_TARGET_NOT_FOUND")


def public_governance_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": GOVERNANCE_SCHEMA_VERSION,
        "artifact_type": "platform_governance_bundle",
        "feedback": payload.get("feedback"),
        "rules": payload.get("rules"),
        "rule": payload.get("rule"),
        "overlay_report": payload.get("overlay_report") or payload.get("report") or payload,
        "artifact_refs": payload.get("artifact_refs", []),
    }


def _source_hashes(workspace: Path, codebase_id: str) -> dict[str, str]:
    paths = {
        "platform_console": console_payload_path(workspace, codebase_id),
    }
    return {name: _file_hash(path) for name, path in paths.items() if path.exists()}


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_id(prefix: str, *parts: Any) -> str:
    payload = json.dumps([str(part) for part in parts], sort_keys=True, ensure_ascii=False)
    return f"{prefix}_{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"
