# V4.1 Final Acceptance Report

status: passed-terminal-app

date: 2026-05-26

## Scope

V4.1 implemented a CLI-side read-only safe-field probe path for Terminal.app and iTerm2 planning scope.

V4.1 did not implement:

- binding UX.
- selected-terminal routing.
- lifecycle monitoring.
- PetEvent emission.
- `PetInstance` mutation.
- desktop UI.
- VS Code / Warp / Ghostty support.

## Evidence

- `docs/V4.x/v4_1-development-plan.md`
- `docs/V4.x/v4_1-acceptance-plan.md`
- `docs/V4.x/v4_1-prd-spec-review.md`
- `docs/V4.x/v4_1-plan-audit.md`
- `docs/V4.x/evidence/v4_1-safe-field-probe-2026-05-26.md`

## Automatic Checks

| Check | Result |
| --- | --- |
| `pnpm --filter @agent-desktop-pet/petctl check` | passed |
| `pnpm --filter @agent-desktop-pet/petctl test` | passed, 33 tests including Node-packaged Codex CLI detection and local `codex.js` false-positive guard |
| `pnpm --filter @agent-desktop-pet/petctl build` | passed |

## Runtime Smoke

| Probe | Result | Reason |
| --- | --- | --- |
| Terminal.app | passed | focused Terminal.app Codex TUI returned `ok=true`, `processName=codex`, `codexCliVersion=codex-cli 0.131.0`, and `candidate_detected` |
| iTerm2 | blocked | probe unavailable in current local environment |

## Regression Fix

The user-provided runtime sample showed a real Codex TUI on `ttys013` with Codex represented by same-TTY `node` processes rather than a direct `codex` process name. V4.1 now performs a two-stage process check:

- read safe same-TTY process summaries with `ps -axo pid=,comm=,tty=`.
- inspect only same-TTY Node-wrapper candidate PIDs with `ps -p <pid> -o args=` for internal Codex signatures.

The args inspection is classifier-only. Probe output does not include raw args, command text, local paths, prompt text, or workspace path.

## PRD Review

Result: no major or critical mismatch.

V4.1 remains aligned with PRD because:

- it is a safe-field probe only.
- it does not claim binding or lifecycle monitoring.
- it does not read terminal text, prompt text, command text, workspace path, or full local path.
- Node-wrapper process args are used only for internal Codex classification and are not emitted in output or evidence.
- it does not include asset, renderer, or productization work.

## False-green Risk Assessment

| Risk | Level | Result |
| --- | --- | --- |
| Probe counted as binding | Medium | mitigated by no PetEvent / no `PetInstance` mutation |
| Probe counted as lifecycle monitoring | Medium | mitigated by Terminal.app-only probe acceptance and no state claim |
| Runtime blocked converted to passed | Medium | Terminal.app has passed runtime evidence; iTerm2 remains blocked and is not generalized |
| Node-wrapper detection overmatches ordinary Node processes | Medium | mitigated by same-TTY PID scoping and Codex-specific args signatures |

Overall risk: Medium for the Terminal.app-scoped claim; High if generalized to iTerm2, all terminals, binding, or lifecycle monitoring.

## Claim Decision

Allowed statement:

```text
V4.1 macOS active window safe-field probe completed for Terminal.app on tested local environment.
```

Forbidden statements:

```text
V4.1 macOS active window safe-field probe completed for iTerm2 on tested local environment.
V4.1 macOS active window safe-field probe completed for all terminal apps.
OS-level Codex window binding ready
interactive Codex TUI monitoring ready
already-open Codex window auto-detection ready
```

## Final Decision

V4.1 final acceptance is passed for Terminal.app only.

V4.2 may be planned from Terminal.app-only safe-field evidence. It must not claim iTerm2 support, all-terminal support, selected-terminal routing, lifecycle monitoring, or OS-level Codex window binding readiness.
