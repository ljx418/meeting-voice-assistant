# V4.7 Session Status Smoke Evidence

status: passed

date: 2026-05-27

## Commands

```bash
node scripts/v4_4_managed_session_smoke.mjs
node packages/petctl/dist/cli.js codex session status --json
```

## Result

The managed exec JSONL smoke passed and created sanitized managed session records. The status command returned:

| Field | Result |
| --- | --- |
| `ok` | true |
| `instanceId` | present |
| redacted `bindingId` | present, `binding_*` format |
| `mode` | `exec` |
| `monitor` | `jsonl` |
| `status` | `stale` after process exit |
| `lastEventKind` | `process.exit` |
| `lastSeenAt` | present |

## Automatic Checks

| Check | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed, 51 tests |
| `node scripts/v4_4_managed_session_smoke.mjs` | passed |

## Security Scan

No raw binding id, raw TTY, raw args, window title, path, prompt, tool command, raw hook payload, token, or Authorization is recorded in this evidence.

## Claim

Allowed:

```text
V4.7 managed session status and stale-binding diagnostics passed for tested local wrapper-launched scenarios.
```
