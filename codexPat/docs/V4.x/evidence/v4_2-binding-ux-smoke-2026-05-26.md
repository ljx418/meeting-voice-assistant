# V4.2 Binding UX Smoke Evidence

status: blocked-runtime-focus

date: 2026-05-26

## Scope

V4.2 implements Terminal.app-only preview / confirm candidate-to-PetInstance binding UX.

This evidence does not claim lifecycle monitoring, state routing, iTerm2 support, all-terminal support, or OS-level binding readiness.

## Commands

Automatic checks:

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
```

Runtime preview attempt:

```bash
node packages/petctl/dist/cli.js codex bind active-window --terminal terminal --preview --json
```

## Results

| Check | Result |
| --- | --- |
| petctl check | passed |
| petctl test | passed, 40 tests |
| petctl build | passed |
| preview does not create binding | passed in unit regression |
| confirm creates binding only after explicit candidate | passed in unit regression |
| expired candidate confirm fails | passed in unit regression |
| inactive candidate confirm fails | passed in unit regression |
| confirm avoids PetEvent endpoint | passed in unit regression |
| runtime focused Terminal.app preview | blocked / focused app was Chrome |

Runtime preview result summary:

```text
ok=false
reasonCode=unsupported_terminal
verdict=unsupported
permissionState=granted
observed safe app summary=Google Chrome / com.google.Chrome
```

## Acceptance Decision

status: blocked-runtime-focus

Reason:

- V4.2 implementation and automated checks passed.
- The runtime preview attempt did not have Terminal.app as the focused app.
- No runtime candidateId was produced, so runtime confirm acceptance could not be executed.

Allowed conclusion:

```text
V4.2 CLI-side preview / confirm binding UX implementation built and unit-tested; runtime acceptance blocked on focused Terminal.app Codex TUI evidence.
```

Forbidden conclusion:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
OS-level Codex window binding ready.
interactive Codex TUI monitoring ready.
```

## Security Review

Evidence and runtime summaries do not include:

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

## Manual Unblock Steps

1. Keep a Terminal.app window running Codex TUI.
2. In a second Terminal.app window, run:

```bash
cd <repo>
sleep 8; node packages/petctl/dist/cli.js codex bind active-window --terminal terminal --preview --json
```

3. During the 8 seconds, click the Codex TUI Terminal.app window.
4. Use the returned `candidateId`:

```bash
node packages/petctl/dist/cli.js codex bind confirm --candidate <candidateId> --name "V4.2 Cat" --json
```

V4.2 can only pass after both runtime preview and confirm succeed without sensitive output.
