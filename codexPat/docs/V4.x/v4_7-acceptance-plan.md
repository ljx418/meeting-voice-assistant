# V4.7 Managed Session Status Acceptance Plan

status: completed

date: 2026-05-27

## Required Checks

- `pnpm --filter @agent-desktop-pet/petctl build`
- `pnpm --filter @agent-desktop-pet/petctl check`
- `pnpm --filter @agent-desktop-pet/petctl test`
- `node scripts/v4_4_managed_session_smoke.mjs`
- `node packages/petctl/dist/cli.js codex session status --json`

## Acceptance Criteria

- Status command returns `ok: true`.
- Output includes only allowed sanitized fields.
- `bindingId` is redacted and does not expose raw binding id.
- Completed managed exec session reports `stale` after process exit.
- `lastEventKind` uses structured JSONL event names or managed process marker only.
- Output does not include raw TTY, raw args, window title, path, prompt, tool command, raw hook payload, token, or Authorization.

## Allowed Claim

```text
V4.7 managed session status and stale-binding diagnostics passed for tested local wrapper-launched scenarios.
```

## Forbidden Claims

```text
interactive Codex TUI monitoring ready
OS-level Codex window binding ready
already-open Codex window auto-monitoring ready
all Codex workflows verified
```
