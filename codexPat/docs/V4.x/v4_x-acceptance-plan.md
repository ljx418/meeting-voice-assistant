# V4.x Acceptance Plan

status: v4-1-terminal-app-passed-v4-2-planned

date: 2026-05-26

## Acceptance Principle

V4.x cannot pass by repeating V3.7 wrapper-launched JSONL monitor evidence.

V4.x also cannot pass by detecting a terminal window alone. Discovery / binding and state event source are separate gates:

- discovery / binding answers which candidate window or session can be associated with a `PetInstance`.
- state event source answers where lifecycle events come from and how they are proven to belong to that bound session.

V4.0 is feasibility only. V4.1 has accepted Terminal.app safe-field probe evidence. V4.2 and V4.3 remain planned and must not expand V4.1 into binding readiness or lifecycle monitoring.

## Phase Acceptance Gates

| Phase | Required Result | Explicitly Out Of Scope |
| --- | --- | --- |
| V4.0 | feasibility report, terminal matrix, permission model, privacy model, safe identity fields, unsupported/no-go scenarios, go/no-go decision | active window probe, user binding UX, selected-terminal routing |
| V4.1 | Terminal.app active window safe-field probe evidence | binding ready, lifecycle monitoring, multi-terminal claim |
| V4.2 | explicit preview / confirm Terminal.app candidate-to-PetInstance binding UX evidence | silent auto-bind, PetEvent emission, state routing claim |
| V4.3 | manual route-test prototype for a validated Terminal.app binding | lifecycle routing, all terminal support, interactive TUI monitoring ready |
| V4.x Final | evidence closure, regression, security scan, claim scan | new feature work |

## V4.0 Required Evidence

Accepted file:

- `docs/V4.x/v4_0-os-binding-feasibility-review.md`

V4.0 evidence must include:

- `docs/V4.x/v4_0-development-plan.md`.
- `docs/V4.x/v4_0-acceptance-plan.md`.
- `docs/V4.x/v4_0-prd-spec-review.md`.
- `docs/V4.x/v4_0-plan-audit.md`.
- feasibility report.
- terminal app matrix for Terminal.app, iTerm2, VS Code integrated terminal, Warp, and Ghostty.
- permission model for Accessibility, Automation, terminal APIs, shell helper, and local helper processes.
- privacy model and redaction rules.
- allowed and forbidden field list.
- unsupported / no-go scenarios.
- answers for state event source, session identity, `AGENT_DESKTOP_PET_INSTANCE_ID` injection, and event ownership proof.
- scoped go / no-go decision.
- claim scan showing forbidden claims are not used as ready / passed.

Allowed V4.0 claim:

```text
V4.0 OS-level Codex window/session binding feasibility review completed with scoped go/no-go decision.
```

V4.0 decision:

- Go for V4.1 planning for Terminal.app and iTerm2 safe-field probe only.
- No-go for V4.3 selected-terminal routing from OS-level discovery alone.
- No-go for interactive Codex TUI monitoring ready.

## V4.1 Accepted Evidence

Accepted files:

- `docs/V4.x/evidence/v4_1-safe-field-probe-2026-05-26.md`
- `docs/V4.x/v4_1-final-acceptance-report.md`

Allowed V4.1 claim:

```text
V4.1 macOS active window safe-field probe completed for Terminal.app on tested local environment.
```

V4.1 does not prove:

```text
binding ready
lifecycle monitoring
iTerm2 support
VS Code support
Warp support
Ghostty support
OS-level Codex window binding ready
```

## V4.2 Acceptance Gate

V4.2 must prevent silent binding. The planned command flow is:

```bash
petctl codex bind active-window --terminal terminal --preview --json
petctl codex bind confirm --candidate <candidateId> --name "<cat name>" --json
```

If a future implementation keeps a single command, missing explicit confirmation must return:

```text
confirmation_required
```

V4.2 binding records must include:

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

V4.2 must pass these cases:

- `preview` does not create a binding.
- `confirm` creates or links the binding only after explicit user confirmation.
- expired candidate confirm fails safely.
- closed terminal candidate confirm fails safely.
- non-Terminal.app and non-Codex candidate fail safely.
- output and evidence contain no forbidden fields.
- V4.2 does not send PetEvent.
- V4.2 does not claim lifecycle monitoring.

Allowed V4.2 claim:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
```

## V4.3 Acceptance Gate

V4.3 is a manual route-test prototype only. The planned command flow is:

```bash
petctl codex route test --binding <bindingId> --level running --json
```

Before route-test delivery, V4.3 must revalidate:

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

V4.3 must pass these cases:

- event only affects the bound PetInstance.
- default pet remains unchanged.
- other Codex pets remain unchanged.
- unknown binding does not route.
- stale binding does not route.
- terminal mismatch does not route.
- missing PetInstance does not route.
- output and evidence contain no forbidden fields.

V4.3 must never fallback to default.

Allowed V4.3 claim:

```text
V4.3 user-confirmed Terminal.app binding manual route-test prototype passed for tested local environment.
```

V4.3 must not claim:

```text
interactive Codex TUI monitoring ready
state lifecycle routing ready
OS-level Codex window binding ready
already-open Codex window auto-detection ready
```

## Terminal Matrix Fields

Each terminal row must include:

| Field | Requirement |
| --- | --- |
| active window detection | Whether focused terminal detection is possible without reading terminal text. |
| Codex process identification | Whether Codex CLI process identity can be determined safely. |
| TTY/session identity | Whether a redacted TTY/session identity can be used as a route key. |
| event source availability | Whether reliable lifecycle events are available for that session. |
| privacy risk | Risk level and reason. |
| permission requirement | Required OS / terminal / shell permissions. |
| verdict | supported candidate, prototype candidate, unsupported, or no-go. |

## Field And Redaction Gate

Allowed V4.1 probe fields:

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

Allowed V4.2/V4.3 binding fields:

```text
bindingId
terminal app name / bundle id
process id
process name
Codex CLI version
TTY id redacted summary
session id redacted summary
PetInstance id
candidateObservedAt
bindingCreatedAt
lastValidatedAt
expiresAt
bindingStatus
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
raw TTY
raw process args
window title
transcript_path
full /Users path
workspace path
config path
api-token.json
```

## V3.7 Non-regression

V4.x must preserve V3.7 as the default reliable path:

```bash
node scripts/v3_7_codex_exec_jsonl_monitor_smoke.mjs
```

V4.x must not describe V3.7 evidence as:

```text
already-open window binding
interactive Codex TUI monitoring
OS-level binding ready
```

## V4.x Final Acceptance

V4.x Final must not add features. It must close evidence, regression, PRD review, security scan, and claim scan.

Allowed final claim, only after V4.2 and V4.3 pass:

```text
V4.x Terminal.app scoped Codex candidate discovery, user-confirmed PetInstance binding, and explicit route-test prototype passed for tested local environment.
```

Final report must explicitly state the project still does not support:

```text
interactive Codex TUI monitoring
already-open Codex auto-detection ready
lifecycle event routing from OS discovery
all terminal apps
iTerm2 / VS Code / Warp / Ghostty support
OS-level Codex window binding ready
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
