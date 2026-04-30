from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.meeting_mcp.service import MeetingMcpService


class FakeAsrAdapter:
    def __init__(self) -> None:
        self.initialized = False
        self.closed = False

    async def initialize(self) -> None:
        self.initialized = True

    async def recognize_file(self, file_path: Path):
        yield SimpleNamespace(
            text="张三负责完成测试。",
            speaker="speaker_0",
            start_time=0.0,
            end_time=1.8,
            confidence=0.91,
            is_final=True,
        )
        yield SimpleNamespace(
            text="李四负责准备发布材料。",
            speaker="speaker_1",
            start_time=1.8,
            end_time=3.6,
            confidence=0.94,
            is_final=True,
        )

    async def close(self) -> None:
        self.closed = True


@dataclass
class FakeAnalysisResult:
    theme: str
    summary: str
    chapters: list
    speaker_roles: list
    topics: list
    key_points: list
    action_items: list
    raw_response: str = ""


class FakeAudioAnalyzer:
    def analyze_transcript(self, text: str) -> FakeAnalysisResult:
        return FakeAnalysisResult(
            theme="发布准备会",
            summary=f"会议围绕测试和发布材料展开，共 {len(text)} 字。",
            chapters=[],
            speaker_roles=[],
            topics=["测试", "发布"],
            key_points=["张三负责完成测试", "李四负责准备发布材料"],
            action_items=[{"owner": "张三", "task": "完成测试"}],
        )


def _audio_file(tmp_path: Path) -> Path:
    audio = tmp_path / "meeting.wav"
    audio.write_bytes(b"RIFF\x00\x00\x00\x00WAVE")
    return audio


@pytest.mark.asyncio
async def test_transcribe_file_uses_asr_adapter_and_writes_artifact(monkeypatch, tmp_path):
    adapter = FakeAsrAdapter()
    monkeypatch.setattr("app.meeting_mcp.service.ASRFactory.create", lambda engine: adapter)

    service = MeetingMcpService(output_root=tmp_path / "out")
    result = await service.transcribe_file(str(_audio_file(tmp_path)), engine="mock")

    assert adapter.initialized is True
    assert adapter.closed is True
    assert result["engine"] == "mock"
    assert "张三负责完成测试" in result["text"]
    assert "李四负责准备发布材料" in result["text"]
    assert result["speaker_count"] == 2
    assert len(result["segments"]) == 2

    transcript_path = tmp_path / "out" / result["session_id"] / "transcript.json"
    assert transcript_path.exists()
    saved = json.loads(transcript_path.read_text(encoding="utf-8"))
    assert saved["text"] == result["text"]


@pytest.mark.asyncio
async def test_analyze_text_uses_existing_audio_analyzer(monkeypatch, tmp_path):
    monkeypatch.setattr("app.meeting_mcp.service.AudioAnalyzer", FakeAudioAnalyzer)

    service = MeetingMcpService(output_root=tmp_path / "out")
    result = await service.analyze_text("张三负责完成测试。李四负责准备发布材料。")

    assert result["mode"] == "audio_analyzer"
    assert result["theme"] == "发布准备会"
    assert result["topics"] == ["测试", "发布"]
    assert result["action_items"] == [{"owner": "张三", "task": "完成测试"}]
    assert (tmp_path / "out" / result["session_id"] / "analysis.json").exists()


@pytest.mark.asyncio
async def test_process_file_combines_transcript_analysis_and_artifacts(monkeypatch, tmp_path):
    monkeypatch.setattr("app.meeting_mcp.service.ASRFactory.create", lambda engine: FakeAsrAdapter())
    monkeypatch.setattr("app.meeting_mcp.service.AudioAnalyzer", FakeAudioAnalyzer)

    service = MeetingMcpService(output_root=tmp_path / "out")
    result = await service.process_file(str(_audio_file(tmp_path)), engine="mock", analyze=True)

    assert result["session_id"].startswith("meeting_")
    assert "张三负责完成测试" in result["transcript"]
    assert result["analysis"]["theme"] == "发布准备会"
    assert sorted(result["artifacts"].keys()) == ["analysis", "result", "transcript"]
    assert Path(result["artifacts"]["result"]).exists()


@pytest.mark.asyncio
async def test_build_minutes_creates_markdown_artifact(monkeypatch, tmp_path):
    monkeypatch.setattr("app.meeting_mcp.service.ASRFactory.create", lambda engine: FakeAsrAdapter())
    monkeypatch.setattr("app.meeting_mcp.service.AudioAnalyzer", FakeAudioAnalyzer)

    service = MeetingMcpService(output_root=tmp_path / "out")
    result = await service.process_file(str(_audio_file(tmp_path)), engine="mock", analyze=True)
    minutes = service.build_minutes(session_id=result["session_id"], title="项目发布会议")

    assert minutes["session_id"] == result["session_id"]
    assert "# 项目发布会议" in minutes["markdown"]
    assert "张三: 完成测试" in minutes["markdown"]
    assert "Transcript Preview" in minutes["markdown"]
    assert Path(minutes["path"]).exists()
    assert "minutes" in minutes["artifacts"]


def test_agent_guide_is_meeting_scoped():
    service = MeetingMcpService()
    guide = service.agent_guide()

    assert guide["scope"] == "meeting"
    assert "interview workflows" in guide["non_goals"]
    assert any("meeting_process_file" in " ".join(item["steps"]) for item in guide["recommended_workflows"])


