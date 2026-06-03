"""V4.6 governed Agent workflow builder BFF routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from apps.api.auth import add_dev_warning, authorize_http_request, http_error_response
from apps.api.dependencies import get_gateway_service
from apps.gateway.service import GatewayService
from core.protocol.schemas.errors import ProtocolError
from core.workflows.v4_6_agent_builder import (
    assert_no_forbidden_text,
    build_handoff,
    create_builder_session,
    explain_workflow_plan,
    generate_workflow_draft,
    propose_debug_repair,
)


router = APIRouter()

_SESSIONS: dict[str, dict[str, Any]] = {}
_PROPOSALS: dict[str, dict[str, Any]] = {}
_EXPLANATIONS: dict[str, dict[str, Any]] = {}
_REPAIRS: dict[str, dict[str, Any]] = {}
_HANDOFFS: dict[str, dict[str, Any]] = {}


@router.post("/agent-builder/sessions")
async def create_agent_builder_session(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        session = create_builder_session(user_request=str(body.get("user_request") or ""), scope=auth.scope.to_dict())
        _SESSIONS[session["agent_builder_session_id"]] = session
        response = JSONResponse(session)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/agent-builder/sessions/{session_id}/draft")
async def draft_agent_builder_workflow(session_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        session = _require_session(session_id)
        proposal = generate_workflow_draft(session)
        _PROPOSALS[proposal["proposal_id"]] = proposal
        response = JSONResponse(proposal)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/agent-builder/sessions/{session_id}/explain/{proposal_id}")
async def explain_agent_builder_workflow(session_id: str, proposal_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        session = _require_session(session_id)
        proposal = _require_proposal(proposal_id)
        explanation = explain_workflow_plan(session, proposal)
        _EXPLANATIONS[explanation["explanation_id"]] = explanation
        response = JSONResponse(explanation)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/agent-builder/sessions/{session_id}/debug-repair")
async def debug_repair_agent_builder_workflow(session_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        session = _require_session(session_id)
        repair = propose_debug_repair(session, failed_station_id=str(body.get("failed_station_id") or "markdown_parse"))
        _REPAIRS[repair["repair_proposal_id"]] = repair
        response = JSONResponse(repair)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/agent-builder/sessions/{session_id}/handoff")
async def handoff_agent_builder_workflow(session_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await _json_body(request)
        auth = await authorize_http_request(request, gateway=gateway, params=_query_scope_params(request), capability="workflows.read")
        session = _require_session(session_id)
        proposal_id = str(body.get("proposal_id") or "")
        if proposal_id not in _PROPOSALS and proposal_id not in _REPAIRS:
            raise ProtocolError("PROPOSAL_NOT_FOUND", "Agent builder proposal not found.", {"proposal_id": proposal_id})
        handoff = build_handoff(session, proposal_id=proposal_id, target_panel=str(body.get("target_panel") or "editing_panel"))
        _HANDOFFS[handoff["handoff_id"]] = handoff
        response = JSONResponse(handoff)
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


def _require_session(session_id: str) -> dict[str, Any]:
    session = _SESSIONS.get(session_id)
    if session is None:
        raise ProtocolError("SESSION_NOT_FOUND", "Agent builder session not found.", {"session_id": session_id})
    assert_no_forbidden_text(session)
    return session


def _require_proposal(proposal_id: str) -> dict[str, Any]:
    proposal = _PROPOSALS.get(proposal_id)
    if proposal is None:
        raise ProtocolError("PROPOSAL_NOT_FOUND", "Agent builder proposal not found.", {"proposal_id": proposal_id})
    assert_no_forbidden_text(proposal)
    return proposal


async def _json_body(request: Request) -> dict[str, Any]:
    body = await request.json()
    if not isinstance(body, dict):
        raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
    if body.get("source") == "agent":
        raise ProtocolError("METHOD_FORBIDDEN", "Agent builder source cannot execute mutations.", {"source": "agent"})
    return body


def _query_scope_params(request: Request) -> dict[str, Any]:
    return {key: value for key in ("app_id", "project_id", "workspace_id", "scope_mode") if (value := request.query_params.get(key))}

