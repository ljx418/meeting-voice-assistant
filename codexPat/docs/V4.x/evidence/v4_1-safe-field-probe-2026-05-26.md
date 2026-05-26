# V4.1 Safe-field Probe Evidence

status: passed-terminal-app

date: 2026-05-26

## Scope

V4.1 implementation attempted a CLI-side read-only active window safe-field probe for:

- Terminal.app
- iTerm2

This evidence does not claim binding, routing, lifecycle monitoring, or OS-level readiness.

## Commands

Build and checks:

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
```

Runtime probes:

```bash
node packages/petctl/dist/cli.js codex probe active-window --terminal terminal --json
node packages/petctl/dist/cli.js codex probe active-window --terminal iterm2 --json
```

Regression fix run:

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
node packages/petctl/dist/cli.js codex probe active-window --terminal terminal --json
```

## Results

| Check | Result |
| --- | --- |
| petctl check | passed |
| petctl test | passed, 33 tests including Node-packaged Codex CLI detection and local `codex.js` false-positive guard |
| petctl build | passed |
| Node-packaged Codex process detection | passed in unit regression |
| Terminal.app runtime probe | passed for focused Terminal.app Codex TUI |
| iTerm2 runtime probe | blocked / probe unavailable |

Initial Terminal.app probe result summary:

```text
ok=false
reasonCode=unsupported_terminal
verdict=unsupported
permissionState=granted
observed safe app summary=Google Chrome / com.google.Chrome
```

Accepted Terminal.app probe result summary:

```text
ok=true
exitCode=0
terminalAppName=Terminal
terminalBundleId=com.apple.Terminal
windowSummary=focused-window
processId=75164
processName=codex
ttySummary=tty_7823ab0aeb81
sessionSummary=session_7823ab0aeb81
permissionState=granted
codexCliVersion=codex-cli 0.131.0
verdict=candidate
reasonCode=candidate_detected
```

Regression note:

- A manually observed Terminal.app Codex session exposed Codex as same-TTY `node` processes instead of a `codex` process name.
- The V4.1 probe was updated to inspect only same-TTY Node-wrapper candidate PIDs with `ps -p <pid> -o args=` for internal classification.
- Raw process args are not emitted. Successful matches are normalized to `processName=codex`.
- Unrelated same-TTY Node processes remain `codex_process_not_found`.

iTerm2 probe result summary:

```text
ok=false
reasonCode=probe_unavailable
verdict=unavailable
permissionState=unknown
observed safe app summary=iTerm2 / com.googlecode.iterm2
```

## Acceptance Decision

status: passed for Terminal.app; iTerm2 remains blocked

Reason:

- The original `codex_process_not_found` failure was traced to Node-packaged Codex CLI process naming and covered by unit regression.
- A follow-up manual runtime run with a focused Terminal.app Codex TUI returned `ok=true` and `candidate_detected`.
- iTerm2 probe was unavailable in the current local environment.
- Runtime evidence demonstrates a passed safe-field probe for Terminal.app only.

Allowed conclusion:

```text
V4.1 macOS active window safe-field probe completed for Terminal.app on tested local environment.
```

Forbidden conclusion:

```text
V4.1 macOS active window safe-field probe completed for iTerm2 on tested local environment.
V4.1 macOS active window safe-field probe completed for all terminal apps.
OS-level Codex window binding ready.
```

Terminal.app is now allowed as a terminal-specific scoped claim. The iTerm2 claim remains forbidden.

## Security Review

Evidence and runtime summaries do not include:

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
full local path
workspace path
config path
api-token.json
```

## Claim Review

V4.1 Terminal.app safe-field probe passed for the tested local environment. iTerm2 remains blocked and must not be generalized from Terminal.app evidence.

V4.2 may be planned from Terminal.app-only evidence, but it must not claim iTerm2 support, OS-level binding readiness, or lifecycle monitoring.