@pytest.mark.asyncio
async def test_mcp_stdio_lists_tools_and_dispatches_analyze(monkeypatch):
    pytest.importorskip("mcp")
    from app.meeting_mcp import mcp_stdio

    tools = await mcp_stdio.list_tools()
    assert {tool.name for tool in tools} >= {
        "meeting_transcribe_file",
        "meeting_analyze_text",
        "meeting_process_file",
    }

    class FakeService:
        async def analyze_text(self, **kwargs):
            return {"ok": True, "kwargs": kwargs}

    monkeypatch.setattr(mcp_stdio, "_service", FakeService())
    content = await mcp_stdio.call_tool(
        "meeting_analyze_text",
        {"text": "张三负责完成测试。李四负责准备发布材料。", "mode": "audio_analyzer"},
    )

    payload = json.loads(content[0].text)
    assert payload["ok"] is True
    assert payload["kwargs"]["mode"] == "audio_analyzer"


@pytest.mark.asyncio
async def test_mcp_stdio_reads_formats_resource(monkeypatch):
    pytest.importorskip("mcp")
    from app.meeting_mcp import mcp_stdio

    class FakeService:
        def formats(self):
            return {"audio": ["wav"], "video": ["mp4"], "engines": ["mock"]}

    monkeypatch.setattr(mcp_stdio, "_service", FakeService())
    content = await mcp_stdio.read_resource("meeting://formats")
    payload = json.loads(content[0].text)

    assert payload == {"audio": ["wav"], "video": ["mp4"], "engines": ["mock"]}


@pytest.mark.asyncio
async def test_mcp_stdio_jsonrpc_fallback_lists_tools():
    from app.meeting_mcp import mcp_stdio

    response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
    })

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert {tool["name"] for tool in response["result"]["tools"]} >= {
        "meeting_transcribe_file",
        "meeting_analyze_text",
        "meeting_process_file",
        "meeting_build_minutes",
    }


@pytest.mark.asyncio
async def test_mcp_stdio_jsonrpc_fallback_dispatches_tool(monkeypatch):
    from app.meeting_mcp import mcp_stdio

    class FakeService:
        async def analyze_text(self, text, **kwargs):
            return {"ok": True, "text": text, "kwargs": kwargs}

    monkeypatch.setattr(mcp_stdio, "_service", FakeService())
    response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "meeting_analyze_text",
            "arguments": {
                "text": "张三负责完成测试。李四负责准备发布材料。",
                "mode": "audio_analyzer",
            },
        },
    })

    assert response["id"] == 2
    content = response["result"]["content"]
    payload = json.loads(content[0]["text"])
    assert payload["ok"] is True
    assert "张三负责完成测试" in payload["text"]
    assert payload["kwargs"]["mode"] == "audio_analyzer"


@pytest.mark.asyncio
async def test_mcp_stdio_jsonrpc_fallback_reads_resource(monkeypatch):
    from app.meeting_mcp import mcp_stdio

    class FakeService:
        def formats(self):
            return {"audio": ["wav"], "video": ["mp4"], "engines": ["mock"]}

    monkeypatch.setattr(mcp_stdio, "_service", FakeService())
    response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "resources/read",
        "params": {"uri": "meeting://formats"},
    })

    payload = json.loads(response["result"]["contents"][0]["text"])
    assert payload == {"audio": ["wav"], "video": ["mp4"], "engines": ["mock"]}


@pytest.mark.asyncio
async def test_mcp_stdio_jsonrpc_fallback_reads_agent_guide(monkeypatch):
    from app.meeting_mcp import mcp_stdio

    class FakeService:
        def agent_guide(self):
            return {"scope": "meeting", "non_goals": ["interview workflows"]}

    monkeypatch.setattr(mcp_stdio, "_service", FakeService())
    response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "resources/read",
        "params": {"uri": "meeting://agent-guide"},
    })

    payload = json.loads(response["result"]["contents"][0]["text"])
    assert payload["scope"] == "meeting"
    assert "interview workflows" in payload["non_goals"]


@pytest.mark.asyncio
async def test_mcp_stdio_jsonrpc_fallback_builds_minutes(monkeypatch):
    from app.meeting_mcp import mcp_stdio

    class FakeService:
        def build_minutes(self, **kwargs):
            return {"ok": True, "kwargs": kwargs, "path": "/tmp/minutes.md"}

    monkeypatch.setattr(mcp_stdio, "_service", FakeService())
    response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "meeting_build_minutes",
            "arguments": {
                "session_id": "meeting_abc",
                "title": "周会",
                "include_transcript_preview": False,
            },
        },
    })

    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload["ok"] is True
    assert payload["kwargs"]["session_id"] == "meeting_abc"
    assert payload["kwargs"]["include_transcript_preview"] is False


@pytest.mark.asyncio
async def test_mcp_stdio_jsonrpc_fallback_prompts_are_meeting_only():
    from app.meeting_mcp import mcp_stdio

    list_response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": 7,
        "method": "prompts/list",
    })
    assert list_response["result"]["prompts"][0]["name"] == "meeting_process_recording"

    get_response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": 8,
        "method": "prompts/get",
        "params": {
            "name": "meeting_process_recording",
            "arguments": {"path": "/tmp/demo.mp3", "engine": "funasr", "language": "zh"},
        },
    })
    text = get_response["result"]["messages"][0]["content"]["text"]
    assert "meeting_process_file" in text
    assert "meeting_build_minutes" in text
    assert "Do not invoke interview tools" in text


@pytest.mark.asyncio
async def test_mcp_stdio_jsonrpc_fallback_initialize():
    from app.meeting_mcp import mcp_stdio

    response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
    })

    assert response["result"]["serverInfo"]["name"] == "meeting"
    assert "tools" in response["result"]["capabilities"]
    assert "resources" in response["result"]["capabilities"]
