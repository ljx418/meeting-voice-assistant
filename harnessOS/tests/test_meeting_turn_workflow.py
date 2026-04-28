from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.meeting import MeetingMcpError, MeetingWorkflow, extract_audio_path
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from core.config import get_meeting_mcp_config


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
        minutes_id = meeting["artifacts"]["minutes"]["artifact_id"]
        read = await service.handle_rpc(
            RpcRequest(id="4", method="artifact.read", params={"artifact_id": minutes_id})
        )
        assert "测试摘要" in read.result["content"]

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
    audio_dir = Path(os.environ.get("HARNESS_MEETING_MCP_AUDIO_DIR", config.audio_dir)).expanduser().resolve()
    assert audio_dir == Path("/Users/Zhuanz/Desktop/workspace/音频资料")
    audio_files = [
        path for path in sorted(audio_dir.iterdir())
        if path.is_file() and path.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
    ]
    assert audio_files, f"no acceptance audio files found in: {audio_dir}"

    async def run():
        service = GatewayService()
        started = await service.handle_rpc(RpcRequest(id="1", method="session.start"))
        response = await service.handle_rpc(
            RpcRequest(
                id="2",
                method="turn.start",
                params={
                    "session_id": started.result["session_id"],
                    "input": f"请分析 {audio_files[0]}，生成会议纪要",
                },
            )
        )

        assert response.error is None, response.error
        final_text = response.result["final_text"]
        assert "会议分析已完成" in final_text
        assert "主题：" in final_text
        assert "会议纪要：" in final_text
        completed = response.result["events"][-1]
        assert completed["type"] == "turn.completed"
        meeting = completed["data"]["meeting"]
        assert meeting["transcript_chars"] > 0
        assert meeting["segment_count"] > 0
        assert meeting["analysis"]["theme"]
        assert Path(meeting["minutes_path"]).exists()

    asyncio.run(run())
