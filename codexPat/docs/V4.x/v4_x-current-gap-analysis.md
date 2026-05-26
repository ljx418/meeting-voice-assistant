# V4.x Current Gap Analysis

status: v4-1-terminal-app-passed-v4-2-planned

date: 2026-05-26

## Current State

Current supported Codex monitoring is V3.7:

```bash
petctl codex launch --monitor jsonl --name "<cat>" -- exec --json "<prompt>"
```

This requires launching Codex through the project wrapper and only covers wrapper-launched `codex exec --json` sessions.

V4.0 feasibility review is complete:

- `docs/V4.x/v4_0-os-binding-feasibility-review.md`

V4.0 accepted only scoped feasibility. It did not implement active window probe, binding UX, selected-terminal routing, or state monitoring.

V4.1 Terminal.app safe-field probe is passed for the tested local environment:

- `docs/V4.x/evidence/v4_1-safe-field-probe-2026-05-26.md`
- `docs/V4.x/v4_1-final-acceptance-report.md`

V4.1 does not prove iTerm2, VS Code, Warp, Ghostty, lifecycle monitoring, or OS-level binding readiness.

## Primary Gap

The project cannot currently:

- discover an already-open Codex terminal window beyond the Terminal.app candidate evidence accepted in V4.1.
- safely associate a focused terminal/session with a `PetInstance`.
- inject `AGENT_DESKTOP_PET_INSTANCE_ID` into an already-running Codex session.
- prove that later lifecycle events belong to a user-confirmed bound session.
- monitor interactive Codex TUI state through OS-level discovery.
- claim OS-level Codex window binding ready.

## Discovery vs Event Source Gap

V4.x must not treat window discovery as state monitoring.

| Area | Current | Needed Answer | Status |
| --- | --- | --- | --- |
| Candidate discovery | Terminal.app CLI probe built, unit-tested, and runtime accepted | Can active terminal window/session be identified using safe fields? | V4.1 passed for Terminal.app only |
| Candidate binding | CLI implementation built and unit-tested; runtime acceptance blocked on Terminal.app focus | Can user explicitly bind a candidate to a `PetInstance` without silent binding? | V4.2 blocked-runtime-focus |
| State event source | V3.7 wrapper JSONL only | What event source exists for already-running sessions? | V4.0 accepted: OS discovery alone is not an event source |
| Manual route-test | Not implemented | Can a validated binding route an explicit manual test event only to the bound pet? | planned V4.3 Terminal.app-only manual route-test |
| Event ownership proof | Not implemented | Can lifecycle events be proven to belong to the bound session? | no-go from OS discovery alone |
| Existing session env injection | Not supported | If env injection is impossible, should user relaunch through wrapper? | V4.0 accepted: use V3.7 wrapper fallback |

## Terminal Matrix Gap

V4.0 must evaluate Terminal.app, iTerm2, VS Code integrated terminal, Warp, and Ghostty with these fields:

- active window detection.
- Codex process identification.
- TTY/session identity.
- event source availability.
- privacy risk.
- permission requirement.
- verdict.

## Field Boundary Gap

Allowed fields are limited to:

```text
terminal app name / bundle id
window id or redacted summary
process id
process name
Codex CLI version
TTY id redacted summary
session id redacted summary
permission granted/denied
```

Forbidden fields:

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
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## Main Risks

| Risk | Level | Notes |
| --- | --- | --- |
| Event source absence | High | Already-running interactive Codex sessions may not expose routeable lifecycle events. |
| False binding | High | Active window or process metadata may not uniquely identify a Codex session. |
| Privacy leakage | High | OS-level probes can expose text, prompts, paths, commands, or screen contents. |
| Terminal fragmentation | High | Terminal.app, iTerm2, VS Code, Warp, and Ghostty expose different capabilities. |
| False-green claim | High | Probe evidence cannot imply OS-level binding readiness. |
| Permission burden | Medium | Accessibility and Automation permissions require clear user consent. |

overall risk: Medium after V4.0 scoped feasibility decision

## V4.1 Runtime Gap Update

The observed Terminal.app failure had two layers:

- The original `codex_process_not_found` was caused by Codex CLI v0.131.0 appearing as same-TTY `node` processes instead of a direct `codex` process name. V4.1 now covers Node-packaged Codex process detection with same-TTY PID scoping and classifier-only args inspection.
- A follow-up local probe with a focused Terminal.app Codex TUI returned `ok=true`, `processName=codex`, `codexCliVersion=codex-cli 0.131.0`, and `candidate_detected`.

go / no-go: V4.1 implementation built and unit-tested, including Node-packaged Codex detection. Terminal.app runtime acceptance passed for the tested local environment. Go for V4.2 planning from Terminal.app-only evidence; no-go for iTerm2/all-terminal claims, lifecycle monitoring claims, or OS-level binding readiness claims.

## V4.2 Gap

V4.2 must close only this gap:

```text
Terminal.app Codex candidate -> explicit user confirmation -> PetInstance binding record.
```

Required design constraints:

- two-step preview / confirm flow.
- `preview` must not create a binding.
- `confirm` must fail for expired or inactive candidates.
- binding records must include stale / TTL fields: `candidateObservedAt`, `bindingCreatedAt`, `lastValidatedAt`, `expiresAt`, and `bindingStatus`.
- V4.2 must not send PetEvent.
- V4.2 must not claim lifecycle monitoring.

Allowed V4.2 future claim:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
```

go / no-go: V4.2 implementation is built and unit-tested, but runtime acceptance is blocked because the local runtime preview observed Google Chrome instead of a focused Terminal.app Codex TUI. No-go for V4.3 implementation until V4.2 runtime preview and confirm pass, or the product owner explicitly accepts a blocked/no-go transition.

## V4.3 Gap

V4.3 must close only this gap:

```text
Validated Terminal.app binding -> explicit manual route-test event -> bound PetInstance only.
```

V4.3 does not close lifecycle monitoring, interactive TUI monitoring, or event source gaps.

Required design constraints:

- route-test must revalidate binding before delivery.
- failures must include `binding_not_found`, `binding_stale`, `candidate_not_active`, `terminal_mismatch`, and `pet_instance_not_found`.
- route-test must never fall back to default.
- evidence must prove default pet and other Codex pets remain unchanged.

Allowed V4.3 future claim:

```text
V4.3 user-confirmed Terminal.app binding manual route-test prototype passed for tested local environment.
```

go / no-go: Go for V4.3 planning only after V4.2 passes. No-go for implementation unless route-test is described as manual/test-only and not lifecycle routing.
