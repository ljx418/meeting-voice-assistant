from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from packs.meeting.connector import (
    MEETING_MCP_STDIO_LIMIT,
    MeetingGatewayService,
    MeetingMcpError,
    _compact_transcript_for_analysis,
)
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.config import MeetingMcpConfig


class FakeMeetingClient:
    def __init__(self, _config):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def list_tools(self):
        return [
            {"name": "meeting_process_file"},
            {"name": "meeting_analyze_text"},
            {"name": "meeting_build_minutes"},
        ]

    async def read_resource(self, uri):
        assert uri == "meeting://agent-guide"
        return '{"scope":"meeting","non_goals":["interview workflows"]}'

    async def get_prompt(self, name, arguments=None):
        assert name == "meeting_process_recording"
        return {"description": "Meeting workflow", "messages": []}

    async def call_tool(self, name, arguments=None):
        self.calls.append((name, arguments or {}))
        if name == "meeting_analyze_text":
            return {
                "session_id": "meeting_text",
                "theme": "项目发布计划",
                "summary": "讨论测试、发布材料和回滚预案。",
                "key_points": ["张三负责测试"],
                "action_items": [{"owner": "张三", "task": "完成测试"}],
            }
        if name == "meeting_process_file":
            return {
                "session_id": "meeting_file",
                "transcript": "hello meeting transcript",
                "segments": [{"text": "hello", "start_time": 0, "end_time": 1}],
                "analysis": {
                    "session_id": "meeting_file",
                    "theme": "TED Talk Notes",
                    "summary": "A talk summary.",
                },
                "artifacts": {"result": "/tmp/result.json"},
            }
        if name == "meeting_build_minutes":
            return {
                "session_id": arguments.get("session_id"),
                "path": "/tmp/minutes.md",
                "artifacts": {"minutes": "/tmp/minutes.md"},
            }
        raise AssertionError(f"unexpected tool: {name}")


class FakeLongTranscriptMeetingClient(FakeMeetingClient):
    async def call_tool(self, name, arguments=None):
        self.calls.append((name, arguments or {}))
        if name == "meeting_process_file" and arguments.get("analyze"):
            raise MeetingMcpError("Separator is found, but chunk is longer than limit")
        if name == "meeting_process_file":
            return {
                "session_id": "meeting_long",
                "transcript": "开场。" + ("长音频内容 " * 2500) + "结尾。",
                "segments": [{"text": "开场", "start_time": 0, "end_time": 1}],
                "analysis": None,
                "artifacts": {"result": "/tmp/result.json", "transcript": "/tmp/transcript.json"},
            }
        if name == "meeting_analyze_text":
            assert arguments["session_id"] == "meeting_long"
            assert len(arguments["text"]) < 9000
            assert "省略中间转写" in arguments["text"]
            return {
                "session_id": "meeting_long",
                "theme": "长音频降级分析",
                "summary": "压缩转写后完成分析。",
            }
        if name == "meeting_build_minutes":
            return {
                "session_id": arguments.get("session_id"),
                "path": "/tmp/long_minutes.md",
                "artifacts": {"minutes": "/tmp/long_minutes.md"},
            }
        raise AssertionError(f"unexpected tool: {name}")


def _meeting_service(tmp_path: Path) -> MeetingGatewayService:
    module_path = tmp_path / "app" / "meeting_mcp" / "mcp_stdio.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text("# fake meeting mcp module\n", encoding="utf-8")
    config = MeetingMcpConfig(
        cwd=str(tmp_path),
        command="python3",
        args="-m app.meeting_mcp.mcp_stdio",
        audio_dir=str(tmp_path),
    )
    return MeetingGatewayService(config=config, client_factory=FakeMeetingClient)


def _long_transcript_meeting_service(tmp_path: Path) -> MeetingGatewayService:
    module_path = tmp_path / "app" / "meeting_mcp" / "mcp_stdio.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text("# fake meeting mcp module\n", encoding="utf-8")
    config = MeetingMcpConfig(
        cwd=str(tmp_path),
        command="python3",
        args="-m app.meeting_mcp.mcp_stdio",
        audio_dir=str(tmp_path),
    )
    return MeetingGatewayService(config=config, client_factory=FakeLongTranscriptMeetingClient)


