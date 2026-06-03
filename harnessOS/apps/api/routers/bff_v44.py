"""V4.4 parallel deliberation BFF routes."""

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
from core.workflows.v4_4_parallel_deliberation import (
    assert_no_forbidden_text,
    attempt_history,
    build_deliberation_spec,
    continue_deliberation_downstream,
    rerun_persona_station,
    run_deliberation_workflow,
)


router = APIRouter()

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_QUESTION_PATH = REPO_ROOT / "tests" / "fixtures" / "v4_4" / "deliberation" / "project_question.md"
ALLOWED_RUNTIME_SOURCES = {"workflow_console", "run_panel", "command_palette", "tui"}
FORBIDDEN_SOURCES = {"agent"}

_RUNS: dict[str, dict[str, Any]] = {}
_EVIDENCE: dict[str, list[dict[str, Any]]] = {}


@router.get("/runtime/workflows/parallel-deliberation/spec")
async def get_parallel_deliberation_spec(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        spec = build_deliberation_spec()
        assert_no_forbidden_text(spec)
        response = JSONResponse(spec)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/runtime/workflows/parallel-deliberation/start")
async def start_parallel_deliberation_runtime(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        question_path = _resolve_question_path(str(body.get("question_path") or DEFAULT_QUESTION_PATH))
        run = run_deliberation_workflow(question_text=question_path.read_text(encoding="utf-8"), question_path=_display_path(question_path), scope=auth.scope.to_dict())
        _RUNS[run["workflow_instance_id"]] = run
        _record_evidence(run, operation="workflow.instance.start", status="succeeded", source=str(body.get("source") or ""), runtime_result_ref={"type": "workflow_instance", "resource_id": run["workflow_instance_id"], "status": run["status"]}, risk_flags=["dev_local_deliberation"])
        response = JSONResponse(_runtime_result(run))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/runtime/instances/{workflow_instance_id}/rerun-station")
async def rerun_parallel_deliberation_station(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        station_id = str(body.get("station_id") or "")
        rerun = rerun_persona_station(run, station_id)
        _RUNS[workflow_instance_id] = rerun
        _record_evidence(rerun, operation="station.rerun", status="succeeded", source=str(body.get("source") or ""), runtime_result_ref={"type": "station_run_attempt", "resource_id": _latest_attempt_id(rerun, station_id), "status": "completed"}, risk_flags=["persona_rerun", "downstream_stale"])
        response = JSONResponse(_runtime_result(rerun))
        add_dev_warning(response, auth)
        return response
    except ValueError as exc:
        return http_error_response(ProtocolError("INVALID_PARAMS", str(exc), {}))
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/runtime/instances/{workflow_instance_id}/continue-downstream")
async def continue_parallel_deliberation_downstream(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        if not run.get("downstream_stale"):
            raise ProtocolError("WORKFLOW_INVALID_STATE", "Parallel deliberation workflow has no stale downstream stations.", {"workflow_instance_id": workflow_instance_id})
        continued = continue_deliberation_downstream(run)
        _RUNS[workflow_instance_id] = continued
        _record_evidence(continued, operation="workflow.instance.continue_downstream", status="succeeded", source=str(body.get("source") or ""), runtime_result_ref={"type": "workflow_instance", "resource_id": workflow_instance_id, "status": continued["status"]}, risk_flags=["deliberation_continue"])
        response = JSONResponse(_runtime_result(continued))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}/attempt-history")
async def get_parallel_deliberation_attempt_history(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(attempt_history(run))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}/evidence")
async def list_parallel_deliberation_evidence(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(_EVIDENCE.get(workflow_instance_id, []))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


def _runtime_result(run: dict[str, Any]) -> dict[str, Any]:
    result = {**run, "attempt_history": attempt_history(run), "operation_evidence": _EVIDENCE.get(run["workflow_instance_id"], []), "redaction_status": "redacted"}
    assert_no_forbidden_text(result)
    return result


def _record_evidence(run: dict[str, Any], *, operation: str, status: str, source: str, runtime_result_ref: dict[str, Any], risk_flags: list[str]) -> None:
    evidence = {
        "evidence_id": f"v44_evidence_{uuid4().hex[:12]}",
        "workflow_instance_id": run["workflow_instance_id"],
        "workflow_template_id": run["workflow_template_id"],
        "operation": operation,
        "operation_type": operation,
        "status": status,
        "correlation_id": f"corr_{uuid4().hex[:12]}",
        "operation_id": f"op_{uuid4().hex[:12]}",
        "idempotency_key": f"idem_{uuid4().hex[:12]}",
        "user_confirmed": True,
        "source": source,
        "risk_flags": risk_flags,
        "policy_decision": "user_confirmed_only",
        "capability_decision": "bff_parallel_deliberation_runtime_allowed",
        "runtime_result_ref": {**runtime_result_ref, "workflow_instance_id": run["workflow_instance_id"], "trace_id": f"trace_{uuid4().hex[:8]}"},
        "created_at": datetime.now(UTC).isoformat(),
        "created_by": source or "workflow_console",
        "redaction_status": "redacted",
    }
    assert_no_forbidden_text(evidence)
    _EVIDENCE.setdefault(run["workflow_instance_id"], []).append(evidence)


def _require_run(workflow_instance_id: str, scope: ScopeContext) -> dict[str, Any]:
    run = _RUNS.get(workflow_instance_id)
    if run is None or run.get("scope") != scope.to_dict():
        raise ProtocolError("WORKFLOW_INSTANCE_NOT_FOUND", "Parallel deliberation workflow instance not found.", {"workflow_instance_id": workflow_instance_id})
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
    return {key: value for key in ("app_id", "project_id", "workspace_id", "scope_mode") if (value := request.query_params.get(key))}


def _resolve_question_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    path = path.resolve()
    allowed_root = (REPO_ROOT / "tests" / "fixtures" / "v4_4" / "deliberation").resolve()
    if allowed_root not in path.parents and path != allowed_root:
        raise ProtocolError("METHOD_FORBIDDEN", "V4.4 dev/local deliberation workflow can only read the deliberation fixture directory.", {"question_path": value})
    if not path.exists() or path.suffix.lower() != ".md":
        raise ProtocolError("INVALID_PARAMS", "Deliberation question must be an existing Markdown file.", {"question_path": value})
    return path


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _latest_attempt_id(run: dict[str, Any], station_id: str) -> str:
    station = next(node for node in run["nodes"] if node["station_id"] == station_id)
    return str((station.get("attempts") or [{}])[-1].get("attempt_id") or station_id)

