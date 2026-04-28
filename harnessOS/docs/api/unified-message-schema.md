# Unified Message Schema

## Overview

This document defines the standard message format for all agent communications in harnessOS. Based on successful patterns from DeerFlow and OpenHarness.

## Core Message Types

### 1. ConversationMessage

The primary message type for user/assistant interactions.

```typescript
interface ConversationMessage {
  /** Message role: 'user' | 'assistant' */
  role: 'user' | 'assistant';

  /** Content blocks composing the message */
  content: ContentBlock[];

  /** Optional metadata */
  metadata?: {
    timestamp?: string;       // ISO 8601
    message_id?: string;     // Unique identifier
    session_id?: string;      // Conversation session
    user_id?: string;         // User identifier
    model?: string;            // Model used for response
    usage?: UsageSnapshot;     // Token usage statistics
  };
}
```

### 2. ContentBlock

Content blocks are the fundamental unit of message content, supporting text, images, and tool interactions.

```typescript
type ContentBlock = TextBlock | ImageBlock | ToolUseBlock | ToolResultBlock;

// Text content
interface TextBlock {
  type: 'text';
  text: string;
}

// Image content (multimodal)
interface ImageBlock {
  type: 'image';
  media_type: string;        // e.g., 'image/png', 'image/jpeg'
  data: string;              // Base64-encoded image data
  source_path?: string;       // Optional source file path
}

// Tool invocation request
interface ToolUseBlock {
  type: 'tool_use';
  id: string;                // Unique tool call ID
  name: string;              // Tool name
  input: Record<string, any>; // Tool input parameters
}

// Tool execution result
interface ToolResultBlock {
  type: 'tool_result';
  tool_use_id: string;       // References the ToolUseBlock id
  content: string;           // Result content
  is_error: boolean;         // Whether tool execution failed
}
```

### 3. SessionMessage

Messages within a session context.

```typescript
interface SessionMessage {
  /** Unique message identifier */
  id: string;

  /** Session this message belongs to */
  session_id: string;

  /** The conversation message */
  message: ConversationMessage;

  /** Sequence number within session */
  sequence: number;

  /** Parent message ID (for threading) */
  parent_id?: string;

  /** Timestamp */
  created_at: string;        // ISO 8601
}
```

### 4. StreamEvent

Events yielded during streaming responses.

```typescript
type StreamEvent =
  | AssistantTextDelta      // Incremental assistant text
  | AssistantTurnComplete   // Completed assistant turn
  | ToolExecutionStarted    // Tool execution began
  | ToolExecutionCompleted  // Tool execution finished
  | ErrorEvent              // Error occurred
  | StatusEvent             // Transient status message
  | CompactProgressEvent;   // Context compaction progress

interface AssistantTextDelta {
  type: 'text_delta';
  text: string;
}

interface AssistantTurnComplete {
  type: 'turn_complete';
  message: ConversationMessage;
  usage: UsageSnapshot;
}

interface ToolExecutionStarted {
  type: 'tool_started';
  tool_name: string;
  tool_input: Record<string, any>;
}

interface ToolExecutionCompleted {
  type: 'tool_completed';
  tool_name: string;
  output: string;
  is_error: boolean;
}

interface ErrorEvent {
  type: 'error';
  message: string;
  recoverable: boolean;
}

interface StatusEvent {
  type: 'status';
  message: string;
}

interface CompactProgressEvent {
  type: 'compact_progress';
  phase: 'hooks_start' | 'context_collapse_start' | 'context_collapse_end' |
         'session_memory_start' | 'session_memory_end' | 'compact_start' |
         'compact_retry' | 'compact_end' | 'compact_failed';
  trigger: 'auto' | 'manual' | 'reactive';
  message?: string;
  attempt?: number;
}
```

### 5. UsageSnapshot

Token usage statistics.

```typescript
interface UsageSnapshot {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cache_hits?: number;       // Cached token hits
  cache_misses?: number;     // Cache misses
}
```

## Message Flow

```
User Input → ContentBlock[] → ConversationMessage → SessionMessage → Response
                      ↓
              [TextBlock | ImageBlock | ToolUseBlock]
```

## Validation Rules

1. **Role**: Must be either 'user' or 'assistant'
2. **Content**: Cannot be null; empty array allowed
3. **ToolUseBlock.id**: Must be unique within a message
4. **ToolResultBlock.tool_use_id**: Must reference an existing ToolUseBlock.id
5. **SessionMessage.sequence**: Must be monotonically increasing within a session

## JSON Representation

```json
{
  "id": "msg_abc123",
  "session_id": "sess_xyz789",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Hello, analyze this image"
      },
      {
        "type": "image",
        "media_type": "image/png",
        "data": "base64encodedstring..."
      }
    ]
  },
  "sequence": 1,
  "created_at": "2026-04-23T10:30:00Z"
}
```
