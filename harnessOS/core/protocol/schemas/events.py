"""V3.5 protocol event schema registry."""

from __future__ import annotations

from typing import Any, Dict, List

from core.protocol.contracts.event_inventory import EVENT_INVENTORY


EVENT_ENVELOPE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["event_id", "type", "channel", "cursor", "timestamp", "scope", "data"],
    "properties": {
        "event_id": {"type": "string"},
        "type": {"type": "string"},
        "channel": {"type": "string"},
        "cursor": {"type": "string"},
        "timestamp": {"type": "string"},
        "scope": {"type": "object"},
        "session_id": {"type": ["string", "null"]},
        "turn_id": {"type": ["string", "null"]},
        "job_id": {"type": ["string", "null"]},
        "artifact_id": {"type": ["string", "null"]},
        "approval_id": {"type": ["string", "null"]},
        "trace_id": {"type": ["string", "null"]},
        "data": {"type": "object", "additionalProperties": True},
    },
}


EVENT_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": entry["type"],
        "channel": entry["channel"],
        "status": entry["status"],
        "replayable": entry["replayable"],
        "aliases": entry["aliases"],
        "envelope_schema": EVENT_ENVELOPE_SCHEMA,
        "data_schema": {"type": "object", "additionalProperties": True},
    }
    for entry in EVENT_INVENTORY
]


def get_event_schema(event_type: str) -> Dict[str, Any]:
    for schema in EVENT_SCHEMAS:
        if schema["type"] == event_type:
            return schema
    raise KeyError(f"Event schema not found: {event_type}")
