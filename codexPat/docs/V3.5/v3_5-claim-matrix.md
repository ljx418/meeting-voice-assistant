# V3.5 Claim Matrix

文档状态：final

## Allowed Claim

| Claim | Preconditions | Evidence |
| --- | --- | --- |
| `V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.` | `petctl codex doctor` implemented; diagnostics smoke passed; petctl check/test passed; redaction scan passed. | `docs/V3.5/evidence/hook-diagnostics-smoke-2026-05-25.md` |

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

- Say `diagnostics and recovery smoke passed` only for the tested diagnostics scenarios.
- Do not imply new hook mappings were added.
- Do not imply real workflow coverage expanded in V3.5.
