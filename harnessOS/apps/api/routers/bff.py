"""Workflow Console BFF structured routes for V4.0-A2."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse

from apps.api.auth import add_dev_warning, authorize_http_request, http_error_response
from apps.api.dependencies import get_gateway_service
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.apps.scope import ScopeContext
from core.protocol.event_bridge import (
    collect_event_envelopes,
    ensure_channel_capabilities,
    heartbeat_frame,
    normalize_event_channels,
    read_event_cursor,
    sse_frame,
)
from core.protocol.schemas.errors import ProtocolError

router = APIRouter()

SENSITIVE_KEY_PARTS = (
    "token",
    "authorization",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
)


@router.get("/workflows")
async def list_workflows(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.template.list", params)
        response = JSONResponse(_redact([_workflow_summary(item) for item in result.get("templates", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}")
async def get_workflow(workflow_template_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.template.get", params)
        response = JSONResponse(_redact(_workflow_summary(result["template"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/versions")
async def list_workflow_versions(workflow_template_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.version.list", params)
        response = JSONResponse(_redact([_version_summary(item) for item in result.get("versions", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances")
async def list_instances(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.instance.list", params)
        response = JSONResponse(_redact([_instance_summary(item) for item in result.get("workflow_instances", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/status")
async def get_instance_status(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.instance.status", params)
        response = JSONResponse(_redact(_status_dto(result["status"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/board")
async def get_instance_board(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="board.read")
        result = await _rpc(gateway, "workflow.board.get", params)
        response = JSONResponse(_redact(result["board"]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/quality")
async def list_instance_quality(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.read")
        result = await _rpc(gateway, "quality.evaluation.list", params)
        response = JSONResponse(_redact([_quality_dto(item) for item in result.get("evaluations", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/quality/{evaluation_id}")
async def get_instance_quality(
    workflow_instance_id: str,
    evaluation_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "evaluation_id": evaluation_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.read")
        result = await _rpc(gateway, "quality.evaluation.get", params)
        evaluation = result["evaluation"]
        _ensure_quality_in_instance(evaluation, workflow_instance_id)
        response = JSONResponse(_redact(_quality_dto(evaluation)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/approvals")
async def list_instance_approvals(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="approvals.read")
        gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        result = await _rpc(gateway, "approval.list", params)
        approvals = [
            _approval_dto(approval)
            for approval in result.get("approvals", [])
            if _approval_workflow_binding(approval).get("workflow_instance_id") == workflow_instance_id
        ]
        response = JSONResponse(_redact(approvals))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/approvals/{approval_id}/respond")
async def respond_instance_approval(
    workflow_instance_id: str,
    approval_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        if body.get("user_confirmed") is not True or body.get("source") != "approval_panel":
            raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Approval response requires explicit user confirmation.", {"source": body.get("source")})
        decision = body.get("decision")
        if decision not in {"approve", "reject"}:
            raise ProtocolError("APPROVAL_INVALID_DECISION", "decision must be approve or reject", {"decision": decision})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "approval_id": approval_id,
            "decision": decision,
            "reason": body.get("reason"),
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="approvals")
        approval = gateway.approval_store.get_approval(approval_id)
        _ensure_approval_in_instance(approval, workflow_instance_id)
        result = await _rpc(gateway, "approval.respond", params)
        response = JSONResponse(
            _redact(
                _operation_result(
                    "approval.respond",
                    status=str(result.get("status") or ""),
                    resource=_approval_dto(result.get("approval") or {}),
                    idempotent=bool(result.get("idempotent")),
                    workflow_side_effect=result.get("workflow_side_effect"),
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except KeyError as exc:
        return http_error_response(ProtocolError("APPROVAL_NOT_FOUND", str(exc), {"approval_id": approval_id}))
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/context")
async def get_instance_context(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_context.read")
        result = await _rpc(gateway, "workflow.context.get", params)
        response = JSONResponse(_redact(_context_dto(result["context"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/context/update")
async def update_instance_context(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        if body.get("op") != "set":
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Only path-based set is supported.", {"op": body.get("op")})
        path = str(body.get("path") or "")
        if not path.startswith("business.") or path == "business.":
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Only business.* context paths can be updated.", {"path": path})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "path": path,
            "value": body.get("value"),
            "expected_revision": body.get("expected_revision"),
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_context.write")
        result = await _rpc(gateway, "workflow.context.update", params)
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.context.update",
                    status="updated",
                    resource=_context_dto(result["context"]),
                    trace_id=result.get("trace_id"),
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/business-events")
async def emit_instance_business_event(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        event_type = str(body.get("event_type") or body.get("type") or "")
        for denied_prefix in ("meeting.", "knowledge.", "video."):
            if event_type.startswith(denied_prefix):
                raise ProtocolError("BUSINESS_EVENT_INVALID", "Business event cannot use a core business canonical namespace.", {"event_type": event_type})
        if not event_type.startswith("business.") or event_type == "business.*":
            raise ProtocolError("BUSINESS_EVENT_INVALID", "event_type must be a concrete business.* event.", {"event_type": event_type})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "event": {
                "event_id": body.get("event_id"),
                "idempotency_key": body.get("idempotency_key"),
                "type": event_type,
                "payload": body.get("payload") if isinstance(body.get("payload"), dict) else {},
                "workflow_instance_id": workflow_instance_id,
            },
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="business_events.write")
        binding = body.get("binding")
        if isinstance(binding, dict):
            if not _auth_has_capability(auth, "workflow_context.write"):
                raise ProtocolError(
                    "CAPABILITY_DENIED",
                    "Business event binding requires workflow_context.write capability.",
                    {"capability": "workflow_context.write"},
                )
            existing_bindings = gateway.workflow_repository.list_business_event_bindings(
                scope=auth.scope,
                workflow_instance_id=workflow_instance_id,
                event_type=event_type,
            )
            has_binding = any(
                existing.target_path == binding.get("target_path") and existing.payload_path == binding.get("payload_path")
                for existing in existing_bindings
            )
            bind_params = {
                **params,
                "binding": {
                    "binding_id": binding.get("binding_id") or f"bff_{workflow_instance_id}_{event_type}".replace(".", "_"),
                    "workflow_instance_id": workflow_instance_id,
                    "event_type": event_type,
                    "target_path": binding.get("target_path"),
                    "payload_path": binding.get("payload_path"),
                    "mode": binding.get("mode") or "set",
                    "enabled": binding.get("enabled", True),
                },
            }
            if not has_binding:
                await _rpc(gateway, "business.event.bind", bind_params)
        result = await _rpc(gateway, "business.event.emit", params)
        response = JSONResponse(
            _redact(
                _operation_result(
                    "business.event.emit",
                    status="received",
                    resource={"event": _business_event_dto(result.get("event") or {}), "context": _context_dto(result["context"])},
                    idempotent=bool(result.get("idempotent")),
                    trace_id=result.get("trace_id"),
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/patches/propose")
async def propose_workflow_patch(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        patch = body.get("patch") if isinstance(body.get("patch"), dict) else body
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "patch": patch}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        result = await _rpc(gateway, "workflow.patch.propose", params)
        response = JSONResponse(_redact(_patch_proposal_dto(result["patch"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff")
async def get_workflow_patch_diff(
    workflow_template_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        _ensure_patch_in_template(gateway, workflow_patch_id, workflow_template_id, auth.scope)
        result = await _rpc(gateway, "workflow.patch.diff", params)
        response = JSONResponse(_redact(_patch_diff_dto(result["diff"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/patches/{workflow_patch_id}/diff")
async def get_instance_patch_diff(
    workflow_instance_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        _ensure_patch_in_instance(gateway, workflow_patch_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "workflow.patch.diff", params)
        response = JSONResponse(_redact(_patch_diff_dto(result["diff"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/stations/{station_run_id}/outputs")
async def list_station_outputs(station_run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "station_run_id": station_run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="stations.read")
        result = await _rpc(gateway, "station.output.list", params)
        response = JSONResponse(_redact(result.get("artifacts", [])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/stations/{station_run_id}/outputs")
async def list_instance_station_outputs(
    workflow_instance_id: str,
    station_run_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "station_run_id": station_run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="stations.read")
        _ensure_station_run_in_instance(gateway, station_run_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "station.output.list", params)
        response = JSONResponse(_redact(result.get("artifacts", [])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/artifacts/{artifact_id}/metadata")
async def get_artifact_metadata(artifact_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _artifact_metadata_response(artifact_id, request, gateway, workflow_instance_id=None)


@router.get("/instances/{workflow_instance_id}/artifacts/{artifact_id}/metadata")
async def get_instance_artifact_metadata(
    workflow_instance_id: str,
    artifact_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    return await _artifact_metadata_response(artifact_id, request, gateway, workflow_instance_id=workflow_instance_id)


@router.get("/artifacts/{artifact_id}/lineage")
async def get_artifact_lineage(artifact_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _artifact_lineage_response(artifact_id, request, gateway, workflow_instance_id=None)


@router.get("/instances/{workflow_instance_id}/artifacts/{artifact_id}/lineage")
async def get_instance_artifact_lineage(
    workflow_instance_id: str,
    artifact_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    return await _artifact_lineage_response(artifact_id, request, gateway, workflow_instance_id=workflow_instance_id)


@router.get("/events/subscribe")
async def subscribe_events(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    params = dict(request.query_params)
    try:
        channels = normalize_event_channels(params.get("channels"))
        auth_params = dict(params)
        auth = await authorize_http_request(request, gateway=gateway, params=auth_params, capability="events")
        capabilities = tuple(auth_params.get("_auth_capabilities") or ())
        ensure_channel_capabilities(channels, capabilities)
        cursor = request.headers.get("last-event-id") or params.get("cursor") or params.get("last_event_id")
        start_sequence = read_event_cursor(cursor, auth.scope)
    except ProtocolError as exc:
        return http_error_response(exc)

    filters = {
        key: params.get(key)
        for key in ("workflow_instance_id", "workflow_patch_id", "approval_id", "artifact_id", "job_id", "trace_id")
        if params.get(key)
    }
    follow = _truthy(params.get("follow"))
    heartbeat_interval = _float_param(params.get("heartbeat_interval"), default=15.0)
    max_heartbeats = _int_param(params.get("max_heartbeats"))

    async def event_source():
        last_sequence = start_sequence
        sent_keys: set[tuple[str, str]] = set()
        events, last_sequence = _collect_unsent_events(
            gateway,
            scope=auth.scope,
            channels=channels,
            filters=filters,
            last_sequence=last_sequence,
            sent_keys=sent_keys,
        )
        for event in events:
            yield sse_frame(_redact(event))
        if not follow:
            return
        sent_heartbeats = 0
        while True:
            await asyncio.sleep(max(heartbeat_interval, 0.01))
            events, last_sequence = _collect_unsent_events(
                gateway,
                scope=auth.scope,
                channels=channels,
                filters=filters,
                last_sequence=last_sequence,
                sent_keys=sent_keys,
            )
            if events:
                for event in events:
                    yield sse_frame(_redact(event))
                continue
            yield heartbeat_frame()
            sent_heartbeats += 1
            if max_heartbeats is not None and sent_heartbeats >= max_heartbeats:
                return

    response = StreamingResponse(event_source(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    add_dev_warning(response, auth)
    return response


async def _artifact_metadata_response(
    artifact_id: str,
    request: Request,
    gateway: GatewayService,
    *,
    workflow_instance_id: str | None,
) -> Any:
    try:
        params = {**_query_scope_params(request), "artifact_id": artifact_id}
        if workflow_instance_id:
            params["workflow_instance_id"] = workflow_instance_id
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="artifacts.read")
        if workflow_instance_id:
            _ensure_artifact_in_instance(gateway, artifact_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "artifact.read_metadata", params)
        response = JSONResponse(_redact(result["artifact"]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


async def _artifact_lineage_response(
    artifact_id: str,
    request: Request,
    gateway: GatewayService,
    *,
    workflow_instance_id: str | None,
) -> Any:
    try:
        params = {**_query_scope_params(request), "artifact_id": artifact_id}
        if workflow_instance_id:
            params["workflow_instance_id"] = workflow_instance_id
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="artifacts.read")
        if workflow_instance_id:
            _ensure_artifact_in_instance(gateway, artifact_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "artifact.lineage", params)
        response = JSONResponse(_redact(result))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


async def _rpc(gateway: GatewayService, method: str, params: dict[str, Any]) -> dict[str, Any]:
    response = await gateway.handle_rpc(RpcRequest(id=method, method=method, params=params))
    if response.error is not None:
        raise ProtocolError(response.error.code, response.error.message, response.error.data or {})
    return response.result or {}


def _workflow_summary(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_template_id": template.get("workflow_template_id"),
        "name": template.get("name"),
        "latest_version_id": template.get("latest_published_version_id"),
        "status": template.get("status"),
    }


def _version_summary(version: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_version_id": version.get("workflow_version_id"),
        "workflow_template_id": version.get("workflow_template_id"),
        "version": version.get("version"),
    }


def _instance_summary(instance: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": instance.get("workflow_instance_id"),
        "workflow_template_id": instance.get("workflow_template_id"),
        "workflow_version_id": instance.get("workflow_version_id"),
        "status": instance.get("status"),
    }


def _status_dto(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": status.get("workflow_instance_id"),
        "status": status.get("status"),
        "current_station_ids": status.get("current_station_ids") or [],
        "station_counts": status.get("station_run_status_counts") or {},
        "job_counts": status.get("job_status_counts") or {},
        "artifact_count": status.get("artifact_count") or 0,
        "quality_count": status.get("quality_evaluation_count") or 0,
    }


def _quality_dto(evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "evaluation_id": evaluation.get("evaluation_id"),
        "workflow_instance_id": evaluation.get("workflow_instance_id"),
        "station_run_id": evaluation.get("station_run_id"),
        "artifact_id": evaluation.get("artifact_id"),
        "rubric_id": evaluation.get("rubric_id"),
        "evaluator_type": evaluation.get("evaluator_type"),
        "score": evaluation.get("score"),
        "status": evaluation.get("status"),
        "issues": evaluation.get("issues") or [],
        "suggestions": evaluation.get("suggestions") or [],
        "created_at": evaluation.get("created_at"),
    }


def _approval_dto(approval: dict[str, Any]) -> dict[str, Any]:
    binding = _approval_workflow_binding(approval)
    return {
        "approval_id": approval.get("approval_id"),
        "workflow_instance_id": binding.get("workflow_instance_id"),
        "station_run_id": binding.get("station_run_id"),
        "station_id": binding.get("station_id"),
        "status": approval.get("status"),
        "action": approval.get("action"),
        "request_summary": approval.get("request_summary"),
        "risk_level": approval.get("risk_level"),
        "decision_reason": approval.get("decision_reason"),
        "active": binding.get("active", True),
        "inactive_reason": binding.get("inactive_reason"),
        "created_at": approval.get("created_at"),
        "decided_at": approval.get("decided_at"),
    }


def _context_dto(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": context.get("workflow_instance_id"),
        "revision": context.get("revision"),
        "business": context.get("business") if isinstance(context.get("business"), dict) else {},
        "updated_at": context.get("updated_at"),
        "trace_id": context.get("trace_id"),
    }


def _business_event_dto(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("event_id"),
        "idempotency_key": event.get("idempotency_key"),
        "type": event.get("type"),
        "workflow_instance_id": event.get("workflow_instance_id"),
        "payload": event.get("payload") if isinstance(event.get("payload"), dict) else {},
    }


def _patch_diff_dto(diff: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_patch_id": diff.get("workflow_patch_id"),
        "workflow_draft_id": diff.get("workflow_draft_id"),
        "base_revision": diff.get("base_revision"),
        "operation": diff.get("operation"),
        "target": diff.get("target") if isinstance(diff.get("target"), dict) else {},
        "before_summary": diff.get("before_summary"),
        "after_summary": diff.get("after_summary"),
        "risk_flags": diff.get("risk_flags") if isinstance(diff.get("risk_flags"), list) else [],
        "requires_approval": bool(diff.get("requires_approval")),
        "redacted": True,
    }


def _patch_proposal_dto(patch: dict[str, Any]) -> dict[str, Any]:
    metadata = patch.get("metadata") if isinstance(patch.get("metadata"), dict) else {}
    return {
        "workflow_patch_id": patch.get("workflow_patch_id"),
        "workflow_template_id": patch.get("workflow_template_id"),
        "workflow_draft_id": patch.get("workflow_draft_id"),
        "operation": patch.get("operation"),
        "status": patch.get("status"),
        "proposed_by": patch.get("proposed_by"),
        "requires_approval": bool(metadata.get("requires_approval") or patch.get("requires_approval")),
        "risk_flags": metadata.get("risk_flags") if isinstance(metadata.get("risk_flags"), list) else patch.get("risk_flags", []),
    }


def _operation_result(
    operation: str,
    *,
    status: str,
    resource: Any,
    trace_id: Any = None,
    idempotent: bool = False,
    workflow_side_effect: Any = None,
) -> dict[str, Any]:
    result = {
        "operation": operation,
        "status": status,
        "resource": resource,
        "idempotent": idempotent,
    }
    if trace_id:
        result["trace_id"] = trace_id
    if workflow_side_effect is not None:
        result["workflow_side_effect"] = workflow_side_effect
    return result


def _approval_workflow_binding(approval: dict[str, Any]) -> dict[str, Any]:
    metadata = approval.get("metadata") if isinstance(approval.get("metadata"), dict) else {}
    binding = metadata.get("workflow_binding") if isinstance(metadata.get("workflow_binding"), dict) else {}
    return binding


def _ensure_approval_in_instance(approval: dict[str, Any], workflow_instance_id: str) -> None:
    if _approval_workflow_binding(approval).get("workflow_instance_id") != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Approval does not belong to workflow instance.", {"resource": "approval_id"})


def _ensure_quality_in_instance(evaluation: dict[str, Any], workflow_instance_id: str) -> None:
    if evaluation.get("workflow_instance_id") != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Quality evaluation does not belong to workflow instance.", {"resource": "evaluation_id"})


def _ensure_station_run_in_instance(gateway: GatewayService, station_run_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    station_run = gateway.workflow_repository.get_station_run(station_run_id, scope=scope)
    if station_run.workflow_instance_id != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Station run does not belong to workflow instance.", {"resource": "station_run_id"})


def _ensure_artifact_in_instance(gateway: GatewayService, artifact_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
    if artifact_id in set(instance.artifact_ids):
        return
    station_runs = gateway.workflow_repository.list_station_runs(workflow_instance_id, scope=scope)
    for run in station_runs:
        if artifact_id in set(run.input_artifact_ids) or artifact_id in set(run.output_artifact_ids):
            return
    raise ProtocolError("SCOPE_MISMATCH", "Artifact does not belong to workflow instance.", {"resource": "artifact_id"})


def _ensure_patch_in_template(gateway: GatewayService, workflow_patch_id: str, workflow_template_id: str, scope: ScopeContext) -> None:
    patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
    if patch.workflow_template_id != workflow_template_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not belong to workflow template.", {"resource": "workflow_patch_id"})


def _ensure_patch_in_instance(gateway: GatewayService, workflow_patch_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
    patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
    if patch.workflow_template_id != instance.workflow_template_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not belong to workflow instance template.", {"resource": "workflow_patch_id"})
    metadata = patch.metadata if isinstance(patch.metadata, dict) else {}
    bound_instance_id = metadata.get("workflow_instance_id")
    if bound_instance_id != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch is not bound to this workflow instance.", {"resource": "workflow_patch_id"})


def _auth_has_capability(auth: Any, capability: str) -> bool:
    if getattr(auth, "dev_mode", False):
        return True
    claims = getattr(auth, "claims", None)
    capabilities = getattr(claims, "capabilities", ()) if claims is not None else ()
    return capability in set(capabilities)


def _collect_unsent_events(
    gateway: GatewayService,
    *,
    scope: ScopeContext,
    channels: list[str],
    filters: dict[str, Any],
    last_sequence: int,
    sent_keys: set[tuple[str, str]],
) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    current_sequence = last_sequence
    for event in collect_event_envelopes(gateway, scope=scope, channels=channels, filters=filters):
        sequence = read_event_cursor(event["cursor"], scope)
        key = (str(event.get("channel") or ""), str(event.get("event_id") or ""))
        if sequence > current_sequence and key not in sent_keys:
            events.append(event)
            current_sequence = max(current_sequence, sequence)
            sent_keys.add(key)
    return events, current_sequence


def _query_scope_params(request: Request) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for key in ("app_id", "project_id", "workspace_id"):
        value = request.query_params.get(key)
        if value:
            params[key] = value
    return params


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lower = str(key).lower()
            if any(part in lower for part in SENSITIVE_KEY_PARTS):
                continue
            redacted[key] = _redact(item)
        return redacted
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str) and ("Bearer " in value or "subscription_token" in value or "capability_token" in value):
        return "[redacted]"
    return value


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _float_param(value: Any, *, default: float) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("INVALID_PARAMS", "heartbeat_interval must be numeric.", {"field": "heartbeat_interval"}) from exc


def _int_param(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("INVALID_PARAMS", "max_heartbeats must be an integer.", {"field": "max_heartbeats"}) from exc
