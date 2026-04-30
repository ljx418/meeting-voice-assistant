"""MCP stdio server for meeting capabilities.

The preferred path uses the official ``mcp`` Python SDK.  When that package is
not installed, this module falls back to a small line-delimited JSON-RPC stdio
server that implements the MCP methods used by current clients.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, List, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, TextContent, TextResourceContents, Tool
    _HAS_MCP_SDK = True
except ModuleNotFoundError:  # pragma: no cover - environment dependent
    Server = None  # type: ignore[assignment]
    stdio_server = None  # type: ignore[assignment]
    _HAS_MCP_SDK = False

    @dataclass
    class Resource:  # type: ignore[no-redef]
        uri: str
        name: str
        description: str
        mimeType: str

    @dataclass
    class TextResourceContents:  # type: ignore[no-redef]
        uri: str
        mimeType: str
        text: str

    @dataclass
    class Tool:  # type: ignore[no-redef]
        name: str
        description: str
        inputSchema: dict[str, Any]

    @dataclass
    class TextContent:  # type: ignore[no-redef]
        type: str
        text: str

from .service import MeetingMcpService


server = Server("meeting") if _HAS_MCP_SDK else None
_output_root = Path(os.getenv("MEETING_MCP_OUTPUT_ROOT", "")).expanduser() if os.getenv("MEETING_MCP_OUTPUT_ROOT") else None
_service = MeetingMcpService(output_root=_output_root)


async def list_resources() -> List[Resource]:
    return [
        Resource(
            uri="meeting://formats",
            name="Supported Meeting Formats",
            description="Supported audio/video formats and ASR engines",
            mimeType="application/json",
        ),
        Resource(
            uri="meeting://latest-session",
            name="Latest Meeting MCP Session",
            description="Latest meeting session produced by this MCP process",
            mimeType="application/json",
        ),
        Resource(
            uri="meeting://agent-guide",
            name="Meeting Agent Guide",
            description="Recommended agent workflows and quality checks for meeting MCP tools",
            mimeType="application/json",
        ),
    ]


async def read_resource(uri: str) -> TextResourceContents:
    if uri == "meeting://formats":
        return TextResourceContents(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(_service.formats(), ensure_ascii=False, indent=2),
        )
    if uri == "meeting://latest-session":
        return TextResourceContents(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(_service.latest_session(), ensure_ascii=False, indent=2),
        )
    if uri == "meeting://agent-guide":
        return TextResourceContents(
            uri=uri,
            mimeType="application/json",
            text=json.dumps(_service.agent_guide(), ensure_ascii=False, indent=2),
        )
    raise ValueError(f"Unknown resource: {uri}")


async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="meeting_transcribe_file",
            description="Transcribe a local audio/video file through the configured meeting ASR adapter",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "engine": {"type": "string"},
                    "language": {"type": "string", "default": "zh"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="meeting_analyze_text",
            description="Analyze meeting transcript text into summary, chapters, speakers, and action items",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "session_id": {"type": "string"},
                    "mode": {"type": "string", "enum": ["audio_analyzer", "llm"], "default": "audio_analyzer"},
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="meeting_process_file",
            description="Transcribe a local audio/video file and optionally analyze the transcript",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "engine": {"type": "string"},
                    "language": {"type": "string", "default": "zh"},
                    "analyze": {"type": "boolean", "default": True},
                    "mode": {"type": "string", "enum": ["audio_analyzer", "llm"], "default": "audio_analyzer"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="meeting_build_minutes",
            description="Build a human-readable Markdown meeting minutes artifact from a previous meeting MCP session",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "title": {"type": "string"},
                    "include_transcript_preview": {"type": "boolean", "default": True},
                },
            },
        ),
    ]


async def call_tool(name: str, arguments: Optional[dict[str, Any]]) -> List[TextContent]:
    arguments = arguments or {}
    if name == "meeting_transcribe_file":
        payload = await _service.transcribe_file(
            arguments.get("path", ""),
            engine=arguments.get("engine"),
            language=arguments.get("language", "zh"),
        )
        return [_json_text(payload)]

    if name == "meeting_analyze_text":
        payload = await _service.analyze_text(
            arguments.get("text", ""),
            session_id=arguments.get("session_id"),
            mode=arguments.get("mode", "audio_analyzer"),
        )
        return [_json_text(payload)]

    if name == "meeting_process_file":
        payload = await _service.process_file(
            arguments.get("path", ""),
            engine=arguments.get("engine"),
            language=arguments.get("language", "zh"),
            analyze=_as_bool(arguments.get("analyze", True)),
            mode=arguments.get("mode", "audio_analyzer"),
        )
        return [_json_text(payload)]

    if name == "meeting_build_minutes":
        payload = _service.build_minutes(
            session_id=arguments.get("session_id"),
            title=arguments.get("title"),
            include_transcript_preview=_as_bool(arguments.get("include_transcript_preview", True)),
        )
        return [_json_text(payload)]

    raise ValueError(f"Unknown tool: {name}")


if server is not None:
    server.list_resources()(list_resources)
    server.read_resource()(read_resource)
    server.list_tools()(list_tools)
    server.call_tool()(call_tool)


def _json_text(payload: dict[str, Any]) -> TextContent:
    return TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() not in {"0", "false", "no", "off"}
    return bool(value)


async def main() -> None:
    if server is not None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
        return
    await run_jsonrpc_stdio()


async def run_jsonrpc_stdio() -> None:
    """Run a minimal MCP-compatible JSON-RPC stdio loop without the SDK."""
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.buffer.readline)
        if not line:
            break
        try:
            request = json.loads(line.decode("utf-8"))
            response = await handle_jsonrpc_request(request)
        except Exception as exc:  # pragma: no cover - defensive boundary
            response = _jsonrpc_error(None, -32700, f"Invalid JSON-RPC request: {exc}")
        if response is None:
            continue
        sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
        sys.stdout.flush()


async def handle_jsonrpc_request(request: dict[str, Any]) -> Optional[dict[str, Any]]:
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    if request_id is None and method in {"notifications/initialized", "notifications/cancelled"}:
        return None

    try:
        if method == "initialize":
            return _jsonrpc_result(request_id, {
                "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                "capabilities": {
                    "resources": {},
                    "tools": {},
                },
                "serverInfo": {
                    "name": "meeting",
                    "version": "0.1.0",
                },
            })
        if method == "ping":
            return _jsonrpc_result(request_id, {})
        if method == "resources/list":
            return _jsonrpc_result(request_id, {"resources": [_to_wire(item) for item in await list_resources()]})
        if method == "resources/read":
            uri = params.get("uri", "")
            item = await read_resource(uri)
            return _jsonrpc_result(request_id, {"contents": [_to_wire(item)]})
        if method == "prompts/list":
            return _jsonrpc_result(request_id, {"prompts": [_meeting_prompt_summary()]})
        if method == "prompts/get":
            name = params.get("name", "")
            if name != "meeting_process_recording":
                return _jsonrpc_error(request_id, -32602, f"Unknown prompt: {name}")
            arguments = params.get("arguments") or {}
            return _jsonrpc_result(request_id, _meeting_prompt_get(arguments))
        if method == "tools/list":
            return _jsonrpc_result(request_id, {"tools": [_to_wire(item) for item in await list_tools()]})
        if method == "tools/call":
            content = await call_tool(params.get("name", ""), params.get("arguments") or {})
            return _jsonrpc_result(request_id, {
                "content": [_to_wire(item) for item in content],
                "isError": False,
            })
        return _jsonrpc_error(request_id, -32601, f"Method not found: {method}")
    except Exception as exc:
        return _jsonrpc_error(request_id, -32000, str(exc))


def _jsonrpc_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _jsonrpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _to_wire(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True)
    if hasattr(value, "dict"):
        return value.dict(by_alias=True)
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return dict(value)


def _meeting_prompt_summary() -> dict[str, Any]:
    return {
        "name": "meeting_process_recording",
        "description": "Guide an agent to process a meeting recording into transcript, summary, action items, and Markdown minutes.",
        "arguments": [
            {
                "name": "path",
                "description": "Local audio or video file path",
                "required": True,
            },
            {
                "name": "engine",
                "description": "ASR engine, for example mock, funasr, dashscope_file",
                "required": False,
            },
            {
                "name": "language",
                "description": "Primary language hint such as zh or en",
                "required": False,
            },
        ],
    }


def _meeting_prompt_get(arguments: dict[str, Any]) -> dict[str, Any]:
    path = arguments.get("path", "<audio-or-video-path>")
    engine = arguments.get("engine", "funasr")
    language = arguments.get("language", "zh")
    text = (
        "Use the meeting MCP tools only for meeting workflows. "
        "Do not invoke interview tools or generate interview coaching. "
        f"Call meeting_process_file with path={path!r}, engine={engine!r}, language={language!r}, analyze=true. "
        "After it returns, inspect transcript length, segment count, analysis.theme, summary, key_points, and action_items. "
        "Then call meeting_build_minutes with the returned session_id and report the minutes path plus the main summary."
    )
    return {
        "description": "Meeting recording processing workflow",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": text,
                },
            }
        ],
    }


if __name__ == "__main__":
    asyncio.run(main())
