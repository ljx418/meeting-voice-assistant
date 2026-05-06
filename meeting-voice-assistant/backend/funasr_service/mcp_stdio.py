"""MCP stdio server for FunASR service access."""

from __future__ import annotations

import asyncio
import json
import mimetypes
import os
import sys
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, List, Optional
from urllib import error, request

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


SUPPORTED_SUFFIXES = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
DEFAULT_AUDIO_ROOTS = [
    "/Users/Zhuanz/Desktop/workspace/音频资料",
    "/tmp",
]

server = Server("funasr") if _HAS_MCP_SDK else None


def _endpoint() -> str:
    return os.getenv(
        "HARNESS_FUNASR_MCP_ENDPOINT",
        os.getenv("FUNASR_MCP_ENDPOINT", os.getenv("FUNASR_ENDPOINT", "http://localhost:8001")),
    ).rstrip("/")


def _timeout() -> int:
    try:
        return int(os.getenv(
            "HARNESS_FUNASR_MCP_REQUEST_TIMEOUT",
            os.getenv("FUNASR_MCP_TIMEOUT", os.getenv("FUNASR_TIMEOUT", "3600")),
        ))
    except ValueError:
        return 3600


def _max_file_bytes() -> int:
    try:
        mb = int(os.getenv(
            "HARNESS_FUNASR_MCP_MAX_FILE_SIZE_MB",
            os.getenv("FUNASR_MCP_MAX_FILE_SIZE_MB", "500"),
        ))
    except ValueError:
        mb = 500
    return mb * 1024 * 1024


def _audio_roots() -> list[Path]:
    configured = os.getenv(
        "HARNESS_FUNASR_MCP_AUDIO_ROOTS",
        os.getenv("HARNESS_FUNASR_AUDIO_ROOTS", ""),
    ).strip()
    raw_roots = configured.split(os.pathsep) if configured else DEFAULT_AUDIO_ROOTS
    roots: list[Path] = []
    for raw_root in raw_roots:
        if not raw_root:
            continue
        root = Path(raw_root).expanduser()
        try:
            roots.append(root.resolve())
        except OSError:
            continue
    return roots


def _capabilities() -> dict[str, Any]:
    return {
        "service": "funasr",
        "transport": "mcp_stdio",
        "proxy_endpoint": _endpoint(),
        "supported_suffixes": sorted(SUPPORTED_SUFFIXES),
        "audio_roots": [str(path) for path in _audio_roots()],
        "timeout": _timeout(),
        "max_file_size_mb": _max_file_bytes() // (1024 * 1024),
        "tools": ["funasr_health", "funasr_recognize_file"],
    }


async def list_resources() -> List[Resource]:
    return [
        Resource(
            uri="funasr://capabilities",
            name="FunASR MCP Capabilities",
            description="FunASR MCP proxy endpoint, accepted formats, and file access policy",
            mimeType="application/json",
        )
    ]


async def read_resource(uri: str) -> TextResourceContents:
    if uri != "funasr://capabilities":
        raise ValueError(f"Unknown resource: {uri}")
    return TextResourceContents(
        uri=uri,
        mimeType="application/json",
        text=json.dumps(_capabilities(), ensure_ascii=False, indent=2),
    )


async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="funasr_health",
            description="Check the configured FunASR HTTP service health endpoint",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="funasr_recognize_file",
            description="Transcribe one allowed local audio/video file through the FunASR HTTP service",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        ),
    ]


async def call_tool(name: str, arguments: Optional[dict[str, Any]]) -> List[TextContent]:
    arguments = arguments or {}
    if name == "funasr_health":
        return [_json_text(await _health())]
    if name == "funasr_recognize_file":
        return [_json_text(await _recognize_file(str(arguments.get("path", ""))))]
    raise ValueError(f"Unknown tool: {name}")


if server is not None:
    server.list_resources()(list_resources)
    server.read_resource()(read_resource)
    server.list_tools()(list_tools)
    server.call_tool()(call_tool)


async def _health() -> dict[str, Any]:
    return await asyncio.to_thread(_request_json, "GET", f"{_endpoint()}/health", None, None)


