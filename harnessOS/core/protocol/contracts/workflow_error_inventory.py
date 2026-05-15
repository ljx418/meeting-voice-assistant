"""V3.6 workflow runtime error inventory.

non-runtime contract metadata only; no handler registration; no behavior change
"""

from __future__ import annotations

from typing import Any, Dict, List

WorkflowErrorEntry = Dict[str, Any]

FAMILY = "workflow_runtime"
INTRODUCED_IN = "V3.6"


def _error(code: str, category: str, planned_phase: str, *, retryable: bool = False) -> WorkflowErrorEntry:
    return {
        "code": code,
        "status": "planned",
        "category": category,
        "retryable": retryable,
        "planned_phase": planned_phase,
        "family": FAMILY,
        "introduced_in": INTRODUCED_IN,
    }


WORKFLOW_ERROR_INVENTORY: List[WorkflowErrorEntry] = [
    _error("WORKFLOW_TEMPLATE_ALREADY_EXISTS", "workflow", "V3.6-B"),
    _error("WORKFLOW_TEMPLATE_NOT_FOUND", "workflow", "V3.6-B"),
    _error("WORKFLOW_VERSION_NOT_FOUND", "workflow", "V3.6-B"),
    _error("WORKFLOW_DRAFT_NOT_FOUND", "workflow", "V3.6-B"),
    _error("WORKFLOW_DRAFT_CONFLICT", "workflow", "V3.6-B"),
    _error("WORKFLOW_VERSION_CONFLICT", "workflow", "V3.6-B"),
    _error("WORKFLOW_TEMPLATE_ARCHIVED", "workflow", "V3.6-B"),
    _error("WORKFLOW_SCHEMA_INVALID", "workflow", "V3.6-B"),
    _error("WORKFLOW_INSTANCE_NOT_FOUND", "workflow", "V3.6-C"),
    _error("STATION_NOT_FOUND", "station", "V3.6-C"),
    _error("STATION_RUN_NOT_FOUND", "station", "V3.6-C"),
    _error("QUALITY_EVALUATION_NOT_FOUND", "quality", "V3.6-F"),
    _error("QUALITY_EVALUATION_INVALID", "quality", "V3.6-F"),
    _error("QUALITY_EVALUATION_UNSUPPORTED", "quality", "V3.6-F"),
    _error("QUALITY_EVALUATION_ALREADY_ATTACHED", "quality", "V3.6-F"),
    _error("WORKFLOW_CONTEXT_NOT_FOUND", "workflow_context", "V3.6-H"),
    _error("WORKFLOW_PATCH_NOT_FOUND", "workflow_patch", "V3.6-I"),
    _error("WORKFLOW_INVALID_STATE", "workflow", "V3.6-C"),
    _error("WORKFLOW_PUBLISHED_IMMUTABLE", "workflow", "V3.6-B"),
    _error("WORKFLOW_PATCH_CONFLICT", "workflow_patch", "V3.6-I"),
    _error("WORKFLOW_PATCH_INVALID", "workflow_patch", "V3.6-I"),
    _error("WORKFLOW_ACTION_FORBIDDEN", "workflow", "V3.6-C"),
    _error("WORKFLOW_RUNTIME_UNSUPPORTED", "workflow", "V3.6-C"),
    _error("WORKFLOW_EXECUTION_FAILED", "workflow", "V3.6-C", retryable=True),
    _error("WORKFLOW_APPROVAL_REQUIRED", "approval", "V3.6-D"),
    _error("WORKFLOW_APPROVAL_INACTIVE", "approval", "V3.6-D"),
    _error("WORKFLOW_APPROVAL_SIDE_EFFECT_FAILED", "approval", "V3.6-D", retryable=True),
    _error("WORKFLOW_ARTIFACT_CONTRACT_MISSING", "artifact", "V3.6-E"),
    _error("WORKFLOW_ARTIFACT_CONTRACT_INVALID", "artifact", "V3.6-E"),
    _error("WORKFLOW_ARTIFACT_INPUT_MISSING", "artifact", "V3.6-E"),
    _error("WORKFLOW_ARTIFACT_OUTPUT_INVALID", "artifact", "V3.6-E"),
    _error("WORKFLOW_ARTIFACT_KIND_MISMATCH", "artifact", "V3.6-E"),
    _error("WORKFLOW_ARTIFACT_REGISTRATION_FAILED", "artifact", "V3.6-E", retryable=True),
    _error("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "workflow_context", "V3.6-H"),
    _error("WORKFLOW_CONTEXT_CONFLICT", "workflow_context", "V3.6-H"),
    _error("BUSINESS_EVENT_INVALID", "business_event", "V3.6-H"),
    _error("BUSINESS_EVENT_UNBOUND", "business_event", "V3.6-H"),
    _error("BUSINESS_EVENT_ALREADY_APPLIED", "business_event", "V3.6-H"),
    _error("BUSINESS_EVENT_BINDING_NOT_FOUND", "business_event", "V3.6-H"),
    _error("BUSINESS_EVENT_BINDING_INVALID", "business_event", "V3.6-H"),
    _error("BOARD_NOT_AVAILABLE", "board", "V3.6-G", retryable=True),
]
