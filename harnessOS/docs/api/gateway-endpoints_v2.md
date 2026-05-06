# API Gateway Endpoints

## Overview

The harnessOS API Gateway provides a BFF (Backend for Frontend) layer based on FastAPI, following patterns from DeerFlow's Gateway implementation.

## Base Configuration

- **Base URL**: `http://localhost:8000`
- **API Version**: v1
- **API Prefix**: `/api/v1`
- **Documentation**: `/docs` (Swagger UI), `/redoc` (ReDoc)

## Authentication

All endpoints (except health check) require authentication via API Key.

| Method | Header | Query Param |
|--------|--------|-------------|
| WebSocket | - | `?api_key=<key>` |
| HTTP | `X-API-Key: <key>` | - |

## Endpoints Overview

| Category | Prefix | Description |
|----------|--------|-------------|
| Health | `/health` | Service health check |
| Gateway RPC | `/v1/rpc` | JSON-RPC style control-plane endpoint |
| Auth | `/api/v1/auth` | Authentication & session |
| Sessions | `/api/v1/sessions` | Session management |
| Chat | `/api/v1/chat` | Message sending & streaming |
| Files | `/api/v1/files` | File upload & management |
| Agents | `/api/v1/agents` | Agent CRUD operations |
| Models | `/api/v1/models` | LLM model configuration |
| Skills | `/api/v1/skills` | Skills management |
| Memory | `/api/v1/memory` | Memory management |
| Tasks | `/api/v1/tasks` | Task query & status |

---

## Gateway RPC Methods

### POST /v1/rpc

Execute one Gateway RPC request.

Meeting Phase1 methods:

| Method | Description |
|--------|-------------|
| `meeting.capabilities` | Discover Meeting MCP tools, prompt, and `meeting://agent-guide` |
| `meeting.analyze_text` | Analyze meeting transcript text and build minutes |
| `meeting.process_recording` | Process one real audio file through Meeting MCP |
| `meeting.process_audio_dir` | Process supported audio files under `/Users/Zhuanz/Desktop/workspace/音频资料` |

Meeting Phase1-B turn orchestration:

| Entry | Description |
|-------|-------------|
| `turn.start` with `domain=meeting` | Routes the turn directly to Meeting workflow |
| `turn.start` natural-language prompt with meeting keyword + local audio path | Automatically routes to Meeting workflow |

Phase1-C artifact methods:

| Method | Description |
|--------|-------------|
| `artifact.register` | Register an existing local output file as a harnessOS artifact |
| `artifact.list` | List artifacts by `session_id`, `domain`, or `kind` |
| `artifact.get` | Return artifact metadata by `artifact_id` |
| `artifact.read` | Read artifact content as text or JSON |

Phase1-D workflow methods:

| Method | Description |
|--------|-------------|
| `workflow.list` | List registered DomainWorkflow entries, including pack metadata when available |

Core v1.5-B pack methods:

| Method | Description |
|--------|-------------|
| `pack.list` | List registered Domain Pack manifests; optional `domain` and `status` filters |
| `pack.get` | Return one Domain Pack manifest by `name` or `domain` |

Core v1.5-F connector methods:

| Method | Description |
|--------|-------------|
| `connector.list` | List registered connector records; optional `domain`, `kind`, and `health` filters |
| `connector.get` | Return one connector record by `connector_id` |
| `connector.health` | Refresh and return one connector health result |
| `connector.submit` | Submit a connector tool execution and create a governed Core job/artifact record |
| `connector.poll` | Poll one connector execution job |
| `connector.cancel` | Cancel a connector execution job when it is still cancellable |
| `connector.collect` | Return connector execution result artifacts and artifact lineage |

Phase 5-D cross-domain MCP execution:

