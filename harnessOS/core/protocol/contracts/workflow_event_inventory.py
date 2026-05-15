"""V3.6 workflow runtime event inventory.

non-runtime contract metadata only; no handler registration; no behavior change
"""

from __future__ import annotations

from typing import Any, Dict, List

WorkflowEventEntry = Dict[str, Any]

FAMILY = "workflow_runtime"
INTRODUCED_IN = "V3.6"


def _event(event_type: str, channel: str, planned_phase: str, *, replayable: bool = True) -> WorkflowEventEntry:
    return {
        "type": event_type,
        "channel": channel,
        "status": "planned",
        "replayable": replayable,
        "aliases": (),
        "planned_phase": planned_phase,
        "family": FAMILY,
        "introduced_in": INTRODUCED_IN,
    }


WORKFLOW_EVENT_INVENTORY: List[WorkflowEventEntry] = [
    _event("workflow.template.created", "workflow", "V3.6-B"),
    _event("workflow.template.published", "workflow", "V3.6-B"),
    _event("workflow.instance.started", "workflow", "V3.6-C"),
    _event("workflow.instance.paused", "workflow", "V3.6-C"),
    _event("workflow.instance.resumed", "workflow", "V3.6-C"),
    _event("workflow.instance.completed", "workflow", "V3.6-C"),
    _event("workflow.instance.failed", "workflow", "V3.6-C"),
    _event("workflow.instance.cancelled", "workflow", "V3.6-C"),
    _event("station.run.started", "station", "V3.6-C"),
    _event("station.run.waiting_approval", "station", "V3.6-D"),
    _event("station.run.completed", "station", "V3.6-C"),
    _event("station.run.failed", "station", "V3.6-C"),
    _event("station.run.rerun_requested", "station", "V3.6-C"),
    _event("quality.evaluated", "quality", "V3.6-F"),
    _event("workflow.context.updated", "workflow_context", "V3.6-H"),
    _event("business.event.received", "business", "V3.6-H"),
    _event("workflow.patch.proposed", "workflow_patch", "V3.6-I"),
    _event("workflow.patch.applied", "workflow_patch", "V3.6-I"),
    _event("workflow.patch.rejected", "workflow_patch", "V3.6-I"),
    {
        "type": "business.*",
        "channel": "business",
        "status": "reserved",
        "replayable": False,
        "aliases": (),
        "planned_phase": "V3.6-H",
        "family": FAMILY,
        "introduced_in": INTRODUCED_IN,
    },
]

