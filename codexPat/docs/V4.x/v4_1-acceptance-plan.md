# V4.1 Acceptance Plan

status: passed-terminal-app

date: 2026-05-26

## Acceptance Principle

V4.1 can only pass as an active window safe-field probe for a scoped terminal app. It cannot pass by proving binding, routing, lifecycle monitoring, or all-terminal support.

V4.1 must be accepted separately for:

- Terminal.app.
- iTerm2.

One terminal passing must not imply the other terminal passed.

## Future Runtime Acceptance

When implementation begins, V4.1 must cover:

| Case | Expected Result |
| --- | --- |
| Terminal.app focused | returns safe field summary or safe unsupported reason |
| iTerm2 focused | returns safe field summary or safe unsupported reason |
| unsupported active app | returns `unsupported_terminal` |
| permission denied | returns `permission_denied` and prints no raw OS data |
| Codex process not found | returns `codex_process_not_found` |
| Node-packaged Codex CLI on focused terminal TTY | detects Codex only when same-TTY Node candidate has Codex-specific args signature; prints no raw args |
| unrelated Node process on focused terminal TTY | returns `codex_process_not_found` |
| no TTY/session identity | returns `session_identity_unavailable` |
| `--json` output | contains only allowed fields |

## Allowed Fields

```text
ok
terminalAppName
terminalBundleId
windowSummary
processId
processName
codexCliVersion
ttySummary
sessionSummary
permissionState
verdict
reasonCode
```

## Forbidden Fields And Evidence Content

Evidence must not contain:

```text
terminal text
prompt text
tool command text
shell history
screen contents
clipboard contents
token
Authorization
raw payload
raw OS probe output
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## Claim Acceptance

Allowed future V4.1 claim, only after runtime evidence:

```text
V4.1 macOS active window safe-field probe completed for <terminal app> on tested local environment.
```

Forbidden claims:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
all Codex workflows verified
Codex internal reasoning exact mapping ready
Windows ready
cross-platform ready
production signed release ready
```

## Planning Acceptance

Current V4.1 planning may proceed to implementation only if:

- `v4_1-prd-spec-review.md` has no critical or major mismatch.
- `v4_1-plan-audit.md` has no open critical or major finding.
- false-green risk is not High.
- implementation remains read-only and CLI-side.
- V4.1 still excludes binding, routing, PetEvent emission, and desktop UI.

## Current Acceptance Decision

status: passed for Terminal.app; iTerm2 remains blocked

Evidence:

- `docs/V4.x/evidence/v4_1-safe-field-probe-2026-05-26.md`
- `docs/V4.x/v4_1-final-acceptance-report.md`

Reason:

- CLI implementation built and unit-tested.
- Node-packaged Codex CLI process detection was fixed and covered by regression tests.
- Terminal.app runtime probe passed with a focused Terminal.app Codex TUI.
- iTerm2 runtime probe was blocked because probe was unavailable in the local environment.
- Terminal.app is the only terminal-specific runtime probe accepted in this evidence.

V4.1 may claim a completed safe-field probe for Terminal.app only. It must not claim iTerm2 support, all-terminal support, binding, routing, or lifecycle monitoring.
