"""Bridge legacy Gateway runtime events into Core v1.5 records."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from core.protocol import (
    ApprovalRecord,
    ArtifactRecord,
    ItemRecord,
    RetryRecord,
    SessionRecord,
    ThreadRecord,
    TraceRecord,
    TurnRecord,
)
from core.stores.sqlite import CoreSQLiteStore


class CoreRuntimeRecorder:
    """Record Gateway sessions and events as Core protocol objects."""

    def __init__(self, store: CoreSQLiteStore) -> None:
        self.store = store
        self._thread_cache: Dict[Tuple[str, Optional[str]], str] = {}

    def record_session(self, session: Any) -> SessionRecord:
        """Persist or update a Gateway runtime session as a Core session."""
        record = SessionRecord(
            session_id=str(session.session_id),
            client_type="gateway",
            status=str(getattr(session, "state", "unknown")),
            metadata={
                "model": getattr(session, "model", None),
                "backend": getattr(session, "backend", None),
                "interrupted": bool(getattr(session, "interrupted", False)),
            },
        )
        return self.store.save_session(record)

    def record_event(self, event: Any) -> None:
        """Persist one GatewayEvent as Core turn/item records."""
        session_id = getattr(event, "session_id", None)
        turn_id = getattr(event, "turn_id", None)
        if not session_id or not turn_id:
            return
        event_type = str(getattr(event, "type", "gateway.event"))
        data = dict(getattr(event, "data", {}) or {})
        domain = data.get("domain") if isinstance(data.get("domain"), str) else None
        thread = self._ensure_thread(str(session_id), domain)

        if event_type == "turn.started":
            self._save_started_turn(event, thread.thread_id, data)
            self._save_item(
                event=event,
                thread_id=thread.thread_id,
                item_type="user_message",
                role="user",
                content={"text": str(data.get("input", "")), "event": _event_payload(event)},
                status="completed",
            )
            return

        if event_type == "item.delta":
            self._save_item(
                event=event,
                thread_id=thread.thread_id,
                item_type="assistant_message_delta",
                role="assistant",
                content={"text": str(data.get("text", "")), "event": _event_payload(event)},
                status="streaming",
            )
            return

        if event_type == "turn.completed":
            self._update_turn_state(str(turn_id), "completed")
            self._record_artifacts_from_event(data, thread_id=thread.thread_id)
            self._save_item(
                event=event,
                thread_id=thread.thread_id,
                item_type="assistant_message",
                role="assistant",
                content={"text": _assistant_text(data), "event": _event_payload(event)},
                status="completed",
            )
            return

        if event_type == "turn.failed":
            self._update_turn_state(str(turn_id), "failed")
        elif event_type == "turn.interrupted":
            self._update_turn_state(str(turn_id), "interrupted")

        self._save_item(
            event=event,
            thread_id=thread.thread_id,
            item_type=event_type,
            role="system",
            content={"event": _event_payload(event)},
            status=_status_from_event_type(event_type),
        )

    def record_trace(self, record: Dict[str, Any]) -> TraceRecord:
        """Persist a legacy Gateway trace dict as a Core trace record."""
        trace = TraceRecord(
            trace_id=str(record.get("trace_id") or "trace_unknown"),
            session_id=_optional_text(record.get("session_id")),
            turn_id=_optional_text(record.get("turn_id")),
            event_type=str(record.get("event_type") or "trace.event"),
            status=str(record.get("status") or "running"),
            workflow_id=_optional_text(record.get("workflow_id")),
            artifact_ids=_text_list(record.get("artifact_ids")),
            approval_ids=_text_list(record.get("approval_ids")),
            input_summary=str(record.get("input_summary") or ""),
            metadata={"gateway_trace": record},
        )
        if not trace.trace_id:
            trace.trace_id = self.store.path.stem
        return self.store.save_trace_record(trace)

    def record_approval(self, record: Dict[str, Any]) -> ApprovalRecord:
        """Persist a legacy Gateway approval dict as a Core approval record."""
        approval_id = str(record.get("approval_id") or "")
        turn_id = _optional_text(record.get("turn_id"))
        target_id = turn_id or approval_id
        approval = ApprovalRecord(
            approval_id=approval_id,
            target_type="turn" if turn_id else "approval",
            target_id=target_id,
            risk_class=str(record.get("risk_level") or "medium"),
            reason=str(record.get("request_summary") or record.get("action") or ""),
            decision=str(record.get("status") or "pending"),
            decided_at=_parse_datetime(record.get("decided_at")),
            metadata={"gateway_approval": record},
        )
        return self.store.save_approval(approval)

    def record_retry(self, record: Dict[str, Any]) -> RetryRecord:
        """Persist a legacy Gateway retry dict as a Core retry record."""
        retry = RetryRecord(
            retry_id=str(record.get("retry_id") or ""),
            source_turn_id=str(record.get("source_turn_id") or ""),
            session_id=str(record.get("session_id") or ""),
            input=str(record.get("input") or ""),
            domain=_optional_text(record.get("domain")),
            trace_id=_optional_text(record.get("trace_id")),
            approval_id=_optional_text(record.get("approval_id")),
            status=str(record.get("status") or "pending_approval"),
            workflow_id=_optional_text(record.get("workflow_id")),
            failure_message=_optional_text(record.get("failure_message")),
            artifact_ids=_text_list(record.get("artifact_ids")),
            policy=record.get("policy") if isinstance(record.get("policy"), dict) else {},
            retried_at=_parse_datetime(record.get("retried_at")),
            retry_turn_id=_optional_text(record.get("retry_turn_id")),
            retry_trace_id=_optional_text(record.get("retry_trace_id")),
            metadata={"gateway_retry": record},
        )
        return self.store.save_retry(retry)

    def record_artifact(self, record: Dict[str, Any], *, thread_id: Optional[str] = None) -> ArtifactRecord:
        """Persist a legacy Gateway artifact dict as a Core artifact record."""
        artifact = ArtifactRecord(
            artifact_id=str(record.get("artifact_id") or ""),
            domain=_optional_text(record.get("domain")),
            kind=str(record.get("kind") or "artifact"),
            owner_session_id=_optional_text(record.get("session_id")),
            owner_thread_id=thread_id,
            owner_turn_id=_optional_text(record.get("turn_id")),
            uri=str(record.get("path") or record.get("uri") or ""),
            name=str(record.get("name") or ""),
            mime=str(record.get("mime") or "application/octet-stream"),
            metadata={"gateway_artifact": record},
        )
        return self.store.save_artifact(artifact)

    def _ensure_thread(self, session_id: str, domain: Optional[str]) -> ThreadRecord:
        cache_key = (session_id, domain)
        cached_thread_id = self._thread_cache.get(cache_key)
        if cached_thread_id:
            try:
                return self.store.get_thread(cached_thread_id)
            except KeyError:
                self._thread_cache.pop(cache_key, None)

        for thread in self.store.list_threads(session_id=session_id):
            if thread.metadata.get("gateway_default") and thread.domain == domain:
                self._thread_cache[cache_key] = thread.thread_id
                return thread

        thread = ThreadRecord(
            session_id=session_id,
            domain=domain,
            title=f"{domain or 'default'} thread",
            metadata={"gateway_default": True},
        )
        self.store.save_thread(thread)
        self._thread_cache[cache_key] = thread.thread_id
        return thread

    def _save_started_turn(self, event: Any, thread_id: str, data: Dict[str, Any]) -> None:
        turn = TurnRecord(
            turn_id=str(event.turn_id),
            session_id=str(event.session_id),
            thread_id=thread_id,
            input=str(data.get("input", "")),
            state="running",
            trace_id=data.get("trace_id") if isinstance(data.get("trace_id"), str) else None,
            metadata={
                "domain": data.get("domain"),
                "model": data.get("model"),
                "retry_of_turn_id": data.get("retry_of_turn_id"),
                "approval_id": data.get("approval_id"),
            },
        )
        self.store.save_turn(turn)

    def _update_turn_state(self, turn_id: str, state: str) -> None:
        try:
            turn = self.store.get_turn(turn_id)
        except KeyError:
            return
        turn.state = state
        turn.updated_at = datetime.now()
        if state in {"completed", "failed", "interrupted"}:
            turn.completed_at = datetime.now()
        self.store.save_turn(turn)

    def _save_item(
        self,
        *,
        event: Any,
        thread_id: str,
        item_type: str,
        role: Optional[str],
        content: Dict[str, Any],
        status: str,
    ) -> None:
        item = ItemRecord(
            item_id=str(event.item_id),
            session_id=str(event.session_id),
            thread_id=thread_id,
            turn_id=str(event.turn_id),
            item_type=item_type,
            role=role,
            content=content,
            status=status,
        )
        self.store.save_item(item)

    def _record_artifacts_from_event(self, data: Dict[str, Any], *, thread_id: str) -> None:
        artifact_records = data.get("artifact_records")
        if not isinstance(artifact_records, dict):
            meeting = data.get("meeting")
            artifact_records = meeting.get("artifact_records") if isinstance(meeting, dict) else None
        if not isinstance(artifact_records, dict):
            return
        for record in artifact_records.values():
            if isinstance(record, dict) and record.get("artifact_id"):
                self.record_artifact(record, thread_id=thread_id)


def _event_payload(event: Any) -> Dict[str, Any]:
    if hasattr(event, "model_dump"):
        return event.model_dump(mode="json")
    return {
        "type": getattr(event, "type", "gateway.event"),
        "session_id": getattr(event, "session_id", None),
        "turn_id": getattr(event, "turn_id", None),
        "data": getattr(event, "data", {}),
    }


def _assistant_text(data: Dict[str, Any]) -> str:
    message = data.get("message")
    blocks = message.get("content") if isinstance(message, dict) else None
    if not isinstance(blocks, list):
        return ""
    return "".join(
        str(block.get("text", ""))
        for block in blocks
        if isinstance(block, dict) and block.get("type") == "text"
    )


def _status_from_event_type(event_type: str) -> str:
    if event_type.endswith(".failed") or event_type == "turn.failed":
        return "failed"
    if event_type.endswith(".interrupted") or event_type == "turn.interrupted":
        return "interrupted"
    if event_type.endswith(".completed") or event_type == "turn.completed":
        return "completed"
    return "created"


def _optional_text(value: Any) -> Optional[str]:
    if isinstance(value, str) and value:
        return value
    return None


def _text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
