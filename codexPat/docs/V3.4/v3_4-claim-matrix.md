# V3.4 Claim Matrix

文档状态：final.

## Allowed Claims

| Claim | Preconditions |
| --- | --- |
| `V3.4 Codex hook wrapper fixture smoke passed.` | `scripts/v3_4_codex_hook_fixture_smoke.mjs` passed; no sensitive output. |
| `V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.` | real Codex lifecycle observed after `/hooks` trust; target cat states verified; security scan passed. |

Current decision: both claims are allowed after 2026-05-25 operator acceptance.

## Forbidden Claims

Forbidden as ready claims:

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

- Say `hook wrapper fixture smoke passed` when only fixture evidence exists.
- Say `tested local Codex hook scenarios` only after real lifecycle evidence.
- Do not imply exact model reasoning state.
- Do not imply arbitrary terminal windows are detected.
