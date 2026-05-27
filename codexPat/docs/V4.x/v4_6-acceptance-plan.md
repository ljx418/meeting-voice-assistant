# V4.6 Managed Session Startup Diagnostics Acceptance Plan

status: completed

date: 2026-05-27

## Required Checks

- `pnpm --filter @agent-desktop-pet/petctl build`
- `pnpm --filter @agent-desktop-pet/petctl check`
- `pnpm --filter @agent-desktop-pet/petctl test`
- `node packages/petctl/dist/cli.js codex doctor --json`

## Acceptance Criteria

- `codex_cli` diagnostic reports passed when Codex CLI is available.
- `hook_config` diagnostic reports passed for the supported project hook schema.
- `hook_wrapper` diagnostic reports passed after syntax check.
- `desktop_health` diagnostic reports passed when the desktop bridge is running.
- `hook_trust_required` is a warning/instruction, not a lifecycle acceptance claim.
- `binding_env_missing` is a warning outside wrapper-launched children.
- Output does not leak token, Authorization header, raw hook payload, prompt text, tool command text, transcript path, config path, workspace path, or full local path.

## Allowed Claim

```text
V4.6 managed session startup diagnostics and UX hardening passed for tested local wrapper-launched scenarios.
```

## Forbidden Claims

```text
TUI hook mapping passed from diagnostics alone
interactive Codex TUI monitoring ready
OS-level binding ready
already-open Codex window auto-monitoring ready
all Codex workflows verified
```
