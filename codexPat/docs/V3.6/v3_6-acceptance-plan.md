# V3.6 Acceptance Plan

文档状态：historical blocked；deprecated active strategy

## Required Gates

| Gate | Required result | Current result |
| --- | --- | --- |
| simple answer real Codex workflow | passed | passed |
| tool success real Codex workflow | passed | passed |
| tool failure real Codex workflow | `PostToolUse failure -> error`, not overwritten by `Stop` | blocked |
| PermissionRequest real Codex workflow | `PermissionRequest -> need_input` | not-run |
| V3.4 fixture regression | passed | passed |
| V3.1 runtime regression | passed | passed |
| V3.3 binding regression | passed | passed |
| petctl check/test | passed | passed |

## Blocker

In the tested local Codex `exec` failure scenario, the `PostToolUse` hook payload exposed safe field names including `cwd`, `hook_event_name`, `model`, `permission_mode`, `session_id`, and `tool_input`, but no stable exit code/status/result field.

Because V3.x forbids parsing terminal text and treating `transcript_path` as a stable interface, this stage cannot safely claim real failure mapping.

Strategy update: V3.6 hook-only monitoring is deprecated as the active strategy. V3.7 JSONL monitor is now the recommended Codex exec monitoring path for supported wrapper-launched `codex exec --json` sessions.

## Allowed Claim

No V3.6 pass claim is allowed while status is historical blocked.

Allowed historical / strategy claim:

```text
V3.6 final acceptance blocked on real PostToolUse failure evidence; V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

## Forbidden Claims

```text
V3.6 selected Codex workflow hook coverage smoke passed for tested local scenarios
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
all Codex workflows verified
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```
