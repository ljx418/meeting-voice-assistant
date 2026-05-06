# Phase 3 Manual Acceptance Checklist

This document defines the user-facing terminal acceptance path for Phase 3.
It intentionally uses CLI, stdio JSONL, and local services instead of pytest.

## Scope

Phase 3 is accepted when a user can verify the following from a normal terminal:

- Basic headless turns complete and return protocol metadata.
- Domain Packs are visible and active packs are assembled.
- Connector Registry exposes Meeting MCP after Phase 3-F.
- Real meeting audio can run through the assembled Meeting Pack.
- Job, Trace, Artifact, Policy, and Approval records are queryable.

## 0. Start Local Dependencies

Start the local FunASR service from the sibling meeting project when real audio
acceptance is required:

```bash
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend
python3 -m uvicorn funasr_service.main:app --host 127.0.0.1 --port 8001
```

Then use another terminal for harnessOS:

```bash
cd /Users/Zhuanz/Desktop/workspace/harnessOS
```

## 1. Basic Headless CLI

```bash
python3 -m cli.main run --json "你好"
```

Expected result:

- Exit code is `0`.
- JSON contains `session_id`, `turn_id`, and `trace_id`.
- `events` contains `turn.started`, `item.delta`, and `turn.completed`.

## 2. Pack Assembly

```bash
printf '%s\n' \
'{"id":"init","method":"initialize","params":{}}' \
'{"id":"packs","method":"pack.list","params":{}}' \
'{"id":"workflows","method":"workflow.list","params":{}}' \
| python3 -m apps.gateway.stdio_server
```

Expected result:

- `pack.list` shows `meeting`, `knowledge`, `investment`, `interview`, and
  `video_studio`.
- `meeting` and `knowledge` are active assembled packs.
- Stub packs are visible but not reported as runnable.
- `workflow.list` shows `meeting.workflow` and `knowledge.workflow` with pack
  assembly metadata.

## 3. Connector Registry

After Phase 3-F, run:

```bash
printf '%s\n' \
'{"id":"c1","method":"connector.list","params":{}}' \
'{"id":"c2","method":"connector.get","params":{"connector_id":"meeting_voice_mcp"}}' \
'{"id":"c3","method":"connector.health","params":{"connector_id":"meeting_voice_mcp"}}' \
| python3 -m apps.gateway.stdio_server
```

Expected result:

- `connector.list` shows `meeting_voice_mcp`.
- `connector.get` returns kind, domain, capabilities, health, and config_ref.
- `connector.health` returns `available`, `unavailable`, or
  `missing_dependency` with an explainable message.
- Secrets and raw sensitive config values are not returned.

## 4. Real Meeting Audio

Prefer the team fixture when available:

```bash
scripts/e2e_meeting_validation.sh ./fixtures/audio_samples/sample_ted_talk.mp3
```

If the fixture is not available, use a local audio path as validation evidence:

```bash
scripts/e2e_meeting_validation.sh \
"/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"
```

Expected result:

- Script output contains `"status": "passed"`.
- `domain` is `meeting`.
- Artifacts include `transcript`, `analysis`, `result`, and `minutes`.
- `lineage.edges` is exactly `transcript -> analysis -> result -> minutes`.
- No ComfyUI or remote video workstation is required for this acceptance path.
- FunASR logs show `/recognize` returning `200 OK`.

## 5. Job, Trace, and Artifact Queries

Use the `trace_id`, `job_id`, and artifact IDs returned by the meeting run:

```bash
printf '%s\n' \
'{"id":"t1","method":"trace.get","params":{"trace_id":"<trace_id>"}}' \
'{"id":"j1","method":"job.get","params":{"job_id":"<job_id>"}}' \
'{"id":"j2","method":"job.events","params":{"job_id":"<job_id>"}}' \
'{"id":"a1","method":"artifact.list","params":{}}' \
| python3 -m apps.gateway.stdio_server
```

Expected result:

- `trace.get` contains turn, job, and artifact-related records.
- `job.events` contains `job.queued`, `job.started`, and `job.completed`.
- `artifact.list` shows meeting artifacts.
- `artifact.lineage` can return the meeting artifact graph for the same session.
- `artifact.read` can read transcript or minutes content by artifact ID.

## 6. Governance

```bash
python3 -m cli.main run --json \
"请在 workspace 下写入 approval_test.txt，内容为 hello"
```

Expected result:

- The write action is not executed directly.
- The turn is blocked by policy or creates a pending approval.
- Trace/approval queries show the governance decision.

Direct policy check:

```bash
printf '%s\n' \
'{"id":"p1","method":"policy.evaluate","params":{"tool_name":"workspace_write_file","tool_input":{"file_path":"approval_test.txt"}}}' \
'{"id":"ap1","method":"approval.list","params":{}}' \
| python3 -m apps.gateway.stdio_server
```

## Final Pass Criteria

Phase 3 user-state acceptance passes when all of the following are true:

- Basic headless turn succeeds from terminal.
- `pack.list/get` exposes five packs and assembly states.
- `connector.list/get/health` exposes Meeting MCP after Phase 3-F.
- Real meeting audio generates minutes and registers job, trace, artifacts, and the `transcript -> analysis -> result -> minutes` lineage.
- Write-class actions cannot bypass policy and approval.
