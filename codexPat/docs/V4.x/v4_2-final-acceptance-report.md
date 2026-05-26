# V4.2 Final Acceptance Report

status: blocked-runtime-focus

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
| Terminal.app preview | blocked | focused app was Google Chrome, not Terminal.app |
| Terminal.app confirm | not run | no runtime candidateId was produced |

## PRD Review

Result: no critical or major mismatch.

Known PRD evolution:

- The older PRD says the product is not an OS-level window recognition system.
- V4.x has narrowed this to Terminal.app safe-field candidate feasibility and explicit confirmation, not readiness.

This remains acceptable because V4.2 does not claim auto-detection readiness, lifecycle monitoring, or OS-level binding ready.

## False-green Risk Assessment

| Risk | Level | Result |
| --- | --- | --- |
| Binding counted as OS-level ready | Medium | mitigated by blocked runtime and scoped claim language |
| Binding counted as lifecycle monitoring | Medium | V4.2 sends no PetEvent and no state route |
| Runtime blocked converted to passed | High if misclaimed | blocked; no V4.2 passed claim made |
| Sensitive field leakage | Medium | output/evidence use sanitized summaries only |

Overall risk: High if V4.2 is declared passed from current evidence.

## Claim Decision

Allowed statement:

```text
V4.2 CLI-side preview / confirm binding UX implementation built and unit-tested; runtime acceptance blocked on focused Terminal.app Codex TUI evidence.
```

Forbidden statements:

```text
V4.2 user-confirmed Terminal.app Codex candidate-to-PetInstance binding UX passed for tested local environment.
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
state lifecycle routing ready
```

## Final Decision

V4.2 final acceptance is blocked.

Do not start V4.3 implementation from this evidence. To unblock V4.2, rerun runtime preview and confirm with a focused Terminal.app Codex TUI and record passed evidence without leaking forbidden fields.
