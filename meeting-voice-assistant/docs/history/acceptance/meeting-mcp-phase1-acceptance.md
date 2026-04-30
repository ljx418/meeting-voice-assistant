# Meeting MCP Phase1 Acceptance

## Scope

Phase1 keeps the project focused on the existing meeting assistant capabilities:

- local audio/video transcription through the unified ASR adapter layer
- meeting transcript analysis through the existing audio analyzer
- MCP tool/resource exposure for agent use
- meeting-only agent guidance and acceptance tests

Interview workflows are intentionally excluded from this phase.

## Current Meeting MCP Surface

Resources:

- `meeting://formats`
- `meeting://latest-session`
- `meeting://agent-guide`

Tools:

- `meeting_transcribe_file`
- `meeting_analyze_text`
- `meeting_process_file`
- `meeting_build_minutes`

Fallback JSON-RPC stdio methods:

- `initialize`
- `ping`
- `resources/list`
- `resources/read`
- `tools/list`
- `tools/call`
- `prompts/list`
- `prompts/get`

Prompt:

- `meeting_process_recording`

## Agent Acceptance Criteria

An agent passes the meeting scenario when it can:

1. Start `python3 -m app.meeting_mcp.mcp_stdio` without requiring the Python `mcp` package.
2. Read `meeting://agent-guide` and stay within meeting-only scope.
3. Discover the four meeting tools through `tools/list`.
4. Use `meeting_process_file` for a local recording, then inspect transcript length, segment count, summary, key points, and action items.
5. Use `meeting_build_minutes` with the returned `session_id` and produce a Markdown minutes artifact.
6. Avoid interview workflows, candidate scoring, and answer coaching in this phase.

## Verification Commands

Run from `backend/`:

```bash
PYTHONPYCACHEPREFIX=/tmp/meeting-va-pycache python3 -m compileall app/meeting_mcp tests/test_meeting_mcp.py
```

```bash
ASR_ENGINE=mock PYTHONPYCACHEPREFIX=/tmp/meeting-va-pycache python3 -m pytest \
  tests/test_meeting_mcp.py \
  tests/test_data_service.py \
  tests/test_llm_prompts.py \
  tests/test_asr_factory.py
```

For real audio validation, start the configured ASR backend first, then call `meeting_process_file` through MCP with the local audio path.

## Manual Test Cases

Run all commands from `backend/` unless noted otherwise.

### MTC-001: Start MCP Stdio Without SDK

Goal: verify the fallback JSON-RPC stdio server starts when Python `mcp` is not installed.

Steps:

1. Run `python3 -m app.meeting_mcp.mcp_stdio`.
2. Paste one JSON-RPC line:
   ```json
   {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}
   ```
3. Press Enter.

Expected:

- Response contains `"serverInfo":{"name":"meeting","version":"0.1.0"}`.
- Response contains `tools` and `resources` capabilities.

### MTC-002: Discover Meeting Tools

Goal: verify the agent can discover all meeting tools.

Steps:

1. Start `python3 -m app.meeting_mcp.mcp_stdio`.
2. Send:
   ```json
   {"jsonrpc":"2.0","id":2,"method":"tools/list"}
   ```

Expected:

- Response lists:
  - `meeting_transcribe_file`
  - `meeting_analyze_text`
  - `meeting_process_file`
  - `meeting_build_minutes`

### MTC-003: Read Meeting Agent Guide

Goal: verify the agent receives meeting-only operating boundaries.

Steps:

1. Start `python3 -m app.meeting_mcp.mcp_stdio`.
2. Send:
   ```json
   {"jsonrpc":"2.0","id":3,"method":"resources/read","params":{"uri":"meeting://agent-guide"}}
   ```

Expected:

- Response JSON text contains `"scope": "meeting"`.
- Response includes non-goals:
  - `interview workflows`
  - `candidate scoring`
  - `answer coaching`

### MTC-004: Get Meeting Workflow Prompt

Goal: verify MCP prompt guides an agent through the meeting recording workflow.

Steps:

