# V4.4 Claim Matrix

status: planned

date: 2026-05-27

## Allowed Claims

| Claim | Condition |
| --- | --- |
| `V4.4 managed Codex exec JSONL state mapping passed for tested local wrapper-launched scenario.` | Managed exec JSONL smoke passes. |
| `V4.4 managed Codex TUI hook state mapping passed for tested local wrapper-launched scenario.` | Real trusted TUI hook lifecycle evidence passes. |
| `V4.4 managed Codex session-to-PetInstance binding with scoped state mapping passed for tested local wrapper-launched scenarios.` | Both accepted scoped event sources pass, or final report explicitly scopes to the source that passed. |

## Forbidden Claims

Forbidden as ready / passed:

```text
OS-level Codex window binding ready
already-open Codex window auto-monitoring ready
interactive Codex TUI monitoring ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
PostToolUse failure hook evidence passed
cross-platform ready
Windows ready
production signed release ready
```

## Claim Boundary

V4.4 is a managed-launch state mapping phase. It does not upgrade V4.3 Terminal.app candidate binding into lifecycle monitoring.