| Entry | Description |
|-------|-------------|
| `funasr_mcp.funasr_recognize_file` | Explicitly gated by `HARNESS_FUNASR_MCP_EXECUTION=stdio`; transcribes audio through the adjacent FunASR MCP stdio server and registers a connector result artifact |
| `data_service_mcp.*` lifecycle tools | Explicitly gated by `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio`; runs Knowledge workspace create/import/build/query/feedback/review/archive through a persistent MCP stdio session |
| `turn.start(domain=meeting)` | When FunASR stdio execution is enabled, Meeting workflow can use `funasr_mcp` for transcription before calling Meeting text analysis/minutes |
| `MeetingToKnowledgeMcpRunner` | Backend acceptance runner, not a public RPC method; validates `audio -> transcript -> minutes -> knowledge import/build/query` and artifact lineage |

Core v1.5-C job methods:

| Method | Description |
|--------|-------------|
| `job.list` | List Core job records; optional `session_id`, `thread_id`, `turn_id`, `domain`, and `status` filters |
| `job.get` | Return one Core job record by `job_id` |
| `job.cancel` | Mark one Core job record as cancelled |
| `core.job.list` | Core-native alias for listing job records |

Core v1.5-D tool policy:

| Surface | Description |
|--------|-------------|
| builtin tools | `workspace_write_file`, `kb_ingest`, `artifact_save`, and pattern-matched mutating tools are blocked before execution unless `approved=true` or an approved `approval_id` is supplied |
| Core engine tool loop | `_execute_tool_call` reads `tool_metadata.policy_evaluator` and blocks risky tools before `tool.execute(...)` |
| `policy.evaluate` | Still available for dry-run classification of user input or tool invocation |

Core v1.5-E runtime adapter:

| Surface | Description |
|--------|-------------|
| `RuntimeHandle` / `RuntimeAdapter` | Core runtime boundary for Simple/OpenHarness implementations |
| `SimpleRuntimeAdapter` | Starts the Simple/deepagents-compatible agent path and supports non-streaming invoke |
| `OpenHarnessRuntimeAdapter` | Starts OpenHarness RuntimeBundle and supports streaming turn events and pending continuation |
| Gateway runtime pool | Uses adapter `start/invoke/stream/continue_pending/close` instead of directly constructing runtime internals |

Core v1.5-A query methods:

| Method | Description |
|--------|-------------|
| `session.get` | Return the Core v1.5 session record mirrored from Gateway runtime |
| `thread.list` | List Core v1.5 threads, optionally filtered by `session_id` |
| `turn.get` | Return one Core v1.5 turn record by `turn_id` |
| `turn.items` | List Core v1.5 items for one turn |
| `core.artifact.list` | List Core v1.5 artifact records, optionally filtered by `owner_thread_id`、`domain`、`kind` |
| `core.trace.list` | List Core v1.5 trace records, optionally filtered by `trace_id`、`session_id`、`turn_id`、`event_type` |
| `core.approval.list` | List Core v1.5 approval records, optionally filtered by `decision`、`target_type`、`target_id` |
| `core.retry.list` | List Core v1.5 retry records, optionally filtered by `session_id`、`approval_id`、`status` |

These methods read the new SQLite-backed Core records. Existing Gateway methods such as `session.read`, `session.events`, and `session.transcript` remain available during migration.

Registered workflows:

| Workflow | Domain | Description |
|----------|--------|-------------|
| `meeting.workflow` | `meeting` | Meeting audio/text analysis through Meeting MCP |
| `knowledge.workflow` | `knowledge` | Knowledge search/ingest MVP backed by existing kb tools |

Example:

```json
{
  "id": "m1",
  "method": "meeting.process_recording",
  "params": {
    "path": "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_How to tune your inner voice  Rhonda Ross Daniel A.mp3",
    "engine": "funasr",
    "language": "en"
  }
}
```

Response result includes:

