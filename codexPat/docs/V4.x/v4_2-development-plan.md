# V4.2 Development Plan

status: planned-audit-ready

date: 2026-05-26

## Scope

V4.2 implements Terminal.app-only user-confirmed candidate-to-PetInstance binding UX.

Baseline:

- V4.0 feasibility review completed.
- V4.1 Terminal.app active window safe-field probe passed for the tested local environment.
- V3.7 remains the default reliable monitoring path for wrapper-launched `codex exec --json`.

V4.2 does not implement lifecycle monitoring, interactive Codex TUI monitoring, selected-terminal routing, iTerm2 / VS Code / Warp / Ghostty support, or OS-level binding readiness.

## CLI Shape

V4.2 must use a two-step flow:

```bash
petctl codex bind active-window --terminal terminal --preview --json
petctl codex bind confirm --candidate <candidateId> --name "<cat name>" --json
```

`preview` observes the focused Terminal.app Codex candidate and stores only a short-lived sanitized candidate record.

`confirm` validates the candidate again, creates or links a PetInstance, and stores a stale-aware binding record.

No single-command silent binding is allowed. If a single-command form is introduced later, missing explicit confirmation must return `confirmation_required`.

## Binding Record

Binding records must include:

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

Candidate and binding records must not store raw TTY, raw process args, window title, terminal text, prompt text, tool command text, shell history, screen contents, clipboard contents, token, Authorization, transcript_path, full `/Users` path, workspace path, config path, or `api-token.json`.

## Implementation Plan

| Step | Goal | Output | Stop Condition |
| --- | --- | --- | --- |
| V4.2.1 PRD Review | Confirm V4.2 remains a scoped advanced feasibility feature | `v4_2-prd-spec-review.md` | critical/major PRD mismatch |
| V4.2.2 Plan Audit | Close false-green and drift risks | `v4_2-plan-audit.md` | High overall risk |
| V4.2.3 CLI Args | Add `codex bind active-window --preview` and `codex bind confirm` parsing | petctl args tests | ambiguous command can silently bind |
| V4.2.4 Candidate Store | Add local sanitized short-lived candidate/binding store | store unit tests | raw fields can be persisted or printed |
| V4.2.5 Confirm Flow | Revalidate candidate and create/link PetInstance | confirm tests | expired/inactive candidate can bind |
| V4.2.6 Evidence | Record automated and runtime evidence | evidence + final report | evidence leaks sensitive data |

## Acceptance Boundary

Allowed future claim:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
```

Forbidden claims:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
state lifecycle routing ready
iTerm2 support passed
all terminal apps supported
```

## Go / No-go

go / no-go: go for V4.2 implementation only if `v4_2-prd-spec-review.md` and `v4_2-plan-audit.md` have no open critical/major findings and no High false-green risk.
