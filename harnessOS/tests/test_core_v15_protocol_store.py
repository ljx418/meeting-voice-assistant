from __future__ import annotations

import asyncio
import json
import sqlite3
from types import SimpleNamespace

import pytest

from core.jobs import BackgroundJobWorker
from core.apps import ScopeContext
from core.protocol import (
    ApprovalRecord,
    ArtifactRecord,
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
from core.services import CoreAppService
from core.stores import CoreSQLiteStore
from core.stores.sqlite import (
    LEGACY_SCOPE_DEFAULT_APP_ID,
    LEGACY_SCOPE_MEETING_APP_ID,
    SCOPE_MIGRATION_NAME,
)


def test_core_protocol_objects_round_trip() -> None:
    session = SessionRecord(client_type="test", user_id="user_1")
    thread = ThreadRecord(session_id=session.session_id, domain="meeting", title="Demo")
    turn = TurnRecord(session_id=session.session_id, thread_id=thread.thread_id, input="你好")
    item = ItemRecord(
        session_id=session.session_id,
        thread_id=thread.thread_id,
        turn_id=turn.turn_id,
        item_type="assistant_message",
        role="assistant",
        content={"text": "你好，有什么可以帮你？"},
    )

    assert session.session_id.startswith("sess_")
    assert thread.thread_id.startswith("thread_")
    assert turn.turn_id.startswith("turn_")
    assert item.item_id.startswith("item_")
    assert item.content["text"].startswith("你好")
    memory = MemoryRecord(session_id=session.session_id, kind="session_summary", content="demo summary")
    assert memory.memory_id.startswith("mem_")
    assert memory.content == "demo summary"


def test_core_app_service_records_runtime_session_via_native_mutation(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)

    session = SimpleNamespace(
        session_id="sess_service",
        state="idle",
        model="test-model",
        backend="simple",
        interrupted=False,
    )

    service.record_runtime_session(session)
    session.state = "closed"
    service.record_runtime_session(session)

    record = service.get_session("sess_service")
    assert record.session_id == "sess_service"
    assert record.client_type == "gateway"
    assert record.status == "closed"
    assert record.metadata["model"] == "test-model"


def test_core_app_service_records_gateway_events_via_native_mutation(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)
    event_base = {
        "session_id": "sess_events",
        "turn_id": "turn_events",
        "model_dump": lambda **_kwargs: {},
    }

    started = SimpleNamespace(
        **event_base,
        type="turn.started",
        item_id="item_user",
        data={"input": "你好", "domain": "meeting", "trace_id": "trace_events"},
    )
    delta = SimpleNamespace(
        **event_base,
        type="item.delta",
        item_id="item_delta",
        data={"text": "处理中", "trace_id": "trace_events"},
    )
    completed = SimpleNamespace(
        **event_base,
        type="turn.completed",
        item_id="item_assistant",
        data={
            "message": {"role": "assistant", "content": [{"type": "text", "text": "完成"}]},
            "trace_id": "trace_events",
        },
    )

    service.record_gateway_event(started)
    service.record_gateway_event(delta)
    service.record_gateway_event(completed)

    turns = store.list_turns(session_id="sess_events")
    items = store.list_items(turn_id="turn_events")

    assert len(turns) == 1
    assert turns[0].state == "completed"
    assert turns[0].trace_id == "trace_events"
    assert [item.item_type for item in items] == [
        "user_message",
        "assistant_message_delta",
        "assistant_message",
    ]
    session_view = service.read_session_snapshot("sess_events")
    events = service.read_session_events("sess_events")
    transcript = service.read_session_transcript("sess_events")
    assert session_view["session_id"] == "sess_events"
    assert [event["type"] for event in events] == ["turn.started", "item.delta", "turn.completed"]
    assert [item["role"] for item in transcript] == ["user", "assistant"]
    assert transcript[0]["content"] == "你好"
    assert transcript[1]["content"] == "处理中"


def test_core_app_service_records_governance_and_artifacts_via_native_mutation(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)

    artifact = service.record_gateway_artifact(
        {
            "artifact_id": "art_native",
            "session_id": "sess_native",
            "turn_id": "turn_native",
            "domain": "meeting",
            "kind": "minutes",
            "name": "minutes.md",
            "path": "/tmp/minutes.md",
            "mime": "text/markdown",
        }
    )
    trace = service.record_gateway_trace(
        {
            "trace_id": "trace_native",
            "session_id": "sess_native",
            "turn_id": "turn_native",
            "event_type": "turn.completed",
            "status": "success",
            "workflow_id": "meeting.workflow",
            "artifact_ids": ["art_native"],
            "approval_ids": ["appr_native"],
            "input_summary": "meeting done",
        }
    )
    approval = service.record_gateway_approval(
        {
            "approval_id": "appr_native",
            "turn_id": "turn_native",
            "risk_level": "high",
            "request_summary": "write file",
            "status": "approved",
            "decided_at": "2026-04-27T12:00:00",
        }
    )
    retry = service.record_gateway_retry(
        {
            "retry_id": "retry_native",
            "source_turn_id": "turn_native",
            "session_id": "sess_native",
            "input": "write file",
            "domain": "meeting",
            "trace_id": "trace_native",
            "approval_id": "appr_native",
            "status": "retried",
            "workflow_id": "meeting.workflow",
            "artifact_ids": ["art_native"],
            "policy": {"requires_approval": True},
            "retried_at": "2026-04-27T12:01:00",
            "retry_turn_id": "turn_retry",
            "retry_trace_id": "trace_retry",
        }
    )

    assert artifact.owner_thread_id is not None
    assert store.get_artifact("art_native").owner_session_id == "sess_native"
    assert store.get_trace_record(trace.record_id).artifact_ids == ["art_native"]
    assert store.get_approval("appr_native").decision == "approved"
    assert store.get_approval("appr_native").target_type == "turn"
    assert store.get_retry("retry_native").retry_turn_id == "turn_retry"
    assert service.list_artifacts(domain="meeting", kind="minutes")[0].artifact_id == "art_native"
    assert service.list_trace_records(trace_id="trace_native")[0].event_type == "turn.completed"
    assert service.list_approvals(decision="approved")[0].approval_id == "appr_native"
    assert service.list_retries(approval_id="appr_native")[0].retry_id == retry.retry_id


def test_core_app_service_job_lifecycle(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)
    service.upsert_session(session_id="sess_job", client_type="test")
    thread = service.ensure_thread(session_id="sess_job", domain="meeting")

    job = service.start_job(
        workflow_id="meeting.workflow",
        domain="meeting",
        session_id="sess_job",
        thread_id=thread.thread_id,
        turn_id="turn_job",
        trace_id="trace_job",
        metadata={"input": "audio.mp3"},
    )
    assert job.status == "running"
    assert service.get_job(job.job_id).progress == 0.0
    assert [event.event_type for event in service.list_job_events(job_id=job.job_id)] == [
        "job.queued",
        "job.started",
    ]

    completed = service.update_job(
        job_id=job.job_id,
        status="completed",
        progress=1.0,
        artifact_ids=["art_minutes"],
    )
    assert completed.status == "completed"
    assert completed.artifact_ids == ["art_minutes"]
    assert service.list_jobs(session_id="sess_job", domain="meeting", status="completed")[0].job_id == job.job_id
    assert service.list_job_events(job_id=job.job_id)[-1].event_type == "job.completed"
    traces = service.list_trace_records(trace_id="trace_job")
    assert [trace.event_type for trace in traces] == ["job.queued", "job.started", "job.completed"]
    assert {trace.session_id for trace in traces} == {"sess_job"}
    assert {trace.turn_id for trace in traces} == {"turn_job"}
    assert traces[-1].artifact_ids == ["art_minutes"]

    cancelled = service.cancel_job(job.job_id, reason="manual")
    assert cancelled.status == "completed"
    assert service.list_job_events(job_id=job.job_id)[-1].event_type == "job.cancel_ignored"
    ignored = service.list_trace_records(trace_id="trace_job")[-1]
    assert ignored.event_type == "job.cancel_ignored"
    assert ignored.session_id == "sess_job"


def test_core_app_service_failed_job_trace_keeps_origin_context(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)

    job = service.create_job(
        workflow_id="background.workflow",
        domain="background",
        session_id="sess_failed_job",
        turn_id="turn_failed_job",
        trace_id="trace_failed_job",
        scope=ScopeContext(app_id="meeting", workspace_id="workspace_m"),
        external_job_ref="external_1",
        parent_job_id="job_parent",
    )
    service.update_job(
        job_id=job.job_id,
        status="failed",
        progress=1.0,
        failure_context={
            "type": "background_worker_failed",
            "retryable": False,
            "message": "boom",
        },
    )

    failed = service.list_trace_records(trace_id="trace_failed_job")[-1]
    assert failed.event_type == "job.failed"
    assert failed.session_id == "sess_failed_job"
    assert failed.turn_id == "turn_failed_job"
    assert failed.workflow_id == "background.workflow"
    assert failed.metadata["metadata"]["failure_context"]["message"] == "boom"
    assert failed.metadata["metadata"]["external_job_ref"] == "external_1"
    assert failed.app_id == "meeting"
    assert failed.workspace_id == "workspace_m"


def test_core_app_service_session_summary_and_artifact_memory_refs(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)

    started = SimpleNamespace(
        session_id="sess_memory",
        turn_id="turn_memory",
        type="turn.started",
        item_id="item_memory_user",
        data={"input": "请总结这次会议", "domain": "meeting", "trace_id": "trace_memory"},
        model_dump=lambda **_kwargs: {},
    )
    completed = SimpleNamespace(
        session_id="sess_memory",
        turn_id="turn_memory",
        type="turn.completed",
        item_id="item_memory_assistant",
        data={
            "message": {"role": "assistant", "content": [{"type": "text", "text": "会议纪要已完成 sk-12345678"}]},
            "trace_id": "trace_memory",
        },
        model_dump=lambda **_kwargs: {},
    )
    service.record_gateway_event(started)
    service.record_gateway_event(completed)

    summary = service.build_session_summary(session_id="sess_memory", trace_id="trace_memory")

    assert summary.kind == "session_summary"
    assert "请总结这次会议" in summary.content
    assert "[REDACTED]" in summary.content
    assert service.list_memory_records(session_id="sess_memory", kind="session_summary")[0].memory_id == summary.memory_id

    artifact = service.record_gateway_artifact(
        {
            "artifact_id": "art_minutes_memory",
            "session_id": "sess_memory",
            "turn_id": "turn_memory",
            "domain": "meeting",
            "kind": "minutes",
            "name": "minutes.md",
            "path": str(tmp_path / "minutes.md"),
            "mime": "text/markdown",
        }
    )
    refs = service.extract_artifact_memory_refs(session_id="sess_memory", domain="meeting", trace_id="trace_memory")
    context = service.memory_context_for_turn(session_id="sess_memory", domain="meeting", trace_id="trace_memory")

    assert artifact.artifact_id in {ref.source_artifact_id for ref in refs}
    assert "artifact=art_minutes_memory" in context["prompt"]
    assert service.list_trace_records(trace_id="trace_memory", event_type="memory.write")

    queued = service.create_job(workflow_id="meeting.workflow", session_id="sess_job")
    assert queued.status == "queued"
    cancelled_queued = service.cancel_job(queued.job_id, reason="manual")
    assert cancelled_queued.status == "cancelled"
    assert cancelled_queued.metadata["cancel_reason"] == "manual"


@pytest.mark.asyncio
async def test_background_job_worker_lifecycle(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)
    worker = BackgroundJobWorker(core_service=service)

    async def handler(job: JobRecord) -> dict:
        assert job.status == "running"
        await asyncio.sleep(0)
        return {"artifact_ids": ["art_worker"], "message": "done"}

    scope = ScopeContext(app_id="meeting", project_id="project_a", workspace_id="workspace_a")
    job = worker.submit(workflow_id="meeting.workflow", handler=handler, domain="meeting", scope=scope)
    assert job.status == "queued"
    assert job.app_id == "meeting"

    completed = await worker.wait(job.job_id)
    assert completed.status == "completed"
    assert completed.workspace_id == "workspace_a"
    assert completed.progress == 1.0
    assert completed.artifact_ids == ["art_worker"]
    assert [event.event_type for event in service.list_job_events(job_id=job.job_id)] == [
        "job.queued",
        "job.running",
        "job.completed",
    ]
    traces = service.list_trace_records(event_type="job.completed", app_id="meeting", workspace_id="workspace_a")
    assert traces


@pytest.mark.asyncio
async def test_background_job_worker_failure_context(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    service = CoreAppService(store=store)
    worker = BackgroundJobWorker(core_service=service)

    def handler(_job: JobRecord) -> dict:
        raise RuntimeError("boom")

    job = worker.submit(workflow_id="meeting.workflow", handler=handler, domain="meeting")
    failed = await worker.wait(job.job_id)
    assert failed.status == "failed"
    assert failed.failure_context["error_type"] == "RuntimeError"
    assert failed.failure_context["message"] == "boom"
    assert failed.metadata["failure_context"]["error_type"] == "RuntimeError"
    assert failed.metadata["failure_context"]["message"] == "boom"


def test_core_sqlite_store_crud_and_filters(tmp_path) -> None:
    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    session = store.save_session(SessionRecord(client_type="cli", user_id="u1"))
    thread = store.save_thread(ThreadRecord(session_id=session.session_id, domain="meeting", title="Meeting"))
    other_thread = store.save_thread(ThreadRecord(session_id=session.session_id, domain="knowledge", title="Knowledge"))
    turn = store.save_turn(
        TurnRecord(
            session_id=session.session_id,
            thread_id=thread.thread_id,
            input="请生成会议纪要",
            trace_id="trace_demo",
        )
    )
    item = store.save_item(
        ItemRecord(
            session_id=session.session_id,
            thread_id=thread.thread_id,
            turn_id=turn.turn_id,
            item_type="user_message",
            role="user",
            content={"text": "请生成会议纪要"},
        )
    )
    job = store.save_job(
        JobRecord(
            workflow_id="meeting.workflow",
            domain="meeting",
            session_id=session.session_id,
            thread_id=thread.thread_id,
            turn_id=turn.turn_id,
            status="completed",
            progress=1.0,
        )
    )
    artifact = store.save_artifact(
        ArtifactRecord(
            domain="meeting",
            kind="minutes",
            owner_session_id=session.session_id,
            owner_thread_id=thread.thread_id,
            owner_turn_id=turn.turn_id,
            uri="file:///tmp/minutes.md",
            name="minutes.md",
        )
    )
    trace = store.save_trace_record(
        TraceRecord(
            trace_id="trace_demo",
            session_id=session.session_id,
            turn_id=turn.turn_id,
            event_type="turn.completed",
            status="success",
            artifact_ids=[artifact.artifact_id],
        )
    )
    approval = store.save_approval(
        ApprovalRecord(
            approval_id="appr_demo",
            target_type="turn",
            target_id=turn.turn_id,
            risk_class="high",
            reason="write file",
            decision="pending",
        )
    )
    retry = store.save_retry(
        RetryRecord(
            retry_id="retry_demo",
            source_turn_id=turn.turn_id,
            session_id=session.session_id,
            input="请写入文件",
            trace_id="trace_demo",
            approval_id=approval.approval_id,
            status="pending_approval",
        )
    )

    assert store.get_session(session.session_id).client_type == "cli"
    assert store.get_thread(thread.thread_id).domain == "meeting"
    assert store.get_turn(turn.turn_id).trace_id == "trace_demo"
    assert store.get_item(item.item_id).role == "user"
    assert store.get_job(job.job_id).status == "completed"
    assert store.get_artifact(artifact.artifact_id).kind == "minutes"
    assert store.get_trace_record(trace.record_id).event_type == "turn.completed"
    assert store.get_approval(approval.approval_id).decision == "pending"
    assert store.get_retry(retry.retry_id).approval_id == approval.approval_id

    assert [record.thread_id for record in store.list_threads(session_id=session.session_id)] == [
        thread.thread_id,
        other_thread.thread_id,
    ]
    assert [record.turn_id for record in store.list_turns(thread_id=thread.thread_id)] == [turn.turn_id]
    assert [record.item_id for record in store.list_items(turn_id=turn.turn_id)] == [item.item_id]
    assert [record.job_id for record in store.list_jobs(thread_id=thread.thread_id, status="completed")] == [job.job_id]
    assert [record.artifact_id for record in store.list_artifacts(owner_thread_id=thread.thread_id)] == [
        artifact.artifact_id
    ]
    assert [record.record_id for record in store.list_trace_records(trace_id="trace_demo")] == [trace.record_id]
    assert [record.approval_id for record in store.list_approvals(decision="pending")] == [approval.approval_id]
    assert [record.retry_id for record in store.list_retries(approval_id=approval.approval_id)] == [retry.retry_id]


def test_core_sqlite_store_imports_legacy_gateway_sessions(tmp_path) -> None:
    legacy_root = tmp_path / "legacy_sessions"
    session_dir = legacy_root / "sess_legacy"
    session_dir.mkdir(parents=True)
    (session_dir / "snapshot.json").write_text(
        json.dumps(
            {
                "session_id": "sess_legacy",
                "model": "test-model",
                "state": "idle",
                "backend": "simple",
                "created_at": "2026-04-27T00:00:00",
                "last_active_at": "2026-04-27T00:00:01",
            }
        ),
        encoding="utf-8",
    )
    (session_dir / "events.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "turn.started",
                        "session_id": "sess_legacy",
                        "turn_id": "turn_legacy",
                        "data": {"input": "你好"},
                    }
                ),
                json.dumps(
                    {
                        "type": "turn.completed",
                        "session_id": "sess_legacy",
                        "turn_id": "turn_legacy",
                        "data": {"message": {"role": "assistant"}},
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    store = CoreSQLiteStore(tmp_path / "core.sqlite3")
    assert store.import_legacy_sessions(legacy_root) == 1

    session = store.get_session("sess_legacy")
    threads = store.list_threads(session_id=session.session_id)
    turns = store.list_turns(session_id=session.session_id)
    items = store.list_items(thread_id=threads[0].thread_id)

    assert session.client_type == "legacy_gateway"
    assert len(threads) == 1
    assert len(turns) == 1
    assert turns[0].input == "你好"
    assert [item.item_type for item in items] == ["turn.started", "turn.completed"]
    assert session.app_id == LEGACY_SCOPE_DEFAULT_APP_ID


def test_core_sqlite_store_scope_migration_backfills_legacy_schema(tmp_path) -> None:
    path = tmp_path / "legacy_core.sqlite3"
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE sessions (
                session_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO sessions (session_id, payload, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                "sess_legacy_schema",
                json.dumps(SessionRecord(session_id="sess_legacy_schema").model_dump(mode="json"), ensure_ascii=False),
                "2026-05-01T00:00:00",
                "2026-05-01T00:00:00",
            ),
        )

    store = CoreSQLiteStore(path)
    session = store.get_session("sess_legacy_schema")
    migration = store.scope_migration_status()

    assert session.app_id == LEGACY_SCOPE_DEFAULT_APP_ID
    assert migration["migration_name"] == SCOPE_MIGRATION_NAME
    assert migration["strategy"] == "forward_only"
    assert migration["rollback"] == "non_destructive"


def test_core_sqlite_store_imports_legacy_meeting_sessions_with_meeting_backfill(tmp_path) -> None:
    legacy_root = tmp_path / "legacy_sessions"
    session_dir = legacy_root / "sess_meeting_legacy"
    session_dir.mkdir(parents=True)
    (session_dir / "snapshot.json").write_text(
        json.dumps(
            {
                "session_id": "sess_meeting_legacy",
                "model": "test-model",
                "state": "idle",
                "backend": "simple",
            }
        ),
        encoding="utf-8",
    )
    (session_dir / "events.jsonl").write_text(
        json.dumps(
            {
                "type": "turn.started",
                "session_id": "sess_meeting_legacy",
                "turn_id": "turn_meeting_legacy",
                "data": {
                    "input": "/tmp/meeting_audio.wav",
                    "domain": "meeting",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    store = CoreSQLiteStore(tmp_path / "core_meeting.sqlite3")
    assert store.import_legacy_sessions(legacy_root) == 1

    session = store.get_session("sess_meeting_legacy")
    thread = store.list_threads(session_id=session.session_id)[0]
    turn = store.list_turns(session_id=session.session_id)[0]
    item = store.list_items(thread_id=thread.thread_id)[0]

    assert session.app_id == LEGACY_SCOPE_MEETING_APP_ID
    assert thread.app_id == LEGACY_SCOPE_MEETING_APP_ID
    assert turn.app_id == LEGACY_SCOPE_MEETING_APP_ID
    assert item.app_id == LEGACY_SCOPE_MEETING_APP_ID
