# V3.5 Final Acceptance Report

status: passed

date: 2026-05-25

## Scope

V3.5 implemented Codex hook diagnostics and recovery checks through `petctl codex doctor` and a repeatable diagnostics smoke.

## Evidence Gate

Passed:

- `docs/V3.5/evidence/hook-diagnostics-smoke-2026-05-25.md`
- `scripts/v3_5_hook_diagnostics_smoke.mjs`

## Automatic Checks

| Command | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |
| `node scripts/v3_5_hook_diagnostics_smoke.mjs` | passed |

## Security Redaction

Passed. Diagnostics output does not print token, Authorization header, raw hook payload, config path, workspace path, full local path, or `api-token.json`.

## Claim Scan

Passed. V3.5 only allows the scoped diagnostics claim and does not expand hook mapping, real workflow coverage, MCP readiness, third-party integration, OS-level binding, or production readiness.

## Risk Assessment

| Risk | Level | Notes |
| --- | --- | --- |
| Development plan drift | Low | Implementation is limited to diagnostics and recovery visibility. |
| False-green acceptance | Low | Smoke covers hard failures and warnings separately; no fixture is used as real lifecycle evidence. |
| Claim expansion | Low | Claim matrix remains scoped to diagnostics. |
| Security redaction | Low | Smoke output redaction scan passed. |
| Regression coverage | Medium | V3.5 reran petctl checks and diagnostics smoke; broader runtime regression remains for V3.x Final. |

overall risk: Medium

go / no-go: go

## Allowed Claim

```text
V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.
```

## Final Decision

V3.5 final acceptance passed for scoped Codex hook diagnostics and recovery. No High risk remains, so V3.6 may proceed.
