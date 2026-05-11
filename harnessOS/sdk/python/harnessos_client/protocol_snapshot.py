"""SDK-local protocol surface snapshot.

The runtime SDK must not import harnessOS server internals. Tests compare this
snapshot against the server schema registry.
"""

from __future__ import annotations

DEFAULT_METHODS = {
    "session.start",
    "turn.start",
    "events.subscribe",
    "artifact.list",
    "artifact.read_metadata",
    "artifact.register_external",
    "artifact.lineage",
    "job.get",
    "job.list",
    "approval.respond",
    "connector.health",
    "pack.list",
    "pack.get",
}

FORBIDDEN_PATTERNS = (
    "meeting.",
    "knowledge.",
)

FORBIDDEN_METHODS = {
    "approval.approve",
    "approval.reject",
    "workflow.execute_stub",
    "pack.execute_stub",
    "meeting.process_recording",
    "meeting.process_audio_dir",
    "meeting.analyze_text",
    "meeting.capabilities",
}

WRAPPER_METHODS = {
    "session_start": "session.start",
    "turn_start": "turn.start",
    "events_subscribe": "events.subscribe",
    "artifact_list": "artifact.list",
    "artifact_read_metadata": "artifact.read_metadata",
    "artifact_register_external": "artifact.register_external",
    "artifact_lineage": "artifact.lineage",
    "job_get": "job.get",
    "job_list": "job.list",
    "approval_respond": "approval.respond",
    "connector_health": "connector.health",
    "pack_list": "pack.list",
    "pack_get": "pack.get",
}


def is_default_method(method: str) -> bool:
    return method in DEFAULT_METHODS


def is_forbidden_method(method: str) -> bool:
    return method in FORBIDDEN_METHODS or any(method.startswith(prefix) for prefix in FORBIDDEN_PATTERNS)
