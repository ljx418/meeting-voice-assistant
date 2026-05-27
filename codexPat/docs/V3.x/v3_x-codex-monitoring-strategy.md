# V3.x Codex Monitoring Strategy

status: active

date: 2026-05-26

## Decision

Use V3.7 Codex Exec JSONL Monitor as the current primary Codex state monitoring path for supported local Codex workflows.

The deprecated V3.6 hook-only failure mapping path remains historical blocked evidence and is no longer the active implementation strategy.

## Primary Supported Path

```bash
node packages/petctl/dist/cli.js codex launch \
  --monitor jsonl \
  --name "Review Cat" \
  -- exec --json "summarize this repository"
```

This path is supported for wrapper-launched `codex exec --json` sessions.

## Why V3.7 Replaces V3.6 As The Active Strategy

V3.6 tried to prove `PostToolUse failure -> error` through official hook lifecycle payloads. The real tested `PostToolUse` payload did not expose stable failure fields such as exit code, status, success, error, result, tool result, or response.

V3.7 uses Codex's structured JSONL stdout from `codex exec --json`. The tested local failure scenario exposed structured `turn.failed` / `error` signals, which can be mapped to the desktop pet `error` state without parsing human terminal text.

## Boundaries

V3.7 JSONL monitor is:

- project-owned structured monitoring.
- routed through `petctl codex launch --monitor jsonl`.
- limited to wrapper-launched `codex exec --json` sessions.
- the recommended path for Codex exec state mapping.

V3.7 JSONL monitor is not:

- official Codex hook lifecycle evidence.
- interactive Codex TUI coverage.
- OS-level Codex window binding.
- all Codex workflows verification.
- proof of `PostToolUse failure hook evidence passed`.

## State Mapping

| JSONL event type | Pet state | Rule |
| --- | --- | --- |
| `thread.started` | marker-only | Do not emit pet state. |
| `turn.started` | `thinking` | New turn started. |
| `item.started` | `running` | Tool/item execution started. |
| `item.completed` | marker / keep current | Single item completion is not task success. |
| `turn.completed` | `success` / `idle` | Only if the current turn has no error. |
| `turn.failed` | `error` | Structured failure. |
| `error` | `error` | Structured error. |

## Security Boundary

The monitor must not record:

```text
token
Authorization
raw JSONL payload
prompt text
tool command text
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## Allowed Claim

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
```

## Deprecated / Historical Claim

```text
V3.6 final acceptance blocked on real PostToolUse failure evidence; V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

## Forbidden Claims

```text
V3.6 selected Codex workflow hook coverage smoke passed
PostToolUse failure hook evidence passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```
