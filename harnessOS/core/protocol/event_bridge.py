"""V3.5 local Browser Event Bridge helpers.

This module implements persisted replay plus a local follow transport helper.
It is not a distributed event bus and does not guarantee multi-worker real-time
ordering.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from core.apps.scope import ScopeContext
from core.protocol.schemas.errors import ProtocolError


DEFAULT_CHANNELS = ("chat", "job", "artifact", "approval")
SUPPORTED_CHANNELS = ("chat", "job", "artifact", "approval", "trace", "business", "workflow_context", "workflow_patch")
CHANNEL_CAPABILITIES = {
    "chat": {"events", "turns"},
    "job": {"events", "jobs"},
    "artifact": {"events", "artifacts"},
    "approval": {"events", "approvals"},
    "trace": {"events", "traces.read"},
    "business": {"events", "business_events.read"},
    "workflow_context": {"events", "workflow_context.read"},
    "workflow_patch": {"events", "workflow_patches.read"},
}


def normalize_event_channels(value: Any) -> list[str]:
    """Normalize comma-separated or list channel input."""
    if value is None or value == "":
        channels = list(DEFAULT_CHANNELS)
    elif isinstance(value, str):
        channels = [part.strip() for part in value.split(",") if part.strip()]
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        channels = [item.strip() for item in value if item.strip()]
    else:
        raise ProtocolError("INVALID_PARAMS", "channels must be a string list or comma-separated string.", {"field": "channels"})
    unsupported = [channel for channel in channels if channel not in SUPPORTED_CHANNELS]
    if unsupported:
        raise ProtocolError("INVALID_PARAMS", "Unsupported event channel.", {"channels": unsupported})
    return sorted(set(channels), key=channels.index)


def ensure_channel_capabilities(channels: Iterable[str], capabilities: Iterable[str]) -> None:
    """Ensure a capability token can subscribe to all requested channels."""
    available = set(capabilities)
    for channel in channels:
        required = CHANNEL_CAPABILITIES.get(channel, {"events"})
        missing = sorted(required - available)
        if missing:
            raise ProtocolError(
                "CAPABILITY_DENIED",
                "Capability token cannot subscribe to requested event channel.",
                {"channel": channel, "missing_capabilities": missing},
            )


def make_event_cursor(scope: ScopeContext, sequence: int, *, secret: Optional[str] = None) -> str:
    """Create an opaque, scope-bound event cursor."""
    payload = {
        "scope": scope.to_dict(),
        "sequence": sequence,
    }
    raw = _json(payload)
    signature = _sign(raw, _resolve_secret(secret))
    return f"{_b64(raw)}.{_b64(signature)}"


def read_event_cursor(cursor: Optional[str], scope: ScopeContext, *, secret: Optional[str] = None) -> int:
    """Read a cursor sequence after validating scope binding."""
    if not cursor:
        return -1
    try:
        payload_part, signature_part = cursor.split(".", 1)
        raw = _unb64(payload_part)
        signature = _unb64(signature_part)
    except Exception as exc:
        raise ProtocolError("EVENT_CURSOR_INVALID", "Event cursor is invalid.", {"reason": "malformed_cursor"}) from exc
    if not hmac.compare_digest(signature, _sign(raw, _resolve_secret(secret))):
        raise ProtocolError("EVENT_CURSOR_INVALID", "Event cursor is invalid.", {"reason": "invalid_signature"})
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ProtocolError("EVENT_CURSOR_INVALID", "Event cursor is invalid.", {"reason": "invalid_payload"}) from exc
    cursor_scope = payload.get("scope") if isinstance(payload, dict) else None
    if cursor_scope != scope.to_dict():
        raise ProtocolError("SCOPE_MISMATCH", "Event cursor does not match requested scope.", {"reason": "cursor_scope_mismatch"})
    sequence = payload.get("sequence")
    if not isinstance(sequence, int) or sequence < -1:
        raise ProtocolError("EVENT_CURSOR_INVALID", "Event cursor is invalid.", {"reason": "invalid_sequence"})
    return sequence


def collect_event_envelopes(
    gateway: Any,
    *,
    scope: ScopeContext,
    channels: Iterable[str],
    filters: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    """Collect replayable event envelopes from local persisted records."""
    filters = filters or {}
    records: list[dict[str, Any]] = []
    channel_set = set(channels)
    if "chat" in channel_set:
        records.extend(_chat_events(gateway, scope=scope, filters=filters))
    if "job" in channel_set:
        records.extend(_job_events(gateway, scope=scope, filters=filters))
    if "artifact" in channel_set:
        records.extend(_artifact_events(gateway, scope=scope, filters=filters))
    if "approval" in channel_set:
        records.extend(_approval_events(gateway, scope=scope, filters=filters))
    if "trace" in channel_set:
        records.extend(_trace_events(gateway, scope=scope, filters=filters))
    if "business" in channel_set:
        records.extend(_business_events(gateway, scope=scope, filters=filters))
    if "workflow_context" in channel_set:
        records.extend(_workflow_context_events(gateway, scope=scope, filters=filters))
    if "workflow_patch" in channel_set:
        records.extend(_workflow_patch_events(gateway, scope=scope, filters=filters))
    records = _dedupe(records)
    records.sort(key=lambda event: (str(event.get("timestamp") or ""), str(event.get("event_id") or "")))
    for index, event in enumerate(records):
        event["cursor"] = make_event_cursor(scope, index)
    return records


def sse_frame(event: dict[str, Any]) -> str:
    """Serialize one event envelope as an SSE frame."""
    return (
        f"id: {event['cursor']}\n"
        f"event: {event['type']}\n"
        f"data: {json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}\n\n"
    )


def heartbeat_frame() -> str:
    """Return an SSE heartbeat comment that is not persisted."""
    return ": heartbeat\n\n"


def _chat_events(gateway: Any, *, scope: ScopeContext, filters: dict[str, Any]) -> list[dict[str, Any]]:
    session_ids = []
    if isinstance(filters.get("session_id"), str):
        session_ids = [filters["session_id"]]
    else:
        for session in gateway.runtime_pool.list_sessions():
            if _matches_scope(session, scope) and isinstance(session.get("session_id"), str):
                session_ids.append(session["session_id"])
    events: list[dict[str, Any]] = []
    for session_id in session_ids:
        for raw in gateway.runtime_pool.read_events(session_id):
            if not isinstance(raw, dict) or str(raw.get("type") or "") not in {"turn.started", "item.delta", "turn.completed", "turn.failed"}:
                continue
            if not _matches_scope(raw, scope):
                continue
            if filters.get("turn_id") and raw.get("turn_id") != filters.get("turn_id"):
                continue
            events.append(
                _envelope(
                    event_id=str(raw.get("item_id") or raw.get("event_id") or f"chat:{session_id}:{raw.get('type')}:{raw.get('timestamp')}"),
                    event_type=str(raw["type"]),
                    channel="chat",
                    scope=scope,
                    timestamp=str(raw.get("timestamp") or raw.get("created_at") or _now()),
                    session_id=session_id,
                    turn_id=raw.get("turn_id"),
                    data={k: v for k, v in raw.items() if k not in {"app_id", "project_id", "workspace_id"}},
                )
            )
    return events


def _job_events(gateway: Any, *, scope: ScopeContext, filters: dict[str, Any]) -> list[dict[str, Any]]:
    raw_events = gateway.core_service.list_job_events(
        job_id=filters.get("job_id"),
        app_id=scope.app_id,
        project_id=scope.project_id,
        workspace_id=scope.workspace_id,
    )
    events = []
    for record in raw_events:
        raw = _dump(record)
        event_type = _job_event_type(str(raw.get("status") or raw.get("event_type") or ""))
        events.append(
            _envelope(
                event_id=str(raw.get("event_id") or f"job:{raw.get('job_id')}:{event_type}:{raw.get('created_at')}"),
                event_type=event_type,
                channel="job",
                scope=scope,
                timestamp=str(raw.get("created_at") or _now()),
                job_id=raw.get("job_id"),
                data=raw,
            )
        )
    return events


def _artifact_events(gateway: Any, *, scope: ScopeContext, filters: dict[str, Any]) -> list[dict[str, Any]]:
    records = gateway.artifact_registry.list_artifacts(
        session_id=filters.get("session_id"),
        app_id=scope.app_id,
        project_id=scope.project_id,
        workspace_id=scope.workspace_id,
    )
    events = []
    for raw in records:
        if filters.get("artifact_id") and raw.get("artifact_id") != filters.get("artifact_id"):
            continue
        events.append(
            _envelope(
                event_id=f"artifact:{raw.get('artifact_id')}:registered",
                event_type="artifact.registered",
                channel="artifact",
                scope=scope,
                timestamp=str(raw.get("created_at") or _now()),
                session_id=raw.get("session_id") or raw.get("owner_session_id"),
                turn_id=raw.get("turn_id") or raw.get("owner_turn_id"),
                artifact_id=raw.get("artifact_id"),
                data=raw,
            )
        )
    trace_records = gateway.core_service.list_trace_records(
        trace_id=filters.get("trace_id"),
        session_id=filters.get("session_id"),
        turn_id=filters.get("turn_id"),
        event_type="artifact.read",
        app_id=scope.app_id,
        project_id=scope.project_id,
        workspace_id=scope.workspace_id,
    )
    for record in trace_records:
        raw = _dump(record)
        if raw.get("status") != "blocked":
            continue
        artifact_ids = raw.get("artifact_ids") if isinstance(raw.get("artifact_ids"), list) else []
        artifact_id = artifact_ids[0] if artifact_ids and isinstance(artifact_ids[0], str) else None
        if filters.get("artifact_id") and artifact_id != filters.get("artifact_id"):
            continue
        events.append(
            _envelope(
                event_id=str(raw.get("record_id") or f"artifact:{artifact_id}:read_blocked:{raw.get('created_at')}"),
                event_type="artifact.read_blocked",
                channel="artifact",
                scope=scope,
                timestamp=str(raw.get("created_at") or _now()),
                session_id=raw.get("session_id"),
                turn_id=raw.get("turn_id"),
                artifact_id=artifact_id,
                trace_id=raw.get("trace_id"),
                data=raw,
            )
        )
    return events


def _approval_events(gateway: Any, *, scope: ScopeContext, filters: dict[str, Any]) -> list[dict[str, Any]]:
    records = gateway.approval_store.list_approvals(
        app_id=scope.app_id,
        project_id=scope.project_id,
        workspace_id=scope.workspace_id,
    )
    events = []
    for raw in records:
        if filters.get("approval_id") and raw.get("approval_id") != filters.get("approval_id"):
            continue
        event_type = {
            "approved": "approval.approved",
            "rejected": "approval.rejected",
        }.get(str(raw.get("status") or ""), "approval.required")
        data = dict(raw)
        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        workflow_binding = metadata.get("workflow_binding") if isinstance(metadata, dict) else None
        if isinstance(workflow_binding, dict):
            data["workflow_binding"] = dict(workflow_binding)
        events.append(
            _envelope(
                event_id=f"approval:{raw.get('approval_id')}:{event_type}",
                event_type=event_type,
                channel="approval",
                scope=scope,
                timestamp=str(raw.get("decided_at") or raw.get("created_at") or _now()),
                session_id=raw.get("session_id"),
                turn_id=raw.get("turn_id"),
                approval_id=raw.get("approval_id"),
                trace_id=raw.get("trace_id"),
                data=data,
            )
        )
    return events


def _trace_events(gateway: Any, *, scope: ScopeContext, filters: dict[str, Any]) -> list[dict[str, Any]]:
    raw_events = gateway.core_service.list_trace_records(
        trace_id=filters.get("trace_id"),
        session_id=filters.get("session_id"),
        turn_id=filters.get("turn_id"),
        app_id=scope.app_id,
        project_id=scope.project_id,
        workspace_id=scope.workspace_id,
    )
    events = []
    for record in raw_events:
        raw = _dump(record)
        events.append(
            _envelope(
                event_id=str(raw.get("record_id") or f"trace:{raw.get('trace_id')}:{raw.get('created_at')}"),
                event_type="trace.recorded",
                channel="trace",
                scope=scope,
                timestamp=str(raw.get("created_at") or _now()),
                session_id=raw.get("session_id"),
                turn_id=raw.get("turn_id"),
                trace_id=raw.get("trace_id"),
                data=raw,
            )
        )
    return events


def _business_events(gateway: Any, *, scope: ScopeContext, filters: dict[str, Any]) -> list[dict[str, Any]]:
    return _workflow_trace_backed_events(
        gateway,
        scope=scope,
        filters=filters,
        event_type="business.event.received",
        channel="business",
    )


def _workflow_context_events(gateway: Any, *, scope: ScopeContext, filters: dict[str, Any]) -> list[dict[str, Any]]:
    return _workflow_trace_backed_events(
        gateway,
        scope=scope,
        filters=filters,
        event_type="workflow.context.updated",
        channel="workflow_context",
    )


def _workflow_patch_events(gateway: Any, *, scope: ScopeContext, filters: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for event_type in ("workflow.patch.proposed", "workflow.patch.applied", "workflow.patch.rejected"):
        events.extend(
            _workflow_trace_backed_events(
                gateway,
                scope=scope,
                filters=filters,
                event_type=event_type,
                channel="workflow_patch",
            )
        )
    return events


def _workflow_trace_backed_events(
    gateway: Any,
    *,
    scope: ScopeContext,
    filters: dict[str, Any],
    event_type: str,
    channel: str,
) -> list[dict[str, Any]]:
    raw_events = gateway.trace_store.list_records(
        trace_id=filters.get("trace_id"),
        event_type=event_type,
        app_id=scope.app_id,
        project_id=scope.project_id,
        workspace_id=scope.workspace_id,
    )
    events = []
    for record in raw_events:
        raw = _dump(record)
        event = ((raw.get("metadata") or {}).get("event") or {}) if isinstance(raw.get("metadata"), dict) else {}
        data = event.get("data") if isinstance(event, dict) and isinstance(event.get("data"), dict) else raw
        workflow_instance_id = data.get("workflow_instance_id")
        if filters.get("workflow_instance_id") and workflow_instance_id != filters.get("workflow_instance_id"):
            continue
        workflow_patch_id = data.get("workflow_patch_id")
        if filters.get("workflow_patch_id") and workflow_patch_id != filters.get("workflow_patch_id"):
            continue
        events.append(
            _envelope(
                event_id=str(raw.get("record_id") or f"{event_type}:{workflow_instance_id}:{raw.get('created_at')}"),
                event_type=event_type,
                channel=channel,
                scope=scope,
                timestamp=str(raw.get("created_at") or _now()),
                trace_id=raw.get("trace_id"),
                workflow_instance_id=workflow_instance_id,
                workflow_patch_id=workflow_patch_id,
                data=data,
            )
        )
    return events


def _envelope(
    *,
    event_id: str,
    event_type: str,
    channel: str,
    scope: ScopeContext,
    timestamp: str,
    data: dict[str, Any],
    session_id: Any = None,
    turn_id: Any = None,
    job_id: Any = None,
    artifact_id: Any = None,
    approval_id: Any = None,
    trace_id: Any = None,
    workflow_instance_id: Any = None,
    workflow_patch_id: Any = None,
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "type": event_type,
        "channel": channel,
        "cursor": "",
        "timestamp": timestamp,
        "scope": scope.to_dict(),
        "session_id": session_id if isinstance(session_id, str) else None,
        "turn_id": turn_id if isinstance(turn_id, str) else None,
        "job_id": job_id if isinstance(job_id, str) else None,
        "artifact_id": artifact_id if isinstance(artifact_id, str) else None,
        "approval_id": approval_id if isinstance(approval_id, str) else None,
        "trace_id": trace_id if isinstance(trace_id, str) else None,
        "workflow_instance_id": workflow_instance_id if isinstance(workflow_instance_id, str) else None,
        "workflow_patch_id": workflow_patch_id if isinstance(workflow_patch_id, str) else None,
        "data": data,
    }


def _job_event_type(status: str) -> str:
    if status in {"queued", "running", "completed", "failed", "cancelled"}:
        return f"job.{status}"
    if status.startswith("job."):
        return status
    return "job.running"


def _dedupe(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    deduped = []
    for event in events:
        key = (event.get("channel"), event.get("event_id"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(event)
    return deduped


def _matches_scope(record: dict[str, Any], scope: ScopeContext) -> bool:
    return (
        record.get("app_id", "default") == scope.app_id
        and record.get("project_id") == scope.project_id
        and record.get("workspace_id") == scope.workspace_id
    )


def _dump(record: Any) -> dict[str, Any]:
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    return dict(record)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_secret(secret: Optional[str]) -> bytes:
    value = secret if secret is not None else os.getenv("HARNESS_CAPABILITY_TOKEN_SECRET")
    if not value:
        raise ProtocolError("AUTH_INVALID", "Capability token secret is not configured.", {"reason": "auth_not_configured"})
    return value.encode("utf-8")


def _json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign(payload: bytes, secret: bytes) -> bytes:
    return hmac.new(secret, payload, hashlib.sha256).digest()


def _b64(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _unb64(payload: str) -> bytes:
    return base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
