"""Command line entrypoints for the standalone voice service."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from urllib import error, request

from funasr_service.config import SERVICE_HOST, SERVICE_PORT
from funasr_service.service import recognize_file_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="voice-service")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_http = subparsers.add_parser("serve-http", help="Run the HTTP/WebSocket API")
    serve_http.add_argument("--host", default=SERVICE_HOST)
    serve_http.add_argument("--port", type=int, default=SERVICE_PORT)
    serve_http.add_argument("--reload", action="store_true")

    health = subparsers.add_parser("health", help="Check a running HTTP service")
    health.add_argument("--endpoint", default=f"http://localhost:{SERVICE_PORT}")

    recognize = subparsers.add_parser("recognize", help="Recognize a local audio file directly")
    recognize.add_argument("audio_path")
    recognize.add_argument("--json", action="store_true", dest="as_json")

    subparsers.add_parser("serve-mcp", help="Run the MCP stdio server")

    args = parser.parse_args(argv)
    if args.command == "serve-http":
        return _serve_http(args.host, args.port, args.reload)
    if args.command == "health":
        return _health(args.endpoint)
    if args.command == "recognize":
        return _recognize(args.audio_path, args.as_json)
    if args.command == "serve-mcp":
        from funasr_service.mcp_stdio import main as mcp_main

        asyncio.run(mcp_main())
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


def _serve_http(host: str, port: int, reload: bool) -> int:
    import uvicorn

    uvicorn.run("funasr_service.main:app", host=host, port=port, reload=reload)
    return 0


def _health(endpoint: str) -> int:
    try:
        with request.urlopen(f"{endpoint.rstrip('/')}/health", timeout=10) as response:
            sys.stdout.write(response.read().decode("utf-8") + "\n")
        return 0
    except error.URLError as exc:
        sys.stderr.write(f"voice service unavailable: {exc}\n")
        return 1


def _recognize(audio_path: str, as_json: bool) -> int:
    response = recognize_file_path(Path(audio_path).expanduser())
    payload = response.model_dump() if hasattr(response, "model_dump") else response.dict()
    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(payload["text"] + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
