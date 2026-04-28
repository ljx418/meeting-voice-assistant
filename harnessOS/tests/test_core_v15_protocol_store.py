from __future__ import annotations

import json
from types import SimpleNamespace

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
from core.services import CoreAppService
from core.stores import CoreSQLiteStore


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

    completed = service.update_job(
        job_id=job.job_id,
        status="completed",
        progress=1.0,
        artifact_ids=["art_minutes"],
    )
    assert completed.status == "completed"
    assert completed.artifact_ids == ["art_minutes"]
    assert service.list_jobs(session_id="sess_job", domain="meeting", status="completed")[0].job_id == job.job_id

    cancelled = service.cancel_job(job.job_id, reason="manual")
    assert cancelled.status == "cancelled"
    assert cancelled.metadata["cancel_reason"] == "manual"


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
