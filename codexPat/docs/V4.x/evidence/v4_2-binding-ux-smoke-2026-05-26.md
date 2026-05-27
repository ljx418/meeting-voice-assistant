# V4.2 Binding UX Smoke Evidence

status: passed

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

Desktop health after starting desktop dev:

```bash
curl -sS http://127.0.0.1:17321/api/health
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
| desktop health | passed after starting desktop dev |
| runtime focused Terminal.app preview before desktop bridge | passed once; candidate produced |
| runtime confirm before desktop bridge | blocked / desktop_not_running |
| runtime focused Terminal.app preview after confirm fix | passed |
| runtime confirm after confirm fix | passed |

Runtime preview result summary:

```text
ok=false
reasonCode=unsupported_terminal
verdict=unsupported
permissionState=granted
observed safe app summary=Google Chrome / com.google.Chrome
```

Runtime preview once passed before desktop bridge:

```text
ok=true
candidateId=cand_3cf4d601421d414cbc937910
terminalAppName=Terminal
terminalBundleId=com.apple.Terminal
processId=933
processName=codex
codexCliVersion=codex-cli 0.131.0
ttySummary=tty_380ea400d2a8
sessionSummary=session_380ea400d2a8
bindingStatus=candidate
```

Accepted runtime preview and confirm after confirm revalidation fix:

```text
preview:
ok=true
candidateId=cand_851ef8c6b86a4bbd86b35593
terminalAppName=Terminal
terminalBundleId=com.apple.Terminal
processId=12613
processName=codex
codexCliVersion=codex-cli 0.131.0
ttySummary=tty_e6be0a5ac6b4
sessionSummary=session_e6be0a5ac6b4
bindingStatus=candidate

confirm:
ok=true
instanceId=codex_1779846896461
displayName=V4.2 Cat
windowLabel=pet-codex_1779846896461
bindingId=bind_ea708974960b49cfbd7ee847
petInstanceId=codex_1779846896461
bindingStatus=active
```

Runtime confirm before desktop bridge:

```text
ok=false
reasonCode=desktop_not_running
reason=fetch failed
```

Desktop health summary after starting desktop dev:

```text
ok=true
app=agent-desktop-pet
listenAddress=127.0.0.1:17321
```

Runtime preview after desktop bridge before confirm revalidation fix:

```text
ok=false
reasonCode=probe_unavailable
verdict=unavailable
permissionState=unknown
observed safe app summary=Terminal / com.apple.Terminal
```

## Acceptance Decision

status: passed

Reason:

- V4.2 implementation and automated checks passed.
- A runtime preview produced a sanitized candidate before the desktop bridge was running.
- Confirm could not complete until the desktop bridge was started.
- The first confirm attempt after a user-provided preview exposed an implementation flaw: confirm re-probed the focused terminal instead of revalidating the candidate process/TTY.
- Confirm revalidation was fixed to validate the candidate `processId`, Codex classifier, and redacted TTY/session summaries without requiring the Codex TUI to remain focused.
- Runtime confirm then succeeded and created `petInstanceId=codex_1779846896461`.

Allowed conclusion:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
```

Forbidden conclusion:

```text
OS-level Codex window binding ready.
interactive Codex TUI monitoring ready.
state lifecycle routing ready.
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

V4.2 passed after both runtime preview and confirm succeeded in the same live desktop session without sensitive output.
