from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool, normalize_runtime_event
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from core.stores import CoreSQLiteStore


class FakeAgent:
    def invoke(self, user_input: str):
        return {
            "status": "success",
            "content": f"reply: {user_input}",
            "model": "fake-model",
        }


class AssistantTextDelta:
    text = "hello"


class AssistantTurnComplete:
    message = None
    usage = None


class FakeBundleEngine:
    async def submit_message(self, user_input: str):
        event = AssistantTextDelta()
        event.text = f"bundle: {user_input}"
        yield event
        yield AssistantTurnComplete()

    async def continue_pending(self):
        event = AssistantTextDelta()
        event.text = "continued"
        yield event
        yield AssistantTurnComplete()


class FakeBundle:
    engine = FakeBundleEngine()


class ArtifactWorkflowOrchestrator:
    def __init__(self, artifact_path: Path) -> None:
        self.artifact_path = artifact_path
        self.registry = self

    def list_workflows(self):
        return [{"workflow_id": "meeting.workflow", "domain": "meeting"}]

    def select(self, user_input, context):
        return self

    workflow_id = "meeting.workflow"
    domain = "meeting"

    async def run(self, user_input, context):
        return await self.run_if_applicable(user_input, context)

    async def run_if_applicable(self, user_input, context):
        artifact = context.artifact_registry.register_file(
            str(self.artifact_path),
            session_id=context.session_id,
            turn_id=context.turn_id,
            domain="meeting",
            kind="minutes",
        )
        return {
            "status": "success",
            "content": "meeting artifact ready",
            "meeting": {"artifact_records": {"minutes": artifact}},
            "domain": "meeting",
            "workflow_id": "meeting.workflow",
        }


def test_gateway_rpc_happy_path(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )
        service = GatewayService(pool)
        init = await service.handle_rpc(RpcRequest(id="1", method="initialize"))
        assert init.error is None
        assert init.result["protocol_version"] == "v1alpha"

        started = await service.handle_rpc(RpcRequest(id="2", method="session.start"))
        assert started.error is None
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="3",
                method="turn.start",
                params={"session_id": session_id, "input": "你好"},
            )
        )
        assert turn.error is None
        assert turn.result["final_text"] == "reply: 你好"
        assert [event["type"] for event in turn.result["events"]] == [
            "turn.started",
            "item.delta",
            "turn.completed",
        ]
        events = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="session.events",
                params={"session_id": session_id},
            )
        )
        assert events.error is None
        assert len(events.result["events"]) == 3

    asyncio.run(run())


def test_gateway_pack_list_and_get(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )
        service = GatewayService(pool)

        listed = await service.handle_rpc(RpcRequest(id="packs", method="pack.list"))
        assert listed.error is None
        assert {pack["name"] for pack in listed.result["packs"]} == {
            "meeting",
            "knowledge",
            "investment",
            "interview",
            "video_studio",
        }

        active = await service.handle_rpc(
            RpcRequest(id="active", method="pack.list", params={"status": "active"})
        )
        assert active.error is None
        assert {pack["name"] for pack in active.result["packs"]} == {"meeting", "knowledge"}

        meeting = await service.handle_rpc(
            RpcRequest(id="meeting", method="pack.get", params={"domain": "meeting"})
        )
        assert meeting.error is None
        assert meeting.result["pack"]["status"] == "active"
        assert "meeting.workflow" in meeting.result["pack"]["workflows"]

    asyncio.run(run())


def test_turn_start_records_trace(tmp_path):
    async def run():
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(id="2", method="turn.start", params={"session_id": session_id, "input": "trace"})
        )

        assert turn.error is None
        assert turn.result["trace_id"].startswith("trace_")
        assert all(
            event["data"].get("trace_id") == turn.result["trace_id"]
            for event in turn.result["events"]
            if event["type"] in {"turn.started", "item.delta", "turn.completed"}
        )

    asyncio.run(run())


