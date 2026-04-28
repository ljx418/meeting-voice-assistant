"""
Intent router for harnessOS.

Routes user requests to the appropriate agent based on intent detection.
"""

from core.schemas import AgentType, IntentRoutingRequest, IntentRoutingResponse, IntentType


class IntentRouter:
    """
    Routes user requests to appropriate agents based on intent detection.

    This is a placeholder implementation. In Phase 2, this will use
    LLM-based intent classification or a dedicated classifier model.
    """

    # Keyword-based simple routing for initial implementation
    INTENT_KEYWORDS = {
        IntentType.MEETING_ASSIST: [
            "meeting", "会议", "transcribe", "transcription", "voice",
            "语音", "speaker", "说话人", "minutes", "纪要"
        ],
        IntentType.INTERVIEW_PREP: [
            "interview", "面试", "resume", "简历", "question",
            "问题", "prepare", "准备", "coach", "辅导"
        ],
        IntentType.KNOWLEDGE_QUERY: [
            "knowledge", "知识", "wiki", "search", "search",
            "搜索", "query", "查询", "graph", "图谱"
        ],
        IntentType.VIDEO_PRODUCTION: [
            "video", "视频", "render", "渲染", "production",
            "制作", "storyboard", "脚本", "media", "媒体"
        ],
    }

    def __init__(self):
        """Initialize the intent router."""
        pass

    async def route(self, request: IntentRoutingRequest) -> IntentRoutingResponse:
        """
        Route a user request to the appropriate agent.

        Args:
            request: The intent routing request containing user input

        Returns:
            Intent routing response with suggested agent
        """
        user_input = request.user_input.lower()
        context = request.context or {}

        # Simple keyword-based routing
        intent_scores: dict[IntentType, float] = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword.lower() in user_input)
            intent_scores[intent] = score

        # Find the intent with highest score
        if max(intent_scores.values()) > 0:
            detected_intent = max(intent_scores, key=intent_scores.get)  # type: ignore
            confidence = min(intent_scores[detected_intent] / 3.0, 1.0)
        else:
            detected_intent = IntentType.GENERAL_CHAT
            confidence = 0.5

        # Map intent to agent type
        agent_mapping = {
            IntentType.MEETING_ASSIST: AgentType.MEETING_ANALYST,
            IntentType.INTERVIEW_PREP: AgentType.INTERVIEW_COACH,
            IntentType.KNOWLEDGE_QUERY: AgentType.KB_CURATOR,
            IntentType.VIDEO_PRODUCTION: AgentType.MEDIA_ORCHESTRATOR,
            IntentType.GENERAL_CHAT: AgentType.GENERAL_PURPOSE,
        }

        suggested_agent = agent_mapping.get(detected_intent, AgentType.GENERAL_PURPOSE)

        return IntentRoutingResponse(
            intent=detected_intent,
            confidence=confidence,
            suggested_agent=suggested_agent,
            reasoning=f"Detected intent '{detected_intent.value}' with confidence {confidence:.2f}"
        )