"""Run PhaseE Knowledge Pack validation through the Gateway standard path."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService


REQUIRED_KINDS = {"source_reference", "note", "brief", "citation_bundle"}


async def _run(args: argparse.Namespace) -> dict[str, Any]:
    if os.environ.get("HARNESS_DATA_SERVICE_MCP_EXECUTION") != "stdio":
        return {
            "status": "blocked",
            "reason": "Set HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio to run real Knowledge MCP validation.",
        }

    service = GatewayService(GatewayRuntimePool(runtime_backend="simple"))
    connector = await service.handle_rpc(
        RpcRequest(id="knowledge-connector", method="connector.get", params={"connector_id": "data_service_mcp"})
    )
    if connector.error is not None:
        return {"status": "failed", "stage": "connector_preflight", "error": connector.error.message}
    connector_record = connector.result.get("connector", {})
    if connector_record.get("health") not in {"available", "configured"}:
        return {
            "status": "failed",
            "stage": "connector_preflight",
            "connector_id": "data_service_mcp",
            "health": connector_record.get("health"),
            "message": connector_record.get("capabilities", {}).get("health_message"),
            "next_actions": [
                "Start or repair the adjacent data_service MCP stdio environment.",
                "Keep HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio for real validation.",
            ],
        }
    started = await service.handle_rpc(
        RpcRequest(
            id="knowledge-session",
            method="session.start",
            params={"scope": {"app_id": "knowledge", "workspace_id": args.workspace_id}},
        )
    )
    if started.error is not None:
        return {"status": "failed", "stage": "session_start", "error": started.error.message}
    session_id = started.result["session_id"]

    user_input = args.query
    if args.document:
        document_path = Path(args.document).expanduser()
        if not document_path.exists():
            return {"status": "failed", "stage": "preflight", "reason": f"document not found: {document_path}"}
        user_input = f"录入知识库: {document_path.read_text(encoding='utf-8')}"

    turn = await service.handle_rpc(
        RpcRequest(
            id="knowledge-turn",
            method="turn.start",
            params={"session_id": session_id, "domain": "knowledge", "input": user_input},
        )
    )
    if turn.error is not None:
        return {"status": "failed", "stage": "turn_start", "error": turn.error.message, "session_id": session_id}

    final = turn.result
    failed = _failed_turn_event(final)
    if failed is not None:
        return {
            "status": "failed",
            "stage": "workflow",
            "session_id": session_id,
            "message": failed.get("data", {}).get("message"),
        }
    completed_data = final["events"][-1]["data"] if final.get("events") else {}
    if completed_data.get("approval_required"):
        approval_id = completed_data["approval"]["approval_id"]
        approved = await service.handle_rpc(
            RpcRequest(
                id="knowledge-approve",
                method="approval.approve",
                params={
                    "approval_id": approval_id,
                    "app_id": "knowledge",
                    "workspace_id": args.workspace_id,
                },
            )
        )
        if approved.error is not None:
            return {
                "status": "failed",
                "stage": "approval",
                "error": approved.error.message,
                "session_id": session_id,
            }
        retried = await service.handle_rpc(
            RpcRequest(
                id="knowledge-retry",
                method="turn.retry",
                params={
                    "session_id": session_id,
                    "approval_id": approval_id,
                    "app_id": "knowledge",
                    "workspace_id": args.workspace_id,
                },
            )
        )
        if retried.error is not None:
            return {
                "status": "failed",
                "stage": "turn_retry",
                "error": retried.error.message,
                "session_id": session_id,
                "approval_id": approval_id,
            }
        final = retried.result
        failed = _failed_turn_event(final)
        if failed is not None:
            return {
                "status": "failed",
                "stage": "workflow",
                "session_id": session_id,
                "approval_id": approval_id,
                "message": failed.get("data", {}).get("message"),
            }
        completed_data = final["events"][-1]["data"] if final.get("events") else {}

    lineage = await service.handle_rpc(
        RpcRequest(
            id="knowledge-lineage",
            method="artifact.lineage",
            params={"session_id": session_id, "domain": "knowledge", "app_id": "knowledge"},
        )
    )
    jobs = await service.handle_rpc(
        RpcRequest(id="knowledge-jobs", method="job.list", params={"session_id": session_id, "app_id": "knowledge"})
    )
    traces = await service.handle_rpc(
        RpcRequest(
            id="knowledge-traces",
            method="core.trace.list",
            params={"session_id": session_id, "app_id": "knowledge"},
        )
    )
    if lineage.error is not None:
        return {"status": "failed", "stage": "lineage", "error": lineage.error.message, "session_id": session_id}

    kinds = {artifact["kind"] for artifact in lineage.result.get("artifacts", [])}
    missing = sorted(REQUIRED_KINDS - kinds)
    if missing:
        return {
            "status": "failed",
            "stage": "artifact_validation",
            "missing_artifact_kinds": missing,
            "present_artifact_kinds": sorted(kinds),
            "session_id": session_id,
        }
    workflow_jobs = [
        job for job in (jobs.result.get("jobs", []) if jobs.error is None else [])
        if job.get("workflow_id") == "knowledge.workflow"
    ]
    if not workflow_jobs or not workflow_jobs[-1].get("artifact_ids"):
        return {"status": "failed", "stage": "job_binding", "session_id": session_id}
    if traces.error is not None or traces.result.get("count", 0) == 0:
        return {"status": "failed", "stage": "trace_binding", "session_id": session_id}

    return {
        "status": "passed",
        "session_id": session_id,
        "workspace_id": args.workspace_id,
        "artifact_kinds": sorted(kinds),
        "lineage_count": lineage.result["count"],
        "lineage_roots": lineage.result["roots"],
        "lineage_leaves": lineage.result["leaves"],
        "workflow_job_id": workflow_jobs[-1]["job_id"],
        "workflow_artifact_ids": workflow_jobs[-1]["artifact_ids"],
        "trace_count": traces.result["count"],
    }


def _failed_turn_event(result: dict[str, Any]) -> dict[str, Any] | None:
    for event in result.get("events", []):
        if isinstance(event, dict) and event.get("type") == "turn.failed":
            return event
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PhaseE Knowledge Pack E2E validation.")
    parser.add_argument("document", nargs="?", help="Optional UTF-8 document to ingest through the standard path.")
    parser.add_argument("--query", default="HarnessOS PhaseE Knowledge Pack validation")
    parser.add_argument("--workspace-id", default="harnessos-phasee-knowledge")
    args = parser.parse_args()

    result = asyncio.run(_run(args))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
