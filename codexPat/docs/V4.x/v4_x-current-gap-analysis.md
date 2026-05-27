# V4.x Current Gap Analysis

status: v4-5-preflight-passed-lifecycle-pending

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
| Candidate binding | CLI implementation built, unit-tested, and runtime accepted for Terminal.app | Can user explicitly bind a candidate to a `PetInstance` without silent binding? | V4.2 passed Terminal.app-only |
| State event source | V3.7 wrapper JSONL only | What event source exists for already-running sessions? | V4.0 accepted: OS discovery alone is not an event source |
| Manual route-test | CLI implementation built, unit-tested, and runtime accepted for Terminal.app manual route-test | Can a validated binding route an explicit manual test event only to the bound pet? | V4.3 passed Terminal.app-only |
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

go / no-go: V4.2 implementation is built, unit-tested, and runtime accepted for Terminal.app candidate-to-PetInstance binding UX. Go for V4.3 stage planning and audit from Terminal.app-only evidence. No-go for lifecycle monitoring, OS-level binding readiness, iTerm2/all-terminal claims, or V4.3 implementation before its own PRD review and plan audit.

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

go / no-go: V4.3 implementation is built, unit-tested, and runtime accepted for Terminal.app manual route-test. Go for V4.x Final acceptance evidence closure. No-go for lifecycle monitoring, OS-level binding readiness, iTerm2/all-terminal claims, or additional feature work during final acceptance.

## V4.x Final Status

V4.x final acceptance passed for the scoped managed-session and Terminal.app prototype line:

```text
V4.x managed Codex session-to-PetInstance state mapping passed for tested local wrapper-launched exec JSONL and scoped managed TUI hook scenarios, with Terminal.app candidate binding and manual route-test prototype accepted.
```

Remaining gaps:

- no broad interactive Codex TUI monitoring readiness.
- no lifecycle event routing from OS discovery.
- no OS-level Codex window binding readiness.
- no iTerm2, VS Code integrated terminal, Warp, or Ghostty support claim.
- no all-terminal or cross-platform claim.

V3.7 remains the default reliable Codex state monitoring path for wrapper-launched `codex exec --json` sessions.

## V4.4 Managed Session Update

V4.4 adds a user-facing managed session entry for the reliable JSONL path:

```bash
node packages/petctl/dist/cli.js codex session start \
  --mode exec \
  --monitor jsonl \
  --name "Review Cat" \
  -- codex exec --json "task"
```

Closed gap:

- managed exec JSONL session creates one PetInstance.
- wrapper injects `AGENT_DESKTOP_PET_INSTANCE_ID`.
- wrapper injects redacted `AGENT_DESKTOP_PET_BINDING_ID`.
- structured JSONL state maps to the managed session cat.
- simple / tool-success / tool-failure scenarios passed.

Remaining gap:

- managed TUI wrapper preflight passed, and real hooks passed for `UserPromptSubmit`, `PreToolUse`, and `Stop` in the tested wrapper-launched local scenario. `PermissionRequest` was not observed because local policy did not emit it.
- arbitrary already-open Codex TUI windows still cannot be automatically monitored.
- OS-level discovery still is not a state event source.

Allowed V4.4 scoped claim:

```text
V4.4 managed Codex exec JSONL state mapping passed for tested local wrapper-launched scenario.
```

## V4.5 Managed TUI Hook Update

Current status:

```text
V4.5 managed Codex TUI hook state mapping passed for UserPromptSubmit, PreToolUse, and Stop in tested local wrapper-launched scenario; PermissionRequest remains blocked by local policy.
```

Accepted real lifecycle path:

- start managed TUI through `petctl codex session start --mode tui --monitor hooks`.
- run `/hooks` inside Codex TUI.
- review/trust project hooks.
- submit a real prompt.
- trigger tool use.
- trigger permission request if local policy allows; this was not observed in the tested local run.
- let the turn stop.
- confirm target cat changes.
- confirm default and unrelated pets remain unchanged.

Required real lifecycle evidence:

- `UserPromptSubmit -> thinking`.
- `PreToolUse -> running`.
- `Stop -> success` / idle marker.
- `PermissionRequest -> need_input`, or blocked by local policy. The tested local run did not emit this event.
- no curl, no manual `petctl notify`, no fixture smoke as lifecycle evidence.
- no terminal text parsing, no `transcript_path`, no raw hook payload, no prompt text, no tool command text.

## V4.6 UX Hardening

Current status:

```text
V4.6 managed session startup diagnostics and UX hardening passed for tested local wrapper-launched scenarios.
```

Allowed scope:

- desktop health preflight.
- hooks config check.
- wrapper script check.
- Codex CLI check.
- clear "run `/hooks` and trust hooks" instruction.
- stable reasonCode.

Recommended reasonCode:

```text
desktop_not_running
hook_config_missing
hook_wrapper_missing
hook_trust_required
hook_lifecycle_not_observed
codex_not_found
pet_instance_create_failed
binding_env_missing
```

Allowed claim:

```text
V4.6 managed session startup diagnostics and UX hardening passed for tested local wrapper-launched scenarios.
```

Forbidden expansion:

- TUI hook mapping passed.
- interactive Codex TUI monitoring ready.
- OS-level binding ready.

## V4.7 Session Status

Current status:

```text
V4.7 managed session status and stale-binding diagnostics passed for tested local wrapper-launched scenarios.
```

Allowed scope:

```bash
petctl codex session status --json
```

Allowed fields:

- `instanceId`
- redacted `bindingId`
- `mode`
- `monitor`
- `status` as `active` / `stale` / `unknown`
- `lastEventKind`
- `lastSeenAt`

Forbidden fields:

- raw TTY
- raw args
- window title
- path
- prompt
- tool command
- raw hook payload
- token
- Authorization

Allowed claim:

```text
V4.7 managed session status and stale-binding diagnostics passed for tested local wrapper-launched scenarios.
```

## V4.x Final Boundary

```text
V4.x managed Codex session-to-PetInstance state mapping passed for tested local wrapper-launched exec JSONL and scoped managed TUI hook scenarios, with Terminal.app candidate binding and manual route-test prototype accepted.
```

Still forbidden:

- OS-level Codex window binding ready.
- already-open Codex window auto-monitoring ready.
- interactive Codex TUI monitoring ready.
- all Codex workflows verified.
- production signed release ready.