```json
{
  "source_path": "...",
  "session_id": "meeting_8e8d3499",
  "transcript_chars": 575,
  "segment_count": 10,
  "analysis": {"theme": "..."},
  "minutes_path": ".../minutes.md",
  "artifacts": {
    "transcript": ".../transcript.json",
    "analysis": ".../analysis.json",
    "result": ".../result.json",
    "minutes": ".../minutes.md"
  }
}
```

Phase1 acceptance requires real audio from `/Users/Zhuanz/Desktop/workspace/音频资料`; mock audio is not sufficient for final acceptance.

Headless chat example:

```bash
python3 -m cli.main run --json '请分析 /Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_How to tune your inner voice  Rhonda Ross Daniel A.mp3，生成会议纪要'
```

Expected result: `final_text` includes `会议分析已完成`, `主题：`, and `会议纪要：`; the final `turn.completed` event includes `data.meeting` with transcript, analysis, minutes, and artifact paths.

Phase1-C expected meeting artifact shape:

```json
{
  "artifacts": {
    "minutes": {
      "path": ".../minutes.md",
      "artifact_id": "art_..."
    },
    "analysis": {
      "path": ".../analysis.json",
      "artifact_id": "art_..."
    }
  }
}
```

Phase1-C keeps the current path-based fields while adding artifact ids. Real-audio acceptance produced:

- Gateway session: `sess_a08b1f628ce2`
- Meeting session: `meeting_c4dc4073`
- Minutes artifact: `art_c27fa88d8d93`
- Analysis artifact: `art_9c1eb1071d60`

Phase1-D meeting results include workflow metadata:

```json
{
  "domain": "meeting",
  "workflow_id": "meeting.workflow"
}
```

---

## Health Endpoints

### GET /health

Health check endpoint (no authentication required).

**Response 200**:
```json
{
  "status": "healthy",
  "service": "harnessos-gateway",
  "version": "0.1.0",
  "timestamp": "2026-04-23T10:00:00Z"
}
```

---

## Auth Endpoints

### POST /api/v1/auth/login

Authenticate and create a session.

**Request**:
```json
{
  "api_key": "your-api-key"
}
```

**Response 200**:
```json
{
  "session_token": "tok_abc123",
  "expires_at": "2026-04-24T10:00:00Z",
  "user": {
    "id": "user_001",
    "name": "User"
  }
}
```

**Response 401**: Invalid API key

---

## Session Endpoints

### POST /api/v1/sessions

Create a new conversation session.

**Request**:
```json
{
  "agent_id": "meeting-assistant",
  "config": {
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "metadata": {
    "topic": "Project Discussion",
    "language": "zh"
  }
}
```

