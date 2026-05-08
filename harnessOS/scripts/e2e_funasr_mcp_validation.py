"""Run harnessOS FunASR MCP stdio acceptance workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run FunASR MCP stdio validation.")
    parser.add_argument("--audio", required=True, help="Local audio file path accepted by FunASR MCP.")
    args = parser.parse_args()

    if os.environ.get("HARNESS_FUNASR_MCP_EXECUTION") != "stdio":
        print(json.dumps({
            "status": "blocked",
            "reason": "Set HARNESS_FUNASR_MCP_EXECUTION=stdio to run real FunASR MCP validation.",
        }, ensure_ascii=False, indent=2))
        return 2

    audio_path = Path(args.audio).expanduser()
    if not audio_path.exists() or not audio_path.is_file():
        print(json.dumps({
            "status": "blocked",
            "reason": f"Audio file does not exist: {audio_path}",
        }, ensure_ascii=False, indent=2))
        return 2

    service = GatewayService(GatewayRuntimePool(runtime_backend="simple"))
    health = _run_rpc(service, RpcRequest(
        id="funasr-health",
        method="connector.health",
        params={"connector_id": "funasr_mcp"},
    ))
    if health["health"]["status"] != "available":
        print(json.dumps({
            "status": "blocked",
            "health": health,
        }, ensure_ascii=False, indent=2))
        return 2

    tool_health = _submit_with_approval(
        service,
        request_id="funasr-tool-health",
        tool="funasr_health",
        payload={},
    )
    submitted = _submit_with_approval(
        service,
        request_id="funasr-submit",
        tool="funasr_recognize_file",
        payload={"path": str(audio_path.resolve())},
    )
    status = submitted["job"]["status"]
    print(json.dumps({
        "status": "ok" if status == "completed" else status,
        "health": health,
        "tool_health": tool_health,
        "submission": submitted,
    }, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 1


def _run_rpc(service: GatewayService, request: RpcRequest) -> dict:
    import asyncio

    async def run() -> dict:
        response = await service.handle_rpc(request)
        if response.error is not None:
            raise RuntimeError(response.error.message)
        return response.result

    return asyncio.run(run())


def _submit_with_approval(service: GatewayService, *, request_id: str, tool: str, payload: dict) -> dict:
    submitted = _run_rpc(service, RpcRequest(
        id=request_id,
        method="connector.submit",
        params={
            "connector_id": "funasr_mcp",
            "tool": tool,
            "input": payload,
        },
    ))
    if not submitted.get("approval_required"):
        return submitted
    approval_id = submitted["approval"]["approval_id"]
    _run_rpc(service, RpcRequest(
        id=f"{request_id}-approve",
        method="approval.approve",
        params={"approval_id": approval_id, "reason": "Explicit local FunASR MCP acceptance."},
    ))
    return _run_rpc(service, RpcRequest(
        id=f"{request_id}-approved",
        method="connector.submit",
        params={
            "connector_id": "funasr_mcp",
            "tool": tool,
            "input": payload,
            "approval_id": approval_id,
        },
    ))


if __name__ == "__main__":
    raise SystemExit(main())
