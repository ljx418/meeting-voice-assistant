"""
Intent routing endpoints for harnessOS API.
"""

from fastapi import APIRouter

from core.orchestration.intent_router import IntentRouter
from core.schemas import IntentRoutingRequest, IntentRoutingResponse

router = APIRouter()

# Global intent router instance
_intent_router = IntentRouter()


@router.post("/intent", response_model=IntentRoutingResponse)
async def route_intent(request: IntentRoutingRequest) -> IntentRoutingResponse:
    """
    Route a user request to the appropriate agent based on intent.

    This endpoint uses keyword-based routing for now.
    LLM-based intent classification will be added in Phase 2.
    """
    return await _intent_router.route(request)
