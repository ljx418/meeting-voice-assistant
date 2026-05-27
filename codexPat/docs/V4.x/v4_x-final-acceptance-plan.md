# V4.x Final Acceptance Plan

status: planned-audit-ready

date: 2026-05-27

## Scope

V4.x Final is evidence closure only. It must not add features.

Baseline:

- V4.0 feasibility review completed.
- V4.1 Terminal.app safe-field probe passed.
- V4.2 Terminal.app candidate-to-PetInstance binding UX passed.
- V4.3 Terminal.app manual route-test prototype passed.
- V4.4 managed exec JSONL state mapping passed.
- V4.5 managed TUI hook lifecycle passed for observed hook events.
- V4.6 startup diagnostics passed.
- V4.7 managed session status passed.
- V3.7 remains the default reliable monitoring path for wrapper-launched `codex exec --json`.

## Required Evidence

- `docs/V4.x/v4_0-os-binding-feasibility-review.md`
- `docs/V4.x/v4_1-final-acceptance-report.md`
- `docs/V4.x/evidence/v4_1-safe-field-probe-2026-05-26.md`
- `docs/V4.x/v4_2-final-acceptance-report.md`
- `docs/V4.x/evidence/v4_2-binding-ux-smoke-2026-05-26.md`
- `docs/V4.x/v4_3-final-acceptance-report.md`
- `docs/V4.x/evidence/v4_3-manual-route-test-smoke-2026-05-27.md`
- `docs/V4.x/v4_4-final-acceptance-report.md`
- `docs/V4.x/evidence/v4_4-managed-exec-jsonl-smoke-2026-05-27.md`
- `docs/V4.x/v4_5-final-acceptance-report.md`
- `docs/V4.x/evidence/v4_5-managed-tui-hook-lifecycle-smoke-2026-05-27.md`
- `docs/V4.x/evidence/v4_6-startup-diagnostics-smoke-2026-05-27.md`
- `docs/V4.x/evidence/v4_7-session-status-smoke-2026-05-27.md`

## Final Gates

- PRD review has no critical or major mismatch.
- V4.1/V4.2/V4.3 evidence is passed for Terminal.app only.
- claim scan confirms forbidden claims are not used as ready/passed.
- security scan confirms evidence does not include forbidden sensitive fields.
- automatic checks have no hard failure.
- V4.x Final does not add functionality.

## Allowed Final Claim

```text
V4.x managed Codex session-to-PetInstance state mapping passed for tested local wrapper-launched exec JSONL and scoped managed TUI hook scenarios, with Terminal.app candidate binding and manual route-test prototype accepted.
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
```
