"""Meeting-domain Gateway integration backed by the external Meeting MCP server."""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from apps.gateway.artifacts import ArtifactError, ArtifactRegistry
from core.config import MeetingMcpConfig, get_meeting_mcp_config


SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
MAX_FALLBACK_ANALYSIS_CHARS = 8000
MEETING_MCP_STDIO_LIMIT = 128 * 1024 * 1024


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
        env.setdefault("ASR_ENGINE", self.config.default_engine)
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
        await self.request("initialize", {"protocolVersion": "2024-11-05"})

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
            raise MeetingMcpError(f"Meeting MCP {method} failed: {message}")
        return dict(response.get("result") or {})

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
    """Gateway-facing meeting workflow facade."""

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
        async with self.client_factory(self.config) as client:
            process_args = {
                "path": str(audio_path),
                "engine": engine or self.config.default_engine,
                "language": language or self.config.default_language,
                "analyze": True,
                "mode": "audio_analyzer",
            }
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


class MeetingWorkflow:
    """Natural-language meeting workflow used by turn.start."""

    def __init__(
        self,
        service: Optional[MeetingGatewayService] = None,
        artifact_registry: Optional[ArtifactRegistry] = None,
    ) -> None:
        self.service = service or MeetingGatewayService()
        self.artifact_registry = artifact_registry or ArtifactRegistry()

    def should_handle(self, user_input: str, *, domain: Optional[str] = None) -> bool:
        """Return whether this turn should use the meeting workflow."""
        if domain == "meeting":
            return True
        if domain and domain != "meeting":
            return False
        lowered = user_input.lower()
        if any(keyword in lowered for keyword in ("interview", "面试", "候选人", "简历", "candidate", "resume")):
            return False
        has_meeting_keyword = any(
            keyword in lowered
            for keyword in ("meeting", "会议", "纪要", "转写", "音频", "summary", "minutes", "transcribe")
        )
        return has_meeting_keyword and bool(extract_audio_path(user_input))

    async def run(
        self,
        user_input: str,
        *,
        domain: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Run a meeting task and return text plus structured metadata."""
        audio_path = extract_audio_path(user_input)
        if audio_path:
            result = await self.service.process_recording(
                audio_path,
                engine=None,
                language=None,
                title=Path(audio_path).stem,
            )
        elif domain == "meeting":
            result = await self.service.analyze_text(user_input, title="Meeting Notes")
        else:
            raise MeetingMcpError("Meeting workflow requires a supported audio path or explicit domain=meeting text.")
        register_meeting_artifacts(
            result,
            artifact_registry=self.artifact_registry,
            session_id=session_id,
            turn_id=turn_id,
        )
        text = format_meeting_final_text(result)
        return {"status": "success", "content": text, "meeting": result}


def extract_audio_path(text: str) -> Optional[str]:
    """Extract the first supported local audio path from user text."""
    extension_pattern = "|".join(re.escape(ext.lstrip(".")) for ext in sorted(SUPPORTED_AUDIO_EXTENSIONS))
    for match in re.finditer(rf"\.({extension_pattern})\b", text, flags=re.IGNORECASE):
        prefix = text[:match.start()]
        slash_positions = [index for index, char in enumerate(prefix) if char == "/"]
        if not slash_positions:
            continue
        candidates = []
        existing_candidates = []
        for start in reversed(slash_positions):
            candidate = text[start:match.end()].strip().strip("\"'")
            candidate = candidate.rstrip(" \t\r\n，。；;、,.)）]】")
            if candidate:
                candidates.append(candidate)
                if Path(candidate).expanduser().exists():
                    existing_candidates.append(candidate)
        if existing_candidates:
            return max(existing_candidates, key=len)
        if candidates:
            return candidates[-1]
    return None


def format_meeting_final_text(result: dict[str, Any]) -> str:
    """Render a user-facing meeting workflow result."""
    analysis = result.get("analysis") or {}
    theme = analysis.get("theme") or "未识别主题"
    summary = analysis.get("summary") or ""
    minutes_path = result.get("minutes_path") or ""
    artifacts = result.get("artifacts") or {}
    lines = [
        "会议分析已完成。",
        f"主题：{theme}",
        f"转写字数：{result.get('transcript_chars', 0)}",
        f"分段数量：{result.get('segment_count', 0)}",
    ]
    if summary:
        lines.append(f"摘要：{summary}")
    if minutes_path:
        lines.append(f"会议纪要：{minutes_path}")
    if artifacts:
        artifact_parts = []
        for name, value in artifacts.items():
            if isinstance(value, dict):
                path = value.get("path", "")
                artifact_id = value.get("artifact_id")
                suffix = f" ({artifact_id})" if artifact_id else ""
                artifact_parts.append(f"{name}: {path}{suffix}")
            else:
                artifact_parts.append(f"{name}: {value}")
        artifact_text = "，".join(artifact_parts)
        lines.append(f"Artifacts：{artifact_text}")
    return "\n".join(lines)


def register_meeting_artifacts(
    result: dict[str, Any],
    *,
    artifact_registry: ArtifactRegistry,
    session_id: Optional[str] = None,
    turn_id: Optional[str] = None,
) -> dict[str, Any]:
    """Register meeting output paths as harnessOS artifact records."""
    artifacts = result.get("artifacts") or {}
    if not isinstance(artifacts, dict):
        return {}

    registered: dict[str, Any] = {}
    for kind, value in list(artifacts.items()):
        path = value.get("path") if isinstance(value, dict) else value
        if not isinstance(path, str) or not path:
            continue
        try:
            record = artifact_registry.register_file(
                path,
                session_id=session_id,
                turn_id=turn_id,
                domain="meeting",
                kind=str(kind),
                metadata={
                    "meeting_session_id": result.get("session_id"),
                    "source_path": result.get("source_path"),
                },
            )
        except ArtifactError:
            continue
        registered[str(kind)] = {"path": path, "artifact_id": record["artifact_id"], "record": record}

    if registered:
        result["artifacts"] = registered
        result["artifact_records"] = {kind: item["record"] for kind, item in registered.items()}
    return registered


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
    return {
        "source_path": source_path or payload.get("source_path"),
        "session_id": payload.get("session_id") or analysis_payload.get("session_id") or minutes.get("session_id"),
        "transcript_chars": len(transcript),
        "segment_count": len(segments),
        "analysis": analysis_payload,
        "minutes_path": minutes.get("path"),
        "artifacts": minutes.get("artifacts") or payload.get("artifacts") or {},
        "raw": payload or analysis_payload,
    }