def test_meeting_capabilities_rpc(tmp_path):
    async def run():
        service = GatewayService(meeting_service=_meeting_service(tmp_path))
        response = await service.handle_rpc(RpcRequest(id="m1", method="meeting.capabilities"))

        assert response.error is None
        assert response.result["server"] == "meeting"
        assert "meeting_process_file" in response.result["tools"]
        assert response.result["agent_guide"]["scope"] == "meeting"
        assert "interview workflows" in response.result["agent_guide"]["non_goals"]

    asyncio.run(run())


def test_meeting_analyze_text_rpc_builds_minutes(tmp_path):
    async def run():
        service = GatewayService(meeting_service=_meeting_service(tmp_path))
        response = await service.handle_rpc(
            RpcRequest(
                id="m2",
                method="meeting.analyze_text",
                params={"text": "今天会议讨论项目发布计划。张三负责完成测试。", "title": "发布会议"},
            )
        )

        assert response.error is None
        assert response.result["session_id"] == "meeting_text"
        assert response.result["analysis"]["theme"] == "项目发布计划"
        assert response.result["minutes_path"] == "/tmp/minutes.md"

    asyncio.run(run())


def test_meeting_process_recording_rpc(tmp_path):
    audio = tmp_path / "demo.mp3"
    audio.write_bytes(b"demo")

    async def run():
        service = GatewayService(meeting_service=_meeting_service(tmp_path))
        response = await service.handle_rpc(
            RpcRequest(
                id="m3",
                method="meeting.process_recording",
                params={"path": str(audio), "engine": "funasr", "language": "en"},
            )
        )

        assert response.error is None
        assert response.result["session_id"] == "meeting_file"
        assert response.result["transcript_chars"] > 0
        assert response.result["segment_count"] == 1
        assert response.result["analysis"]["theme"] == "TED Talk Notes"
        assert response.result["minutes_path"] == "/tmp/minutes.md"

    asyncio.run(run())


def test_meeting_process_recording_retries_long_transcript_analysis(tmp_path):
    audio = tmp_path / "long.mp3"
    audio.write_bytes(b"demo")

    async def run():
        service = GatewayService(meeting_service=_long_transcript_meeting_service(tmp_path))
        response = await service.handle_rpc(
            RpcRequest(
                id="m-long",
                method="meeting.process_recording",
                params={"path": str(audio), "engine": "funasr", "language": "en"},
            )
        )

        assert response.error is None
        assert response.result["session_id"] == "meeting_long"
        assert response.result["analysis"]["theme"] == "长音频降级分析"
        assert response.result["minutes_path"] == "/tmp/long_minutes.md"

    asyncio.run(run())


def test_compact_transcript_for_analysis_preserves_edges():
    text = "开头。" + ("中间内容 " * 1000) + "结尾。"

    compact = _compact_transcript_for_analysis(text, max_chars=1200)

    assert len(compact) < len(text)
    assert compact.startswith("开头。")
    assert compact.endswith("结尾。")
    assert "省略中间转写" in compact


def test_meeting_mcp_stdio_limit_allows_large_json_responses():
    assert MEETING_MCP_STDIO_LIMIT >= 128 * 1024 * 1024


def test_meeting_process_audio_dir_rpc(tmp_path):
    (tmp_path / "a.mp3").write_bytes(b"a")
    (tmp_path / "b.wav").write_bytes(b"b")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    async def run():
        service = GatewayService(meeting_service=_meeting_service(tmp_path))
        response = await service.handle_rpc(
            RpcRequest(
                id="m4",
                method="meeting.process_audio_dir",
                params={"audio_dir": str(tmp_path), "engine": "funasr", "language": "en"},
            )
        )

        assert response.error is None
        assert response.result["file_count"] == 2
        assert response.result["processed_count"] == 2
        assert all(item["minutes_path"] == "/tmp/minutes.md" for item in response.result["results"])

    asyncio.run(run())


def test_meeting_process_recording_missing_file_returns_error(tmp_path):
    async def run():
        service = GatewayService(meeting_service=_meeting_service(tmp_path))
        response = await service.handle_rpc(
            RpcRequest(
                id="m5",
                method="meeting.process_recording",
                params={"path": str(tmp_path / "missing.mp3")},
            )
        )

        assert response.result is None
        assert response.error is not None
        assert response.error.code == "RUNTIME_ERROR"
        assert "Audio file does not exist" in response.error.message

    asyncio.run(run())
