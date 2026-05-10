"""Meeting MCP connector implementation owned by the Meeting pack."""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from core.config import MeetingMcpConfig, get_meeting_mcp_config


SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
MAX_FALLBACK_ANALYSIS_CHARS = 8000
MEETING_MCP_STDIO_LIMIT = 128 * 1024 * 1024
MEETING_MCP_PROCESS_RETRIES = 3
MEETING_MCP_RETRY_DELAY_SECONDS = 1.0


class MeetingMcpError(RuntimeError):
    """Raised when the Meeting MCP integration cannot complete a request."""


class MeetingMcpJsonRpcClient:
    """Small line-delimited JSON-RPC client for the Meeting MCP fallback server."""

    def __init__(self, config: Optional[MeetingMcpConfig] = None) -> None:
        self.config = config or get_meeting_mcp_config()
        self._process: asyncio.subprocess.Process | None = None
        self._request_id = 0
        self._stderr_tail: list[str] = []
        self._stderr_task: asyncio.Task[None] | None = None

    async def __aenter__(self) -> "MeetingMcpJsonRpcClient":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def start(self) -> None:
        """Start the configured Meeting MCP process."""
        if self._process is not None:
            return
        cwd = Path(self.config.cwd).expanduser().resolve()
        if not cwd.exists():
            raise MeetingMcpError(f"Meeting MCP cwd does not exist: {cwd}")

        env = os.environ.copy()
        for key in list(env):
            if key.startswith("PYTEST_"):
                env.pop(key, None)
        env.setdefault("ASR_ENGINE", self.config.default_engine)
        env.setdefault("ASR_FUNASR_ENDPOINT", "http://127.0.0.1:8001")
        if self.config.output_root:
            env["MEETING_MCP_OUTPUT_ROOT"] = self.config.output_root

        try:
            self._process = await asyncio.create_subprocess_exec(
                self.config.command,
                *self.config.argv,
                cwd=str(cwd),
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=MEETING_MCP_STDIO_LIMIT,
            )
        except OSError as exc:
            raise MeetingMcpError(f"Failed to start Meeting MCP server: {exc}") from exc
        self._stderr_task = asyncio.create_task(self._drain_stderr())
        await self.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "harnessOS", "version": "0.1.0"},
            },
        )
        await self.notify("notifications/initialized")

    async def close(self) -> None:
        """Stop the MCP process."""
        process = self._process
        self._process = None
        if process is not None and process.returncode is None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
        if self._stderr_task is not None:
            self._stderr_task.cancel()
            self._stderr_task = None

    async def list_tools(self) -> list[dict[str, Any]]:
        """Return MCP tools."""
        result = await self.request("tools/list")
        return list(result.get("tools") or [])

    async def read_resource(self, uri: str) -> str:
        """Read one MCP resource as text."""
        result = await self.request("resources/read", {"uri": uri})
        contents = result.get("contents") or []
        if not contents:
            return ""
        return str(contents[0].get("text") or "")

    async def get_prompt(self, name: str, arguments: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Return one MCP prompt."""
        return await self.request("prompts/get", {"name": name, "arguments": arguments or {}})

    async def call_tool(self, name: str, arguments: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Call a Meeting MCP tool and parse the text JSON payload."""
        result = await self.request("tools/call", {"name": name, "arguments": arguments or {}})
        content = result.get("content") or []
        if not content:
            return {}
        text = str(content[0].get("text") or "")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise MeetingMcpError(f"Meeting MCP tool returned non-JSON text: {text[:200]}") from exc

    async def request(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Send one JSON-RPC request."""
        if self._process is None or self._process.stdin is None or self._process.stdout is None:
            raise MeetingMcpError("Meeting MCP process is not started")
        if self._process.returncode is not None:
            raise MeetingMcpError(f"Meeting MCP process exited with code {self._process.returncode}")

        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {},
        }
        self._process.stdin.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        await self._process.stdin.drain()
        try:
            line = await asyncio.wait_for(
                self._process.stdout.readline(),
                timeout=self.config.request_timeout,
            )
        except asyncio.TimeoutError as exc:
            raise MeetingMcpError(f"Meeting MCP request timed out: {method}") from exc
        if not line:
            stderr = "\n".join(self._stderr_tail[-20:])
            raise MeetingMcpError(f"Meeting MCP process closed stdout during {method}. stderr: {stderr}")
        response = json.loads(line.decode("utf-8"))
        if response.get("error"):
            message = response["error"].get("message", "unknown error")
            stderr = "\n".join(self._stderr_tail[-20:])
            if stderr:
                raise MeetingMcpError(f"Meeting MCP {method} failed: {message}. stderr: {stderr}")
            raise MeetingMcpError(f"Meeting MCP {method} failed: {message}")
        return dict(response.get("result") or {})

    async def notify(self, method: str, params: Optional[dict[str, Any]] = None) -> None:
        """Send one JSON-RPC notification."""
        if self._process is None or self._process.stdin is None:
            raise MeetingMcpError("Meeting MCP process is not started")
        if self._process.returncode is not None:
            raise MeetingMcpError(f"Meeting MCP process exited with code {self._process.returncode}")
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }
        self._process.stdin.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        await self._process.stdin.drain()

    async def _drain_stderr(self) -> None:
        if self._process is None or self._process.stderr is None:
            return
        while True:
            line = await self._process.stderr.readline()
            if not line:
                break
            self._stderr_tail.append(line.decode("utf-8", errors="replace").rstrip())
            self._stderr_tail = self._stderr_tail[-100:]


class MeetingGatewayService:
    """Gateway-facing facade over the Meeting MCP connector."""

    def __init__(
        self,
        config: Optional[MeetingMcpConfig] = None,
        client_factory: type[MeetingMcpJsonRpcClient] = MeetingMcpJsonRpcClient,
    ) -> None:
        self.config = config or get_meeting_mcp_config()
        self.client_factory = client_factory

    async def capabilities(self) -> dict[str, Any]:
        """Return Meeting MCP capabilities visible to harnessOS."""
        async with self.client_factory(self.config) as client:
            tools = await client.list_tools()
            guide_text = await client.read_resource("meeting://agent-guide")
            prompt = await client.get_prompt("meeting_process_recording", {})
        return {
            "server": "meeting",
            "tools": [tool.get("name") for tool in tools],
            "agent_guide": _json_or_text(guide_text),
            "prompt": prompt,
        }

    async def analyze_text(self, text: str, *, title: Optional[str] = None) -> dict[str, Any]:
        """Analyze meeting transcript text and build minutes."""
        async with self.client_factory(self.config) as client:
            analysis = await client.call_tool(
                "meeting_analyze_text",
                {"text": text, "mode": "audio_analyzer"},
            )
            minutes = await client.call_tool(
                "meeting_build_minutes",
                {"session_id": analysis.get("session_id"), "title": title or analysis.get("theme")},
            )
        return _summarize_meeting_result(analysis=analysis, minutes=minutes)

    async def process_recording(
        self,
        path: str,
        *,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        title: Optional[str] = None,
    ) -> dict[str, Any]:
        """Transcribe, analyze, and build minutes for one recording."""
        audio_path = Path(path).expanduser().resolve()
        if not audio_path.exists() or not audio_path.is_file():
            raise MeetingMcpError(f"Audio file does not exist: {audio_path}")
        process_args = {
            "path": str(audio_path),
            "engine": engine or self.config.default_engine,
            "language": language or self.config.default_language,
            "analyze": True,
            "mode": "audio_analyzer",
        }
        last_error: MeetingMcpError | None = None
        for attempt in range(1, MEETING_MCP_PROCESS_RETRIES + 1):
            try:
                async with self.client_factory(self.config) as client:
                    try:
                        result = await client.call_tool("meeting_process_file", process_args)
                    except MeetingMcpError as exc:
                        if not _should_retry_without_inline_analysis(exc):
                            raise
                        result = await client.call_tool(
                            "meeting_process_file",
                            {**process_args, "analyze": False},
                        )
                        transcript = str(result.get("transcript") or "")
                        if transcript.strip():
                            result["analysis"] = await _analyze_transcript_with_fallback(
                                client,
                                transcript,
                                session_id=result.get("session_id"),
                                original_error=exc,
                            )
                    minutes = await client.call_tool(
                        "meeting_build_minutes",
                        {"session_id": result.get("session_id"), "title": title or audio_path.stem},
                    )
                return _summarize_meeting_result(process_result=result, minutes=minutes, source_path=str(audio_path))
            except MeetingMcpError as exc:
                last_error = exc
                if not _should_retry_mcp_process(exc) or attempt >= MEETING_MCP_PROCESS_RETRIES:
                    raise
                await asyncio.sleep(MEETING_MCP_RETRY_DELAY_SECONDS)
        if last_error is not None:
            raise last_error
        raise MeetingMcpError("Meeting MCP processing failed without an explicit error")

    async def process_audio_dir(
        self,
        audio_dir: Optional[str] = None,
        *,
        engine: Optional[str] = None,
        language: Optional[str] = None,
    ) -> dict[str, Any]:
        """Process every supported audio file under the configured acceptance directory."""
        root = Path(audio_dir or self.config.audio_dir).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise MeetingMcpError(f"Audio directory does not exist: {root}")
        files = [
            path for path in sorted(root.iterdir())
            if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
        ]
        if not files:
            raise MeetingMcpError(f"No supported audio files found in: {root}")
        results = []
        for path in files:
            results.append(
                await self.process_recording(
                    str(path),
                    engine=engine,
                    language=language,
                    title=path.stem,
                )
            )
        return {
            "audio_dir": str(root),
            "file_count": len(files),
            "processed_count": len(results),
            "results": results,
        }


async def _analyze_transcript_with_fallback(
    client: MeetingMcpJsonRpcClient,
    transcript: str,
    *,
    session_id: Optional[str],
    original_error: Exception,
) -> dict[str, Any]:
    compact_text = _compact_transcript_for_analysis(transcript)
    try:
        return await client.call_tool(
            "meeting_analyze_text",
            {"text": compact_text, "session_id": session_id, "mode": "audio_analyzer"},
        )
    except MeetingMcpError as exc:
        return _fallback_meeting_analysis(transcript, original_error=original_error, analysis_error=exc)


def _should_retry_without_inline_analysis(exc: Exception) -> bool:
    message = str(exc).lower()
    retry_markers = (
        "chunk is longer than limit",
        "separator is found",
        "maximum context",
        "context length",
        "token",
        "分析错误",
    )
    return any(marker in message for marker in retry_markers)


def _should_retry_mcp_process(exc: Exception) -> bool:
    """Retry short-lived MCP/ASR failures during explicit real-audio processing."""
    message = str(exc).lower()
    retry_markers = (
        "funasr 连接失败",
        "connection failed",
        "connection refused",
        "temporarily unavailable",
        "timed out",
    )
    return any(marker in message for marker in retry_markers)


def _compact_transcript_for_analysis(text: str, max_chars: int = MAX_FALLBACK_ANALYSIS_CHARS) -> str:
    """Keep representative transcript slices for analyzers with strict prompt limits."""
    stripped = " ".join((text or "").split())
    if len(stripped) <= max_chars:
        return stripped

    head_chars = max_chars // 2
    tail_chars = max_chars - head_chars
    omitted = len(stripped) - max_chars
    return (
        stripped[:head_chars].rstrip()
        + f"\n\n[省略中间转写 {omitted} 字，保留开头和结尾用于长音频降级分析]\n\n"
        + stripped[-tail_chars:].lstrip()
    )


def _fallback_meeting_analysis(
    transcript: str,
    *,
    original_error: Exception,
    analysis_error: Exception,
) -> dict[str, Any]:
    preview = _compact_transcript_for_analysis(transcript, max_chars=1200)
    first_sentence = re.split(r"(?<=[。！？.!?])\s+", preview.strip(), maxsplit=1)[0].strip()
    summary = first_sentence or preview[:300]
    return {
        "theme": "长音频会议分析",
        "summary": summary,
        "key_points": [summary] if summary else [],
        "action_items": [],
        "chapters": [],
        "speaker_roles": [],
        "fallback": True,
        "fallback_reason": (
            "Meeting MCP inline analysis failed; compact transcript analysis also failed. "
            f"inline_error={original_error}; compact_error={analysis_error}"
        ),
    }


def _json_or_text(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _summarize_meeting_result(
    *,
    analysis: Optional[dict[str, Any]] = None,
    process_result: Optional[dict[str, Any]] = None,
    minutes: Optional[dict[str, Any]] = None,
    source_path: Optional[str] = None,
) -> dict[str, Any]:
    payload = process_result or {}
    analysis_payload = analysis or payload.get("analysis") or {}
    transcript = payload.get("transcript") or ""
    segments = payload.get("segments") or []
    minutes = minutes or {}
    artifacts = {}
    for source in (payload, analysis_payload, minutes):
        source_artifacts = source.get("artifacts") if isinstance(source, dict) else None
        if isinstance(source_artifacts, dict):
            artifacts.update(source_artifacts)
    return {
        "source_path": source_path or payload.get("source_path"),
        "session_id": payload.get("session_id") or analysis_payload.get("session_id") or minutes.get("session_id"),
        "transcript_chars": len(transcript),
        "segment_count": len(segments),
        "analysis": analysis_payload,
        "minutes_path": minutes.get("path"),
        "artifacts": artifacts,
        "raw": payload or analysis_payload,
    }
