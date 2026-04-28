"""
Unified message schemas for harnessOS.

This module defines the core message types used across the entire harnessOS system,
providing a consistent interface for agent communication.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message sender role."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    AGENT = "agent"


class MessageType(str, Enum):
    """Message content type."""
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    FILE = "file"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"


class AgentType(str, Enum):
    """Agent type enumeration."""
    LEAD_ORCHESTRATOR = "lead_orchestrator"
    MEETING_ANALYST = "meeting_analyst"
    INTERVIEW_COACH = "interview_coach"
    KB_CURATOR = "kb_curator"
    MEDIA_ORCHESTRATOR = "media_orchestrator"
    GENERAL_PURPOSE = "general_purpose"


class ExecutionStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Message(BaseModel):
    """Core message schema for agent communication."""
    id: str = Field(..., description="Unique message identifier")
    role: MessageRole = Field(..., description="Sender role")
    content: str = Field(..., description="Message content")
    type: MessageType = Field(default=MessageType.TEXT, description="Content type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ToolCall(BaseModel):
    """Tool call request schema."""
    id: str = Field(..., description="Tool call ID")
    name: str = Field(..., description="Tool name")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING, description="Execution status")


class ToolResult(BaseModel):
    """Tool execution result schema."""
    call_id: str = Field(..., description="Corresponding tool call ID")
    result: Any = Field(..., description="Execution result")
    success: bool = Field(..., description="Whether execution succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")


class AgentRequest(BaseModel):
    """Request schema for agent invocation."""
    agent_type: AgentType = Field(..., description="Type of agent to invoke")
    messages: list[Message] = Field(..., description="Conversation messages")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    config: dict[str, Any] = Field(default_factory=dict, description="Agent configuration")


class AgentResponse(BaseModel):
    """Response schema for agent invocation."""
    request_id: str = Field(..., description="Request tracking ID")
    agent_type: AgentType = Field(..., description="Agent that handled the request")
    messages: list[Message] = Field(..., description="Response messages")
    status: ExecutionStatus = Field(..., description="Execution status")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class WorkflowTask(BaseModel):
    """Workflow task schema."""
    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    agent_type: AgentType = Field(..., description="Required agent type")
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING, description="Task status")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Task input")
    output_data: Optional[dict[str, Any]] = Field(None, description="Task output")
    parent_id: Optional[str] = Field(None, description="Parent task ID for sub-tasks")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class IntentType(str, Enum):
    """User intent types for routing."""
    MEETING_ASSIST = "meeting_assist"
    INTERVIEW_PREP = "interview_prep"
    KNOWLEDGE_QUERY = "knowledge_query"
    VIDEO_PRODUCTION = "video_production"
    GENERAL_CHAT = "general_chat"


class IntentRoutingRequest(BaseModel):
    """Request schema for intent routing."""
    user_input: str = Field(..., description="User's raw input")
    context: dict[str, Any] = Field(default_factory=dict, description="Session context")


class IntentRoutingResponse(BaseModel):
    """Response schema for intent routing."""
    intent: IntentType = Field(..., description="Detected intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    suggested_agent: AgentType = Field(..., description="Recommended agent type")
    reasoning: str = Field(..., description="Routing reasoning")
