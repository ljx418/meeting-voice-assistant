"""Run harnessOS external Data Service MCP acceptance workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.knowledge_mcp_workflow import KnowledgeMcpWorkflowRunner
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Data Service MCP external Harness E2E validation.")
    parser.add_argument("--name", default="HarnessOS Data Service MCP Acceptance")
    parser.add_argument("--query", default="HarnessOS external MCP acceptance")
    parser.add_argument("--text-title", default="HarnessOS Acceptance Note")
    parser.add_argument(
        "--text",
        default="# HarnessOS Acceptance Note\n\nHarnessOS validates Data Service MCP lifecycle tools.",
    )
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--max-polls", type=int, default=120)
    args = parser.parse_args()

    if os.environ.get("HARNESS_DATA_SERVICE_MCP_EXECUTION") != "stdio":
        print(json.dumps({
            "status": "blocked",
            "reason": "Set HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio to run real Data Service MCP validation.",
        }, ensure_ascii=False, indent=2))
        return 2

    service = GatewayService(GatewayRuntimePool(runtime_backend="simple"))
    runner = KnowledgeMcpWorkflowRunner(service.connector_execution_runtime)
    result = runner.run_acceptance(
        name=args.name,
        query=args.query,
        texts=[{"title": args.text_title, "content": args.text, "metadata": {"kind": "acceptance"}}],
        poll_interval=args.poll_interval,
        max_polls=args.max_polls,
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.status in {"ok", "completed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
