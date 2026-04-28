"""Run endpoints backed by the harnessOS gateway service."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from apps.api.dependencies import get_gateway_service
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService

router = APIRouter()


class RunRequest(BaseModel):
    """Request to execute one agent run."""

    input: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    model: Optional[str] = None
    domain: Optional[str] = None
    close_session: bool = False


@router.post("/runs")
async def create_run(
    request: RunRequest,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Run one turn and return the aggregated result."""
    await gateway.initialize({})
    session_id = request.session_id
    if session_id:
        await gateway.session_resume({"session_id": session_id})
    else:
        session = await gateway.session_start({"model": request.model} if request.model else {})
        session_id = str(session["session_id"])

    result = await gateway.turn_start(
        {
            "session_id": session_id,
            "input": request.input,
            "domain": request.domain,
        }
    )
    if request.close_session:
        await gateway.session_close({"session_id": session_id})
    return result


@router.post("/runs/stream")
async def stream_run(
    request: RunRequest,
    gateway: GatewayService = Depends(get_gateway_service),
) -> StreamingResponse:
    """Run one turn and stream normalized protocol events as SSE."""
    await gateway.initialize({})
    session_id = request.session_id
    if session_id:
        await gateway.session_resume({"session_id": session_id})
    else:
        session = await gateway.session_start({"model": request.model} if request.model else {})
        session_id = str(session["session_id"])

    async def event_source():
        try:
            async for event in gateway.turn_stream(
                {
                    "session_id": session_id,
                    "input": request.input,
                    "domain": request.domain,
                }
            ):
                yield f"event: {event.type}\n"
                yield "data: "
                yield event.model_dump_json()
                yield "\n\n"
        finally:
            if request.close_session:
                await gateway.session_close({"session_id": session_id})

    return StreamingResponse(event_source(), media_type="text/event-stream")


@router.get("/sessions/{session_id}/events")
async def get_session_events(
    session_id: str,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Read persisted protocol events for a session."""
    try:
        return await gateway.session_events({"session_id": session_id})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions")
async def list_sessions(gateway: GatewayService = Depends(get_gateway_service)) -> dict[str, Any]:
    """List persisted gateway sessions."""
    return await gateway.session_list()


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Read one persisted gateway session snapshot."""
    try:
        return await gateway.session_read({"session_id": session_id})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/transcript")
async def get_session_transcript(
    session_id: str,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Read a replayed transcript for a session."""
    try:
        return await gateway.session_transcript({"session_id": session_id})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/rpc")
async def gateway_rpc(
    request: RpcRequest,
    gateway: GatewayService = Depends(get_gateway_service),
) -> dict[str, Any]:
    """Execute one gateway JSON-RPC style request."""
    response = await gateway.handle_rpc(request)
    return response.model_dump(mode="json")
