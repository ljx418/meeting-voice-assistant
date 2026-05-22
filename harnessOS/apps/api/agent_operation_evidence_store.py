"""Dev/local operation evidence repository for Agent handoff governance."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock
from typing import Any, Protocol

from core.protocol.schemas.errors import ProtocolError


EVIDENCE_STATUSES = {
    "succeeded",
    "failed",
    "idempotent_replayed",
    "blocked",
    "stale_rejected",
    "expired_rejected",
}
SENSITIVE_KEY_PARTS = (
    "token",
    "authorization",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw_prompt",
)


class AgentOperationEvidenceRepository(Protocol):
    """Repository boundary for user-confirmed operation evidence."""

    def create(self, evidence: dict[str, Any]) -> dict[str, Any]:
        ...

    def get(self, evidence_id: str) -> dict[str, Any]:
        ...

    def list(self, *, workflow_instance_id: str | None = None) -> list[dict[str, Any]]:
        ...

    def append_audit_ref(self, evidence_id: str, audit_ref: dict[str, Any]) -> dict[str, Any]:
        ...

    def find_by_operation_id(self, operation_id: str) -> list[dict[str, Any]]:
        ...

    def find_by_correlation_id(self, correlation_id: str) -> list[dict[str, Any]]:
        ...


class InMemoryAgentOperationEvidenceStore:
    """In-memory dev/local evidence store; not production persistence."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._evidence: dict[str, dict[str, Any]] = {}

    def create(self, evidence: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            evidence_id = str(evidence.get("evidence_id") or "")
            if not evidence_id:
                raise ProtocolError("INVALID_PARAMS", "evidence_id is required.", {"field": "evidence_id"})
            if evidence_id in self._evidence:
                raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Operation evidence already exists.", {"evidence_id": evidence_id})
            status = str(evidence.get("status") or "")
            if status not in EVIDENCE_STATUSES:
                raise ProtocolError("INVALID_PARAMS", "Operation evidence status is invalid.", {"status": status})
            record = _redact(deepcopy(evidence))
            record.setdefault("audit_refs", [])
            record["redaction_status"] = "redacted"
            self._evidence[evidence_id] = record
            return deepcopy(record)

    def get(self, evidence_id: str) -> dict[str, Any]:
        with self._lock:
            record = self._evidence.get(evidence_id)
            if record is None:
                raise ProtocolError("METHOD_NOT_FOUND", "Operation evidence was not found.", {"evidence_id": evidence_id})
            return deepcopy(record)

    def list(self, *, workflow_instance_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            records = list(self._evidence.values())
            if workflow_instance_id is not None:
                records = [item for item in records if item.get("workflow_instance_id") == workflow_instance_id]
            return [deepcopy(item) for item in sorted(records, key=lambda item: str(item.get("created_at") or ""))]

    def append_audit_ref(self, evidence_id: str, audit_ref: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            record = self._evidence.get(evidence_id)
            if record is None:
                raise ProtocolError("METHOD_NOT_FOUND", "Operation evidence was not found.", {"evidence_id": evidence_id})
            refs = record.setdefault("audit_refs", [])
            refs.append(_redact({**audit_ref, "created_at": datetime.now(UTC).isoformat()}))
            return deepcopy(record)

    def find_by_operation_id(self, operation_id: str) -> list[dict[str, Any]]:
        with self._lock:
            return [deepcopy(item) for item in self._evidence.values() if item.get("operation_id") == operation_id]

    def find_by_correlation_id(self, correlation_id: str) -> list[dict[str, Any]]:
        with self._lock:
            return [deepcopy(item) for item in self._evidence.values() if item.get("correlation_id") == correlation_id]


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            lower = key_text.lower()
            if any(part in lower for part in SENSITIVE_KEY_PARTS):
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
        or "raw prompt" in value
        or "upstream signed URL" in value
    ):
        return "[redacted]"
    return deepcopy(value)
