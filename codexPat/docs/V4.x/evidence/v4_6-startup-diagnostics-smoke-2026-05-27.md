# V4.6 Startup Diagnostics Smoke Evidence

status: passed

date: 2026-05-27

## Command

```bash
node packages/petctl/dist/cli.js codex doctor --json
```

## Result

| Diagnostic | Result |
| --- | --- |
| Codex CLI | passed |
| Project hook config | passed |
| Hook wrapper syntax | passed |
| Binding env | warning: `binding_env_missing` outside wrapper child |
| Hook trust instruction | warning: `hook_trust_required` |
| Token source | passed, sanitized |
| Desktop health | passed |

## Automatic Checks

| Check | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed, 48 tests |

## Security Scan

No token, Authorization header, raw hook payload, prompt text, tool command text, transcript path, config path, workspace path, or full local path is recorded in this evidence.

## Claim

Allowed:

```text
V4.6 managed session startup diagnostics and UX hardening passed for tested local wrapper-launched scenarios.
```

Forbidden:

```text
TUI hook mapping passed from diagnostics alone
interactive Codex TUI monitoring ready
OS-level binding ready
already-open Codex window auto-monitoring ready
all Codex workflows verified
```
