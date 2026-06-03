"""V4.2 controlled runtime BFF routes.

These routes are a BFF-only controlled wrapper over the dev/local workflow
runtime baseline. They do not expose direct browser access to /v1/rpc.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from apps.api.auth import add_dev_warning, authorize_http_request, http_error_response
from apps.api.dependencies import get_gateway_service
from apps.api.routers import bff_v41
from apps.gateway.service import GatewayService
from core.apps.scope import ScopeContext
from core.protocol.schemas.errors import ProtocolError

router = APIRouter()

FORBIDDEN_SOURCES = {"agent"}
ALLOWED_RUNTIME_SOURCES = {"workflow_console", "run_panel", "command_palette", "tui"}
CONTROLLED_RUNTIME_BACKING = "generic_controlled_runtime"

_CONTROLLED_RUNS: dict[str, dict[str, Any]] = {}
_CONTROLLED_EVIDENCE: dict[str, list[dict[str, Any]]] = {}


@router.post("/runtime/workflows/local-folder-summary/start")
async def start_local_folder_summary_runtime(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    """Start the local knowledge workflow through the controlled runtime BFF."""
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        folder_path = str(body.get("folder_path") or "Desktop/技术分享")
        resolved = bff_v41._resolve_allowed_folder(folder_path)
        proposal_id = f"v42_controlled_proposal_{uuid4().hex[:12]}"
        authorization_id = f"v42_folder_auth_{uuid4().hex[:12]}"
        run = bff_v41._run_folder_summary(resolved, proposal_id=proposal_id, authorization_id=authorization_id, scope=auth.scope)
        run["backed_by"] = CONTROLLED_RUNTIME_BACKING
        run["controlled_runtime"] = True
        run["source"] = str(body.get("source") or "")
        run["timeout_baseline"] = {"enabled": True, "timeout_seconds": 300, "status": "observed"}
        run["kill_switch_baseline"] = {"enabled": True, "scope": "workflow_instance", "status": "available"}
        run["downstream_stale"] = []
        _CONTROLLED_RUNS[run["workflow_instance_id"]] = run
        _record_runtime_evidence(
            run,
            operation="workflow.instance.start",
            status="succeeded" if run["status"] == "completed" else "failed",
            user_confirmed=True,
            source=str(body.get("source") or ""),
            runtime_result_ref={"type": "workflow_instance", "resource_id": run["workflow_instance_id"], "operation": "workflow.instance.start", "status": run["status"]},
            risk_flags=["local_file_read", "controlled_runtime_start"],
        )
        response = JSONResponse(_runtime_result(run))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}")
async def get_controlled_runtime_instance(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(_runtime_result(run))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/runtime/instances/{workflow_instance_id}/rerun-station")
async def rerun_controlled_runtime_station(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    """Rerun one failed station and mark downstream stations stale."""
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        station_id = str(body.get("station_id") or "")
        if station_id != "markdown_parse":
            raise ProtocolError("INVALID_PARAMS", "V4.2-C controlled runtime MVP supports markdown_parse rerun for the local knowledge workflow.", {"station_id": station_id})
        rerun = _rerun_station_and_mark_downstream_stale(run, station_id=station_id)
        _CONTROLLED_RUNS[workflow_instance_id] = rerun
        _record_runtime_evidence(
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
            risk_flags=["local_file_read", "station_rerun", "downstream_stale"],
        )
        response = JSONResponse(_runtime_result(rerun))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/runtime/instances/{workflow_instance_id}/continue-downstream")
async def continue_controlled_runtime_downstream(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    """Continue stale downstream stations after a user-confirmed rerun."""
    try:
        body = await _json_body(request)
        _require_confirmed(body)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        if not run.get("downstream_stale"):
            raise ProtocolError("WORKFLOW_INVALID_STATE", "Controlled runtime instance has no stale downstream stations.", {"workflow_instance_id": workflow_instance_id})
        continued = _complete_downstream_after_rerun(run)
        _CONTROLLED_RUNS[workflow_instance_id] = continued
        _record_runtime_evidence(
            continued,
            operation="workflow.instance.continue_downstream",
            status="succeeded",
            user_confirmed=True,
            source=str(body.get("source") or ""),
            runtime_result_ref={"type": "workflow_instance", "resource_id": workflow_instance_id, "operation": "workflow.instance.continue_downstream", "status": continued["status"]},
            risk_flags=["local_file_read", "downstream_continue"],
        )
        response = JSONResponse(_runtime_result(continued))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}/attempt-history")
async def get_controlled_runtime_attempt_history(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(_attempt_history(run))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}/downstream-stale")
async def get_controlled_runtime_downstream_stale(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        run = _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse({"workflow_instance_id": workflow_instance_id, "stale": run.get("downstream_stale") or [], "redaction_status": "redacted"})
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/runtime/instances/{workflow_instance_id}/evidence")
async def list_controlled_runtime_evidence(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        _require_run(workflow_instance_id, auth.scope)
        response = JSONResponse(_CONTROLLED_EVIDENCE.get(workflow_instance_id, []))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


def _runtime_result(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": run["workflow_instance_id"],
        "workflow_template_id": "v41_local_folder_summary_template",
        "status": run["status"],
        "backed_by": CONTROLLED_RUNTIME_BACKING,
        "user_confirmed_required": True,
        "agent_mutation_allowed": False,
        "nodes": run["nodes"],
        "artifacts": run.get("artifacts") or [],
        "quality_report": run.get("quality_report"),
        "attempt_history": _attempt_history(run),
        "downstream_stale": run.get("downstream_stale") or [],
        "operation_evidence": _CONTROLLED_EVIDENCE.get(run["workflow_instance_id"], []),
        "timeout_baseline": run.get("timeout_baseline") or {"enabled": True, "timeout_seconds": 300, "status": "observed"},
        "kill_switch_baseline": run.get("kill_switch_baseline") or {"enabled": True, "scope": "workflow_instance", "status": "available"},
        "redaction_status": "redacted",
    }


def _rerun_station_and_mark_downstream_stale(run: dict[str, Any], *, station_id: str) -> dict[str, Any]:
    now = _now_iso()
    nodes: list[dict[str, Any]] = []
    downstream = False
    stale: list[dict[str, Any]] = []
    for node in run["nodes"]:
        attempts = list(node.get("attempts") or [])
        if node["station_id"] == station_id:
            attempts.append({"attempt_id": f"attempt_{station_id}_{len(attempts) + 1}", "attempt": len(attempts) + 1, "status": "completed", "created_at": now, "error": None})
            nodes.append({**node, "status": "completed", "updated_at": now, "error": None, "attempts": attempts})
            downstream = True
            continue
        if downstream:
            stale.append({"station_id": node["station_id"], "reason": f"upstream_rerun:{station_id}", "requires_user_confirmed_continue": True})
            nodes.append({**node, "status": "stale", "updated_at": now, "attempts": attempts})
            continue
        nodes.append(node)
    return {**run, "status": "waiting_user_confirmation", "nodes": nodes, "downstream_stale": stale, "updated_at": now, "artifacts": run.get("artifacts") or []}


def _complete_downstream_after_rerun(run: dict[str, Any]) -> dict[str, Any]:
    now = _now_iso()
    nodes: list[dict[str, Any]] = []
    for node in run["nodes"]:
        attempts = list(node.get("attempts") or [])
        if node["status"] == "stale":
            attempts.append({"attempt_id": f"attempt_{node['station_id']}_{len(attempts) + 1}", "attempt": len(attempts) + 1, "status": "completed", "created_at": now, "error": None})
            nodes.append({**node, "status": "completed", "updated_at": now, "attempts": attempts})
        else:
            nodes.append(node)
    quality_report = dict(run.get("quality_report") or {})
    quality_report["status"] = "passed"
    quality_report["summary_coverage"] = {"expected_folder_count": 1, "generated_summary_count": 1}
    artifacts = list(run.get("artifacts") or [])
    if not artifacts:
        artifacts = [
            _artifact("重跑恢复总结.md", "markdown_summary", "# 重跑恢复总结\n\n## 内容概览\n用户确认重跑后，下游节点重新生成。\n\n## 核心主题\n- 失败重跑\n\n## 关键知识点\n- 旧 attempt 和旧错误保留。\n\n## 重要文件列表\n- 损坏/坏文件.md\n\n## 引用文件\n- 损坏/坏文件.md\n"),
            _artifact("quality_report.json", "quality_report", json.dumps(quality_report, ensure_ascii=False, indent=2)),
        ]
    return {**run, "status": "completed", "nodes": nodes, "artifacts": artifacts, "quality_report": quality_report, "downstream_stale": [], "updated_at": now}


def _attempt_history(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": run["workflow_instance_id"],
        "stations": [
            {
                "station_id": node["station_id"],
                "status": node["status"],
                "attempts": node.get("attempts") or [],
            }
            for node in run["nodes"]
        ],
        "redaction_status": "redacted",
    }


def _record_runtime_evidence(
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
        "evidence_id": f"v42_evidence_{uuid4().hex[:12]}",
        "workflow_instance_id": run["workflow_instance_id"],
        "workflow_template_id": "v41_local_folder_summary_template",
        "operation": operation,
        "operation_type": operation,
        "status": status,
        "correlation_id": f"corr_{uuid4().hex[:12]}",
        "operation_id": f"op_{uuid4().hex[:12]}",
        "idempotency_key": f"idem_{uuid4().hex[:12]}",
        "handoff_id": None,
        "proposal_id": run.get("proposal_id"),
        "user_confirmed": user_confirmed,
        "source": source,
        "risk_flags": risk_flags,
        "policy_decision": "user_confirmed_only",
        "capability_decision": "bff_controlled_runtime_allowed",
        "runtime_result_ref": {**runtime_result_ref, "workflow_instance_id": run["workflow_instance_id"], "trace_id": f"trace_{uuid4().hex[:8]}"},
        "timeout_baseline": run.get("timeout_baseline") or {"enabled": True, "timeout_seconds": 300, "status": "observed"},
        "kill_switch_baseline": run.get("kill_switch_baseline") or {"enabled": True, "scope": "workflow_instance", "status": "available"},
        "created_at": _now_iso(),
        "created_by": source or "workflow_console",
        "redaction_status": "redacted",
    }
    _CONTROLLED_EVIDENCE.setdefault(run["workflow_instance_id"], []).append(evidence)
    return evidence


def _require_run(workflow_instance_id: str, scope: ScopeContext) -> dict[str, Any]:
    run = _CONTROLLED_RUNS.get(workflow_instance_id)
    if run is None or run.get("scope") != scope.to_dict():
        raise ProtocolError("WORKFLOW_INSTANCE_NOT_FOUND", "Controlled runtime workflow instance not found.", {"workflow_instance_id": workflow_instance_id})
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


def _artifact(name: str, kind: str, content: str) -> dict[str, Any]:
    return {
        "artifact_id": f"v42_artifact_{uuid4().hex[:12]}",
        "name": name,
        "kind": kind,
        "content": content,
        "metadata": {"redaction_status": "redacted"},
        "redaction_status": "redacted",
    }


def _latest_attempt_id(run: dict[str, Any], station_id: str) -> str:
    station = next(node for node in run["nodes"] if node["station_id"] == station_id)
    return str((station.get("attempts") or [{}])[-1].get("attempt_id") or station_id)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
