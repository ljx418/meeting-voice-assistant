"""Models and constants for V2.1 code quality governance."""

from __future__ import annotations

import hashlib
import json
from typing import Any


QUALITY_SCHEMA_VERSION = "v2.1"

SUPPORTED_TARGET_TYPES = {
    "codebase",
    "repo_snapshot",
    "code_file",
    "code_symbol",
    "code_route",
    "code_mcp_tool",
    "code_cli_command",
    "public_surface",
    "capability",
    "devwiki_page",
    "devwiki_section",
    "agent_context_pack",
    "agent_context_item",
    "code_graph_node",
    "code_graph_edge",
    "architecture_role",
    "architecture_layer",
    "architecture_boundary",
    "architecture_pattern",
    "architecture_drift_finding",
    "architecture_doc",
    "architecture_doc_claim",
    "architecture_doc_relation",
    "architecture_doc_quality_finding",
    "architecture_doc_code_alignment",
    "architecture_reconstructed_node",
    "architecture_reconstructed_edge",
}

SUPPORTED_RULE_TYPES = {
    "wrong_summary",
    "missing_evidence",
    "stale_snapshot",
    "wrong_capability_mapping",
    "wrong_surface_mapping",
    "missing_public_surface",
    "doc_code_mismatch",
    "low_confidence_inference",
    "overbroad_architecture_claim",
    "missing_acceptance_gate",
    "wrong_target_current_split",
    "unsafe_rendered_output",
    "broken_cross_link",
    "stale_document",
    "overbroad_agent_context",
    "unsafe_path_exposure",
}

SUPPORTED_REVIEW_STATUSES = {"approved", "rejected", "revoked"}


def validate_target_type(target_type: str) -> str:
    normalized = str(target_type or "").strip()
    if normalized not in SUPPORTED_TARGET_TYPES:
        raise ValueError("UNSUPPORTED_TARGET_TYPE")
    return normalized


def validate_rule_type(rule_type: str) -> str:
    normalized = str(rule_type or "").strip()
    if normalized not in SUPPORTED_RULE_TYPES:
        raise ValueError("UNSUPPORTED_RULE_TYPE")
    return normalized


def validate_review_status(status: str) -> str:
    normalized = str(status or "").strip()
    if normalized not in SUPPORTED_REVIEW_STATUSES:
        raise ValueError("UNSUPPORTED_REVIEW_STATUS")
    return normalized


def stable_id(prefix: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"
