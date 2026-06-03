"""V4.3 serial video workflow BFF routes.

These routes expose a dev/local deterministic serial video workflow runtime.
They do not create an Agent executor and do not call external video tools.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from apps.api.auth import add_dev_warning, authorize_http_request, http_error_response
from apps.api.dependencies import get_gateway_service
from apps.gateway.service import GatewayService
from core.apps.scope import ScopeContext
from core.protocol.schemas.errors import ProtocolError
from core.workflows.v4_3_serial_video import (
    assert_no_forbidden_text,
    attempt_history,
    build_video_workflow_spec,
    continue_video_downstream,
    run_serial_video_workflow,
    rerun_video_station,
)


router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BRIEF_PATH = REPO_ROOT / "tests" / "fixtures" / "v4_3" / "video_brief" / "launch_brief.md"
ALLOWED_RUNTIME_SOURCES = {"workflow_console", "run_panel", "command_palette", "tui"}
FORBIDDEN_SOURCES = {"agent"}
VIDEO_RUNTIME_BACKING = "v4_3_serial_video_runtime"

_VIDEO_RUNS: dict[str, dict[str, Any]] = {}
_VIDEO_EVIDENCE: dict[str, list[dict[str, Any]]] = {}


@router.post("/runtime/workflows/serial-video/start")
async def start_serial_video_runtime(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        brief_path = _resolve_brief_path(str(body.get("brief_path") or DEFAULT_BRIEF_PATH))
        brief_text = brief_path.read_text(encoding="utf-8")
        simulate_failure_station = body.get("simulate_failure_station")
        run = run_serial_video_workflow(
            brief_text=brief_text,
            brief_path=_display_path(brief_path),
            scope=auth.scope.to_dict(),
            simulate_failure_station=str(simulate_failure_station) if simulate_failure_station else None,
        )
        _VIDEO_RUNS[run["workflow_instance_id"]] = run
        _record_evidence(
            run,
            operation="workflow.instance.start",
            status="succeeded" if run["status"] == "completed" else "failed",
            user_confirmed=True,
            source=str(body.get("source") or ""),
            runtime_result_ref={"type": "workflow_instance", "resource_id": run["workflow_instance_id"], "operation": "workflow.instance.start", "status": run["status"]},
            risk_flags=["dev_local_video_workflow", "deterministic_text_artifacts"],
        )
        response = JSONResponse(_runtime_result(run))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/workflows/serial-video/spec")
async def get_serial_video_spec(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        spec = build_video_workflow_spec()
        assert_no_forbidden_text(spec)
        response = JSONResponse(spec)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}")
async def get_serial_video_instance(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(_runtime_result(run))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/runtime/instances/{workflow_instance_id}/rerun-station")
async def rerun_serial_video_station(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        station_id = str(body.get("station_id") or "")
        rerun = rerun_video_station(run, station_id)
        _VIDEO_RUNS[workflow_instance_id] = rerun
        _record_evidence(
            rerun,
            operation="station.rerun",
            status="succeeded",
            user_confirmed=True,
            source=str(body.get("source") or ""),
            runtime_result_ref={
                "type": "station_run_attempt",
                "resource_id": _latest_attempt_id(rerun, station_id),
                "workflow_instance_id": workflow_instance_id,
                "operation": "station.rerun",
                "status": "completed",
            },
            risk_flags=["station_rerun", "downstream_stale", "dev_local_video_workflow"],
        )
        response = JSONResponse(_runtime_result(rerun))
        add_dev_warning(response, auth)
        return response
    except ValueError as exc:
        return http_error_response(ProtocolError("INVALID_PARAMS", str(exc), {}))
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/runtime/instances/{workflow_instance_id}/continue-downstream")
async def continue_serial_video_downstream(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        if not run.get("downstream_stale"):
            raise ProtocolError("WORKFLOW_INVALID_STATE", "Serial video workflow has no stale downstream stations.", {"workflow_instance_id": workflow_instance_id})
        continued = continue_video_downstream(run)
        _VIDEO_RUNS[workflow_instance_id] = continued
        _record_evidence(
            continued,
            operation="workflow.instance.continue_downstream",
            status="succeeded",
            user_confirmed=True,
            source=str(body.get("source") or ""),
            runtime_result_ref={"type": "workflow_instance", "resource_id": workflow_instance_id, "operation": "workflow.instance.continue_downstream", "status": continued["status"]},
            risk_flags=["downstream_continue", "dev_local_video_workflow"],
        )
        response = JSONResponse(_runtime_result(continued))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}/attempt-history")
async def get_serial_video_attempt_history(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(attempt_history(run))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}/downstream-stale")
async def get_serial_video_downstream_stale(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse({"workflow_instance_id": workflow_instance_id, "stale": run.get("downstream_stale") or [], "redaction_status": "redacted"})
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}/evidence")
async def list_serial_video_evidence(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(_VIDEO_EVIDENCE.get(workflow_instance_id, []))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


def _runtime_result(run: dict[str, Any]) -> dict[str, Any]:
    result = {
        "workflow_instance_id": run["workflow_instance_id"],
        "workflow_template_id": run["workflow_template_id"],
        "workflow_version_id": run["workflow_version_id"],
        "status": run["status"],
        "backed_by": VIDEO_RUNTIME_BACKING,
        "runtime_mode": "dev_local_deterministic_runner",
        "user_confirmed_required": True,
        "agent_mutation_allowed": False,
        "nodes": run["nodes"],
        "artifacts": run.get("artifacts") or [],
        "quality_report": run.get("quality_report"),
        "attempt_history": attempt_history(run),
        "downstream_stale": run.get("downstream_stale") or [],
        "operation_evidence": _VIDEO_EVIDENCE.get(run["workflow_instance_id"], []),
        "redaction_status": "redacted",
    }
    assert_no_forbidden_text(result)
    return result


def _record_evidence(
    run: dict[str, Any],
    *,
    operation: str,
    status: str,
    user_confirmed: bool,
    source: str,
    runtime_result_ref: dict[str, Any],
    risk_flags: list[str],
) -> dict[str, Any]:
    evidence = {
        "evidence_id": f"v43_evidence_{uuid4().hex[:12]}",
        "workflow_instance_id": run["workflow_instance_id"],
        "workflow_template_id": run["workflow_template_id"],
        "operation": operation,
        "operation_type": operation,
        "status": status,
        "correlation_id": f"corr_{uuid4().hex[:12]}",
        "operation_id": f"op_{uuid4().hex[:12]}",
        "idempotency_key": f"idem_{uuid4().hex[:12]}",
        "proposal_id": None,
        "handoff_id": None,
        "user_confirmed": user_confirmed,
        "source": source,
        "risk_flags": risk_flags,
        "policy_decision": "user_confirmed_only",
        "capability_decision": "bff_serial_video_runtime_allowed",
        "runtime_result_ref": {**runtime_result_ref, "workflow_instance_id": run["workflow_instance_id"], "trace_id": f"trace_{uuid4().hex[:8]}"},
        "created_at": datetime.now(UTC).isoformat(),
        "created_by": source or "workflow_console",
        "redaction_status": "redacted",
    }
    assert_no_forbidden_text(evidence)
    _VIDEO_EVIDENCE.setdefault(run["workflow_instance_id"], []).append(evidence)
    return evidence


def _require_run(workflow_instance_id: str, scope: ScopeContext) -> dict[str, Any]:
    run = _VIDEO_RUNS.get(workflow_instance_id)
    if run is None or run.get("scope") != scope.to_dict():
        raise ProtocolError("WORKFLOW_INSTANCE_NOT_FOUND", "Serial video workflow instance not found.", {"workflow_instance_id": workflow_instance_id})
    return run


def _require_confirmed(body: dict[str, Any]) -> None:
    if body.get("user_confirmed") is not True:
        raise ProtocolError("METHOD_FORBIDDEN", "User confirmation is required.", {"field": "user_confirmed"})
    source = str(body.get("source") or "")
    if source in FORBIDDEN_SOURCES or source not in ALLOWED_RUNTIME_SOURCES:
        raise ProtocolError("METHOD_FORBIDDEN", "Operation source is not allowed.", {"source": source})


async def _json_body(request: Request) -> dict[str, Any]:
    body = await request.json()
    if not isinstance(body, dict):
        raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
    return body


def _query_scope_params(request: Request) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for key in ("app_id", "project_id", "workspace_id", "scope_mode"):
        value = request.query_params.get(key)
        if value:
            params[key] = value
    return params


def _resolve_brief_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    path = path.resolve()
    allowed_root = (REPO_ROOT / "tests" / "fixtures" / "v4_3" / "video_brief").resolve()
    if allowed_root not in path.parents and path != allowed_root:
        raise ProtocolError("METHOD_FORBIDDEN", "V4.3 dev/local video workflow can only read the video brief fixture directory.", {"brief_path": value})
    if not path.exists() or path.suffix.lower() != ".md":
        raise ProtocolError("INVALID_PARAMS", "Video brief must be an existing Markdown file.", {"brief_path": value})
    return path


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _latest_attempt_id(run: dict[str, Any], station_id: str) -> str:
    station = next(node for node in run["nodes"] if node["station_id"] == station_id)
    return str((station.get("attempts") or [{}])[-1].get("attempt_id") or station_id)