def test_turn_start_mirrors_core_records(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(id="2", method="turn.start", params={"session_id": session_id, "input": "core mirror"})
        )

        assert turn.error is None
        sessions = core_store.list_sessions()
        threads = core_store.list_threads(session_id=session_id)
        turns = core_store.list_turns(session_id=session_id)
        items = core_store.list_items(turn_id=turn.result["turn_id"])

        assert [session.session_id for session in sessions] == [session_id]
        assert len(threads) == 1
        assert len(turns) == 1
        assert turns[0].turn_id == turn.result["turn_id"]
        assert turns[0].input == "core mirror"
        assert turns[0].state == "completed"
        assert [item.item_type for item in items] == [
            "user_message",
            "assistant_message_delta",
            "assistant_message",
        ]
        trace_records = core_store.list_trace_records(trace_id=turn.result["trace_id"])
        assert [record.event_type for record in trace_records] == [
            "turn.started",
            "item.delta",
            "turn.completed",
        ]

        rpc_session = await service.handle_rpc(
            RpcRequest(id="3", method="session.get", params={"session_id": session_id})
        )
        rpc_threads = await service.handle_rpc(
            RpcRequest(id="4", method="thread.list", params={"session_id": session_id})
        )
        rpc_turn = await service.handle_rpc(
            RpcRequest(id="5", method="turn.get", params={"turn_id": turn.result["turn_id"]})
        )
        rpc_items = await service.handle_rpc(
            RpcRequest(id="6", method="turn.items", params={"turn_id": turn.result["turn_id"]})
        )
        rpc_traces = await service.handle_rpc(
            RpcRequest(id="7", method="core.trace.list", params={"trace_id": turn.result["trace_id"]})
        )

        assert rpc_session.error is None
        assert rpc_session.result["session"]["session_id"] == session_id
        assert rpc_threads.error is None
        assert rpc_threads.result["count"] == 1
        assert rpc_turn.error is None
        assert rpc_turn.result["turn"]["input"] == "core mirror"
        assert rpc_items.error is None
        assert rpc_items.result["count"] == 3
        assert rpc_traces.error is None
        assert rpc_traces.result["count"] == 3

    asyncio.run(run())


def test_policy_approval_and_retry_mirror_core_governance_records(tmp_path):
    async def run():
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            core_store=core_store,
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        blocked = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请写入 demo.txt，内容为 hello"},
            )
        )

        assert blocked.error is None
        completed = blocked.result["events"][-1]
        approval_id = completed["data"]["approval"]["approval_id"]
        retry_id = completed["data"]["retry_context"]["retry_id"]

        approvals = core_store.list_approvals(decision="pending")
        retries = core_store.list_retries(approval_id=approval_id, status="pending_approval")
        traces = core_store.list_trace_records(trace_id=blocked.result["trace_id"])

        assert [approval.approval_id for approval in approvals] == [approval_id]
        assert [retry.retry_id for retry in retries] == [retry_id]
        assert "approval.request" in [trace.event_type for trace in traces]

        rpc_approvals = await service.handle_rpc(
            RpcRequest(id="3", method="core.approval.list", params={"decision": "pending"})
        )
        rpc_retries = await service.handle_rpc(
            RpcRequest(id="4", method="core.retry.list", params={"approval_id": approval_id})
        )
        rpc_traces = await service.handle_rpc(
            RpcRequest(id="5", method="core.trace.list", params={"trace_id": blocked.result["trace_id"]})
        )

        assert rpc_approvals.error is None
        assert rpc_approvals.result["approvals"][0]["approval_id"] == approval_id
        assert rpc_retries.error is None
        assert rpc_retries.result["retries"][0]["retry_id"] == retry_id
        assert rpc_traces.error is None
        assert any(trace["event_type"] == "approval.request" for trace in rpc_traces.result["traces"])

    asyncio.run(run())


def test_turn_completed_artifacts_mirror_core_records(tmp_path):
    async def run():
        artifact_path = tmp_path / "minutes.md"
        artifact_path.write_text("# Minutes\n", encoding="utf-8")
        core_store = CoreSQLiteStore(tmp_path / "core.sqlite3")
        pool = GatewayRuntimePool(
            model="fake-model",
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            core_store=core_store,
            orchestrator=ArtifactWorkflowOrchestrator(artifact_path),
        )
        service = GatewayService(pool)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "请分析会议音频"},
            )
        )

        assert turn.error is None
        artifacts = core_store.list_artifacts(domain="meeting", kind="minutes")
        assert len(artifacts) == 1
        assert artifacts[0].owner_session_id == session_id
        assert artifacts[0].owner_turn_id == turn.result["turn_id"]
        assert artifacts[0].uri == str(artifact_path)

        rpc_artifacts = await service.handle_rpc(
            RpcRequest(id="3", method="core.artifact.list", params={"domain": "meeting", "kind": "minutes"})
        )
        assert rpc_artifacts.error is None
        assert rpc_artifacts.result["count"] == 1
        assert rpc_artifacts.result["artifacts"][0]["owner_turn_id"] == turn.result["turn_id"]

        jobs = await service.handle_rpc(
            RpcRequest(id="4", method="job.list", params={"session_id": session_id, "domain": "meeting"})
        )
        assert jobs.error is None
        assert jobs.result["count"] == 1
        job = jobs.result["jobs"][0]
        assert job["workflow_id"] == "meeting.workflow"
        assert job["status"] == "completed"
        assert job["progress"] == 1.0
        assert job["turn_id"] == turn.result["turn_id"]
        assert job["artifact_ids"] == [artifacts[0].artifact_id]
        assert turn.result["events"][-1]["data"]["job_id"] == job["job_id"]

        fetched = await service.handle_rpc(RpcRequest(id="5", method="job.get", params={"job_id": job["job_id"]}))
        assert fetched.error is None
        assert fetched.result["job"]["job_id"] == job["job_id"]

    asyncio.run(run())


