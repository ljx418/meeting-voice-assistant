"""Core v1.5 application service facade."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from apps.gateway.secrets import mask_value
from core.apps import ScopeContext, resolve_scope_context
from core.protocol import (
    ApprovalRecord,
    ArtifactRecord,
    ConnectorRecord,
    ItemRecord,
    JobEventRecord,
    JobRecord,
    MemoryRecord,
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
        self._thread_cache: Dict[Tuple[str, Optional[str], str, Optional[str], Optional[str]], str] = {}

    def upsert_session(
        self,
        *,
        session_id: str,
        client_type: str = "unknown",
        status: str = "active",
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        app_id: str = "default",
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionRecord:
        """Create or update a Core session without going through a legacy adapter."""
        try:
            record = self.store.get_session(session_id)
            record.client_type = client_type
            record.user_id = user_id
            record.tenant_id = tenant_id
            record.app_id = app_id
            record.project_id = project_id
            record.workspace_id = workspace_id
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
                app_id=app_id,
                project_id=project_id,
                workspace_id=workspace_id,
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
            app_id=str(getattr(session, "app_id", "default") or "default"),
            project_id=getattr(session, "project_id", None),
            workspace_id=getattr(session, "workspace_id", None),
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
        data = mask_value(dict(getattr(event, "data", {}) or {}))
        scope = resolve_scope_context(data)
        domain = data.get("domain") if isinstance(data.get("domain"), str) else None
        try:
            self.get_session(str(session_id))
        except KeyError:
            self.upsert_session(
                session_id=str(session_id),
                client_type="gateway",
                status="active",
                app_id=scope.app_id,
                project_id=scope.project_id,
                workspace_id=scope.workspace_id,
            )
        thread = self.ensure_thread(session_id=str(session_id), domain=domain, scope=scope)

        if event_type == "turn.started":
            self.start_turn(
                turn_id=str(turn_id),
                session_id=str(session_id),
                thread_id=thread.thread_id,
                user_input=str(data.get("input", "")),
                trace_id=data.get("trace_id") if isinstance(data.get("trace_id"), str) else None,
                scope=scope,
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
                scope=scope,
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
                scope=scope,
            )
            return

        if event_type == "turn.completed":
            self.update_turn_state(turn_id=str(turn_id), state="completed")
            artifact_data = dict(data)
            artifact_data.setdefault("session_id", str(session_id))
            artifact_data.setdefault("turn_id", str(turn_id))
            artifact_data.setdefault("domain", domain)
            artifact_data.setdefault("app_id", scope.app_id)
            artifact_data.setdefault("project_id", scope.project_id)
            artifact_data.setdefault("workspace_id", scope.workspace_id)
            self.record_artifacts_from_event(artifact_data, thread_id=thread.thread_id)
            self.add_item(
                item_id=str(event.item_id),
                session_id=str(session_id),
                thread_id=thread.thread_id,
                turn_id=str(turn_id),
                item_type="assistant_message",
                role="assistant",
                content={"text": _assistant_text(data), "event": _event_payload(event)},
                status="completed",
                scope=scope,
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
            scope=scope,
        )

    def record_gateway_trace(self, record: Dict[str, Any]) -> TraceRecord:
        scope = resolve_scope_context(record.get("scope") if isinstance(record.get("scope"), dict) else record)
        trace = TraceRecord(
            trace_id=str(record.get("trace_id") or "trace_unknown"),
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
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

    def record_memory_trace(
        self,
        *,
        operation: str,
        memory: MemoryRecord,
        status: str = "success",
        trace_id: Optional[str] = None,
    ) -> TraceRecord:
        """Record a memory read/write operation in Core trace records."""
        trace = TraceRecord(
            trace_id=trace_id or memory.trace_id or f"trace_{memory.memory_id}",
            app_id=memory.app_id,
            project_id=memory.project_id,
            workspace_id=memory.workspace_id,
            session_id=memory.session_id,
            turn_id=memory.source_turn_id,
            event_type=f"memory.{operation}",
            status=status,
            artifact_ids=[memory.source_artifact_id] if memory.source_artifact_id else [],
            input_summary=_summarize_text(memory.content),
            metadata={
                "memory_id": memory.memory_id,
                "kind": memory.kind,
                "scope": memory.scope,
                "source_artifact_id": memory.source_artifact_id,
            },
        )
        return self.store.save_trace_record(trace)

    def record_gateway_approval(self, record: Dict[str, Any]) -> ApprovalRecord:
        approval_id = str(record.get("approval_id") or "")
        turn_id = _optional_text(record.get("turn_id"))
        scope = resolve_scope_context(record)
        approval = ApprovalRecord(
            approval_id=approval_id,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
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
        scope = resolve_scope_context(record)
        retry = RetryRecord(
            retry_id=str(record.get("retry_id") or ""),
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
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
        scope = resolve_scope_context(record)
        metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
        if resolved_thread_id is None and session_id is not None:
            resolved_thread_id = self.ensure_thread(session_id=session_id, domain=domain, scope=scope).thread_id
        artifact = ArtifactRecord(
            artifact_id=str(record.get("artifact_id") or ""),
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            domain=domain,
            kind=str(record.get("kind") or "artifact"),
            owner_session_id=session_id,
            owner_thread_id=resolved_thread_id,
            owner_turn_id=_optional_text(record.get("turn_id")),
            uri=str(record.get("path") or record.get("uri") or ""),
            name=str(record.get("name") or ""),
            mime=str(record.get("mime") or "application/octet-stream"),
            parent_ids=_artifact_parent_ids(metadata),
            external_asset_uri=_optional_text(record.get("external_asset_uri")),
            preview_uri=_optional_text(record.get("preview_uri")),
            thumbnail_uri=_optional_text(record.get("thumbnail_uri")),
            metadata={"gateway_artifact": record},
        )
        return self.store.save_artifact(artifact)

    def save_connector(self, record: ConnectorRecord) -> ConnectorRecord:
        """Persist a connector descriptor in the Core store."""
        return self.store.save_connector(record)

    def get_connector(self, connector_id: str) -> ConnectorRecord:
        """Return one connector descriptor."""
        return self.store.get_connector(connector_id)

    def list_connectors(
        self,
        *,
        domain: Optional[str] = None,
        kind: Optional[str] = None,
        health: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ConnectorRecord]:
        """Return connector descriptors with optional filters."""
        return self.store.list_connectors(
            domain=domain,
            kind=kind,
            health=health,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

    def get_artifact(self, artifact_id: str) -> ArtifactRecord:
        """Return one Core artifact."""
        return self.store.get_artifact(artifact_id)

    def artifact_lineage(
        self,
        *,
        artifact_id: Optional[str] = None,
        owner_session_id: Optional[str] = None,
        owner_turn_id: Optional[str] = None,
        domain: Optional[str] = None,
        kind: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return artifact lineage as a directed graph."""
        if artifact_id is not None:
            anchor = self.get_artifact(artifact_id)
            candidates = self.list_artifacts(
                domain=domain or anchor.domain,
                app_id=app_id or anchor.app_id,
                project_id=project_id if project_id is not None else anchor.project_id,
                workspace_id=workspace_id if workspace_id is not None else anchor.workspace_id,
            )
            artifacts = _connected_artifacts(candidates, artifact_id)
        else:
            artifacts = self.list_artifacts(
                owner_session_id=owner_session_id,
                owner_turn_id=owner_turn_id,
                domain=domain,
                kind=kind,
                app_id=app_id,
                project_id=project_id,
                workspace_id=workspace_id,
            )
        artifacts_by_id = {artifact.artifact_id: artifact for artifact in artifacts}
        edges: List[Dict[str, str]] = []
        children_by_parent: Dict[str, List[str]] = {}
        for artifact in artifacts:
            for parent_id in artifact.parent_ids:
                if parent_id not in artifacts_by_id:
                    continue
                edges.append(
                    {
                        "source_artifact_id": parent_id,
                        "target_artifact_id": artifact.artifact_id,
                        "relation": "derived_from",
                    }
                )
                children_by_parent.setdefault(parent_id, []).append(artifact.artifact_id)
        roots = [
            artifact.artifact_id
            for artifact in artifacts
            if not any(parent_id in artifacts_by_id for parent_id in artifact.parent_ids)
        ]
        leaves = [artifact.artifact_id for artifact in artifacts if artifact.artifact_id not in children_by_parent]
        return {
            "artifacts": [_record_to_dict(artifact) for artifact in artifacts],
            "edges": edges,
            "roots": roots,
            "leaves": leaves,
            "count": len(artifacts),
        }

    def create_memory_record(
        self,
        *,
        session_id: str,
        thread_id: Optional[str] = None,
        source_turn_id: Optional[str] = None,
        source_artifact_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        scope_context: Optional[ScopeContext] = None,
        scope: str = "session",
        kind: str = "summary",
        title: str = "",
        content: str = "",
        refs: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryRecord:
        """Create a masked Core memory record and trace the write."""
        resolved_scope = scope_context or ScopeContext()
        memory = MemoryRecord(
            session_id=session_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            thread_id=thread_id,
            source_turn_id=source_turn_id,
            source_artifact_id=source_artifact_id,
            trace_id=trace_id,
            scope=scope,
            kind=kind,
            title=title,
            content=str(mask_value(content)),
            refs=mask_value(list(refs or [])),
            metadata=mask_value(dict(metadata or {})),
        )
        saved = self.store.save_memory(memory)
        self.record_memory_trace(operation="write", memory=saved, trace_id=trace_id)
        return saved

    def get_memory(self, memory_id: str, *, trace_id: Optional[str] = None) -> MemoryRecord:
        """Return one memory record and trace the read."""
        memory = self.store.get_memory(memory_id)
        self.record_memory_trace(operation="read", memory=memory, trace_id=trace_id)
        return memory

    def list_memory_records(
        self,
        *,
        session_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        kind: Optional[str] = None,
        source_artifact_id: Optional[str] = None,
        status: Optional[str] = "active",
        trace_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[MemoryRecord]:
        """List memory records and trace the read operation."""
        records = self.store.list_memory(
            session_id=session_id,
            thread_id=thread_id,
            kind=kind,
            source_artifact_id=source_artifact_id,
            status=status,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )
        for record in records:
            self.record_memory_trace(operation="list", memory=record, trace_id=trace_id)
        return records

    def build_session_summary(
        self,
        *,
        session_id: str,
        thread_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        scope_context: Optional[ScopeContext] = None,
        max_entries: int = 8,
    ) -> MemoryRecord:
        """Build a deterministic session summary from Core transcript records."""
        transcript = self.read_session_transcript(session_id)
        selected = transcript[-max_entries:] if max_entries > 0 else transcript
        lines = []
        refs = []
        for item in selected:
            role = str(item.get("role") or "unknown")
            turn_id = _optional_text(item.get("turn_id"))
            content = _summarize_text(str(item.get("content") or ""), limit=180)
            if content:
                lines.append(f"{role}: {content}")
            if turn_id:
                refs.append({"type": "turn", "turn_id": turn_id, "role": role})
        if not lines:
            lines.append("No prior session content is available.")
        resolved_thread_id = thread_id or self._default_thread_id(session_id)
        return self.create_memory_record(
            session_id=session_id,
            thread_id=resolved_thread_id,
            trace_id=trace_id,
            scope_context=scope_context,
            scope="session",
            kind="session_summary",
            title="Session summary",
            content="\n".join(lines),
            refs=refs,
            metadata={"summary_engine": "deterministic", "entry_count": len(selected)},
        )

    def extract_artifact_memory_refs(
        self,
        *,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        domain: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> List[MemoryRecord]:
        """Create memory refs for existing artifacts, preserving artifact lineage ids."""
        artifacts = self.list_artifacts(
            owner_session_id=session_id,
            owner_turn_id=turn_id,
            domain=domain,
        )
        records: List[MemoryRecord] = []
        for artifact in artifacts:
            if not artifact.owner_session_id:
                continue
            existing = self.store.list_memory(
                session_id=artifact.owner_session_id,
                source_artifact_id=artifact.artifact_id,
                kind=f"artifact_ref:{artifact.kind}",
                status="active",
            )
            if existing:
                records.extend(existing)
                continue
            records.append(
                self.create_memory_record(
                    session_id=artifact.owner_session_id,
                    thread_id=artifact.owner_thread_id,
                    source_turn_id=artifact.owner_turn_id,
                    source_artifact_id=artifact.artifact_id,
                    trace_id=trace_id,
                    scope_context=ScopeContext(
                        app_id=artifact.app_id,
                        project_id=artifact.project_id,
                        workspace_id=artifact.workspace_id,
                    ),
                    scope="session",
                    kind=f"artifact_ref:{artifact.kind}",
                    title=f"{artifact.kind} artifact reference",
                    content=_artifact_memory_content(artifact),
                    refs=[
                        {
                            "type": "artifact",
                            "artifact_id": artifact.artifact_id,
                            "kind": artifact.kind,
                            "uri": artifact.uri,
                            "parent_ids": list(artifact.parent_ids),
                        }
                    ],
                    metadata={"domain": artifact.domain, "artifact_kind": artifact.kind},
                )
            )
        return records

    def memory_context_for_turn(
        self,
        *,
        session_id: str,
        thread_id: Optional[str] = None,
        domain: Optional[str] = None,
        trace_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 6,
    ) -> Dict[str, Any]:
        """Return compact memory context safe to prepend to a model turn."""
        records = self.store.list_memory(
            session_id=session_id,
            thread_id=thread_id,
            status="active",
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )
        if not records and thread_id is not None:
            records = self.store.list_memory(
                session_id=session_id,
                status="active",
                app_id=app_id,
                project_id=project_id,
                workspace_id=workspace_id,
            )
        filtered = [
            record for record in records
            if not domain or record.metadata.get("domain") in {None, domain} or not str(record.kind).startswith("artifact_ref:")
        ]
        selected = filtered[-limit:] if limit > 0 else filtered
        for record in selected:
            self.record_memory_trace(operation="context", memory=record, trace_id=trace_id)
        return {
            "available": bool(selected),
            "records": [_record_to_dict(record) for record in selected],
            "prompt": _memory_prompt(selected),
            "fallback": "" if selected else "No session memory is available for this turn.",
        }

    def ensure_thread(
        self,
        *,
        session_id: str,
        domain: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
    ) -> ThreadRecord:
        """Return the default Core thread for a session/domain, creating it if needed."""
        resolved_scope = scope or ScopeContext()
        cache_key = (
            session_id,
            domain,
            resolved_scope.app_id,
            resolved_scope.project_id,
            resolved_scope.workspace_id,
        )
        cached_thread_id = self._thread_cache.get(cache_key)
        if cached_thread_id:
            try:
                return self.store.get_thread(cached_thread_id)
            except KeyError:
                self._thread_cache.pop(cache_key, None)

        for thread in self.store.list_threads(
            session_id=session_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
        ):
            if thread.metadata.get("gateway_default") and thread.domain == domain:
                self._thread_cache[cache_key] = thread.thread_id
                return thread

        thread = ThreadRecord(
            session_id=session_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            domain=domain,
            title=f"{domain or 'default'} thread",
            metadata={"gateway_default": True, "scope": resolved_scope.to_dict()},
        )
        self.store.save_thread(thread)
        self._thread_cache[cache_key] = thread.thread_id
        return thread

    def _default_thread_id(self, session_id: str) -> Optional[str]:
        for thread in self.store.list_threads(session_id=session_id):
            if thread.metadata.get("gateway_default"):
                return thread.thread_id
        return None

    def start_turn(
        self,
        *,
        turn_id: str,
        session_id: str,
        thread_id: str,
        user_input: str,
        trace_id: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TurnRecord:
        """Create or update a Core turn as running."""
        resolved_scope = scope or ScopeContext()
        try:
            turn = self.store.get_turn(turn_id)
            turn.session_id = session_id
            turn.thread_id = thread_id
            turn.app_id = resolved_scope.app_id
            turn.project_id = resolved_scope.project_id
            turn.workspace_id = resolved_scope.workspace_id
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
                app_id=resolved_scope.app_id,
                project_id=resolved_scope.project_id,
                workspace_id=resolved_scope.workspace_id,
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
        scope: Optional[ScopeContext] = None,
    ) -> ItemRecord:
        """Create or replace a Core item."""
        resolved_scope = scope or ScopeContext()
        item = ItemRecord(
            item_id=item_id,
            session_id=session_id,
            thread_id=thread_id,
            turn_id=turn_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            item_type=item_type,
            role=role,
            content=content,
            status=status,
            parent_item_id=parent_item_id,
        )
        return self.store.save_item(item)

    def record_artifacts_from_event(self, data: Dict[str, Any], *, thread_id: str) -> None:
        scope = resolve_scope_context(data)
        artifact_records = data.get("artifact_records")
        if not isinstance(artifact_records, dict):
            meeting = data.get("meeting")
            artifact_records = meeting.get("artifact_records") if isinstance(meeting, dict) else None
        if not isinstance(artifact_records, dict):
            return
        for record in artifact_records.values():
            if isinstance(record, dict) and record.get("artifact_id"):
                record.setdefault("app_id", scope.app_id)
                record.setdefault("project_id", scope.project_id)
                record.setdefault("workspace_id", scope.workspace_id)
                self.record_gateway_artifact(record, thread_id=thread_id)
        session_id = _optional_text(data.get("session_id"))
        turn_id = _optional_text(data.get("turn_id"))
        domain = _optional_text(data.get("domain"))
        trace_id = _optional_text(data.get("trace_id"))
        if session_id or turn_id:
            self.extract_artifact_memory_refs(
                session_id=session_id,
                turn_id=turn_id,
                domain=domain,
                trace_id=trace_id,
            )

    def start_job(
        self,
        *,
        workflow_id: str,
        domain: Optional[str] = None,
        session_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
        external_job_ref: Optional[str] = None,
        parent_job_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobRecord:
        """Create a Core job for a workflow execution."""
        resolved_scope = scope or ScopeContext()
        job = JobRecord(
            workflow_id=workflow_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            domain=domain,
            session_id=session_id,
            thread_id=thread_id,
            turn_id=turn_id,
            status="running",
            progress=0.0,
            trace_id=trace_id,
            external_job_ref=external_job_ref,
            parent_job_id=parent_job_id,
            metadata=dict(metadata or {}),
        )
        saved = self.store.save_job(job)
        self.record_job_event(
            job_id=saved.job_id,
            event_type="job.queued",
            status="queued",
            progress=0.0,
            message=f"{workflow_id} queued",
            scope=resolved_scope,
            metadata={"workflow_id": workflow_id, "domain": domain, "sync_start": True},
        )
        self.record_job_event(
            job_id=saved.job_id,
            event_type="job.started",
            status=saved.status,
            progress=saved.progress,
            message=f"{workflow_id} started",
            scope=resolved_scope,
            metadata={"workflow_id": workflow_id, "domain": domain},
        )
        return saved

    def create_job(
        self,
        *,
        workflow_id: str,
        domain: Optional[str] = None,
        session_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
        external_job_ref: Optional[str] = None,
        parent_job_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobRecord:
        """Create a queued Core job without starting execution."""
        resolved_scope = scope or ScopeContext()
        job = JobRecord(
            workflow_id=workflow_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            domain=domain,
            session_id=session_id,
            thread_id=thread_id,
            turn_id=turn_id,
            status="queued",
            progress=0.0,
            trace_id=trace_id,
            external_job_ref=external_job_ref,
            parent_job_id=parent_job_id,
            metadata=dict(metadata or {}),
        )
        saved = self.store.save_job(job)
        self.record_job_event(
            job_id=saved.job_id,
            event_type="job.queued",
            status=saved.status,
            progress=saved.progress,
            message=f"{workflow_id} queued",
            scope=resolved_scope,
            metadata={"workflow_id": workflow_id, "domain": domain},
        )
        return saved

    def update_job(
        self,
        *,
        job_id: str,
        status: str,
        progress: Optional[float] = None,
        artifact_ids: Optional[List[str]] = None,
        failure_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobRecord:
        """Update a Core job lifecycle state."""
        job = self.store.get_job(job_id)
        job.status = status
        if progress is not None:
            job.progress = progress
        if artifact_ids is not None:
            job.artifact_ids = list(artifact_ids)
        if failure_context is not None:
            job.failure_context = mask_value(dict(failure_context))
        if metadata:
            job.metadata.update(mask_value(metadata))
        job.updated_at = datetime.now()
        saved = self.store.save_job(job)
        self.record_job_event(
            job_id=saved.job_id,
            event_type=f"job.{status}",
            status=saved.status,
            progress=saved.progress,
            message=str((metadata or {}).get("message") or ""),
            scope=ScopeContext(
                app_id=saved.app_id,
                project_id=saved.project_id,
                workspace_id=saved.workspace_id,
            ),
            metadata=metadata,
        )
        return saved

    def cancel_job(self, job_id: str, *, reason: Optional[str] = None) -> JobRecord:
        """Cancel a queued/running Core job, preserving terminal jobs."""
        job = self.store.get_job(job_id)
        if job.status in {"completed", "failed", "cancelled"}:
            self.record_job_event(
                job_id=job.job_id,
                event_type="job.cancel_ignored",
                status=job.status,
                progress=job.progress,
                message=f"cannot cancel terminal job: {job.status}",
                metadata={"reason": reason, "terminal_status": job.status},
            )
            return job
        metadata = {"cancel_reason": reason} if reason else {}
        return self.update_job(job_id=job_id, status="cancelled", progress=job.progress, metadata=metadata)

    def record_job_event(
        self,
        *,
        job_id: str,
        event_type: str,
        status: str,
        progress: Optional[float] = None,
        message: str = "",
        scope: Optional[ScopeContext] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JobEventRecord:
        """Append a job lifecycle event."""
        job: Optional[JobRecord] = None
        try:
            job = self.store.get_job(job_id)
        except KeyError:
            job = None
        if scope is None:
            if job is not None:
                scope = ScopeContext(app_id=job.app_id, project_id=job.project_id, workspace_id=job.workspace_id)
            else:
                scope = ScopeContext()
        event_metadata = dict(metadata or {})
        if job is not None:
            event_metadata.setdefault("workflow_id", job.workflow_id)
            event_metadata.setdefault("domain", job.domain)
            if job.external_job_ref is not None:
                event_metadata.setdefault("external_job_ref", job.external_job_ref)
            if job.parent_job_id is not None:
                event_metadata.setdefault("parent_job_id", job.parent_job_id)
            if job.artifact_ids:
                event_metadata.setdefault("artifact_ids", list(job.artifact_ids))
            if job.failure_context:
                event_metadata.setdefault("failure_context", dict(job.failure_context))
        event = JobEventRecord(
            job_id=job_id,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            event_type=event_type,
            status=status,
            progress=progress,
            message=message,
            metadata=event_metadata,
        )
        saved = self.store.save_job_event(event)
        self.store.save_trace_record(
            TraceRecord(
                trace_id=str(event_metadata.get("trace_id") or (job.trace_id if job is not None else None) or f"trace_{job_id}"),
                app_id=saved.app_id,
                project_id=saved.project_id,
                workspace_id=saved.workspace_id,
                session_id=job.session_id if job is not None else None,
                turn_id=job.turn_id if job is not None else None,
                event_type=event_type,
                status=status,
                workflow_id=str(event_metadata.get("workflow_id") or "") or None,
                artifact_ids=list(job.artifact_ids) if job is not None else _text_list(event_metadata.get("artifact_ids")),
                input_summary=message,
                metadata=mask_value(
                    {
                        "job_id": job_id,
                        "job_event_id": saved.event_id,
                        "progress": progress,
                        "metadata": event_metadata,
                    }
                ),
            )
        )
        return saved

    def get_session(self, session_id: str) -> SessionRecord:
        return self.store.get_session(session_id)

    def list_sessions(
        self,
        *,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[SessionRecord]:
        return self.store.list_sessions(app_id=app_id, project_id=project_id, workspace_id=workspace_id)

    def read_session_snapshot(self, session_id: str) -> Dict[str, Any]:
        """Return a Gateway-compatible session view from Core records."""
        session = self.get_session(session_id)
        metadata = dict(session.metadata or {})
        return {
            "session_id": session.session_id,
            "model": metadata.get("model"),
            "app_id": session.app_id,
            "project_id": session.project_id,
            "workspace_id": session.workspace_id,
            "state": session.status,
            "backend": metadata.get("backend"),
            "interrupted": bool(metadata.get("interrupted", False)),
            "created_at": session.created_at.isoformat(),
            "last_active_at": session.updated_at.isoformat(),
            "client_type": session.client_type,
            "user_id": session.user_id,
            "tenant_id": session.tenant_id,
            "capabilities": dict(session.capabilities or {}),
            "metadata": metadata,
        }

    def list_session_snapshots(
        self,
        *,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return Gateway-compatible session views from Core records."""
        snapshots = [
            self.read_session_snapshot(session.session_id)
            for session in self.list_sessions(
                app_id=app_id,
                project_id=project_id,
                workspace_id=workspace_id,
            )
        ]
        snapshots.sort(key=lambda item: str(item.get("last_active_at", "")), reverse=True)
        return snapshots

    def read_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Rebuild normalized Gateway events from Core item records."""
        self.get_session(session_id)
        events: List[Dict[str, Any]] = []
        for turn in self.store.list_turns(session_id=session_id):
            for item in self.store.list_items(turn_id=turn.turn_id):
                event = item.content.get("event") if isinstance(item.content, dict) else None
                if isinstance(event, dict):
                    events.append(dict(event))
        events.sort(key=lambda item: str(item.get("timestamp", "")))
        return events

    def read_session_transcript(self, session_id: str) -> List[Dict[str, Any]]:
        """Rebuild a compact transcript from Core item/event records."""
        transcript: List[Dict[str, Any]] = []
        assistant_parts_by_turn: Dict[str, List[str]] = {}
        for event in self.read_session_events(session_id):
            event_type = event.get("type")
            turn_id = str(event.get("turn_id") or "")
            data = event.get("data") if isinstance(event.get("data"), dict) else {}
            if event_type == "turn.started":
                transcript.append(
                    {
                        "role": "user",
                        "turn_id": turn_id,
                        "content": str(data.get("input", "")),
                        "timestamp": event.get("timestamp"),
                    }
                )
            elif event_type == "item.delta":
                assistant_parts_by_turn.setdefault(turn_id, []).append(str(data.get("text", "")))
            elif event_type == "turn.completed":
                content = "".join(assistant_parts_by_turn.pop(turn_id, []))
                if not content:
                    content = _assistant_text(data)
                transcript.append(
                    {
                        "role": "assistant",
                        "turn_id": turn_id,
                        "content": content,
                        "timestamp": event.get("timestamp"),
                    }
                )
            elif event_type in {"turn.failed", "turn.interrupted"}:
                transcript.append(
                    {
                        "role": "system",
                        "turn_id": turn_id,
                        "content": str(data.get("message", event_type)),
                        "timestamp": event.get("timestamp"),
                    }
                )
        return transcript

    def list_threads(
        self,
        *,
        session_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ThreadRecord]:
        return self.store.list_threads(
            session_id=session_id,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

    def get_turn(self, turn_id: str) -> TurnRecord:
        return self.store.get_turn(turn_id)

    def list_items(
        self,
        *,
        turn_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ItemRecord]:
        return self.store.list_items(
            turn_id=turn_id,
            thread_id=thread_id,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

    def list_artifacts(
        self,
        *,
        owner_thread_id: Optional[str] = None,
        owner_session_id: Optional[str] = None,
        owner_turn_id: Optional[str] = None,
        domain: Optional[str] = None,
        kind: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ArtifactRecord]:
        return self.store.list_artifacts(
            owner_thread_id=owner_thread_id,
            owner_session_id=owner_session_id,
            owner_turn_id=owner_turn_id,
            domain=domain,
            kind=kind,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

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
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[JobRecord]:
        return self.store.list_jobs(
            thread_id=thread_id,
            session_id=session_id,
            turn_id=turn_id,
            domain=domain,
            status=status,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

    def list_job_events(
        self,
        *,
        job_id: Optional[str] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[JobEventRecord]:
        return self.store.list_job_events(
            job_id=job_id,
            event_type=event_type,
            status=status,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

    def list_trace_records(
        self,
        *,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        event_type: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[TraceRecord]:
        return self.store.list_trace_records(
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            event_type=event_type,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

    def list_approvals(
        self,
        *,
        decision: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ApprovalRecord]:
        return self.store.list_approvals(
            decision=decision,
            target_type=target_type,
            target_id=target_id,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

    def list_retries(
        self,
        *,
        session_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        status: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[RetryRecord]:
        return self.store.list_retries(
            session_id=session_id,
            approval_id=approval_id,
            status=status,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )


def _event_payload(event: Any) -> Dict[str, Any]:
    if hasattr(event, "model_dump"):
        payload = event.model_dump(mode="json")
        if not isinstance(payload, dict):
            payload = {}
    else:
        payload = {}
    fallback = {
        "type": getattr(event, "type", "gateway.event"),
        "session_id": getattr(event, "session_id", None),
        "turn_id": getattr(event, "turn_id", None),
        "data": getattr(event, "data", {}),
    }
    for key, value in fallback.items():
        payload.setdefault(key, value)
    payload.setdefault("item_id", getattr(event, "item_id", None))
    payload.setdefault("timestamp", getattr(event, "timestamp", None))
    return mask_value(payload)


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


def _artifact_parent_ids(metadata: Dict[str, Any]) -> List[str]:
    parent_ids = []
    source_artifact_id = metadata.get("source_artifact_id")
    if isinstance(source_artifact_id, str) and source_artifact_id:
        parent_ids.append(source_artifact_id)
    explicit_parent_ids = metadata.get("parent_artifact_ids")
    if isinstance(explicit_parent_ids, list):
        parent_ids.extend(item for item in explicit_parent_ids if isinstance(item, str) and item)
    lineage = metadata.get("lineage")
    if isinstance(lineage, dict):
        namespaced_parent_ids = lineage.get("parent_artifact_ids")
        if isinstance(namespaced_parent_ids, list):
            parent_ids.extend(item for item in namespaced_parent_ids if isinstance(item, str) and item)
    return list(dict.fromkeys(parent_ids))


def _connected_artifacts(artifacts: List[ArtifactRecord], artifact_id: str) -> List[ArtifactRecord]:
    artifacts_by_id = {artifact.artifact_id: artifact for artifact in artifacts}
    if artifact_id not in artifacts_by_id:
        return []
    children_by_parent: Dict[str, List[str]] = {}
    for artifact in artifacts:
        for parent_id in artifact.parent_ids:
            children_by_parent.setdefault(parent_id, []).append(artifact.artifact_id)
    selected_ids = {artifact_id}
    frontier = [artifact_id]
    while frontier:
        current_id = frontier.pop()
        current = artifacts_by_id.get(current_id)
        neighbor_ids = []
        if current is not None:
            neighbor_ids.extend(current.parent_ids)
        neighbor_ids.extend(children_by_parent.get(current_id, []))
        for neighbor_id in neighbor_ids:
            if neighbor_id in artifacts_by_id and neighbor_id not in selected_ids:
                selected_ids.add(neighbor_id)
                frontier.append(neighbor_id)
    return [artifact for artifact in artifacts if artifact.artifact_id in selected_ids]


def _record_to_dict(record: Any) -> Dict[str, Any]:
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    return dict(record)


def _summarize_text(value: str, *, limit: int = 240) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "..."


def _artifact_memory_content(artifact: ArtifactRecord) -> str:
    parent_text = f" parents={','.join(artifact.parent_ids)}" if artifact.parent_ids else ""
    return _summarize_text(
        f"{artifact.kind} artifact {artifact.artifact_id} from domain {artifact.domain or 'unknown'} "
        f"at {artifact.uri}.{parent_text}",
        limit=360,
    )


def _memory_prompt(records: List[MemoryRecord]) -> str:
    if not records:
        return ""
    lines = ["Relevant session memory:"]
    for record in records:
        ref_text = ""
        if record.source_artifact_id:
            ref_text = f" artifact={record.source_artifact_id}"
        elif record.source_turn_id:
            ref_text = f" turn={record.source_turn_id}"
        lines.append(f"- {record.kind}{ref_text}: {_summarize_text(record.content, limit=220)}")
    return "\n".join(lines)


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
