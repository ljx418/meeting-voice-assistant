"""V3.5 event inventory.

non-runtime contract metadata only; no handler registration; no behavior change
"""

from __future__ import annotations

from typing import Any, Dict, List

EventEntry = Dict[str, Any]


EVENT_INVENTORY: List[EventEntry] = [
    {"type": "turn.started", "channel": "chat", "status": "implemented", "replayable": True, "aliases": ()},
    {"type": "item.delta", "channel": "chat", "status": "implemented", "replayable": True, "aliases": ()},
    {"type": "turn.completed", "channel": "chat", "status": "implemented", "replayable": True, "aliases": ()},
    {"type": "turn.failed", "channel": "chat", "status": "implemented", "replayable": True, "aliases": ()},
    {"type": "job.queued", "channel": "job", "status": "planned", "replayable": True, "aliases": ()},
    {"type": "job.running", "channel": "job", "status": "planned", "replayable": True, "aliases": ()},
    {"type": "job.completed", "channel": "job", "status": "planned", "replayable": True, "aliases": ()},
    {"type": "job.failed", "channel": "job", "status": "planned", "replayable": True, "aliases": ()},
    {"type": "job.cancelled", "channel": "job", "status": "planned", "replayable": True, "aliases": ()},
    {
        "type": "artifact.registered",
        "channel": "artifact",
        "status": "planned",
        "replayable": True,
        "aliases": ("artifact.created",),
    },
    {"type": "artifact.updated", "channel": "artifact", "status": "planned", "replayable": True, "aliases": ()},
    {
        "type": "artifact.read_blocked",
        "channel": "artifact",
        "status": "planned",
        "replayable": True,
        "aliases": (),
    },
    {"type": "approval.required", "channel": "approval", "status": "implemented", "replayable": True, "aliases": ()},
    {"type": "approval.approved", "channel": "approval", "status": "implemented", "replayable": True, "aliases": ()},
    {"type": "approval.rejected", "channel": "approval", "status": "implemented", "replayable": True, "aliases": ()},
    {"type": "trace.recorded", "channel": "trace", "status": "planned", "replayable": True, "aliases": ()},
    {"type": "business.*", "channel": "business", "status": "reserved", "replayable": False, "aliases": ()},
]
