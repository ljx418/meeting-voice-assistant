"""V3.6 workflow runtime event schema drafts."""

from __future__ import annotations

from typing import Any, Dict, List

from core.protocol.contracts.workflow_event_inventory import WORKFLOW_EVENT_INVENTORY

WORKFLOW_EVENT_ENVELOPE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["event_id", "type", "channel", "cursor", "timestamp", "scope", "data"],
    "properties": {
        "event_id": {"type": "string"},
        "type": {"type": "string"},
        "channel": {"type": "string"},
        "cursor": {"type": "string"},
        "timestamp": {"type": "string"},
        "scope": {"type": "object"},
        "workflow_template_id": {"type": ["string", "null"]},
        "workflow_instance_id": {"type": ["string", "null"]},
        "station_run_id": {"type": ["string", "null"]},
        "artifact_id": {"type": ["string", "null"]},
        "approval_id": {"type": ["string", "null"]},
        "quality_evaluation_id": {"type": ["string", "null"]},
        "workflow_patch_id": {"type": ["string", "null"]},
        "trace_id": {"type": ["string", "null"]},
        "data": {"type": "object", "additionalProperties": True},
    },
}


WORKFLOW_EVENT_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": entry["type"],
        "channel": entry["channel"],
        "status": entry["status"],
        "replayable": entry["replayable"],
        "aliases": entry["aliases"],
        "planned_phase": entry["planned_phase"],
        "family": entry["family"],
        "introduced_in": entry["introduced_in"],
        "envelope_schema": WORKFLOW_EVENT_ENVELOPE_SCHEMA,
        "data_schema": {"type": "object", "additionalProperties": True},
    }
    for entry in WORKFLOW_EVENT_INVENTORY
]

