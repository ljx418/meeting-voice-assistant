"""harnessOS API server entry point."""

from __future__ import annotations

import argparse
import socket
import sys
from collections.abc import Sequence

import uvicorn
from core.config import get_server_config


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    config = get_server_config()
    parser = argparse.ArgumentParser(description="Run the harnessOS API server.")
    parser.add_argument("--host", default=config.host, help=f"Bind host. Default: {config.host}")
    parser.add_argument("--port", type=int, default=config.port, help=f"Bind port. Default: {config.port}")
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable uvicorn auto-reload. Useful for one-off local validation.",
    )
    return parser.parse_args(argv)


def _port_is_available(host: str, port: int) -> bool:
    probe_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    try:
        with socket.create_connection((probe_host, port), timeout=0.2):
            return False
    except OSError:
        return True


def main(argv: Sequence[str] | None = None) -> int:
    """Run the harnessOS API server."""
    args = _parse_args(argv)
    if not _port_is_available(args.host, args.port):
        example_port = args.port + 10
        print(
            "\n".join(
                [
                    f"harnessOS cannot start: {args.host}:{args.port} is already in use.",
                    f"Inspect the existing process: lsof -nP -iTCP:{args.port} -sTCP:LISTEN",
                    f"Or start harnessOS on another free port, for example: python3 main.py --port {example_port}",
                ]
            ),
            file=sys.stderr,
        )
        return 1

    uvicorn.run(
        "apps.api:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
