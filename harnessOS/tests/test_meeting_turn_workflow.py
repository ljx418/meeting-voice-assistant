from __future__ import annotations

"""Meeting workflow regression tests, including the PhaseA frozen real-audio gate."""

import asyncio
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from core.config import FunASRMcpConfig, get_meeting_mcp_config
from packs.meeting.connector import MeetingMcpError
from packs.meeting.workflow import MeetingWorkflow, extract_audio_path


def _preferred_acceptance_audio(audio_dir: Path) -> Path:
    audio_files = [
        path for path in sorted(audio_dir.iterdir())
        if path.is_file() and path.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
    ]
    assert audio_files, f"no acceptance audio files found in: {audio_dir}"
    preferred = os.environ.get("HARNESS_MEETING_ACCEPTANCE_AUDIO_FILE")
    if preferred:
        preferred_path = Path(preferred).expanduser().resolve()
        assert preferred_path.exists(), f"configured acceptance audio file does not exist: {preferred_path}"
        return preferred_path
    return min(audio_files, key=lambda path: path.stat().st_size)


def _require_real_audio_dir() -> Path:
    configured = os.environ.get("HARNESS_MEETING_MCP_AUDIO_DIR")
    if not configured:
        pytest.skip("real audio acceptance requires HARNESS_MEETING_MCP_AUDIO_DIR")
    audio_dir = Path(configured).expanduser().resolve()
    if not audio_dir.exists() or not audio_dir.is_dir():
        pytest.skip(f"real audio acceptance directory does not exist: {audio_dir}")
    return audio_dir


class FakeAgent:
    def invoke(self, user_input: str):
        return {"status": "success", "content": f"reply: {user_input}"}


class FakeMeetingService:
    def __init__(self, artifact_dir: Path | None = None):
        self.recording_calls = []
        self.text_calls = []
        self.artifact_dir = artifact_dir

    def _artifacts(self):
        if self.artifact_dir is None:
            return {"minutes": "/tmp/minutes.md"}
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "analysis": self.artifact_dir / "analysis.json",
            "minutes": self.artifact_dir / "minutes.md",
            "result": self.artifact_dir / "result.json",
            "transcript": self.artifact_dir / "transcript.json",
        }
        paths["analysis"].write_text('{"theme":"测试会议"}', encoding="utf-8")
        paths["minutes"].write_text("# 测试会议\n\n测试摘要", encoding="utf-8")
        paths["result"].write_text('{"ok":true}', encoding="utf-8")
        paths["transcript"].write_text('{"text":"hello"}', encoding="utf-8")
        return {kind: str(path) for kind, path in paths.items()}

    async def process_recording(self, path, *, engine=None, language=None, title=None):
        self.recording_calls.append({"path": path, "engine": engine, "language": language, "title": title})
        return {
            "source_path": path,
            "session_id": "meeting_turn",
            "transcript_chars": 123,
            "segment_count": 4,
            "analysis": {"theme": "测试会议", "summary": "测试摘要"},
            "minutes_path": "/tmp/minutes.md",
            "artifacts": self._artifacts(),
        }

    async def analyze_text(self, text, *, title=None):
        self.text_calls.append({"text": text, "title": title})
        return {
            "source_path": None,
            "session_id": "meeting_text",
            "transcript_chars": 0,
            "segment_count": 0,
            "analysis": {"theme": "文本会议", "summary": "文本摘要"},
            "minutes_path": "/tmp/text_minutes.md",
            "artifacts": self._artifacts(),
        }


def _gateway(tmp_path: Path, meeting_service: FakeMeetingService) -> GatewayService:
    registry = ArtifactRegistry(tmp_path / "artifacts")
    return GatewayService(
        GatewayRuntimePool(
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path),
            meeting_workflow=MeetingWorkflow(meeting_service, artifact_registry=registry),
            artifact_registry=registry,
        )
    )


