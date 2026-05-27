# V4.x Final PRD Spec Review

status: no-major-mismatch

date: 2026-05-27

## Reviewed Sources

- `docs/active/agent_desktop_pet_prd_v3x.md`
- `docs/V4.x/v4_x-development-plan.md`
- `docs/V4.x/v4_x-acceptance-plan.md`
- `docs/V4.x/v4_x-claim-matrix.md`
- `docs/V4.x/v4_1-final-acceptance-report.md`
- `docs/V4.x/v4_2-final-acceptance-report.md`
- `docs/V4.x/v4_3-final-acceptance-report.md`

## PRD Alignment

V4.x is a scoped advanced feasibility line layered on top of the PRD's local Codex workflow focus.

It aligns because:

- V3.7 remains the reliable monitoring path.
- V4.x does not claim interactive Codex TUI monitoring.
- V4.x does not claim OS-level Codex window binding readiness.
- V4.x does not parse terminal text, prompt text, tool command text, screen contents, or transcript paths.
- V4.x routes only an explicit manual route-test after user-confirmed binding.

## Findings

| ID | Severity | Finding | Required Action | Status |
| --- | --- | --- | --- | --- |
| PRD-V4.x-FINAL-001 | Medium | The older PRD says the project is not an OS-level window recognition system. | Final claim must stay Terminal.app scoped and prototype-only. | closed |
| PRD-V4.x-FINAL-002 | Medium | Manual route-test could be mistaken for lifecycle monitoring. | Final report must explicitly forbid lifecycle routing claims. | closed |
| PRD-V4.x-FINAL-003 | Medium | Terminal.app evidence could be generalized to iTerm2/all terminals. | Final report must state unsupported terminal boundary. | closed |

No critical or major mismatch found.

## Decision

go / no-go: go for V4.x final claim/security scan and final report.
