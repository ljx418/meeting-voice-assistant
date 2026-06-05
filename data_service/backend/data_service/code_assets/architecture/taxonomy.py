"""V2.6 architecture taxonomy builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json

from ..artifacts import architecture_taxonomy_override_path


SCHEMA_VERSION = "v2.6"
DEFAULT_ROLE_TYPES = ["interface", "application", "domain", "infrastructure", "governance", "runtime", "artifact", "test", "docs"]
DEFAULT_LAYER_TYPES = ["interface", "application", "domain", "infrastructure", "governance", "runtime", "artifact", "test", "docs", "unknown"]
DEFAULT_BOUNDARY_TYPES = ["module_boundary", "service_boundary", "api_boundary", "storage_boundary", "runtime_boundary", "unknown_boundary"]
DEFAULT_PATTERN_TYPES = ["api_surface", "mcp_surface", "cli_surface", "frontend_surface", "provider_adapter", "artifact_pipeline", "unknown_pattern"]


def build_default_taxonomy(*, workspace: Path, workspace_id: str, codebase_id: str) -> dict[str, Any]:
    taxonomy = {
        "schema_version": SCHEMA_VERSION,
        "taxonomy_id": f"taxonomy:{workspace_id}:{codebase_id}:default",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "role_types": list(DEFAULT_ROLE_TYPES),
        "layer_types": list(DEFAULT_LAYER_TYPES),
        "boundary_types": list(DEFAULT_BOUNDARY_TYPES),
        "pattern_types": list(DEFAULT_PATTERN_TYPES),
        "review_reasons": [
            "low_confidence",
            "missing_evidence",
            "unsupported_semantic_claim",
            "conflicting_signals",
            "large_artifact_summary_only",
            "redacted_sensitive_value",
            "unknown_config_type",
        ],
        "confidence_thresholds": {
            "accepted_min": 0.8,
            "needs_review_below": 0.8,
            "major_below": 0.5,
        },
        "override_source": None,
        "created_at": now(),
    }
    override = read_json(architecture_taxonomy_override_path(workspace, codebase_id), None)
    if isinstance(override, dict):
        taxonomy = _merge_override(taxonomy, override)
    return taxonomy


def _merge_override(default: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(default)
    for field in ("role_types", "layer_types", "boundary_types", "pattern_types", "review_reasons"):
        values = override.get(field)
        if isinstance(values, list):
            merged[field] = sorted(set(str(item) for item in [*default[field], *values] if str(item).strip()))
    thresholds = override.get("confidence_thresholds")
    if isinstance(thresholds, dict):
        merged_thresholds = dict(default["confidence_thresholds"])
        for key, value in thresholds.items():
            try:
                merged_thresholds[str(key)] = float(value)
            except (TypeError, ValueError):
                continue
        merged["confidence_thresholds"] = merged_thresholds
    merged["override_source"] = "architecture_taxonomy_override.json"
    return merged