def test_turn_start_domain_meeting_processes_audio_path(tmp_path):
    audio = tmp_path / "demo.mp3"
    audio.write_bytes(b"demo")
    meeting_service = FakeMeetingService()

    async def run():
        service = _gateway(tmp_path, meeting_service)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "domain": "meeting",
                    "input": f"请分析 {audio}，生成会议纪要",
                },
            )
        )

        assert response.error is None
        assert response.result["final_text"].startswith("会议分析已完成")
        assert "主题：测试会议" in response.result["final_text"]
        assert "/tmp/minutes.md" in response.result["final_text"]
        completed = response.result["events"][-1]
        assert completed["type"] == "turn.completed"
        assert completed["data"]["domain"] == "meeting"
        assert completed["data"]["workflow_id"] == "meeting.workflow"
        assert completed["data"]["meeting"]["session_id"] == "meeting_turn"
        assert meeting_service.recording_calls[0]["path"] == str(audio)

    asyncio.run(run())


def test_turn_start_auto_routes_meeting_audio_path(tmp_path):
    audio = tmp_path / "auto.mp3"
    audio.write_bytes(b"demo")
    meeting_service = FakeMeetingService()

    async def run():
        service = _gateway(tmp_path, meeting_service)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "input": f"帮我转写会议音频 {audio} 并生成 minutes",
                },
            )
        )

        assert response.error is None
        assert "主题：测试会议" in response.result["final_text"]
        assert response.result["events"][-1]["data"]["workflow_id"] == "meeting.workflow"
        assert meeting_service.recording_calls

    asyncio.run(run())


def test_turn_start_meeting_registers_artifacts(tmp_path):
    audio = tmp_path / "auto.mp3"
    audio.write_bytes(b"demo")
    meeting_service = FakeMeetingService(tmp_path / "meeting-output")

    async def run():
        service = _gateway(tmp_path, meeting_service)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        session_id = started.result["session_id"]
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": session_id,
                    "input": f"帮我转写会议音频 {audio} 并生成 minutes",
                },
            )
        )

        assert response.error is None
        meeting = response.result["events"][-1]["data"]["meeting"]
        assert response.result["events"][-1]["data"]["domain"] == "meeting"
        assert meeting["artifacts"]["minutes"]["artifact_id"].startswith("art_")
        listed = await service.handle_rpc(
            RpcRequest(id="3", method="artifact.list", params={"session_id": session_id})
        )
        assert listed.error is None
        assert {item["kind"] for item in listed.result["artifacts"]} == {
            "analysis",
            "minutes",
            "result",
            "transcript",
        }
        artifacts_by_kind = {item["kind"]: item for item in listed.result["artifacts"]}
        lineage = await service.handle_rpc(
            RpcRequest(id="4", method="artifact.lineage", params={"session_id": session_id, "domain": "meeting"})
        )
        assert lineage.error is None
        assert lineage.result["count"] == 4
        assert lineage.result["roots"] == [artifacts_by_kind["transcript"]["artifact_id"]]
        assert lineage.result["leaves"] == [artifacts_by_kind["minutes"]["artifact_id"]]
        assert lineage.result["edges"] == [
            {
                "source_artifact_id": artifacts_by_kind["transcript"]["artifact_id"],
                "target_artifact_id": artifacts_by_kind["analysis"]["artifact_id"],
                "relation": "derived_from",
            },
            {
                "source_artifact_id": artifacts_by_kind["analysis"]["artifact_id"],
                "target_artifact_id": artifacts_by_kind["result"]["artifact_id"],
                "relation": "derived_from",
            },
            {
                "source_artifact_id": artifacts_by_kind["result"]["artifact_id"],
                "target_artifact_id": artifacts_by_kind["minutes"]["artifact_id"],
                "relation": "derived_from",
            },
        ]
        minutes_id = meeting["artifacts"]["minutes"]["artifact_id"]
        read = await service.handle_rpc(
            RpcRequest(id="5", method="artifact.read", params={"artifact_id": minutes_id})
        )
        assert "测试摘要" in read.result["content"]

    asyncio.run(run())


