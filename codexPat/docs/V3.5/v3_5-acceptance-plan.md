# V3.5 Acceptance Plan

文档状态：implemented

## Required Gates

| Gate | Required result |
| --- | --- |
| `petctl codex doctor --json` | reports sanitized diagnostics |
| hook config diagnostic | passed for current project |
| hook wrapper diagnostic | passed for current project |
| missing instance env | warning, not false pass |
| invalid instance env | failed with `instance_id_invalid` |
| missing hook config | failed with safe reason |
| redaction scan | no token, Authorization, raw payload, config path, workspace path, full local path, or `api-token.json` |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed |
| `node scripts/v3_5_hook_diagnostics_smoke.mjs` | passed |

## Allowed Claim

```text
V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.
```

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