**Response 201**:
```json
{
  "session_id": "sess_xyz789",
  "agent_id": "meeting-assistant",
  "created_at": "2026-04-23T10:00:00Z",
  "config": {
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### GET /api/v1/sessions

List all sessions for the authenticated user.

**Query Parameters**:
- `limit` (int, default: 20): Maximum results
- `offset` (int, default: 0): Pagination offset
- `agent_id` (string, optional): Filter by agent

**Response 200**:
```json
{
  "sessions": [
    {
      "session_id": "sess_xyz789",
      "agent_id": "meeting-assistant",
      "created_at": "2026-04-23T10:00:00Z",
      "last_message_at": "2026-04-23T10:30:00Z",
      "message_count": 15
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### GET /api/v1/sessions/{session_id}

Get session details.

**Response 200**:
```json
{
  "session_id": "sess_xyz789",
  "agent_id": "meeting-assistant",
  "messages": [...],
  "created_at": "2026-04-23T10:00:00Z",
  "config": {...}
}
```

### DELETE /api/v1/sessions/{session_id}

Delete a session.

**Response 204**: No content

---

## Chat Endpoints

### POST /api/v1/chat/stream

Send a message and receive streaming response (Server-Sent Events).

**Headers**:
- `Content-Type: application/json`
- `Accept: text/event-stream`

**Request**:
```json
{
  "session_id": "sess_xyz789",
  "message": {
    "role": "user",
    "content": [
      {"type": "text", "text": "Hello, summarize the meeting"}
    ]
  },
  "stream": true
}
```

**Response** (SSE stream):
```
event: text_delta
data: {"text": "Hello"}

event: text_delta
data: {"text": ", here"}

event: tool_started
data: {"tool_name": "search", "tool_input": {"query": "..."}}

event: tool_completed
data: {"tool_name": "search", "output": "...", "is_error": false}

event: turn_complete
data: {"message": {...}, "usage": {...}}
```

### POST /api/v1/chat/sync

Send a message and receive a single synchronous response.

**Request**:
```json
{
  "session_id": "sess_xyz789",
  "message": {
    "role": "user",
    "content": [
      {"type": "text", "text": "What's the weather?"}
    ]
  }
}
```

**Response 200**:
```json
{
  "session_id": "sess_xyz789",
  "message": {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "The weather is sunny today."}
    ]
  },
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50,
    "total_tokens": 150
  },
  "model": "deepseek-chat"
}
```

---

## File Endpoints

### POST /api/v1/files/upload

Upload files for a session.

**Request**: `multipart/form-data`
- `session_id` (string, required)
- `files` (file[], required): Max 10 files, 100MB each

**Supported Formats**: pdf, docx, xlsx, pptx, txt, md, png, jpg, mp3, mp4, wav

**Response 201**:
```json
{
  "files": [
    {
      "file_id": "file_abc123",
      "filename": "document.pdf",
      "size": 1024000,
      "mime_type": "application/pdf",
      "status": "ready"
    }
  ]
}
```

### GET /api/v1/files/{file_id}

Download a file.

**Response 200**: Binary file stream

### DELETE /api/v1/files/{file_id}

Delete an uploaded file.

**Response 204**: No content

---

## Agent Endpoints

### GET /api/v1/agents

List all available agents.

**Response 200**:
```json
{
  "agents": [
    {
      "agent_id": "meeting-assistant",
      "name": "Meeting Assistant",
      "description": "AI assistant for meeting transcription and summarization",
      "capabilities": ["transcription", "summarization", "action_items"],
      "created_at": "2026-04-01T00:00:00Z"
    }
  ]
}
```

### GET /api/v1/agents/{agent_id}

Get agent details.

**Response 200**:
```json
{
  "agent_id": "meeting-assistant",
  "name": "Meeting Assistant",
  "description": "AI assistant for meeting transcription and summarization",
  "capabilities": ["transcription", "summarization", "action_items"],
  "config_schema": {...},
  "tools": ["transcribe", "summarize", "extract_actions"],
  "created_at": "2026-04-01T00:00:00Z"
}
```

### POST /api/v1/agents

Create a custom agent (future feature).

**Request**:
```json
{
  "agent_id": "my-agent",
  "name": "My Custom Agent",
  "description": "...",
  "system_prompt": "You are a helpful assistant...",
  "tools": ["search", "calculate"]
}
```

**Response 201**: Created agent details

### PUT /api/v1/agents/{agent_id}

Update agent configuration.

**Request**:
```json
{
  "name": "Updated Name",
  "system_prompt": "New system prompt..."
}
```

**Response 200**: Updated agent details

### DELETE /api/v1/agents/{agent_id}

Delete a custom agent.

**Response 204**: No content

---

## Model Endpoints

### GET /api/v1/models

List available LLM models.

**Response 200**:
```json
{
  "models": [
    {
      "model_id": "deepseek-chat",
      "provider": "deepseek",
      "display_name": "DeepSeek V3",
      "context_window": 64000,
      "supports_vision": false,
      "supports_thinking": false,
      "price_per_1k_input": 0.0001,
      "price_per_1k_output": 0.0003
    },
    {
      "model_id": "MiniMax-M2.1",
      "provider": "minimax",
      "display_name": "MiniMax M2.1",
      "context_window": 1000000,
      "supports_vision": true,
      "supports_thinking": true,
      "price_per_1k_input": 0.0,
      "price_per_1k_output": 0.0
    }
  ]
}
```

### GET /api/v1/models/{model_id}

Get model details.

**Response 200**:
```json
{
  "model_id": "deepseek-chat",
  "provider": "deepseek",
  "display_name": "DeepSeek V3",
  "context_window": 64000,
  "supports_vision": false,
  "supports_thinking": false
}
```

---

## Skills Endpoints

### GET /api/v1/skills

List available skills.

**Response 200**:
```json
{
  "skills": [
    {
      "skill_id": "code-review",
      "name": "Code Review",
      "description": "Automated code review with best practices",
      "enabled": true
    }
  ]
}
```

### PUT /api/v1/skills/{skill_id}

Enable/disable a skill.

**Request**:
```json
{
  "enabled": false
}
```

**Response 200**:
```json
{
  "skill_id": "code-review",
  "enabled": false
}
```

---

## Memory Endpoints

### GET /api/v1/memory

Get user's global memory.

**Response 200**:
```json
{
  "memory": {
    "work_context": "Software engineer working on AI projects",
    "personal_context": "Interested in hiking and photography",
    "facts": [
      {
        "id": "fact_001",
        "content": "User prefers Chinese language",
        "category": "preference",
        "confidence": 0.9
      }
    ]
  }
}
```

### PUT /api/v1/memory

Update user's global memory.

**Request**:
```json
{
  "work_context": "Updated work context",
  "facts": [...]
}
```

**Response 200**: Updated memory

### POST /api/v1/memory/reload

Force reload memory from storage.

**Response 200**:
```json
{
  "status": "reloaded",
  "memory": {...}
}
```

---

## Task Endpoints

### GET /api/v1/tasks

List background tasks.

**Query Parameters**:
- `status` (string, optional): Filter by status (pending, running, completed, failed)
- `limit` (int, default: 20)

**Response 200**:
```json
{
  "tasks": [
    {
      "task_id": "task_abc123",
      "type": "transcription",
      "status": "completed",
      "created_at": "2026-04-23T10:00:00Z",
      "completed_at": "2026-04-23T10:05:00Z",
      "result": {
        "transcript": "Meeting content..."
      }
    }
  ]
}
```

### GET /api/v1/tasks/{task_id}

Get task details.

**Response 200**:
```json
{
  "task_id": "task_abc123",
  "type": "transcription",
  "status": "running",
  "progress": 65,
  "created_at": "2026-04-23T10:00:00Z"
}
```

---

## WebSocket Endpoint

### WS /api/v1/ws/chat

Real-time chat via WebSocket.

**Connection**:
```
ws://localhost:8000/api/v1/ws/chat?api_key=<key>&session_id=<session_id>
```

**Client → Server Messages**:

```json
// Start session
{"type": "start", "agent_id": "meeting-assistant", "config": {...}}

// Send message
{"type": "message", "content": [{"type": "text", "text": "Hello"}]}

// Send file
{"type": "file", "file_id": "file_abc123"}

// Control commands
{"type": "control", "action": "pause|resume|stop"}

// Ping
{"type": "ping"}
```

**Server → Client Messages**:

```json
// Text delta
{"type": "text_delta", "text": "Hello"}

// Tool started
{"type": "tool_started", "tool_name": "search", "tool_input": {...}}

// Tool completed
{"type": "tool_completed", "tool_name": "search", "output": "...", "is_error": false}

// Turn complete
{"type": "turn_complete", "message": {...}, "usage": {...}}

// Error
{"type": "error", "message": "..."}

// Status
{"type": "status", "message": "Processing..."}

// Pong
{"type": "pong"}

// Session info
{"type": "session", "session_id": "sess_xyz789"}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable error message",
    "details": {
      "field": "specific field if applicable"
    }
  }
}
```

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