def test_turn_start_meeting_can_transcribe_with_funasr_mcp_stdio(tmp_path, monkeypatch):
    mcp_package = tmp_path / "funasr_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        result = {
            "content": [{
                "type": "text",
                "text": json.dumps({"transcript": "FunASR MCP transcript text.", "segments": []}),
            }],
            "isError": False,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    audio = tmp_path / "mcp.mp3"
    audio.write_bytes(b"demo")
    meeting_service = FakeMeetingService(tmp_path / "meeting-output")

    async def run():
        registry = ArtifactRegistry(tmp_path / "artifacts")
        pool = GatewayRuntimePool(
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=registry,
        )
        pool._meeting_workflow.service = meeting_service
        service = GatewayService(pool)
        service.connector_registry.funasr_config = FunASRMcpConfig(
            cwd=str(tmp_path),
            command=sys.executable,
            args="-m funasr_service.mcp_stdio",
            execution="stdio",
            request_timeout=5,
            audio_roots=str(tmp_path),
        )
        original_get_connector = service.connector_registry.get_connector

        def get_connector_without_test_approval(connector_id):
            connector = original_get_connector(connector_id)
            if connector_id == "funasr_mcp":
                connector = dict(connector)
                connector["requires_approval_for"] = []
            return connector

        monkeypatch.setattr(service.connector_registry, "get_connector", get_connector_without_test_approval)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "domain": "meeting",
                    "input": f"请分析 {audio}，生成会议纪要",
                },
            )
        )

        assert response.error is None
        meeting = response.result["events"][-1]["data"]["meeting"]
        assert not meeting_service.recording_calls
        assert meeting_service.text_calls[0]["text"] == "FunASR MCP transcript text."
        assert meeting["transcription"]["connector_id"] == "funasr_mcp"
        assert "会议分析已完成。" in response.result["final_text"]
        assert (
            "标准入口：connector funasr_mcp.funasr_recognize_file -> connector meeting_voice_mcp.meeting_analyze_text"
            in response.result["final_text"]
        )
        listed = await service.handle_rpc(
            RpcRequest(id="3", method="artifact.list", params={"session_id": started.result["session_id"]})
        )
        transcript = next(item for item in listed.result["artifacts"] if item["kind"] == "transcript")
        assert transcript["metadata"]["connector_id"] == "funasr_mcp"
        assert transcript["metadata"]["connector_job_id"].startswith("job_")

    asyncio.run(run())


def test_turn_retry_meeting_funasr_mcp_approval_reuses_connector_job(tmp_path):
    mcp_package = tmp_path / "funasr_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        result = {
            "content": [{
                "type": "text",
                "text": json.dumps({"transcript": "Approved FunASR transcript.", "segments": []}),
            }],
            "isError": False,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    audio = tmp_path / "approval.mp3"
    audio.write_bytes(b"demo")

    async def run():
        pool = GatewayRuntimePool(
            agent_factory=lambda _model: FakeAgent(),
            runtime_backend="simple",
            store=GatewaySessionStore(tmp_path / "sessions"),
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
        )
        pool._meeting_workflow.service = FakeMeetingService(tmp_path / "meeting-output")
        service = GatewayService(pool)
        service.connector_registry.funasr_config = FunASRMcpConfig(
            cwd=str(tmp_path),
            command=sys.executable,
            args="-m funasr_service.mcp_stdio",
            execution="stdio",
            request_timeout=5,
            audio_roots=str(tmp_path),
        )
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        blocked = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "domain": "meeting",
                    "input": f"请分析 {audio}，生成会议纪要",
                },
            )
        )
        assert blocked.error is None
        completed = blocked.result["events"][-1]
        assert completed["data"]["approval_required"] is True
        approval_id = completed["data"]["approval"]["approval_id"]
        connector_job_id = completed["data"]["meeting"]["transcription"]["connector_job_id"]
        retries = service.core_service.list_retries(approval_id=approval_id, status="pending_approval")
        assert [retry.approval_id for retry in retries] == [approval_id]

        approved = await service.handle_rpc(
            RpcRequest(id="3", method="approval.approve", params={"approval_id": approval_id})
        )
        assert approved.error is None
        retried = await service.handle_rpc(
            RpcRequest(
                id="4",
                method="turn.retry",
                params={"session_id": started.result["session_id"], "approval_id": approval_id},
            )
        )
        assert retried.error is None
        assert "会议分析已完成。" in retried.result["final_text"]
        meeting = retried.result["events"][-1]["data"]["meeting"]
        assert meeting["transcription"]["connector_job_id"] == connector_job_id
        assert service.core_service.get_job(connector_job_id).status == "completed"

    asyncio.run(run())


def test_extract_audio_path_supports_spaces_and_chinese_punctuation(tmp_path):
    audio = tmp_path / "TED 演讲 demo audio.mp3"
    audio.write_bytes(b"demo")

    assert extract_audio_path(f"请分析 {audio}，生成会议纪要") == str(audio)


