"""Core v1.5 application service facade."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.protocol import (
    ApprovalRecord,
    ArtifactRecord,
    ItemRecord,
    JobRecord,
    RetryRecord,
    SessionRecord,
    ThreadRecord,
    TraceRecord,
    TurnRecord,
)
from core.stores import CoreSQLiteStore


class CoreAppService:
    """Core-native facade over records, store, and Gateway-to-Core writes."""

    def __init__(
        self,
        store: Optional[CoreSQLiteStore] = None,
    ) -> None:
        self.store = store or CoreSQLiteStore()
        self._thread_cache: Dict[Tuple[str, Optional[str]], str] = {}

    def upsert_session(
        self,
        *,
        session_id: str,
        client_type: str = "unknown",
        status: str = "active",
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionRecord:
        """Create or update a Core session without going through a legacy adapter."""
        try:
            record = self.store.get_session(session_id)
            record.client_type = client_type
            record.user_id = user_id
            record.tenant_id = tenant_id
            record.status = status
            record.capabilities = dict(capabilities or {})
            record.metadata = dict(metadata or {})
            record.updated_at = datetime.now()
        except KeyError:
            record = SessionRecord(
                session_id=session_id,
                client_type=client_type,
                user_id=user_id,
                tenant_id=tenant_id,
                status=status,
                capabilities=dict(capabilities or {}),
                metadata=dict(metadata or {}),
            )
        return self.store.save_session(record)

    def record_runtime_session(self, session: Any) -> SessionRecord:
        """Record a Gateway RuntimeSession through the Core-native session mutation path."""
        return self.upsert_session(
            session_id=str(session.session_id),
            client_type="gateway",
            status=str(getattr(session, "state", "unknown")),
            metadata={
                "model": getattr(session, "model", None),
                "backend": getattr(session, "backend", None),
                "interrupted": bool(getattr(session, "interrupted", False)),
            },
        )

    def record_gateway_session(self, session: Any) -> SessionRecord:
        return self.record_runtime_session(session)

    def record_gateway_event(self, event: Any) -> None:
        session_id = getattr(event, "session_id", None)
        turn_id = getattr(event, "turn_id", None)
        if not session_id or not turn_id:
            return
        event_type = str(getattr(event, "type", "gateway.event"))
        data = dict(getattr(event, "data", {}) or {})
        domain = data.get("domain") if isinstance(data.get("domain"), str) else None
        thread = self.ensure_thread(session_id=str(session_id), domain=domain)

        if event_type == "turn.started":
            self.start_turn(
                turn_id=str(turn_id),
                session_id=str(session_id),
                thread_id=thread.thread_id,
                user_input=str(data.get("input", "")),
                trace_id=data.get("trace_id") if isinstance(data.get("trace_id"), str) else None,
                metadata={
                    "domain": data.get("domain"),
                    "model": data.get("model"),
                    "retry_of_turn_id": data.get("retry_of_turn_id"),
                    "approval_id": data.get("approval_id"),
                },
            )
            self.add_item(
                item_id=str(event.item_id),
                session_id=str(session_id),
                thread_id=thread.thread_id,
                turn_id=str(turn_id),
                item_type="user_message",
                role="user",
                content={"text": str(data.get("input", "")), "event": _event_payload(event)},
                status="completed",
            )
            return

        if event_type == "item.delta":
            self.add_item(
                item_id=str(event.item_id),
                session_id=str(session_id),
                thread_id=thread.thread_id,
                turn_id=str(turn_id),
                item_type="assistant_message_delta",
                role="assistant",
                content={"text": str(data.get("text", "")), "event": _event_payload(event)},
                status="streaming",
            )
            return

        if event_type == "turn.completed":
            self.update_turn_state(turn_id=str(turn_id), state="completed")
            self.record_artifacts_from_event(data, thread_id=thread.thread_id)
            self.add_item(
                item_id=str(event.item_id),
                session_id=str(session_id),
                thread_id=thread.thread_id,
                turn_id=str(turn_id),
                item_type="assistant_message",
                role="assistant",
                content={"text": _assistant_text(data), "event": _event_payload(event)},
                status="completed",
            )
            return

        if event_type == "turn.failed":
            self.update_turn_state(turn_id=str(turn_id), state="failed")
        elif event_type == "turn.interrupted":
            self.update_turn_state(turn_id=str(turn_id), state="interrupted")

        self.add_item(
            item_id=str(event.item_id),
            session_id=str(session_id),
            thread_id=thread.thread_id,
            turn_id=str(turn_id),
            item_type=event_type,
            role="system",
            content={"event": _event_payload(event)},
            status=_status_from_event_type(event_type),
        )

    def record_gateway_trace(self, record: Dict[str, Any]) -> TraceRecord:
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
        return self.store.save_trace_record(trace)

    def record_gateway_approval(self, record: Dict[str, Any]) -> ApprovalRecord:
        approval_id = str(record.get("approval_id") or "")
        turn_id = _optional_text(record.get("turn_id"))
        approval = ApprovalRecord(
            approval_id=approval_id,
            target_type="turn" if turn_id else "approval",
            target_id=turn_id or approval_id,
            risk_class=str(record.get("risk_level") or "medium"),
            reason=str(record.get("request_summary") or record.get("action") or ""),
            decision=str(record.get("status") or "pending"),
            decided_at=_parse_datetime(record.get("decided_at")),
            metadata={"gateway_approval": record},
        )
        return self.store.save_approval(approval)

    def record_gateway_retry(self, record: Dict[str, Any]) -> RetryRecord:
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

    def record_gateway_artifact(self, record: Dict[str, Any], *, thread_id: Optional[str] = None) -> ArtifactRecord:
        resolved_thread_id = thread_id
        session_id = _optional_text(record.get("session_id"))
        domain = _optional_text(record.get("domain"))
        if resolved_thread_id is None and session_id is not None:
            resolved_thread_id = self.ensure_thread(session_id=session_id, domain=domain).thread_id
        artifact = ArtifactRecord(
            artifact_id=str(record.get("artifact_id") or ""),
            domain=domain,
            kind=str(record.get("kind") or "artifact"),
            owner_session_id=session_id,
            owner_thread_id=resolved_thread_id,
            owner_turn_id=_optional_text(record.get("turn_id")),
            uri=str(record.get("path") or record.get("uri") or ""),
            name=str(record.get("name") or ""),
            mime=str(record.get("mime") or "application/octet-stream"),
            metadata={"gateway_artifact": record},
        )
        return self.store.save_artifact(artifact)

    def ensure_thread(self, *, session_id: str, domain: Optional[str] = None) -> ThreadRecord:
        """Return the default Core thread for a session/domain, creating it if needed."""
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

    def start_turn(
        self,
        *,
        turn_id: str,
        session_id: str,
        thread_id: str,
        user_input: str,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TurnRecord:
        """Create or update a Core turn as running."""
        try:
            turn = self.store.get_turn(turn_id)
            turn.session_id = session_id
            turn.thread_id = thread_id
            turn.input = user_input
            turn.state = "running"
            turn.trace_id = trace_id
            turn.metadata = dict(metadata or {})
            turn.completed_at = None
            turn.updated_at = datetime.now()
        except KeyError:
            turn = TurnRecord(
                turn_id=turn_id,
                session_id=session_id,
                thread_id=thread_id,
                input=user_input,
                state="running",
                trace_id=trace_id,
                metadata=dict(metadata or {}),
            )
        return self.store.save_turn(turn)

    def update_turn_state(self, *, turn_id: str, state: str) -> Optional[TurnRecord]:
        """Update a Core turn lifecycle state."""
        try:
            turn = self.store.get_turn(turn_id)
        except KeyError:
            return None
        turn.state = state
        turn.updated_at = datetime.now()
        if state in {"completed", "failed", "interrupted"}:
            turn.completed_at = datetime.now()
        return self.store.save_turn(turn)

    def add_item(
        self,
        *,
        item_id: str,
        session_id: str,
        thread_id: str,
        turn_id: str,
        item_type: str,
        role: Optional[str],
        content: Dict[str, Any],
        status: str = "created",
        parent_item_id: Optional[str] = None,
    ) -> ItemRecord:
        """Create or replace a Core item."""
        item = ItemRecord(
            item_id=item_id,
            session_id=session_id,
            thread_id=thread_id,
            turn_id=turn_id,
            item_type=item_type,
            role=role,
            content=content,
            status=status,
            parent_item_id=parent_item_id,
        )
        return self.store.save_item(item)

    def record_artifacts_from_event(self, data: Dict[str, Any], *, thread_id: str) -> None:
        artifact_records = data.get("artifact_records")
        if not isinstance(artifact_records, dict):
            meeting = data.get("meeting")
            artifact_records = meeting.get("artifact_records") if isinstance(meeting, dict) else None
        if not isinstance(artifact_records, dict):
            return
        for record in artifact_records.values():
            if isinstance(record, dict) and record.get("artifact_id"):
                self.record_gateway_artifact(record, thread_id=thread_id)

    def start_job(
        self,
        *,
        workflow_id: str,
        domain: Optional[str] = None,
        session_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobRecord:
        """Create a Core job for a workflow execution."""
        job = JobRecord(
            workflow_id=workflow_id,
            domain=domain,
            session_id=session_id,
            thread_id=thread_id,
            turn_id=turn_id,
            status="running",
            progress=0.0,
            trace_id=trace_id,
            metadata=dict(metadata or {}),
        )
        return self.store.save_job(job)

    def update_job(
        self,
        *,
        job_id: str,
        status: str,
        progress: Optional[float] = None,
        artifact_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobRecord:
        """Update a Core job lifecycle state."""
        job = self.store.get_job(job_id)
        job.status = status
        if progress is not None:
            job.progress = progress
        if artifact_ids is not None:
            job.artifact_ids = list(artifact_ids)
        if metadata:
            job.metadata.update(metadata)
        job.updated_at = datetime.now()
        return self.store.save_job(job)

    def cancel_job(self, job_id: str, *, reason: Optional[str] = None) -> JobRecord:
        """Mark a Core job as cancelled."""
        metadata = {"cancel_reason": reason} if reason else None
        return self.update_job(job_id=job_id, status="cancelled", progress=0.0, metadata=metadata)

    def get_session(self, session_id: str) -> SessionRecord:
        return self.store.get_session(session_id)

    def list_threads(self, *, session_id: Optional[str] = None) -> List[ThreadRecord]:
        return self.store.list_threads(session_id=session_id)

    def get_turn(self, turn_id: str) -> TurnRecord:
        return self.store.get_turn(turn_id)

    def list_items(self, *, turn_id: Optional[str] = None, thread_id: Optional[str] = None) -> List[ItemRecord]:
        return self.store.list_items(turn_id=turn_id, thread_id=thread_id)

    def list_artifacts(
        self,
        *,
        owner_thread_id: Optional[str] = None,
        domain: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> List[ArtifactRecord]:
        return self.store.list_artifacts(owner_thread_id=owner_thread_id, domain=domain, kind=kind)

    def get_job(self, job_id: str) -> JobRecord:
        return self.store.get_job(job_id)

    def list_jobs(
        self,
        *,
        thread_id: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        domain: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[JobRecord]:
        return self.store.list_jobs(
            thread_id=thread_id,
            session_id=session_id,
            turn_id=turn_id,
            domain=domain,
            status=status,
        )

    def list_trace_records(
        self,
        *,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> List[TraceRecord]:
        return self.store.list_trace_records(
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            event_type=event_type,
        )

    def list_approvals(
        self,
        *,
        decision: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> List[ApprovalRecord]:
        return self.store.list_approvals(decision=decision, target_type=target_type, target_id=target_id)

    def list_retries(
        self,
        *,
        session_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[RetryRecord]:
        return self.store.list_retries(session_id=session_id, approval_id=approval_id, status=status)


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


def _text_list(value: Any) -> List[str]:
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
