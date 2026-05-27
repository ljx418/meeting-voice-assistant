# V4.x Final Claim And Security Scan

status: passed

date: 2026-05-27

## Claim Scan

Allowed final claim:

```text
V4.x Terminal.app scoped Codex candidate discovery, user-confirmed PetInstance binding, and explicit route-test prototype passed for tested local environment.
```

Forbidden claims must appear only in forbidden / not-ready context:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
state lifecycle routing ready
lifecycle event routing from OS discovery
all terminal apps supported
iTerm2 support passed
VS Code support passed
Warp support passed
Ghostty support passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
```

## Security Scan

Evidence must not include:

```text
raw TTY
raw process args
window title
terminal text
prompt text
tool command text
shell history
screen contents
clipboard contents
token
Authorization
transcript_path
full local path
workspace path
config path
api-token.json
```

## Scan Result

Automatic scan commands:

```bash
rg -n "/Users/|Authorization|api-token\\.json|raw payload|raw process args|raw TTY|transcript_path|workspace path|config path" docs/V4.x
```

Result:

- Matches appear in forbidden-field lists, no-read/no-save rules, or risk descriptions.
- Accepted runtime evidence summaries use redacted `ttySummary` / `sessionSummary`.
- No token, Authorization header value, raw payload, raw process args, raw TTY, transcript path, full local path, workspace path value, config path value, or `api-token.json` content is recorded as evidence.

Claim scan result:

- Allowed V4.0 / V4.1 / V4.2 / V4.3 scoped claims are present with tested Terminal.app boundaries.
- Forbidden claims appear only in forbidden / not-ready / no-go contexts.