def test_interview_audio_does_not_auto_route_to_meeting(tmp_path):
    audio = tmp_path / "candidate.mp3"
    audio.write_bytes(b"demo")
    meeting_service = FakeMeetingService()

    async def run():
        service = _gateway(tmp_path, meeting_service)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "input": f"请分析面试音频 {audio} 并给出候选人评价",
                },
            )
        )

        assert response.error is None
        assert response.result["final_text"].startswith("reply:")
        assert not meeting_service.recording_calls
        assert not meeting_service.text_calls

    asyncio.run(run())


def test_turn_start_meeting_domain_without_audio_analyzes_text(tmp_path):
    meeting_service = FakeMeetingService()

    async def run():
        service = _gateway(tmp_path, meeting_service)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "domain": "meeting",
                    "input": "今天会议讨论发布计划，张三负责测试，李四负责发布材料。",
                },
            )
        )

        assert response.error is None
        assert "主题：文本会议" in response.result["final_text"]
        assert response.result["events"][-1]["data"]["workflow_id"] == "meeting.workflow"
        assert meeting_service.text_calls

    asyncio.run(run())


def test_meeting_text_analysis_does_not_require_audio_connector(tmp_path):
    class FailingConnectorRegistry:
        def require_available(self, _connector_id: str) -> None:
            raise RuntimeError("audio connector should not be required for plain text")

    meeting_service = FakeMeetingService()

    async def run():
        workflow = MeetingWorkflow(
            meeting_service,
            artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
            connector_registry=FailingConnectorRegistry(),
        )
        result = await workflow.run(
            "今天会议讨论发布计划，张三负责测试，李四负责发布材料。",
            domain="meeting",
            session_id="sess_text",
            turn_id="turn_text",
        )
        assert result["status"] == "success"
        assert meeting_service.text_calls

    asyncio.run(run())


def test_turn_start_non_meeting_keeps_normal_chat(tmp_path):
    meeting_service = FakeMeetingService()

    async def run():
        service = _gateway(tmp_path, meeting_service)
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={"session_id": started.result["session_id"], "input": "你好"},
            )
        )

        assert response.error is None
        assert response.result["final_text"] == "reply: 你好"
        assert not meeting_service.recording_calls
        assert not meeting_service.text_calls

    asyncio.run(run())


def test_phase1b_real_audio_turn_start_acceptance():
    config = get_meeting_mcp_config()
    audio_dir = _require_real_audio_dir()
    audio_file = _preferred_acceptance_audio(audio_dir)

    async def run():
        service = GatewayService()
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "domain": "meeting",
                    "input": f"请分析 {audio_file}，生成会议纪要",
                    "engine": config.default_engine,
                    "language": config.default_language,
                },
            )
        )

        assert response.error is None, response.error
        result = response.result
        completed = result["events"][-1]
        if completed["data"].get("approval_required"):
            approval_id = completed["data"]["approval"]["approval_id"]
            approved = await service.handle_rpc(
                RpcRequest(
                    id="approve-real-audio",
                    method="approval.approve",
                    params={"approval_id": approval_id, "reason": "Explicit real audio turn acceptance."},
                )
            )
            assert approved.error is None, approved.error
            retried = await service.handle_rpc(
                RpcRequest(
                    id="retry-real-audio",
                    method="turn.retry",
                    params={"session_id": started.result["session_id"], "approval_id": approval_id},
                )
            )
            assert retried.error is None, retried.error
            result = retried.result
            completed = result["events"][-1]
        final_text = result["final_text"]
        assert "会议分析已完成" in final_text
        assert "主题：" in final_text
        assert "会议纪要：" in final_text
        assert completed["type"] == "turn.completed"
        meeting = completed["data"]["meeting"]
        assert meeting["transcript_chars"] > 0
        assert meeting["segment_count"] >= 0
        assert meeting["analysis"]["theme"]
        assert Path(meeting["minutes_path"]).exists()

    asyncio.run(run())


def test_turn_start_meeting_failure_surfaces_failed_event_and_text(tmp_path):
    async def run():
        service = GatewayService()
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "domain": "meeting",
                    "input": f"请分析 {tmp_path / 'missing.mp3'}，生成会议纪要",
                },
            )
        )

        assert response.error is None
        assert response.result["final_text"]
        failed = response.result["events"][-1]
        assert failed["type"] == "turn.failed"
        assert failed["data"]["message"]

    asyncio.run(run())
