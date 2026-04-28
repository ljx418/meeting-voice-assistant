"""
Agent management endpoints for harnessOS API.
"""

from typing import Any

from fastapi import APIRouter

from core.schemas import AgentRequest, AgentResponse, AgentType, ExecutionStatus, Message

router = APIRouter()


@router.post("/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest) -> AgentResponse:
    """
    Invoke a specific agent with the given request.

    This is a placeholder endpoint. Actual agent invocation
    will be implemented in Phase 2 with Deep Agents integration.
    """
    return AgentResponse(
        request_id=f"req-{len(request.messages)}",
        agent_type=request.agent_type,
        messages=[],
        status=ExecutionStatus.COMPLETED,
        metadata={"message": "Agent invocation placeholder - to be implemented in Phase 2"}
    )


@router.get("/types")
async def list_agent_types() -> dict[str, Any]:
    """
    List available agent types.

    Returns:
        Dictionary of available agents and their descriptions.
    """
    return {
        "agents": [
            {"type": AgentType.LEAD_ORCHESTRATOR, "description": "Main orchestrator agent"},
            {"type": AgentType.MEETING_ANALYST, "description": "Meeting analysis and transcription"},
            {"type": AgentType.INTERVIEW_COACH, "description": "Interview preparation and coaching"},
            {"type": AgentType.KB_CURATOR, "description": "Knowledge base management"},
            {"type": AgentType.MEDIA_ORCHESTRATOR, "description": "Video production orchestration"},
            {"type": AgentType.GENERAL_PURPOSE, "description": "General purpose agent"},
        ]
    }
