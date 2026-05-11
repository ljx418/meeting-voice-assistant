"""Run endpoints backed by the harnessOS gateway service."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from apps.api.auth import (
    add_dev_warning,
    authorize_http_request,
    authorize_rpc_request,
    http_error_response,
    protocol_error_response,
)
from apps.api.dependencies import get_gateway_service
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.protocol.schemas.errors import ProtocolError

router = APIRouter()


class RunRequest(BaseModel):
    """Request to execute one agent run."""

    input: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    model: Optional[str] = None
    domain: Optional[str] = None
    app_id: Optional[str] = None
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    scope: Optional[dict[str, Any]] = None
    close_session: bool = False

    def scope_params(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.scope is not None:
            payload["scope"] = dict(self.scope)
        if self.app_id is not None:
            payload["app_id"] = self.app_id
        if self.project_id is not None:
            payload["project_id"] = self.project_id
        if self.workspace_id is not None:
            payload["workspace_id"] = self.workspace_id
        return payload


@router.post("/runs")
async def create_run(
    request: RunRequest,
    http_request: Request,
    response: Response,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    """Run one turn and return the aggregated result."""
    auth_params = request.scope_params()
    if request.session_id:
        auth_params["session_id"] = request.session_id
    try:
        auth = await authorize_http_request(http_request, gateway=gateway, params=auth_params, capability="turns")
    except ProtocolError as exc:
        return http_error_response(exc)
    add_dev_warning(response, auth)
    await gateway.initialize({})
    session_id = request.session_id
    if session_id:
        await gateway.session_resume({"session_id": session_id, **auth_params})
    else:
        session_params = {"model": request.model, **auth_params} if request.model else dict(auth_params)
        session = await gateway.session_start(session_params)
        session_id = str(session["session_id"])

    result = await gateway.turn_start(
        {
            "session_id": session_id,
            "input": request.input,
            "domain": request.domain,
            **auth_params,
        }
    )
    if request.close_session:
        await gateway.session_close({"session_id": session_id})
    return result


@router.post("/runs/stream")
async def stream_run(
    request: RunRequest,
    http_request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    """Run one turn and stream normalized protocol events as SSE."""
    auth_params = request.scope_params()
    if request.session_id:
        auth_params["session_id"] = request.session_id
    try:
        auth = await authorize_http_request(http_request, gateway=gateway, params=auth_params, capability="turns")
    except ProtocolError as exc:
        return http_error_response(exc)
    await gateway.initialize({})
    session_id = request.session_id
    if session_id:
        await gateway.session_resume({"session_id": session_id, **auth_params})
    else:
        session_params = {"model": request.model, **auth_params} if request.model else dict(auth_params)
        session = await gateway.session_start(session_params)
        session_id = str(session["session_id"])

    async def event_source():
        try:
            async for event in gateway.turn_stream(
                {
                    "session_id": session_id,
                    "input": request.input,
                    "domain": request.domain,
                    **auth_params,
                }
            ):
                yield f"event: {event.type}\n"
                yield "data: "
                yield event.model_dump_json()
                yield "\n\n"
        finally:
            if request.close_session:
                await gateway.session_close({"session_id": session_id})

    response = StreamingResponse(event_source(), media_type="text/event-stream")
    add_dev_warning(response, auth)
    return response


@router.get("/sessions/{session_id}/events")
async def get_session_events(
    session_id: str,
    request: Request,
    response: Response,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Read persisted protocol events for a session."""
    try:
        auth = await authorize_http_request(request, gateway=gateway, params={"session_id": session_id}, capability="sessions")
    except ProtocolError as exc:
        return http_error_response(exc)
    add_dev_warning(response, auth)
    try:
        return await gateway.session_events({"session_id": session_id, "scope": auth.scope.to_dict()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions")
async def list_sessions(
    request: Request,
    response: Response,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """List persisted gateway sessions."""
    try:
        auth = await authorize_http_request(request, gateway=gateway, params={}, capability="sessions")
    except ProtocolError as exc:
        return http_error_response(exc)
    add_dev_warning(response, auth)
    return await gateway.session_list({"scope": auth.scope.to_dict()})


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    request: Request,
    response: Response,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Read one persisted gateway session snapshot."""
    try:
        auth = await authorize_http_request(request, gateway=gateway, params={"session_id": session_id}, capability="sessions")
    except ProtocolError as exc:
        return http_error_response(exc)
    add_dev_warning(response, auth)
    try:
        return await gateway.session_read({"session_id": session_id, "scope": auth.scope.to_dict()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/transcript")
async def get_session_transcript(
    session_id: str,
    request: Request,
    response: Response,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Read a replayed transcript for a session."""
    try:
        auth = await authorize_http_request(request, gateway=gateway, params={"session_id": session_id}, capability="sessions")
    except ProtocolError as exc:
        return http_error_response(exc)
    add_dev_warning(response, auth)
    try:
        return await gateway.session_transcript({"session_id": session_id, "scope": auth.scope.to_dict()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/rpc")
async def gateway_rpc(
    request: RpcRequest,
    http_request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Execute one gateway JSON-RPC style request."""
    params = dict(request.params or {})
    try:
        await authorize_rpc_request(http_request, gateway=gateway, method=request.method, params=params)
    except ProtocolError as exc:
        return protocol_error_response(exc, request_id=request.id)
    request = RpcRequest(id=request.id, method=request.method, params=params)
    response = await gateway.handle_rpc(request)
    return response.model_dump(mode="json")
