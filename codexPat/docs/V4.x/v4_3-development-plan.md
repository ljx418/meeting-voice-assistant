# V4.3 Development Plan

status: planned-audit-ready

date: 2026-05-27

## Scope

V4.3 implements a Terminal.app-only manual route-test prototype for a V4.2 user-confirmed binding.

Baseline:

- V4.0 feasibility review completed.
- V4.1 Terminal.app safe-field probe passed.
- V4.2 Terminal.app candidate-to-PetInstance binding UX passed.
- V3.7 remains the default reliable monitoring path for wrapper-launched `codex exec --json`.

V4.3 does not implement Codex lifecycle monitoring, interactive TUI monitoring, all-terminal support, or OS-level binding readiness.

## CLI Shape

```bash
petctl codex route test --binding <bindingId> --level running --json
```

The command sends one explicit manual test PetEvent to the bound PetInstance only after revalidating the binding.

## Required Revalidation

Before delivery, V4.3 must check:

- binding exists.
- binding is `active`.
- binding has not expired / gone stale.
- terminal bundle is Terminal.app.
- candidate process / Codex classifier is still valid where possible.
- redacted TTY/session summaries still match where possible.
- PetInstance still exists.

Failure reason codes:

```text
binding_not_found
binding_stale
candidate_not_active
terminal_mismatch
pet_instance_not_found
```

## Implementation Plan

| Step | Goal | Output | Stop Condition |
| --- | --- | --- | --- |
| V4.3.1 PRD Review | Confirm manual route-test remains scoped | `v4_3-prd-spec-review.md` | major/critical mismatch |
| V4.3.2 Plan Audit | Close false-green risks | `v4_3-plan-audit.md` | High overall risk |
| V4.3.3 CLI Args | Add `codex route test` parsing | args tests | command implies lifecycle routing |
| V4.3.4 Binding Lookup | Read active binding record safely | unit tests | missing/stale binding can route |
| V4.3.5 Route Delivery | Send manual test event only to bound PetInstance | route tests | default fallback possible |
| V4.3.6 Evidence | Record acceptance and scans | evidence + final report | evidence leaks sensitive fields |

## Allowed Claim

```text
V4.3 user-confirmed Terminal.app binding manual route-test prototype passed for tested local environment.
```

## Forbidden Claims

```text
interactive Codex TUI monitoring ready
state lifecycle routing ready
OS-level Codex window binding ready
already-open Codex window auto-detection ready
all Codex workflows verified
```

## Go / No-go

go / no-go: go for V4.3 implementation only if `v4_3-prd-spec-review.md` and `v4_3-plan-audit.md` have no open critical/major findings and no High false-green risk.
