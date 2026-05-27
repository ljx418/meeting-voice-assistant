# V3.7 Codex Exec JSONL Monitor Smoke Evidence

status: passed

date: 2026-05-25

## Scope

This evidence covers only `petctl codex launch --monitor jsonl` for wrapper-launched `codex exec --json` sessions.

Strategy update on 2026-05-26: V3.7 JSONL monitor is the current recommended Codex exec monitoring path. V3.6 hook-only monitoring remains historical blocked evidence and is deprecated as the active strategy.

## Required Results

| Scenario | Status | Evidence |
| --- | --- | --- |
| desktop health | passed | `/api/health` returned ok. |
| simple answer | passed | observed `turn.started` and `turn.completed`; mapped `thinking`, final target state `success`. |
| tool success | passed | observed `item.started`; mapped `running`, final target state `success`. |
| tool failure | passed | observed structured `turn.failed`; monitor summary marked failure and target state became `error`. |
| security redaction scan | passed | no sensitive output in smoke summary. |
| claim scan | passed | no forbidden passed claim in smoke summary. |

## Smoke Command

```bash
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
```

Result:

```text
status=passed
runId=1779757764038-0596be
```

## Observed Safe Event Types

The smoke recorded only event type names and mapped states:

```text
turn.started
turn.completed
item.started
turn.failed
```

No raw JSONL payload, prompt text, tool command text, token, Authorization header, transcript path, full local path, workspace path, config path, or `api-token.json` value was recorded.

`thread.started` is marker-only in V3.7. It is not evidence of an emitted `idle` pet state.

## Evidence Policy

Record only event type, safe field names, mapped state, target route, and diagnostics accepted result.

Do not record raw JSONL, prompt text, tool command text, token, Authorization, `transcript_path`, full local paths, workspace path, config path, or `api-token.json`.

## Allowed Claim

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

## Boundary

This evidence does not allow:

```text
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
OS-level Codex window binding ready
```
