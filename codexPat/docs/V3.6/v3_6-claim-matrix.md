# V3.6 Claim Matrix

文档状态：historical blocked；deprecated active strategy

## Allowed Claims

No V3.6 pass claim is currently allowed.

Allowed historical / strategy claim:

```text
V3.6 final acceptance blocked on real PostToolUse failure evidence; V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
```

## Blocked Claim

| Claim | Status | Reason |
| --- | --- | --- |
| `V3.6 selected Codex workflow hook coverage smoke passed for tested local scenarios.` | blocked | Real tool failure workflow did not expose stable failure fields in `PostToolUse` hook payload. |

## Forbidden Claims

```text
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

## Wording Rules

- Say `V3.6 blocked on real PostToolUse failure evidence`.
- Say V3.6 hook-only monitoring is deprecated as the active strategy.
- Say V3.7 JSONL monitor is the current recommended path for supported wrapper-launched `codex exec --json`.
- Do not say `V3.6 selected workflow coverage passed`.
- Do not use fixture evidence as a substitute for real failure workflow evidence.
