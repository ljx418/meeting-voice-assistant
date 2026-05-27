# V3.5 Hook Diagnostics Smoke Evidence

date: 2026-05-25

status: passed

## Commands

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
node scripts/v3_5_hook_diagnostics_smoke.mjs
```

## Results

| Case | Result |
| --- | --- |
| petctl check | passed |
| petctl test | passed |
| petctl build | passed |
| petctl dist exists | passed |
| `petctl codex doctor` exits 0 for valid diagnostics | passed |
| hook config diagnostic | passed |
| hook wrapper diagnostic | passed |
| instance env diagnostic | passed |
| Codex CLI diagnostic present | passed |
| desktop health diagnostic present | passed |
| missing instance env warning | passed |
| invalid instance env fails safely | passed |
| missing hook config fails safely | passed |
| redaction scan | passed |

## Security

Smoke output did not contain token, Authorization header, raw hook stdin, raw payload, prompt text, tool input command, config path, workspace path, full local path, or `api-token.json`.

## Claim Boundary

This evidence allows:

```text
V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.
```

It does not allow all Codex workflows verified, OS-level Codex window binding ready, Claude Code integration verified, MCP ready, third-party agent integration verified, or production readiness claims.
