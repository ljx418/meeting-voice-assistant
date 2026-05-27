# V4.2 Final Acceptance Report

status: passed

date: 2026-05-26

## Scope

V4.2 implemented Terminal.app-only preview / confirm candidate-to-PetInstance binding UX.

V4.2 did not implement:

- PetEvent emission.
- lifecycle monitoring.
- state routing.
- manual route-test.
- iTerm2 / VS Code / Warp / Ghostty support.
- OS-level Codex window binding readiness.

## Evidence

- `docs/V4.x/v4_2-development-plan.md`
- `docs/V4.x/v4_2-acceptance-plan.md`
- `docs/V4.x/v4_2-prd-spec-review.md`
- `docs/V4.x/v4_2-plan-audit.md`
- `docs/V4.x/evidence/v4_2-binding-ux-smoke-2026-05-26.md`

## Automatic Checks

| Check | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed, 40 tests |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |

## Runtime Smoke

| Case | Result | Reason |
| --- | --- | --- |
| Terminal.app preview before desktop bridge | partial | candidate produced, but desktop bridge was not running for confirm |
| Terminal.app confirm before desktop bridge | blocked | `desktop_not_running` |
| desktop health | passed | `/api/health` returned ok after desktop dev started |
| Terminal.app preview after desktop bridge | blocked | Terminal.app probe unavailable or focus returned to Chrome |
| Terminal.app preview from user-provided run | passed | sanitized candidate produced |
| Terminal.app confirm after confirm revalidation fix | passed | candidate process/TTY revalidated and PetInstance created |

## PRD Review

Result: no critical or major mismatch.

Known PRD evolution:

- The older PRD says the product is not an OS-level window recognition system.
- V4.x has narrowed this to Terminal.app safe-field candidate feasibility and explicit confirmation, not readiness.

This remains acceptable because V4.2 does not claim auto-detection readiness, lifecycle monitoring, or OS-level binding ready.

## Runtime Fix

The user-provided preview succeeded, but the first confirm returned `candidate_not_active`. Root cause:

- confirm re-ran the focused active-window probe.
- running confirm shifted focus to the command terminal, so the candidate TTY no longer matched.

Fix:

- confirm now revalidates the stored candidate by `processId`, Codex classifier, `ttySummary`, and `sessionSummary`.
- confirm no longer requires the Codex TUI window to remain frontmost.
- confirm still fails when the candidate process exits, TTY changes, or Codex classifier no longer matches.

## False-green Risk Assessment

| Risk | Level | Result |
| --- | --- | --- |
| Binding counted as OS-level ready | Medium | mitigated by blocked runtime and scoped claim language |
| Binding counted as lifecycle monitoring | Medium | V4.2 sends no PetEvent and no state route |
| Runtime blocked converted to passed | Medium | runtime preview and confirm both passed after revalidation fix |
| Sensitive field leakage | Medium | output/evidence use sanitized summaries only |

Overall risk: Medium for the Terminal.app-scoped V4.2 claim; High if generalized to OS-level readiness or lifecycle monitoring.

## Claim Decision

Allowed statement:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
```

Forbidden statements:

```text
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
state lifecycle routing ready
```

## Final Decision

V4.2 final acceptance is passed for Terminal.app candidate-to-PetInstance binding UX.

V4.3 may proceed to stage planning and audit from this Terminal.app-only evidence. V4.3 must still remain manual route-test only and must not claim lifecycle monitoring or OS-level Codex window binding readiness.
