# V4.3 Manual Route-test Smoke Evidence

status: passed

date: 2026-05-27

## Scope

V4.3 implements a Terminal.app-only manual route-test prototype for a V4.2 user-confirmed binding.

This evidence does not claim lifecycle monitoring, interactive Codex TUI monitoring, all-terminal support, or OS-level binding readiness.

## Commands

Automatic checks:

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
```

Runtime route-test requires a fresh binding:

```bash
node packages/petctl/dist/cli.js codex bind active-window --terminal terminal --preview --json
node packages/petctl/dist/cli.js codex bind confirm --candidate <candidateId> --name "V4.3 Cat" --json
node packages/petctl/dist/cli.js codex route test --binding <bindingId> --level running --json
```

## Results

| Check | Result |
| --- | --- |
| petctl check | passed |
| petctl test | passed, 43 tests |
| petctl build | passed |
| manual route-test only targets bound instance | passed in unit regression |
| unknown binding does not route | passed in unit regression |
| stale binding does not route | passed in unit regression |
| runtime desktop health | passed before route-test attempt |
| runtime route-test | passed |

Accepted runtime route-test summary:

```text
preview:
ok=true
candidateId=cand_e507effdf36648e5af194eb1
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
instanceId=codex_1779848119813
displayName=V4.2 Cat
bindingId=bind_70afb51d19394f4f931fe4bd
petInstanceId=codex_1779848119813
bindingStatus=active

route-test:
ok=true
eventId=evt_1779848188700_1
queued=true
instanceId=codex_1779848119813
bindingId=bind_70afb51d19394f4f931fe4bd
petInstanceId=codex_1779848119813
bindingStatus=active
```

Instance state summary after route-test:

```text
default instance currentState=idle
V3.4 Hook Cat currentState=success
old V4.2 Cat codex_1779846896461 currentState=idle
bound V4.3 route-test target codex_1779848119813 currentState=running
```

## Acceptance Decision

status: passed

Reason:

- V4.3 implementation and automated checks passed.
- A previously confirmed V4.2 binding had correctly become stale, so it could not be reused.
- A fresh Terminal.app candidate was produced, confirmed into `bindingId=bind_70afb51d19394f4f931fe4bd`, and route-tested successfully.
- Route-test affected only the bound PetInstance `codex_1779848119813`.
- Default and unrelated Codex pets remained unchanged.

Allowed conclusion:

```text
V4.3 user-confirmed Terminal.app binding manual route-test prototype passed for tested local environment.
```

Forbidden conclusion:

```text
interactive Codex TUI monitoring ready.
state lifecycle routing ready.
OS-level Codex window binding ready.
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

1. Keep desktop bridge running and healthy.
2. Keep a Terminal.app window running Codex TUI.
3. Generate a fresh candidate:

```bash
sleep 8; node packages/petctl/dist/cli.js codex bind active-window --terminal terminal --preview --json
```

4. During the 8 seconds, click the Codex TUI Terminal.app window.
5. Confirm immediately:

```bash
node packages/petctl/dist/cli.js codex bind confirm --candidate <candidateId> --name "V4.3 Cat" --json
```

6. Route-test immediately:

```bash
node packages/petctl/dist/cli.js codex route test --binding <bindingId> --level running --json
```

V4.3 passed after the route-test succeeded and evidence showed only the bound PetInstance was affected.
