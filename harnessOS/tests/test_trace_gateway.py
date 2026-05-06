from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from packs.meeting.workflow import MeetingWorkflow
from apps.gateway.traces import TraceStore
from tools.knowledge import kb_ingest


class FakeAgent:
    def invoke(self, user_input: str):
        return {"status": "success", "content": f"reply: {user_input}", "model": "fake-model"}


class FakeMeetingService:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    async def process_recording(self, path, *, engine=None, language=None, title=None):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        analysis = self.output_dir / "analysis.json"
        minutes = self.output_dir / "minutes.md"
        result = self.output_dir / "result.json"
        transcript = self.output_dir / "transcript.json"
        analysis.write_text('{"theme":"Trace Meeting"}', encoding="utf-8")
        minutes.write_text("# Trace Meeting\n", encoding="utf-8")
        result.write_text('{"ok":true}', encoding="utf-8")
        transcript.write_text('{"text":"hello"}', encoding="utf-8")
        return {
            "source_path": path,
            "session_id": "meeting_trace",
            "transcript_chars": 5,
            "segment_count": 1,
            "analysis": {"theme": "Trace Meeting", "summary": "trace"},
            "minutes_path": str(minutes),
            "artifacts": {
                "analysis": str(analysis),
                "minutes": str(minutes),
                "result": str(result),
                "transcript": str(transcript),
            },
        }


def _service(tmp_path: Path) -> GatewayService:
    artifacts = ArtifactRegistry(tmp_path / "artifacts")
    traces = TraceStore(tmp_path / "traces")
    meeting = MeetingWorkflow(
        FakeMeetingService(tmp_path / "meeting-output"),
        artifact_registry=artifacts,
    )
    pool = GatewayRuntimePool(
        model="fake-model",
        agent_factory=lambda _model: FakeAgent(),
        runtime_backend="simple",
        store=GatewaySessionStore(tmp_path / "sessions"),
        artifact_registry=artifacts,
        trace_store=traces,
        meeting_workflow=meeting,
    )
    return GatewayService(runtime_pool=pool, artifact_registry=artifacts, trace_store=traces)


def test_turn_start_records_trace_and_trace_rpc(tmp_path):
    async def run():
        service = _service(tmp_path)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(id="2", method="turn.start", params={"session_id": session_id, "input": "你好"})
        )

        assert turn.error is None
        trace_id = turn.result["trace_id"]
        assert trace_id.startswith("trace_")
        assert turn.result["events"][0]["data"]["trace_id"] == trace_id

        listed = await service.handle_rpc(
            RpcRequest(id="3", method="trace.list", params={"session_id": session_id})
        )
        assert listed.error is None
        assert listed.result["count"] >= 3
        assert {record["event_type"] for record in listed.result["traces"]} >= {
            "turn.started",
            "item.delta",
            "turn.completed",
        }

        fetched = await service.handle_rpc(
            RpcRequest(id="4", method="trace.get", params={"trace_id": trace_id})
        )
        assert fetched.error is None
        assert fetched.result["trace_id"] == trace_id
        assert fetched.result["count"] >= 3

    asyncio.run(run())


def test_artifact_read_records_trace(tmp_path):
    artifact_file = tmp_path / "analysis.json"
    artifact_file.write_text('{"theme":"Trace"}', encoding="utf-8")

    async def run():
        service = _service(tmp_path)
        registered = await service.handle_rpc(
            RpcRequest(
                id="1",
                method="artifact.register",
                params={"path": str(artifact_file), "session_id": "sess_art", "kind": "analysis"},
            )
        )
        artifact_id = registered.result["artifact"]["artifact_id"]

        read = await service.handle_rpc(
            RpcRequest(id="2", method="artifact.read", params={"artifact_id": artifact_id})
        )

        assert read.error is None
        trace_id = read.result["trace_id"]
        listed = await service.handle_rpc(
            RpcRequest(id="3", method="trace.list", params={"artifact_id": artifact_id})
        )
        assert listed.error is None
        assert any(record["event_type"] == "artifact.read" for record in listed.result["traces"])
        assert any(record["trace_id"] == trace_id for record in listed.result["traces"])

    asyncio.run(run())


def test_trace_gateway_scope_filters_records(tmp_path):
    async def run():
        service = _service(tmp_path)
        started = await service.handle_rpc(
            RpcRequest(
                id="1",
                method="session.start",
                params={"scope": {"app_id": "knowledge", "workspace_id": "workspace_k"}},
            )
        )
        session_id = started.result["session_id"]

        turn = await service.handle_rpc(
            RpcRequest(id="2", method="turn.start", params={"session_id": session_id, "input": "你好"})
        )
        assert turn.error is None
        trace_id = turn.result["trace_id"]

        listed = await service.handle_rpc(
            RpcRequest(id="3", method="trace.list", params={"session_id": session_id, "app_id": "knowledge"})
        )
        assert listed.error is None
        assert listed.result["count"] >= 3
        assert all(record["app_id"] == "knowledge" for record in listed.result["traces"])

        denied = await service.handle_rpc(
            RpcRequest(id="4", method="trace.get", params={"trace_id": trace_id, "app_id": "meeting"})
        )
        assert denied.error is not None
        assert denied.error.code == "INVALID_PARAMS"

    asyncio.run(run())


def test_meeting_workflow_trace_links_registered_artifacts(tmp_path):
    audio = tmp_path / "meeting.mp3"
    audio.write_bytes(b"demo")

    async def run():
        service = _service(tmp_path)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "input": f"请分析会议音频 {audio}，生成会议纪要"},
            )
        )

        assert turn.error is None
        trace_id = turn.result["trace_id"]
        meeting = turn.result["events"][-1]["data"]["meeting"]
        minutes_id = meeting["artifacts"]["minutes"]["artifact_id"]
        trace = await service.handle_rpc(
            RpcRequest(id="3", method="trace.get", params={"trace_id": trace_id})
        )
        assert trace.error is None
        completed = [record for record in trace.result["records"] if record["event_type"] == "turn.completed"]
        assert completed
        assert minutes_id in completed[-1]["artifact_ids"]
        assert completed[-1]["workflow_id"] == "meeting.workflow"

    asyncio.run(run())


def test_knowledge_workflow_trace_records_workflow_id(tmp_path):
    kb_ingest("TraceStore 可以记录 knowledge workflow。", title="Trace Knowledge")

    async def run():
        service = _service(tmp_path)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        turn = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": session_id, "domain": "knowledge", "input": "检索知识库 TraceStore"},
            )
        )

        assert turn.error is None
        trace = await service.handle_rpc(
            RpcRequest(id="3", method="trace.get", params={"trace_id": turn.result["trace_id"]})
        )
        assert trace.error is None
        completed = [record for record in trace.result["records"] if record["event_type"] == "turn.completed"]
        assert completed[-1]["workflow_id"] == "knowledge.workflow"

    asyncio.run(run())
