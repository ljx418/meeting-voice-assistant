# V3.3 Claim Matrix

文档状态：final；Codex window/session binding scoped claims.

## Allowed Claim

| Claim | Preconditions | Evidence |
| --- | --- | --- |
| `V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.` | `petctl codex launch` smoke passed; session A/B routes isolated; success/error lifecycle states verified; security scan passed. | `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md` |

## Historical / Superseded Claims

The earlier V3.3 Claude Code hook track is no longer the active V3.3 target.

| Claim | Status | Notes |
| --- | --- | --- |
| `V3.3 Claude Code hook Notification -> need_input smoke passed for tested local Claude Code hook scenario.` | not allowed | Historical V3.3 hook evidence failed; project abandoned Claude Code adaptation for this stage. |

## Forbidden Claims

The following claims remain forbidden as ready claims:

```text
OS-level Codex window binding ready
all Codex workflows verified
Claude Code integration verified
Claude Code all workflows verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```

## Wording Rules

- Say `window/session-to-pet binding smoke passed for tested local macOS terminal scenarios`.
- Do not say unqualified `OS-level Codex window binding ready`.
- Do not imply arbitrary Codex terminal windows are detected without `petctl codex launch`.
- Do not imply Claude Code is verified.
