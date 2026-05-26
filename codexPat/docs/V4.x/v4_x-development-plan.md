# V4.x Development Plan

status: planned

date: 2026-05-26

## Scope

V4.x is the macOS-first planning line for OS-level Codex window/session discovery and explicit pet binding.

The V4.x user need is:

```text
An already-open or active Codex terminal window should be discoverable as a candidate and, if feasible, explicitly bindable by the user to one desktop pet.
```

V4.x must distinguish two separate capabilities:

- discovery / binding: candidate terminal window or session identity can be associated with a `PetInstance`.
- state event source: Codex lifecycle state events that can be proven to belong to that bound session.

OS-level discovery alone cannot provide Codex lifecycle state events. V4.x must not describe window discovery as interactive Codex TUI monitoring.

## Current Baseline

V3.7 remains the default reliable Codex monitoring path:

```bash
node packages/petctl/dist/cli.js codex launch \
  --monitor jsonl \
  --name "Review Cat" \
  -- exec --json "summarize this repository"
```

V3.7 applies only to wrapper-launched `codex exec --json` sessions. It is not evidence for already-open window binding, interactive Codex TUI monitoring, or OS-level binding readiness.

## V4.0 Feasibility Questions

V4.0 must answer these questions before any implementation phase starts:

- Where would state events come from for an already-running Codex session?
- Does an already-running Codex session expose a stable `session_id`, TTY identity, hook registry, or other safe route key?
- If `AGENT_DESKTOP_PET_INSTANCE_ID` cannot be injected into the running session, must the user relaunch through the wrapper path?
- How can later events prove they belong to the user-confirmed bound session?
- Which terminal / Codex / macOS combinations are unsupported or no-go?

## Phase Plan

| Phase | Goal | Output | Acceptance Boundary |
| --- | --- | --- | --- |
| V4.0 | strict feasibility review | feasibility report, terminal matrix, permission/privacy model, safe fields, no-go scenarios, go/no-go | completed; no prototype, no binding, no routing |
| V4.1 | Terminal.app active window safe-field probe | Terminal.app probe evidence only | completed for Terminal.app; no binding claim, no state monitoring claim, no iTerm2/all-terminal claim |
| V4.2 | explicit preview / confirm binding UX | UX evidence for Terminal.app candidate-to-PetInstance binding | no silent bind, no PetEvent, no lifecycle monitoring claim |
| V4.3 | manual route-test prototype | scoped route-test smoke for validated Terminal.app binding | manual/test event only; no lifecycle routing claim |
| V4.x Final | scoped evidence closure | final report, regression, security scan, claim scan | no new features |

## V4.2 Binding UX Plan

V4.2 must use a two-step flow to prevent silent binding:

```bash
petctl codex bind active-window --terminal terminal --preview --json
petctl codex bind confirm --candidate <candidateId> --name "<cat name>" --json
```

If a single-command path is added later, it must require an explicit confirmation parameter. Without confirmation it must return `confirmation_required`.

Binding records must be stale-aware and include:

```text
bindingId
terminalAppName
terminalBundleId
processId
processName
codexCliVersion
ttySummary
sessionSummary
petInstanceId
candidateObservedAt
bindingCreatedAt
lastValidatedAt
expiresAt
bindingStatus
```

V4.2 must not save raw TTY, raw process args, window title, terminal text, prompt text, tool command text, shell history, screen contents, clipboard contents, token, Authorization, transcript_path, full `/Users` path, workspace path, config path, or `api-token.json`.

V4.2 must not send PetEvent. It only creates a user-confirmed association between a Terminal.app Codex candidate and a PetInstance.

## V4.3 Manual Route-test Plan

V4.3 must be implemented as an explicit manual route-test prototype:

```bash
petctl codex route test --binding <bindingId> --level running --json
```

Before sending the manual test event, V4.3 must revalidate:

- binding exists.
- terminalBundleId still matches.
- processId / classifier still valid where possible.
- ttySummary / sessionSummary still matches where possible.
- PetInstance still exists.

Failure reason codes:

```text
binding_not_found
binding_stale
candidate_not_active
terminal_mismatch
pet_instance_not_found
```

V4.3 must not fallback to default. The manual test event must affect only the bound PetInstance and must not be described as Codex lifecycle routing.

## Terminal Matrix Requirements

V4.0 terminal matrix must cover:

- Terminal.app
- iTerm2
- VS Code integrated terminal
- Warp
- Ghostty

Each terminal row must include:

| Field | Required Decision |
| --- | --- |
| active window detection | Can the focused terminal window be detected safely? |
| Codex process identification | Can a Codex CLI process be identified without reading terminal text? |
| TTY/session identity | Is a safe TTY/session identity available for routing? |
| event source availability | Is there a reliable lifecycle event source for that session? |
| privacy risk | Could detection expose terminal text, prompts, commands, paths, or screen contents? |
| permission requirement | Accessibility, Automation, terminal API, shell helper, or none. |
| verdict | supported candidate, prototype candidate, unsupported, or no-go. |

## Field Collection Boundary

Allowed fields:

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

## Permission And Privacy Rules

- OS-level discovery must be explicit opt-in.
- Accessibility, Automation, terminal-specific APIs, or shell helper setup must be documented before use.
- Binding must require explicit user confirmation.
- Evidence may record only safe fields, permission state, terminal verdicts, and go/no-go reasoning.
- Evidence must not include terminal text, prompts, commands, raw payloads, local paths, tokens, or config paths.

## Non-active Notes

Bundled assets, license files, renderer changes, 3D models, Rive / Live2D, custom asset imports, and action asset work are not V4.x active gates. They belong to V5.x and must not be used to pass V4.0-V4.3.

## Allowed Claims

V4.0:

```text
V4.0 OS-level Codex window/session binding feasibility review completed with scoped go/no-go decision.
```

V4.1, only if a probe is completed:

```text
V4.1 macOS active window safe-field probe completed for <terminal app> on tested local environment.
```

V4.2, only if preview / confirm binding evidence passes:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
```

V4.3, only if manual route-test evidence passes:

```text
V4.3 user-confirmed Terminal.app binding manual route-test prototype passed for tested local environment.
```

V4.x Final, only if V4.2 and V4.3 pass:

```text
V4.x Terminal.app scoped Codex candidate discovery, user-confirmed PetInstance binding, and explicit route-test prototype passed for tested local environment.
```

## Forbidden Claims

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
MCP ready
Windows ready
cross-platform ready
production signed release ready
```
