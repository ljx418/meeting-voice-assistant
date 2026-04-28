# Agent Orchestrator Interface

## Overview

The Agent Orchestrator is the core coordination layer in harnessOS, responsible for routing intents, dispatching workflows, and managing subagents. Based on patterns from Deep Agents and OpenHarness.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Agent Orchestrator                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Intent      │  │ Workflow    │  │ Subagent                │ │
│  │ Router      │  │ Dispatcher  │  │ Registry                │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Meeting  │    │ Interview│    │ Knowledge│
    │ Agent    │    │ Agent    │    │ Agent    │
    └──────────┘    └──────────┘    └──────────┘
```

Phase1 status:

- Meeting scenario is available through explicit Gateway RPC methods: `meeting.capabilities`, `meeting.analyze_text`, `meeting.process_recording`, and `meeting.process_audio_dir`.
- Meeting execution is backed by the external `meeting-voice-assistant` MCP server.
- `turn.start(domain=meeting)` and natural-language meeting audio path prompts are routed to the Meeting workflow before the generic assistant runtime.
- Real audio acceptance uses `/Users/Zhuanz/Desktop/workspace/音频资料`; the latest chat/headless acceptance produced `meeting_8e8d3499`.
- Interview orchestration is intentionally deferred and must not block Phase1 meeting acceptance.

## Core Interfaces

### 1. Intent Router

Routes user input to the appropriate agent or workflow.

```python
from abc import ABC, abstractmethod
from typing import Any

class IntentResult:
    """Result of intent classification."""
    intent: str                           # e.g., "transcribe_meeting"
    confidence: float                    # 0.0 - 1.0
    entities: dict[str, Any]              # Extracted entities
    suggested_agent: str | None           # Agent ID to use
    suggested_workflow: str | None        # Workflow to invoke


class IntentRouter(ABC):
    """Interface for intent routing."""

    @abstractmethod
    async def route(self, user_input: str, context: dict[str, Any]) -> IntentResult:
        """
        Classify user intent and extract entities.

        Args:
            user_input: Raw user message
            context: Session context (user_id, session_id, etc.)

        Returns:
            IntentResult with classification and extracted data
        """

    @abstractmethod
    async def batch_route(
        self, user_inputs: list[str], context: dict[str, Any]
    ) -> list[IntentResult]:
        """Route multiple inputs in batch."""
```

**Default Implementations**:

| Implementation | Use Case |
|----------------|----------|
| `KeywordIntentRouter` | Simple keyword-based routing |
| `LLMIntentRouter` | LLM-powered intent classification |
| `HybridIntentRouter` | Combines keyword + LLM |

### 2. Workflow Dispatcher

Manages and executes multi-step workflows.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator
from enum import Enum


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""
    step_id: str
    name: str
    agent_id: str | None = None          # Agent to execute
    tool_calls: list[dict[str, Any]] | None = None
    input_mapping: dict[str, str] | None = None  # Map from previous step outputs
    output_key: str | None = None       # Key to store result under
    config: dict[str, Any] | None = None


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""
    workflow_id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    error_handling: str = "stop"  # "stop", "continue", "retry"
    max_retries: int = 3


@dataclass
class WorkflowExecution:
    """Runtime state of a workflow execution."""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: int
    step_results: dict[str, Any]
    started_at: str
    completed_at: str | None = None
    error: str | None = None


class WorkflowDispatcher(ABC):
    """Interface for workflow management."""

    @abstractmethod
    async def start_workflow(
        self, workflow: WorkflowDefinition, input_data: dict[str, Any]
    ) -> WorkflowExecution:
        """Start a new workflow execution."""

    @abstractmethod
    async def get_workflow_status(self, execution_id: str) -> WorkflowExecution:
        """Get the current status of a workflow execution."""

    @abstractmethod
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow."""

    @abstractmethod
    async def stream_workflow(
        self, execution_id: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream workflow execution events."""
```

### 3. Subagent Registry

Manages registration and invocation of subagents.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator


@dataclass
class SubAgentSpec:
    """Specification for a subagent."""
    name: str                            # Unique name
    description: str                     # Human-readable description
    agent_type: str                      # e.g., "general-purpose", "research"
    system_prompt: str | None = None
    model: str | None = None             # Optional model override
    tools: list[str] | None = None       # Tool whitelist
    max_turns: int | None = None         # Max conversation turns
    timeout: int = 900                   # Timeout in seconds (default 15min)


@dataclass
class SubAgentResult:
    """Result from a subagent execution."""
    success: bool
    output: str | None = None
    error: str | None = None
    usage: dict[str, int] | None = None  # Token usage


