"""Run harnessOS Meeting -> Knowledge cross-domain MCP acceptance workflow."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.cross_domain_mcp_workflow import MeetingToKnowledgeMcpRunner
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Meeting -> Knowledge MCP validation.")
    parser.add_argument("--audio", required=True, help="Local audio file path for the meeting workflow.")
    parser.add_argument("--query", default="请基于会议纪要总结关键决策和行动项")
    parser.add_argument("--workspace-name", default="HarnessOS Meeting Knowledge Acceptance")
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--max-polls", type=int, default=120)
    args = parser.parse_args()

    blocked = _blocked_reason(args.audio)
    if blocked:
        print(json.dumps({"status": "blocked", "reason": blocked}, ensure_ascii=False, indent=2))
        return 2

    service = GatewayService(GatewayRuntimePool(runtime_backend="simple"))
    result = asyncio.run(MeetingToKnowledgeMcpRunner(service).run(
        audio_path=args.audio,
        query=args.query,
        workspace_name=args.workspace_name,
        poll_interval=args.poll_interval,
        max_polls=args.max_polls,
    ))
    payload = result.to_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "ok" else 1


def _blocked_reason(audio: str) -> str:
    if os.environ.get("HARNESS_FUNASR_MCP_EXECUTION") != "stdio":
        return "Set HARNESS_FUNASR_MCP_EXECUTION=stdio to run real FunASR MCP transcription."
    if os.environ.get("HARNESS_DATA_SERVICE_MCP_EXECUTION") != "stdio":
        return "Set HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio to run real Data Service MCP lifecycle."
    audio_path = Path(audio).expanduser()
    if not audio_path.exists() or not audio_path.is_file():
        return f"Audio file does not exist: {audio_path}"
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
