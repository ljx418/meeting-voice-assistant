"""V3.6 workflow runtime error schema drafts."""

from __future__ import annotations

from typing import Any, Dict, List

from core.protocol.contracts.workflow_error_inventory import WORKFLOW_ERROR_INVENTORY


def _schema(entry: Dict[str, Any]) -> Dict[str, Any]:
    retryable = bool(entry["retryable"])
    return {
        "code": entry["code"],
        "http_status": 409 if "CONFLICT" in str(entry["code"]) or "IMMUTABLE" in str(entry["code"]) else 404,
        "message_template": str(entry["code"]).replace("_", " ").title() + ".",
        "retryable": retryable,
        "sdk_exception": "WorkflowRuntimeError",
        "data_schema": {"type": "object", "additionalProperties": True},
        "status": entry["status"],
        "category": entry["category"],
        "planned_phase": entry["planned_phase"],
        "family": entry["family"],
        "introduced_in": entry["introduced_in"],
    }


WORKFLOW_ERROR_SCHEMAS: List[Dict[str, Any]] = [_schema(entry) for entry in WORKFLOW_ERROR_INVENTORY]