class SubAgentRegistry(ABC):
    """Interface for subagent management."""

    @abstractmethod
    def register(self, spec: SubAgentSpec) -> None:
        """Register a new subagent."""

    @abstractmethod
    def unregister(self, name: str) -> None:
        """Unregister a subagent."""

    @abstractmethod
    def get(self, name: str) -> SubAgentSpec | None:
        """Get subagent specification."""

    @abstractmethod
    def list_all(self) -> list[SubAgentSpec]:
        """List all registered subagents."""

    @abstractmethod
    async def invoke(
        self,
        name: str,
        prompt: str,
        context: dict[str, Any] | None = None
    ) -> SubAgentResult:
        """Invoke a subagent synchronously."""

    @abstractmethod
    async def invoke_stream(
        self,
        name: str,
        prompt: str,
        context: dict[str, Any] | None = None
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Invoke a subagent with streaming output."""
```

### 4. Session Manager

Manages conversation sessions and state.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Session:
    """Conversation session."""
    session_id: str
    user_id: str
    agent_id: str
    created_at: str
    last_active_at: str
    config: dict[str, Any]
    metadata: dict[str, Any]


class SessionManager(ABC):
    """Interface for session management."""

    @abstractmethod
    async def create_session(
        self, user_id: str, agent_id: str, config: dict[str, Any] | None = None
    ) -> Session:
        """Create a new session."""

    @abstractmethod
    async def get_session(self, session_id: str) -> Session | None:
        """Get session by ID."""

    @abstractmethod
    async def update_session(self, session: Session) -> None:
        """Update session data."""

    @abstractmethod
    async def delete_session(self, session_id: str) -> None:
        """Delete a session."""

    @abstractmethod
    async def list_sessions(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[Session]:
        """List sessions for a user."""
```

## Built-in Agents

### Meeting Assistant Agent

```python
MEETING_AGENT_SPEC = SubAgentSpec(
    name="meeting-assistant",
    description="AI assistant for meeting transcription and summarization",
    agent_type="meeting",
    tools=["transcribe", "summarize", "extract_actions", "generate_notes"],
    max_turns=50,
)
```

**Capabilities**:
- Real-time transcription (via ASR)
- Meeting summarization
- Action item extraction
- Multi-speaker identification

### Interview Assistant Agent

```python
INTERVIEW_AGENT_SPEC = SubAgentSpec(
    name="interview-assistant",
    description="AI assistant for interview preparation and analysis",
    agent_type="interview",
    tools=["generate_questions", "analyze_responses", "score_candidate"],
    max_turns=30,
)
```

**Capabilities**:
- Question generation
- Response analysis
- Candidate scoring

### Knowledge Base Agent

```python
KNOWLEDGE_AGENT_SPEC = SubAgentSpec(
    name="knowledge-agent",
    description="RAG-powered knowledge base assistant",
    agent_type="knowledge",
    tools=["search", "query_graph", "index_document"],
    max_turns=20,
)
```

**Capabilities**:
- Semantic search
- GraphRAG queries
- Document indexing

## Workflow Examples

### Meeting Transcription Workflow

```python
MEETING_TRANSCRIPTION_WORKFLOW = WorkflowDefinition(
    workflow_id="meeting-transcription",
    name="Meeting Transcription",
    description="Transcribe and summarize a meeting",
    steps=[
        WorkflowStep(
            step_id="transcribe",
            name="Transcribe Audio",
            agent_id="meeting-assistant",
            tool_calls=[{"name": "transcribe", "input": {"audio_source": "${input.audio}"}}],
            output_key="transcript"
        ),
        WorkflowStep(
            step_id="summarize",
            name="Summarize Transcript",
            agent_id="meeting-assistant",
            tool_calls=[{"name": "summarize", "input": {"text": "${transcribe.output}"}}],
            output_key="summary"
        ),
        WorkflowStep(
            step_id="extract_actions",
            name="Extract Action Items",
            agent_id="meeting-assistant",
            tool_calls=[{"name": "extract_actions", "input": {"text": "${transcribe.output}"}}],
            output_key="action_items"
        ),
    ]
)
```

### Interview Preparation Workflow

```python
INTERVIEW_PREP_WORKFLOW = WorkflowDefinition(
    workflow_id="interview-prep",
    name="Interview Preparation",
    description="Prepare interview questions and evaluation criteria",
    steps=[
        WorkflowStep(
            step_id="generate_questions",
            name="Generate Questions",
            agent_id="interview-assistant",
            tool_calls=[{"name": "generate_questions", "input": {"job_description": "${input.job_desc}"}}],
            output_key="questions"
        ),
        WorkflowStep(
            step_id="generate_criteria",
            name="Generate Evaluation Criteria",
            agent_id="interview-assistant",
            tool_calls=[{"name": "generate_criteria", "input": {"job_description": "${input.job_desc}"}}],
            output_key="criteria"
        ),
    ]
)
```

## Event System

The orchestrator emits events for monitoring and debugging:

```python
@dataclass
class OrchestratorEvent:
    """Base event from the orchestrator."""
    event_type: str
    timestamp: str
    execution_id: str
    data: dict[str, Any]


# Event Types
EVENT_WORKFLOW_STARTED = "workflow_started"
EVENT_WORKFLOW_STEP_STARTED = "workflow_step_started"
EVENT_WORKFLOW_STEP_COMPLETED = "workflow_step_completed"
EVENT_WORKFLOW_COMPLETED = "workflow_completed"
EVENT_WORKFLOW_FAILED = "workflow_failed"
EVENT_SUBAGENT_INVOKED = "subagent_invoked"
EVENT_SUBAGENT_COMPLETED = "subagent_completed"
EVENT_SUBAGENT_FAILED = "subagent_failed"
EVENT_INTENT_CLASSIFIED = "intent_classified"
```

## Configuration

```python
@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    # Intent routing
    intent_router_type: str = "hybrid"  # "keyword", "llm", "hybrid"
    intent_llm_model: str = "deepseek-chat"
    intent_confidence_threshold: float = 0.7

    # Workflow settings
    max_concurrent_workflows: int = 10
    workflow_timeout: int = 3600  # 1 hour

    # Subagent settings
    max_concurrent_subagents: int = 3
    subagent_timeout: int = 900  # 15 minutes

    # Session settings
    session_ttl: int = 86400  # 24 hours
    max_sessions_per_user: int = 100
```