1. Start `python3 -m app.meeting_mcp.mcp_stdio`.
2. Send:
   ```json
   {"jsonrpc":"2.0","id":4,"method":"prompts/get","params":{"name":"meeting_process_recording","arguments":{"path":"/tmp/demo.mp3","engine":"funasr","language":"zh"}}}
   ```

Expected:

- Prompt text instructs the agent to call `meeting_process_file`.
- Prompt text instructs the agent to call `meeting_build_minutes`.
- Prompt text explicitly says not to invoke interview tools.

### MTC-005: Analyze Transcript Text

Goal: verify text-only meeting analysis works without an audio file.

Steps:

1. Start `python3 -m app.meeting_mcp.mcp_stdio`.
2. Send:
   ```json
   {"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"meeting_analyze_text","arguments":{"text":"今天会议讨论项目发布计划。张三负责完成测试，李四负责准备发布材料，王五负责上线回滚预案。下周一完成最终验收。","mode":"audio_analyzer"}}}
   ```

Expected:

- Response has `"isError": false`.
- Tool content is JSON text.
- JSON contains `session_id`, `theme`, `summary`, `key_points`, and `action_items`.
- `workspace/output/<session_id>/analysis.json` exists.

### MTC-006: Build Minutes From Latest Session

Goal: verify a Markdown meeting minutes artifact can be generated after analysis.

Prerequisite: MTC-005 completed in the same MCP process.

Steps:

1. Send:
   ```json
   {"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"meeting_build_minutes","arguments":{"title":"项目发布计划会议","include_transcript_preview":true}}}
   ```

Expected:

- Response has `"isError": false`.
- Response JSON contains `path` ending with `minutes.md`.
- `minutes.md` exists under the session output directory.
- Markdown contains:
  - `# 项目发布计划会议`
  - `## Summary` or other analysis sections
  - `## Transcript Preview`

### MTC-007: Real Audio Processing With FunASR

Goal: verify a real local audio file can be transcribed, analyzed, and stored.

Prerequisite:

- FunASR service is running and reachable at `http://127.0.0.1:8001/health`.
- Example audio exists:
  `/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3`

Steps:

1. Start FunASR if needed:
   ```bash
   python3 -m uvicorn funasr_service.main:app --host 127.0.0.1 --port 8001
   ```
2. Start MCP stdio:
   ```bash
   ASR_ENGINE=funasr FUNASR_ENDPOINT=http://127.0.0.1:8001 python3 -m app.meeting_mcp.mcp_stdio
   ```
3. Send:
   ```json
   {"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"meeting_process_file","arguments":{"path":"/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3","engine":"funasr","language":"en","analyze":true,"mode":"audio_analyzer"}}}
   ```

Expected:

- Response has `"isError": false`.
- Response JSON contains a non-empty `transcript`.
- `segments` length is greater than 0.
- `analysis.theme` is non-empty.
- Artifact paths include `transcript`, `analysis`, and `result`.

### MTC-008: Generate Minutes For Real Audio Session

Goal: verify the real audio session can be turned into Markdown minutes.

Prerequisite: MTC-007 completed in the same MCP process.

Steps:

1. Send:
   ```json
   {"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"meeting_build_minutes","arguments":{"title":"TED Talk Notes","include_transcript_preview":true}}}
   ```

Expected:

- Response contains a `minutes.md` path.
- Markdown file exists.
- Markdown contains `# TED Talk Notes`.
- Markdown includes transcript preview and any generated analysis sections.

### MTC-009: Latest Session Resource

Goal: verify agents can recover the latest meeting session artifact paths.

Steps:

1. After MTC-005 or MTC-007, send:
   ```json
   {"jsonrpc":"2.0","id":9,"method":"resources/read","params":{"uri":"meeting://latest-session"}}
   ```

Expected:

- Response contains the latest `session_id`.
- Response contains artifact paths for the latest meeting session.

### MTC-010: Unknown Tool Error

Goal: verify invalid tool calls fail clearly.

Steps:

1. Start MCP stdio.
2. Send:
   ```json
   {"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"interview_score_candidate","arguments":{}}}
   ```

Expected:

- Response contains a JSON-RPC `error`.
- Error message includes `Unknown tool`.
- No interview workflow is executed.
