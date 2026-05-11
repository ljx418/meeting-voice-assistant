"""
Intent routing endpoints for harnessOS API.
"""

from fastapi import APIRouter, Depends, Request

from apps.api.auth import authorize_http_request, http_error_response
from apps.api.dependencies import get_gateway_service
from apps.gateway.service import GatewayService
from core.orchestration.intent_router import IntentRouter
from core.schemas import IntentRoutingRequest, IntentRoutingResponse
from core.protocol.schemas.errors import ProtocolError

router = APIRouter()

# Global intent router instance
_intent_router = IntentRouter()


@router.post("/intent", response_model=IntentRoutingResponse)
async def route_intent(
    request: IntentRoutingRequest,
    http_request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> IntentRoutingResponse:
    """
    Route a user request to the appropriate agent based on intent.

    This endpoint uses keyword-based routing for now.
    LLM-based intent classification will be added in Phase 2.
    """
    try:
        await authorize_http_request(http_request, gateway=gateway, params={}, capability="routing", admin_only=True)
    except ProtocolError as exc:
        return http_error_response(exc)
    return await _intent_router.route(request)
