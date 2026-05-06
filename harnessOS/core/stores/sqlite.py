"""SQLite-backed Core v1.5 store."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel

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

RecordT = TypeVar("RecordT", bound=BaseModel)

SCOPE_MIGRATION_NAME = "v3_001_add_scope_columns"
SCOPE_MIGRATION_TABLES = (
    "sessions",
    "threads",
    "turns",
    "items",
    "jobs",
    "job_events",
    "artifacts",
    "trace_records",
    "memory_records",
    "approvals",
    "retries",
    "connectors",
)
LEGACY_SCOPE_DEFAULT_APP_ID = "default"
LEGACY_SCOPE_MEETING_APP_ID = "meeting"


class CoreSQLiteStore:
    """SQLite store for Core protocol records.

    The store is intentionally small at this stage: it provides the canonical
    tables and CRUD/query paths needed before the Gateway is migrated onto Core.
    """

    def __init__(self, path: Optional[Union[str, Path]] = None) -> None:
        default_path = Path(__file__).resolve().parents[2] / ".harnessos" / "core.sqlite3"
        self.path = Path(path or default_path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def initialize(self) -> None:
        """Create schema if it does not already exist."""
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS threads (
                    thread_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    domain TEXT,
                    status TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_threads_session ON threads(session_id);
                CREATE TABLE IF NOT EXISTS turns (
                    turn_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    trace_id TEXT,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_turns_thread ON turns(thread_id);
                CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id);
                CREATE TABLE IF NOT EXISTS items (
                    item_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    turn_id TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_items_turn ON items(turn_id);
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    thread_id TEXT,
                    turn_id TEXT,
                    workflow_id TEXT NOT NULL,
                    domain TEXT,
                    status TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_jobs_thread ON jobs(thread_id);
                CREATE TABLE IF NOT EXISTS job_events (
                    event_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_job_events_job ON job_events(job_id);
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    owner_session_id TEXT,
                    owner_thread_id TEXT,
                    owner_turn_id TEXT,
                    domain TEXT,
                    kind TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_artifacts_thread ON artifacts(owner_thread_id);
                CREATE TABLE IF NOT EXISTS trace_records (
                    record_id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    session_id TEXT,
                    turn_id TEXT,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_trace_records_trace ON trace_records(trace_id);
                CREATE INDEX IF NOT EXISTS idx_trace_records_session ON trace_records(session_id);
                CREATE INDEX IF NOT EXISTS idx_trace_records_turn ON trace_records(turn_id);
                CREATE TABLE IF NOT EXISTS memory_records (
                    memory_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    thread_id TEXT,
                    source_turn_id TEXT,
                    source_artifact_id TEXT,
                    scope TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_memory_session ON memory_records(session_id);
                CREATE INDEX IF NOT EXISTS idx_memory_thread ON memory_records(thread_id);
                CREATE INDEX IF NOT EXISTS idx_memory_kind ON memory_records(kind);
                CREATE INDEX IF NOT EXISTS idx_memory_source_artifact ON memory_records(source_artifact_id);
                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    target_type TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    risk_class TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_approvals_target ON approvals(target_type, target_id);
                CREATE INDEX IF NOT EXISTS idx_approvals_decision ON approvals(decision);
                CREATE TABLE IF NOT EXISTS retries (
                    retry_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    source_turn_id TEXT NOT NULL,
                    approval_id TEXT,
                    status TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_retries_session ON retries(session_id);
                CREATE INDEX IF NOT EXISTS idx_retries_approval ON retries(approval_id);
                CREATE TABLE IF NOT EXISTS connectors (
                    connector_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    domain TEXT,
                    health TEXT NOT NULL,
                    app_id TEXT NOT NULL DEFAULT 'default',
                    project_id TEXT,
                    workspace_id TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_connectors_domain ON connectors(domain);
                CREATE INDEX IF NOT EXISTS idx_connectors_health ON connectors(health);
                """
            )
            self._ensure_scope_columns(conn)
            conn.executescript(
                """
                CREATE INDEX IF NOT EXISTS idx_sessions_scope ON sessions(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_threads_scope ON threads(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_turns_scope ON turns(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_items_scope ON items(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_jobs_scope ON jobs(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_job_events_scope ON job_events(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_artifacts_scope ON artifacts(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_trace_records_scope ON trace_records(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_memory_scope_context ON memory_records(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_approvals_scope ON approvals(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_retries_scope ON retries(app_id, project_id, workspace_id);
                CREATE INDEX IF NOT EXISTS idx_connectors_scope ON connectors(app_id, project_id, workspace_id);
                """
            )

    def scope_migration_status(self) -> Dict[str, Any]:
        """Return the frozen PhaseA scope migration semantics."""
        return {
            "migration_name": SCOPE_MIGRATION_NAME,
            "tables": list(SCOPE_MIGRATION_TABLES),
            "strategy": "forward_only",
            "rollback": "non_destructive",
            "default_backfill_app_id": LEGACY_SCOPE_DEFAULT_APP_ID,
            "meeting_backfill_app_id": LEGACY_SCOPE_MEETING_APP_ID,
        }

    def save_session(self, record: SessionRecord) -> SessionRecord:
        self._upsert(
            "sessions",
            "session_id",
            record.session_id,
            record,
            extra={},
        )
        return record

    def get_session(self, session_id: str) -> SessionRecord:
        return self._get("sessions", "session_id", session_id, SessionRecord)

    def list_sessions(
        self,
        *,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[SessionRecord]:
        return self._list(
            "sessions",
            SessionRecord,
            filters=_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
        )

    def save_thread(self, record: ThreadRecord) -> ThreadRecord:
        self._upsert(
            "threads",
            "thread_id",
            record.thread_id,
            record,
            extra={
                "session_id": record.session_id,
                "domain": record.domain,
                "status": record.status,
            },
        )
        return record

    def get_thread(self, thread_id: str) -> ThreadRecord:
        return self._get("threads", "thread_id", thread_id, ThreadRecord)

    def list_threads(
        self,
        *,
        session_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ThreadRecord]:
        return self._list(
            "threads",
            ThreadRecord,
            filters={
                "session_id": session_id,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_turn(self, record: TurnRecord) -> TurnRecord:
        self._upsert(
            "turns",
            "turn_id",
            record.turn_id,
            record,
            extra={
                "session_id": record.session_id,
                "thread_id": record.thread_id,
                "state": record.state,
                "trace_id": record.trace_id,
            },
        )
        return record

    def get_turn(self, turn_id: str) -> TurnRecord:
        return self._get("turns", "turn_id", turn_id, TurnRecord)

    def list_turns(
        self,
        *,
        thread_id: Optional[str] = None,
        session_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[TurnRecord]:
        return self._list(
            "turns",
            TurnRecord,
            filters={
                "thread_id": thread_id,
                "session_id": session_id,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_item(self, record: ItemRecord) -> ItemRecord:
        self._upsert(
            "items",
            "item_id",
            record.item_id,
            record,
            extra={
                "session_id": record.session_id,
                "thread_id": record.thread_id,
                "turn_id": record.turn_id,
                "item_type": record.item_type,
                "status": record.status,
            },
        )
        return record

    def get_item(self, item_id: str) -> ItemRecord:
        return self._get("items", "item_id", item_id, ItemRecord)

    def list_items(
        self,
        *,
        turn_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[ItemRecord]:
        return self._list(
            "items",
            ItemRecord,
            filters={
                "turn_id": turn_id,
                "thread_id": thread_id,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_job(self, record: JobRecord) -> JobRecord:
        self._upsert(
            "jobs",
            "job_id",
            record.job_id,
            record,
            extra={
                "session_id": record.session_id,
                "thread_id": record.thread_id,
                "turn_id": record.turn_id,
                "workflow_id": record.workflow_id,
                "domain": record.domain,
                "status": record.status,
            },
        )
        return record

    def get_job(self, job_id: str) -> JobRecord:
        return self._get("jobs", "job_id", job_id, JobRecord)

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
        return self._list(
            "jobs",
            JobRecord,
            filters={
                "thread_id": thread_id,
                "session_id": session_id,
                "turn_id": turn_id,
                "domain": domain,
                "status": status,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_job_event(self, record: JobEventRecord) -> JobEventRecord:
        self._upsert(
            "job_events",
            "event_id",
            record.event_id,
            record,
            extra={
                "job_id": record.job_id,
                "event_type": record.event_type,
                "status": record.status,
            },
        )
        return record

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
        return self._list(
            "job_events",
            JobEventRecord,
            filters={
                "job_id": job_id,
                "event_type": event_type,
                "status": status,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_artifact(self, record: ArtifactRecord) -> ArtifactRecord:
        self._upsert(
            "artifacts",
            "artifact_id",
            record.artifact_id,
            record,
            extra={
                "owner_session_id": record.owner_session_id,
                "owner_thread_id": record.owner_thread_id,
                "owner_turn_id": record.owner_turn_id,
                "domain": record.domain,
                "kind": record.kind,
            },
        )
        return record

    def get_artifact(self, artifact_id: str) -> ArtifactRecord:
        return self._get("artifacts", "artifact_id", artifact_id, ArtifactRecord)

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
        return self._list(
            "artifacts",
            ArtifactRecord,
            filters={
                "owner_thread_id": owner_thread_id,
                "owner_session_id": owner_session_id,
                "owner_turn_id": owner_turn_id,
                "domain": domain,
                "kind": kind,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_trace_record(self, record: TraceRecord) -> TraceRecord:
        self._upsert(
            "trace_records",
            "record_id",
            record.record_id,
            record,
            extra={
                "trace_id": record.trace_id,
                "session_id": record.session_id,
                "turn_id": record.turn_id,
                "event_type": record.event_type,
                "status": record.status,
            },
        )
        return record

    def get_trace_record(self, record_id: str) -> TraceRecord:
        return self._get("trace_records", "record_id", record_id, TraceRecord)

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
        return self._list(
            "trace_records",
            TraceRecord,
            filters={
                "trace_id": trace_id,
                "session_id": session_id,
                "turn_id": turn_id,
                "event_type": event_type,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_memory(self, record: MemoryRecord) -> MemoryRecord:
        self._upsert(
            "memory_records",
            "memory_id",
            record.memory_id,
            record,
            extra={
                "session_id": record.session_id,
                "thread_id": record.thread_id,
                "source_turn_id": record.source_turn_id,
                "source_artifact_id": record.source_artifact_id,
                "scope": record.scope,
                "kind": record.kind,
                "status": record.status,
            },
        )
        return record

    def get_memory(self, memory_id: str) -> MemoryRecord:
        return self._get("memory_records", "memory_id", memory_id, MemoryRecord)

    def list_memory(
        self,
        *,
        session_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        kind: Optional[str] = None,
        source_artifact_id: Optional[str] = None,
        status: Optional[str] = None,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[MemoryRecord]:
        return self._list(
            "memory_records",
            MemoryRecord,
            filters={
                "session_id": session_id,
                "thread_id": thread_id,
                "kind": kind,
                "source_artifact_id": source_artifact_id,
                "status": status,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_approval(self, record: ApprovalRecord) -> ApprovalRecord:
        self._upsert(
            "approvals",
            "approval_id",
            record.approval_id,
            record,
            extra={
                "target_type": record.target_type,
                "target_id": record.target_id,
                "decision": record.decision,
                "risk_class": record.risk_class,
            },
        )
        return record

    def get_approval(self, approval_id: str) -> ApprovalRecord:
        return self._get("approvals", "approval_id", approval_id, ApprovalRecord)

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
        return self._list(
            "approvals",
            ApprovalRecord,
            filters={
                "decision": decision,
                "target_type": target_type,
                "target_id": target_id,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_retry(self, record: RetryRecord) -> RetryRecord:
        self._upsert(
            "retries",
            "retry_id",
            record.retry_id,
            record,
            extra={
                "session_id": record.session_id,
                "source_turn_id": record.source_turn_id,
                "approval_id": record.approval_id,
                "status": record.status,
            },
        )
        return record

    def get_retry(self, retry_id: str) -> RetryRecord:
        return self._get("retries", "retry_id", retry_id, RetryRecord)

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
        return self._list(
            "retries",
            RetryRecord,
            filters={
                "session_id": session_id,
                "approval_id": approval_id,
                "status": status,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def save_connector(self, record: ConnectorRecord) -> ConnectorRecord:
        self._upsert(
            "connectors",
            "connector_id",
            record.connector_id,
            record,
            extra={
                "kind": record.kind,
                "domain": record.domain,
                "health": record.health,
            },
        )
        return record

    def get_connector(self, connector_id: str) -> ConnectorRecord:
        return self._get("connectors", "connector_id", connector_id, ConnectorRecord)

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
        return self._list(
            "connectors",
            ConnectorRecord,
            filters={
                "domain": domain,
                "kind": kind,
                "health": health,
                **_scope_filters(app_id=app_id, project_id=project_id, workspace_id=workspace_id),
            },
        )

    def import_legacy_sessions(self, legacy_root: Union[str, Path]) -> int:
        """Import legacy Gateway session snapshots and events into Core records.

        This is intentionally conservative: it imports snapshots as sessions and
        event log lines as items. It does not delete or mutate legacy files.
        """
        root = Path(legacy_root).expanduser().resolve()
        if not root.exists():
            return 0
        imported = 0
        for snapshot_path in sorted(root.glob("*/snapshot.json")):
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
            if not isinstance(snapshot, dict) or not snapshot.get("session_id"):
                continue
            events: list[Dict[str, Any]] = []
            events_path = snapshot_path.parent / "events.jsonl"
            if events_path.exists():
                for line in events_path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        event = json.loads(line)
                        if isinstance(event, dict):
                            events.append(event)
            scope = _legacy_scope_context(snapshot, events)
            session = SessionRecord(
                session_id=str(snapshot["session_id"]),
                client_type="legacy_gateway",
                app_id=scope["app_id"],
                project_id=scope["project_id"],
                workspace_id=scope["workspace_id"],
                status=str(snapshot.get("state") or "unknown"),
                metadata={"legacy_snapshot": snapshot},
            )
            self.save_session(session)
            thread = ThreadRecord(
                session_id=session.session_id,
                app_id=scope["app_id"],
                project_id=scope["project_id"],
                workspace_id=scope["workspace_id"],
                title=f"Legacy session {session.session_id}",
                metadata={"legacy_import": True},
            )
            self.save_thread(thread)
            if events:
                turn_by_legacy_id: Dict[str, str] = {}
                for event in events:
                    event_scope = _legacy_scope_context(snapshot, [event], base_scope=scope)
                    legacy_turn_id = str(event.get("turn_id") or "legacy")
                    if legacy_turn_id not in turn_by_legacy_id:
                        turn = TurnRecord(
                            session_id=session.session_id,
                            thread_id=thread.thread_id,
                            app_id=event_scope["app_id"],
                            project_id=event_scope["project_id"],
                            workspace_id=event_scope["workspace_id"],
                            input=_legacy_event_input(event),
                            state="imported",
                            metadata={"legacy_turn_id": legacy_turn_id},
                        )
                        self.save_turn(turn)
                        turn_by_legacy_id[legacy_turn_id] = turn.turn_id
                    item = ItemRecord(
                        session_id=session.session_id,
                        thread_id=thread.thread_id,
                        turn_id=turn_by_legacy_id[legacy_turn_id],
                        app_id=event_scope["app_id"],
                        project_id=event_scope["project_id"],
                        workspace_id=event_scope["workspace_id"],
                        item_type=str(event.get("type") or "legacy.event"),
                        content={"legacy_event": event},
                        status="imported",
                    )
                    self.save_item(item)
            imported += 1
        return imported

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_scope_columns(self, conn: sqlite3.Connection) -> None:
        for table in SCOPE_MIGRATION_TABLES:
            existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            if "app_id" not in existing:
                conn.execute(
                    f"ALTER TABLE {table} ADD COLUMN app_id TEXT NOT NULL DEFAULT '{LEGACY_SCOPE_DEFAULT_APP_ID}'"
                )
            if "project_id" not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN project_id TEXT")
            if "workspace_id" not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN workspace_id TEXT")

    def _upsert(
        self,
        table: str,
        key_column: str,
        key_value: str,
        record: BaseModel,
        *,
        extra: Dict[str, Any],
    ) -> None:
        payload = _dump_record(record)
        extra = {**_record_scope_extra(record), **extra}
        columns = [key_column, *extra.keys(), "payload", "created_at", "updated_at"]
        values = [
            key_value,
            *extra.values(),
            payload,
            _iso(getattr(record, "created_at")),
            _iso(getattr(record, "updated_at")),
        ]
        placeholders = ", ".join("?" for _ in columns)
        updates = ", ".join(f"{column}=excluded.{column}" for column in columns if column != key_column)
        with self._connect() as conn:
            conn.execute(
                f"""
                INSERT INTO {table} ({", ".join(columns)})
                VALUES ({placeholders})
                ON CONFLICT({key_column}) DO UPDATE SET {updates}
                """,
                values,
            )

    def _get(self, table: str, key_column: str, key_value: str, model: Type[RecordT]) -> RecordT:
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT payload FROM {table} WHERE {key_column} = ?",
                (key_value,),
            ).fetchone()
        if row is None:
            raise KeyError(f"{table} record not found: {key_value}")
        return _load_record(row["payload"], model)

    def _list(
        self,
        table: str,
        model: Type[RecordT],
        *,
        filters: Optional[Dict[str, Optional[str]]] = None,
    ) -> List[RecordT]:
        where: List[str] = []
        values: List[str] = []
        for key, value in (filters or {}).items():
            if value is None:
                continue
            where.append(f"{key} = ?")
            values.append(value)
        sql = f"SELECT payload FROM {table}"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY created_at ASC"
        with self._connect() as conn:
            rows = conn.execute(sql, values).fetchall()
        return [_load_record(row["payload"], model) for row in rows]


def _dump_record(record: BaseModel) -> str:
    if hasattr(record, "model_dump_json"):
        return record.model_dump_json()
    return record.json()


def _record_scope_extra(record: BaseModel) -> Dict[str, Any]:
    return {
        "app_id": str(getattr(record, "app_id", "default") or "default"),
        "project_id": getattr(record, "project_id", None),
        "workspace_id": getattr(record, "workspace_id", None),
    }


def _scope_filters(
    *,
    app_id: Optional[str] = None,
    project_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    return {
        "app_id": app_id,
        "project_id": project_id,
        "workspace_id": workspace_id,
    }


def _load_record(payload: str, model: Type[RecordT]) -> RecordT:
    if hasattr(model, "model_validate_json"):
        return model.model_validate_json(payload)
    return model.parse_raw(payload)


def _iso(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _legacy_event_input(event: Dict[str, Any]) -> str:
    data = event.get("data") if isinstance(event, dict) else None
    if isinstance(data, dict) and isinstance(data.get("input"), str):
        return data["input"]
    return ""


def _legacy_scope_context(
    snapshot: Dict[str, Any],
    events: Sequence[Dict[str, Any]],
    *,
    base_scope: Optional[Dict[str, Optional[str]]] = None,
) -> Dict[str, Optional[str]]:
    base_scope = dict(base_scope or {})
    snapshot_scope = _legacy_scope_from_mapping(snapshot)
    event_scopes = [_legacy_scope_from_mapping(event.get("data")) for event in events if isinstance(event, dict)]

    app_id = (
        _first_text(
            base_scope.get("app_id"),
            snapshot_scope["app_id"],
            *[scope["app_id"] for scope in event_scopes],
        )
        or _legacy_inferred_app_id(snapshot, events)
        or LEGACY_SCOPE_DEFAULT_APP_ID
    )
    return {
        "app_id": app_id,
        "project_id": _first_text(
            base_scope.get("project_id"),
            snapshot_scope["project_id"],
            *[scope["project_id"] for scope in event_scopes],
        ),
        "workspace_id": _first_text(
            base_scope.get("workspace_id"),
            snapshot_scope["workspace_id"],
            *[scope["workspace_id"] for scope in event_scopes],
        ),
    }


def _legacy_scope_from_mapping(payload: Any) -> Dict[str, Optional[str]]:
    if not isinstance(payload, dict):
        return {"app_id": None, "project_id": None, "workspace_id": None}
    scope = payload.get("scope")
    scope_payload = scope if isinstance(scope, dict) else {}
    return {
        "app_id": _text_or_none(scope_payload.get("app_id")) or _text_or_none(payload.get("app_id")),
        "project_id": _text_or_none(scope_payload.get("project_id")) or _text_or_none(payload.get("project_id")),
        "workspace_id": _text_or_none(scope_payload.get("workspace_id")) or _text_or_none(payload.get("workspace_id")),
    }


def _legacy_inferred_app_id(snapshot: Dict[str, Any], events: Sequence[Dict[str, Any]]) -> Optional[str]:
    if _mapping_contains_meeting(snapshot):
        return LEGACY_SCOPE_MEETING_APP_ID
    for event in events:
        if _mapping_contains_meeting(event):
            return LEGACY_SCOPE_MEETING_APP_ID
        data = event.get("data") if isinstance(event, dict) else None
        if isinstance(data, dict) and _mapping_contains_meeting(data):
            return LEGACY_SCOPE_MEETING_APP_ID
    return None


def _mapping_contains_meeting(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    domain = _text_or_none(payload.get("domain"))
    if domain == LEGACY_SCOPE_MEETING_APP_ID:
        return True
    for key in ("path", "audio_path", "source_path", "input"):
        value = _text_or_none(payload.get(key))
        if value and _looks_like_meeting_audio_path(value):
            return True
    return False


def _looks_like_meeting_audio_path(value: str) -> bool:
    lowered = value.lower()
    return lowered.endswith((".wav", ".mp3", ".m4a", ".aac", ".flac"))


def _first_text(*values: Optional[str]) -> Optional[str]:
    for value in values:
        text = _text_or_none(value)
        if text is not None:
            return text
    return None


def _text_or_none(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None
