"""Quality governance MCP tool schemas and handlers."""

from __future__ import annotations

from typing import Any, Callable

from .service import DataService


RULE_STATUSES = ["draft", "approved", "rejected", "archived", "revoked"]

QUALITY_TOOL_NAMES = {
    "knowledge_quality_summary",
    "knowledge_correction_plan",
    "knowledge_quality_feedback",
    "knowledge_correction_rules",
    "knowledge_review_correction_rule",
}

QUALITY_TOOL_SPECS = [
    {
        "name": "knowledge_quality_summary",
        "description": "Read quality governance summary, recent feedback, correction rules, and approved correction plan",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
            },
        },
    },
    {
        "name": "knowledge_correction_plan",
        "description": "Read or rebuild the approved quality correction plan with action impact scopes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "rebuild": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "knowledge_quality_feedback",
        "description": "Submit controlled quality feedback without mutating source data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "target_type": {"type": "string"},
                "target_id": {"type": "string"},
                "action": {"type": "string"},
                "label": {"type": "string"},
                "suggested_value": {"type": "string"},
                "reason": {"type": "string"},
                "metadata": {"type": "object"},
            },
            "required": ["target_type", "target_id", "action"],
        },
    },
    {
        "name": "knowledge_correction_rules",
        "description": "List quality correction rules, optionally filtered by review status",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "limit": {"type": "integer", "default": 100},
                "status": {"type": "string", "enum": RULE_STATUSES},
            },
        },
    },
    {
        "name": "knowledge_review_correction_rule",
        "description": "Review one quality correction rule and refresh the approved correction plan",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "rule_id": {"type": "string"},
                "status": {"type": "string", "enum": RULE_STATUSES},
                "reviewer": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["rule_id", "status"],
        },
    },
]


def handle_quality_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    service: DataService,
    bounded_int: Callable[..., int],
) -> dict[str, Any]:
    if name == "knowledge_quality_summary":
        bundle = service.read_summary_bundle()
        return {
            "workspace": str(service.workspace),
            "quality": bundle.get("quality", {}),
            "quality_feedback": bundle.get("quality_feedback", []),
            "quality_correction_rules": bundle.get("quality_correction_rules", []),
            "quality_correction_plan": bundle.get("quality_correction_plan", {}),
        }

    if name == "knowledge_correction_plan":
        return (
            service.build_quality_correction_plan()
            if bool(arguments.get("rebuild", False))
            else service.read_quality_correction_plan(build_if_missing=False)
        )

    if name == "knowledge_quality_feedback":
        return service.record_quality_feedback(
            target_type=arguments.get("target_type", ""),
            target_id=arguments.get("target_id", ""),
            action=arguments.get("action", ""),
            label=arguments.get("label", ""),
            suggested_value=arguments.get("suggested_value", ""),
            reason=arguments.get("reason", ""),
            metadata=arguments.get("metadata") or {},
        )

    if name == "knowledge_correction_rules":
        return service.read_quality_correction_rules(
            limit=bounded_int(arguments.get("limit"), default=100, minimum=1, maximum=500, field="limit"),
            status=arguments.get("status"),
        )

    if name == "knowledge_review_correction_rule":
        return service.review_quality_correction_rule(
            rule_id=arguments.get("rule_id", ""),
            status=arguments.get("status", ""),
            reviewer=arguments.get("reviewer", ""),
            note=arguments.get("note", ""),
        )

    raise ValueError(f"Unknown quality MCP tool: {name}")
