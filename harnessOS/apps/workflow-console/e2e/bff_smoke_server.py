"""Test-only BFF server for V4.0-F browser smoke.

This server owns a seeded GatewayService and exposes the normal BFF routes used
by the browser. It is intentionally local to the workflow-console e2e harness.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

import uvicorn
from fastapi import Request
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api import create_app  # noqa: E402
from apps.api.auth import LOCAL_ORIGINS  # noqa: E402
from apps.gateway.protocol import GatewayEvent  # noqa: E402
from tests.v4_0_reference_support import build_gateway, rpc, seed_reference_console  # noqa: E402

os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
os.environ.setdefault("HARNESS_CAPABILITY_TOKEN_SECRET", "browser-smoke-secret")
preview_port = os.environ.get("WORKFLOW_CONSOLE_PREVIEW_PORT", "4174")
LOCAL_ORIGINS.add(f"http://127.0.0.1:{preview_port}")
LOCAL_ORIGINS.add(f"http://localhost:{preview_port}")

DEFAULT_SCOPE = {"app_id": "default", "project_id": None, "workspace_id": None}
TMP_ROOT = Path(tempfile.mkdtemp(prefix="harnessos-v4-browser-smoke-"))
GATEWAY = build_gateway(TMP_ROOT)
SEEDED = asyncio.run(seed_reference_console(GATEWAY, template_id="browser_smoke_console", scope=DEFAULT_SCOPE))
app = create_app(gateway_service=GATEWAY)


@app.get("/__test/health")
async def test_health() -> dict[str, Any]:
    """Return seeded fixture ids for the Playwright harness."""
    return {
        "status": "ok",
        "workflow_instance_id": SEEDED["instance"]["workflow_instance_id"],
        "approval_id": SEEDED["approval"]["approval_id"],
        "workflow_template_id": SEEDED["template"]["workflow_template_id"],
        "patch_id": SEEDED["patch"]["workflow_patch_id"],
    }


@app.get("/__test/simple-workflow/status")
async def simple_workflow_status() -> dict[str, Any]:
    """Return the dev/local simple workflow deployment and runtime state."""
    return await _workflow_status(SEEDED)


@app.post("/__test/simple-workflow/deploy")
async def deploy_simple_workflow() -> dict[str, Any]:
    """Seed an isolated dev/local workflow for visible acceptance tests."""
    seeded = await seed_reference_console(GATEWAY, template_id=f"visible_acceptance_{uuid4().hex[:8]}", scope=DEFAULT_SCOPE)
    return await _workflow_status(seeded)


async def _workflow_status(seeded: dict[str, Any]) -> dict[str, Any]:
    instance_id = seeded["instance"]["workflow_instance_id"]
    status = await rpc(GATEWAY, "workflow.instance.status", {"workflow_instance_id": instance_id, "scope": DEFAULT_SCOPE})
    board = await rpc(GATEWAY, "workflow.board.get", {"workflow_instance_id": instance_id, "scope": DEFAULT_SCOPE})
    completed_runs = [
        run
        for station in board["board"].get("stations", [])
        for run in station.get("runs", [])
        if run.get("status") == "completed"
    ]
    output_artifacts = [
        artifact_id
        for station in board["board"].get("stations", [])
        for run in station.get("runs", [])
        for artifact_id in run.get("output_artifact_ids", [])
    ]
    return {
        "status": "ok",
        "workflow_template_id": seeded["template"]["workflow_template_id"],
        "workflow_version_id": seeded["version"]["workflow_version_id"],
        "workflow_instance_id": instance_id,
        "runtime_status": status["status"]["status"],
        "station_count": len(board["board"].get("stations", [])),
        "completed_run_count": len(completed_runs),
        "output_artifact_count": len(output_artifacts),
    }


@app.post("/__test/emit-fake-status-event")
async def emit_fake_status_event(request: Request) -> JSONResponse:
    """Emit a controlled event whose status payload must not become UI truth."""
    body = await request.json()
    workflow_instance_id = str(body.get("workflow_instance_id") or SEEDED["instance"]["workflow_instance_id"])
    fake_status = str(body.get("status") or "forged_failed")
    event = GatewayEvent(
        type="workflow.context.updated",
        app_id="default",
        project_id=None,
        workspace_id=None,
        data={
            "workflow_instance_id": workflow_instance_id,
            "context_revision": body.get("context_revision") or 999,
            "status": fake_status,
            "source": "browser_smoke_fake_event",
        },
    )
    trace = GATEWAY.trace_store.record_event(event)
    GATEWAY.core_service.record_gateway_trace(trace)
    return JSONResponse({"status": "emitted", "workflow_instance_id": workflow_instance_id, "fake_status": fake_status})


@app.post("/__test/emit-fake-agent-event")
async def emit_fake_agent_event(request: Request) -> JSONResponse:
    """Emit a fake Agent payload that must only trigger UI refresh."""
    body = await request.json()
    workflow_instance_id = str(body.get("workflow_instance_id") or SEEDED["instance"]["workflow_instance_id"])
    event_type = str(body.get("type") or "agent.action_proposal.created")
    event = GatewayEvent(
        type=event_type,
        app_id="default",
        project_id=None,
        workspace_id=None,
        data={
            "workflow_instance_id": workflow_instance_id,
            "selected_proposal_id": "fake_proposal_from_event",
            "selected_patch_id": "fake_patch_from_event",
            "selected_evidence_id": "fake_evidence_from_event",
            "raw_trace_payload": "secret-token-value",
        },
    )
    trace = GATEWAY.trace_store.record_event(event)
    GATEWAY.core_service.record_gateway_trace(trace)
    return JSONResponse({"status": "emitted", "workflow_instance_id": workflow_instance_id, "event_type": event_type})


if __name__ == "__main__":
    port = int(os.environ.get("WORKFLOW_CONSOLE_BFF_PORT", "18040"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
