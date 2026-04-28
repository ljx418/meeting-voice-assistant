"""Stdio JSONL gateway server.

Each stdin line is one RpcRequest JSON object. Each stdout line is one
RpcResponse JSON object.
"""

from __future__ import annotations

import asyncio
import json
import sys
import warnings
from typing import Any

warnings.filterwarnings(
    "ignore",
    message=r"urllib3 v2 only supports OpenSSL 1\.1\.1\+.*",
    category=Warning,
    module=r"urllib3(\.|$)",
)

from pydantic import ValidationError

from apps.gateway.protocol import RpcError, RpcRequest, RpcResponse
from apps.gateway.service import GatewayService


async def run_stdio() -> int:
    """Run the stdin/stdout JSONL protocol loop."""
    service = GatewayService()
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        response = await _handle_line(service, line)
        print(response.model_dump_json(), flush=True)
    return 0


async def _handle_line(service: GatewayService, line: str) -> RpcResponse:
    try:
        payload: Any = json.loads(line)
    except json.JSONDecodeError as exc:
        return RpcResponse(
            error=RpcError(
                code="PARSE_ERROR",
                message=str(exc),
            )
        )
    try:
        request = RpcRequest.model_validate(payload)
    except ValidationError as exc:
        return RpcResponse(
            id=payload.get("id") if isinstance(payload, dict) else None,
            error=RpcError(
                code="INVALID_REQUEST",
                message=str(exc),
            ),
        )
    return await service.handle_rpc(request)


def main() -> int:
    """CLI entry point."""
    return asyncio.run(run_stdio())


if __name__ == "__main__":
    raise SystemExit(main())