async def _recognize_file(path: str) -> dict[str, Any]:
    file_path = _validate_audio_path(path)
    headers, body = _multipart_file_body(file_path)
    response = await asyncio.to_thread(
        _request_json,
        "POST",
        f"{_endpoint()}/recognize",
        body,
        headers,
    )
    sentences = list(response.get("sentences", []) or [])
    duration = 0.0
    for sentence in sentences:
        try:
            duration = max(duration, float(sentence.get("end_time", 0.0) or 0.0))
        except (TypeError, ValueError):
            continue
    return {
        "status": "ok" if response.get("success") else "failed",
        "operation_id": None,
        "warnings": (
            [] if response.get("success")
            else [str(response.get("message") or "FunASR recognition failed")]
        ),
        "artifact_refs": [],
        "next_actions": [],
        "data": {
            "engine": "funasr",
            "source_path": str(file_path),
            "text": response.get("text", ""),
            "sentences": sentences,
            "duration": duration,
            "service_response": response,
        },
    }


def _validate_audio_path(path: str) -> Path:
    if not path:
        raise ValueError("path is required")
    candidate = Path(path).expanduser()
    if candidate.is_symlink():
        raise ValueError("path must not be a symlink")
    resolved = candidate.resolve()
    if not resolved.exists() or not resolved.is_file():
        raise FileNotFoundError(f"Audio file not found: {resolved}")
    if resolved.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported audio suffix: {resolved.suffix}")
    if resolved.stat().st_size > _max_file_bytes():
        raise ValueError("Audio file exceeds FUNASR_MCP_MAX_FILE_SIZE_MB")
    roots = _audio_roots()
    if roots and not any(_is_relative_to(resolved, root) for root in roots):
        raise ValueError(f"Audio file is outside allowed roots: {resolved}")
    return resolved


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _multipart_file_body(path: Path) -> tuple[dict[str, str], bytes]:
    boundary = "----funasr-mcp-boundary"
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    file_bytes = path.read_bytes()
    body = b"".join([
        f"--{boundary}\r\n".encode("utf-8"),
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode("utf-8"),
        f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        file_bytes,
        f"\r\n--{boundary}--\r\n".encode("utf-8"),
    ])
    return {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }, body


def _request_json(
    method: str,
    url: str,
    body: bytes | None,
    headers: dict[str, str] | None,
) -> dict[str, Any]:
    req = request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with request.urlopen(req, timeout=_timeout()) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"FunASR HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"FunASR service unavailable: {exc.reason}") from exc


def _json_text(payload: dict[str, Any]) -> TextContent:
    return TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))


async def main() -> None:
    if server is not None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
        return
    await run_jsonrpc_stdio()


async def run_jsonrpc_stdio() -> None:
    loop = asyncio.get_running_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.buffer.readline)
        if not line:
            break
        try:
            request_payload = json.loads(line.decode("utf-8"))
            response = await handle_jsonrpc_request(request_payload)
        except Exception as exc:  # pragma: no cover - defensive boundary
            response = _jsonrpc_error(None, -32700, f"Invalid JSON-RPC request: {exc}")
        if response is None:
            continue
        sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
        sys.stdout.flush()


async def handle_jsonrpc_request(request_payload: dict[str, Any]) -> Optional[dict[str, Any]]:
    request_id = request_payload.get("id")
    method = request_payload.get("method")
    params = request_payload.get("params") or {}

    if request_id is None and method in {"notifications/initialized", "notifications/cancelled"}:
        return None

    try:
        if method == "initialize":
            return _jsonrpc_result(request_id, {
                "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                "capabilities": {"resources": {}, "tools": {}},
                "serverInfo": {"name": "funasr", "version": "0.1.0"},
            })
        if method == "ping":
            return _jsonrpc_result(request_id, {})
        if method == "resources/list":
            return _jsonrpc_result(
                request_id,
                {"resources": [_to_wire(item) for item in await list_resources()]},
            )
        if method == "resources/read":
            item = await read_resource(params.get("uri", ""))
            return _jsonrpc_result(request_id, {"contents": [_to_wire(item)]})
        if method == "tools/list":
            return _jsonrpc_result(request_id, {"tools": [_to_wire(item) for item in await list_tools()]})
        if method == "tools/call":
            content = await call_tool(params.get("name", ""), params.get("arguments") or {})
            return _jsonrpc_result(
                request_id,
                {"content": [_to_wire(item) for item in content], "isError": False},
            )
        return _jsonrpc_error(request_id, -32601, f"Method not found: {method}")
    except Exception as exc:
        return _jsonrpc_error(request_id, -32000, str(exc))


def _jsonrpc_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _jsonrpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


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


if __name__ == "__main__":
    asyncio.run(main())