def test_gateway_rpc_unknown_session(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        response = await service.handle_rpc(
            RpcRequest(
                id="bad",
                method="turn.start",
                params={"session_id": "missing", "input": "hello"},
            )
        )
        assert response.result is None
        assert response.error is not None
        assert response.error.code == "SESSION_NOT_FOUND"

    asyncio.run(run())


def test_gateway_resume_and_interrupt(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "first"},
            )
        )
        await service.handle_rpc(
            RpcRequest(
                id="3",
                method="session.close",
                params={"session_id": session_id},
            )
        )
        resumed = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="session.resume",
                params={"session_id": session_id},
            )
        )
        assert resumed.error is None
        assert resumed.result["session_id"] == session_id

        interrupted = await service.handle_rpc(
            RpcRequest(
                id="5",
                method="turn.interrupt",
                params={"session_id": session_id},
            )
        )
        assert interrupted.error is None
        assert interrupted.result["interrupted"] is True

        continued = await service.handle_rpc(
            RpcRequest(
                id="6",
                method="turn.continue",
                params={"session_id": session_id},
            )
        )
        assert continued.error is None
        assert continued.result["events"][0]["type"] == "item.status"

    asyncio.run(run())


def test_gateway_session_list_read_and_transcript(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "hello"},
            )
        )

        sessions = await service.handle_rpc(RpcRequest(id="3", method="session.list"))
        assert sessions.error is None
        assert sessions.result["sessions"][0]["session_id"] == session_id

        session = await service.handle_rpc(
            RpcRequest(id="4", method="session.read", params={"session_id": session_id})
        )
        assert session.error is None
        assert session.result["session"]["backend"] == "simple"

        transcript = await service.handle_rpc(
            RpcRequest(id="5", method="session.transcript", params={"session_id": session_id})
        )
        assert transcript.error is None
        assert [item["role"] for item in transcript.result["transcript"]] == ["user", "assistant"]
        assert transcript.result["transcript"][1]["content"] == "reply: hello"

    asyncio.run(run())


def test_gateway_unknown_method_error_code(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                agent_factory=lambda _model: FakeAgent(),
                runtime_backend="simple",
                store=GatewaySessionStore(tmp_path),
            )
        )
        response = await service.handle_rpc(RpcRequest(id="bad", method="missing.method"))
        assert response.error is not None
        assert response.error.code == "METHOD_NOT_FOUND"

    asyncio.run(run())


def test_gateway_runtime_bundle_backend_paths(tmp_path):
    async def run():
        service = GatewayService(
            GatewayRuntimePool(
                model="fake-model",
                runtime_factory=lambda _model: FakeBundle(),
                runtime_backend="openharness",
                store=GatewaySessionStore(tmp_path),
            )
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        assert started.error is None
        assert started.result["backend"] == "openharness"
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": "hello"},
            )
        )
        assert turn.error is None
        assert turn.result["final_text"] == "bundle: hello"

        continued = await service.handle_rpc(
            RpcRequest(
                id="3",
                method="turn.continue",
                params={"session_id": session_id},
            )
        )
        assert continued.error is None
        assert continued.result["final_text"] == "continued"

    asyncio.run(run())


def test_normalize_runtime_event_uses_class_name_not_identity():
    event = normalize_runtime_event(
        AssistantTextDelta(),
        session_id="sess_test",
        turn_id="turn_test",
    )
    assert event.type == "item.delta"
    assert event.data["text"] == "hello"
