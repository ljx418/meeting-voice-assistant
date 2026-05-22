"""Dev/local Agent action handoff repository for the Workflow Console BFF."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock
from typing import Any, Protocol

from core.protocol.schemas.errors import ProtocolError


HANDOFF_ACTIVE_STATES = {"active", "opened"}
HANDOFF_TERMINAL_STATES = {"used_for_user_confirmed_action", "dismissed", "expired", "stale", "blocked"}
HANDOFF_STATES = HANDOFF_ACTIVE_STATES | HANDOFF_TERMINAL_STATES
SENSITIVE_KEY_PARTS = (
    "token",
    "authorization",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
)


class AgentHandoffRepository(Protocol):
    """Repository boundary for Agent action handoffs."""

    def create(self, handoff: dict[str, Any]) -> dict[str, Any]:
        ...

    def get(self, handoff_id: str) -> dict[str, Any]:
        ...

    def list(self, *, agent_session_id: str | None = None, workflow_instance_id: str | None = None) -> list[dict[str, Any]]:
        ...

    def mark_opened(self, handoff_id: str) -> dict[str, Any]:
        ...

    def mark_used(self, handoff_id: str) -> dict[str, Any]:
        ...

    def dismiss(self, handoff_id: str) -> dict[str, Any]:
        ...

    def expire(self, handoff_id: str, *, reason: str | None = None) -> dict[str, Any]:
        ...

    def mark_stale(self, handoff_id: str, *, reason: str) -> dict[str, Any]:
        ...

    def mark_blocked(self, handoff_id: str, *, reason: str) -> dict[str, Any]:
        ...

    def append_audit(self, handoff_id: str, event_type: str, *, summary: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        ...

    def list_audit(self, handoff_id: str) -> list[dict[str, Any]]:
        ...


class InMemoryAgentHandoffStore:
    """In-memory dev/local implementation; not production persistence."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._handoffs: dict[str, dict[str, Any]] = {}
        self._audit: dict[str, list[dict[str, Any]]] = {}

    def create(self, handoff: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            handoff_id = str(handoff.get("handoff_id") or "")
            if not handoff_id:
                raise ProtocolError("INVALID_PARAMS", "handoff_id is required.", {"field": "handoff_id"})
            if handoff_id in self._handoffs:
                raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action handoff already exists.", {"handoff_id": handoff_id})
            status = str(handoff.get("status") or "active")
            if status != "active":
                raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "New handoff must start active.", {"status": status})
            record = deepcopy(handoff)
            self._handoffs[handoff_id] = record
            self._audit.setdefault(handoff_id, [])
            return deepcopy(record)

    def get(self, handoff_id: str) -> dict[str, Any]:
        with self._lock:
            record = self._handoffs.get(handoff_id)
            if record is None:
                raise ProtocolError("METHOD_NOT_FOUND", "Agent action handoff was not found.", {"handoff_id": handoff_id})
            return deepcopy(record)

    def list(self, *, agent_session_id: str | None = None, workflow_instance_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            records = list(self._handoffs.values())
            if agent_session_id is not None:
                records = [item for item in records if item.get("agent_session_id") == agent_session_id]
            if workflow_instance_id is not None:
                records = [item for item in records if item.get("workflow_instance_id") == workflow_instance_id]
            return [deepcopy(item) for item in records]

    def mark_opened(self, handoff_id: str) -> dict[str, Any]:
        with self._lock:
            record = self._require(handoff_id)
            status = str(record.get("status"))
            if status == "opened":
                return deepcopy(record)
            self._ensure_can_transition(status, {"active"}, handoff_id)
            return self._set_status(record, "opened")

    def mark_used(self, handoff_id: str) -> dict[str, Any]:
        with self._lock:
            record = self._require(handoff_id)
            status = str(record.get("status"))
            if status == "used_for_user_confirmed_action":
                return deepcopy(record)
            self._ensure_can_transition(status, HANDOFF_ACTIVE_STATES, handoff_id)
            return self._set_status(record, "used_for_user_confirmed_action")

    def dismiss(self, handoff_id: str) -> dict[str, Any]:
        with self._lock:
            record = self._require(handoff_id)
            status = str(record.get("status"))
            if status == "dismissed":
                return deepcopy(record)
            self._ensure_can_transition(status, HANDOFF_ACTIVE_STATES, handoff_id)
            return self._set_status(record, "dismissed")

    def expire(self, handoff_id: str, *, reason: str | None = None) -> dict[str, Any]:
        with self._lock:
            record = self._require(handoff_id)
            status = str(record.get("status"))
            if status == "expired":
                return deepcopy(record)
            self._ensure_can_transition(status, HANDOFF_ACTIVE_STATES, handoff_id)
            record["inactive_reason"] = reason or "handoff_expired"
            return self._set_status(record, "expired")

    def mark_stale(self, handoff_id: str, *, reason: str) -> dict[str, Any]:
        with self._lock:
            record = self._require(handoff_id)
            status = str(record.get("status"))
            if status == "stale":
                return deepcopy(record)
            self._ensure_can_transition(status, HANDOFF_ACTIVE_STATES, handoff_id)
            record["inactive_reason"] = reason
            return self._set_status(record, "stale")

    def mark_blocked(self, handoff_id: str, *, reason: str) -> dict[str, Any]:
        with self._lock:
            record = self._require(handoff_id)
            status = str(record.get("status"))
            if status == "blocked":
                return deepcopy(record)
            self._ensure_can_transition(status, HANDOFF_ACTIVE_STATES, handoff_id)
            record["inactive_reason"] = reason
            return self._set_status(record, "blocked")

    def append_audit(self, handoff_id: str, event_type: str, *, summary: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        with self._lock:
            self._require(handoff_id)
            entry = {
                "audit_id": f"aha_{len(self._audit.setdefault(handoff_id, [])) + 1:04d}",
                "handoff_id": handoff_id,
                "event_type": event_type,
                "summary": summary,
                "data": _redact(data or {}),
                "created_at": datetime.now(UTC).isoformat(),
                "redaction_status": "redacted",
            }
            self._audit[handoff_id].append(entry)
            return deepcopy(entry)

    def list_audit(self, handoff_id: str) -> list[dict[str, Any]]:
        with self._lock:
            self._require(handoff_id)
            return [deepcopy(item) for item in self._audit.get(handoff_id, [])]

    def _require(self, handoff_id: str) -> dict[str, Any]:
        record = self._handoffs.get(handoff_id)
        if record is None:
            raise ProtocolError("METHOD_NOT_FOUND", "Agent action handoff was not found.", {"handoff_id": handoff_id})
        return record

    def _ensure_can_transition(self, status: str, allowed_sources: set[str], handoff_id: str) -> None:
        if status in HANDOFF_TERMINAL_STATES:
            raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Terminal Agent action handoff cannot transition.", {"handoff_id": handoff_id, "status": status})
        if status not in allowed_sources:
            raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action handoff state transition is invalid.", {"handoff_id": handoff_id, "status": status})

    def _set_status(self, record: dict[str, Any], status: str) -> dict[str, Any]:
        if status not in HANDOFF_STATES:
            raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action handoff status is invalid.", {"status": status})
        record["status"] = status
        record["updated_at"] = datetime.now(UTC).isoformat()
        return deepcopy(record)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if any(part in key_text.lower() for part in SENSITIVE_KEY_PARTS):
                continue
            redacted[key_text] = _redact(item)
        return redacted
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str) and (
        "Bearer " in value
        or "subscription_token" in value
        or "capability_token" in value
        or "Authorization" in value
        or "secret-token-value" in value
        or "raw_trace_payload" in value
        or "raw_artifact_content" in value
        or "raw_connector_payload" in value
    ):
        return "[redacted]"
    return deepcopy(value)
