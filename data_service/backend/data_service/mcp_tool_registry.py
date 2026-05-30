"""MCP tool registry specs for data_service."""

from __future__ import annotations

from .mcp_build_tools import BUILD_TOOL_SPECS
from .mcp_code_tools import CODE_TOOL_SPECS
from .mcp_core_tools import CORE_TOOL_SPECS
from .mcp_quality_tools import QUALITY_TOOL_SPECS, RULE_STATUSES
from .mcp_session_tools import SESSION_TOOL_SPECS
from .mcp_source_tools import SOURCE_TOOL_SPECS
from .mcp_workspace_tools import WORKSPACE_TOOL_SPECS
from .models import QueryMode


V2_TOOL_MAP = {
    "knowledge_ingest_v2": "knowledge_ingest",
    "knowledge_query_v2": "knowledge_query",
    "knowledge_quality_summary_v2": "knowledge_quality_summary",
    "knowledge_correction_plan_v2": "knowledge_correction_plan",
    "knowledge_quality_feedback_v2": "knowledge_quality_feedback",
    "knowledge_correction_rules_v2": "knowledge_correction_rules",
    "knowledge_review_correction_rule_v2": "knowledge_review_correction_rule",
}


V2_TOOL_SPECS = [
    {
        "name": "knowledge_ingest_v2",
        "description": "Envelope-wrapped knowledge_ingest for external MCP clients",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {"type": "array", "items": {"type": "string"}},
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
            },
            "required": ["paths"],
        },
    },
    {
        "name": "knowledge_query_v2",
        "description": "Envelope-wrapped knowledge_query for external MCP clients",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "mode": {"type": "string", "enum": [mode.value for mode in QueryMode]},
                "top_k": {"type": "integer", "default": 8},
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "knowledge_quality_summary_v2",
        "description": "Envelope-wrapped knowledge_quality_summary for external MCP clients",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
            },
        },
    },
    {
        "name": "knowledge_correction_plan_v2",
        "description": "Envelope-wrapped knowledge_correction_plan for external MCP clients",
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
        "name": "knowledge_quality_feedback_v2",
        "description": "Envelope-wrapped knowledge_quality_feedback for external MCP clients",
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
        "name": "knowledge_correction_rules_v2",
        "description": "Envelope-wrapped knowledge_correction_rules for external MCP clients",
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
        "name": "knowledge_review_correction_rule_v2",
        "description": "Envelope-wrapped knowledge_review_correction_rule for external MCP clients",
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


def all_tool_specs() -> list[dict]:
    return [
        *CORE_TOOL_SPECS,
        *QUALITY_TOOL_SPECS,
        *V2_TOOL_SPECS,
        *CODE_TOOL_SPECS,
        *WORKSPACE_TOOL_SPECS,
        *SOURCE_TOOL_SPECS,
        *BUILD_TOOL_SPECS,
        *SESSION_TOOL_SPECS,
    ]
