# V4.2 PRD Spec Review

status: no-major-mismatch

date: 2026-05-26

## Reviewed Sources

- `docs/active/agent_desktop_pet_prd_v3x.md`
- `docs/V4.x/v4_x-development-plan.md`
- `docs/V4.x/v4_x-acceptance-plan.md`
- `docs/V4.x/v4_x-claim-matrix.md`
- `docs/V4.x/v4_1-final-acceptance-report.md`
- `docs/V4.x/v4_2-development-plan.md`
- `docs/V4.x/v4_2-acceptance-plan.md`

## PRD Alignment

The PRD says the product is not an OS-level window recognition system. V4.0/V4.1 later narrowed the future line to a Terminal.app safe-field feasibility path, not a readiness claim. V4.2 stays within that revised boundary because it requires explicit user confirmation and does not claim automatic OS-level binding readiness.

V4.2 aligns with the PRD because:

- it preserves V3.7 as the default reliable Codex monitoring path.
- it does not parse terminal text, prompt text, command text, or screen contents.
- it does not bypass PetInstance creation through the existing local bridge.
- it does not route lifecycle state.
- it keeps false-green boundaries explicit.

## Findings

| ID | Severity | Finding | Required Action | Status |
| --- | --- | --- | --- | --- |
| PRD-V4.2-001 | Medium | The older PRD says OS-level window recognition is not a product goal. | Keep V4.2 framed as Terminal.app candidate feasibility + explicit user confirmation, not ready. | closed in plan |
| PRD-V4.2-002 | Medium | Binding UX could be mistaken for monitoring. | V4.2 must not send PetEvent or claim lifecycle routing. | closed in plan |
| PRD-V4.2-003 | Medium | Candidate/binding storage could leak local paths or raw TTY. | Store sanitized summaries only. | closed in plan |

No critical or major mismatch found.

## Decision

go / no-go: go for V4.2 plan audit.
