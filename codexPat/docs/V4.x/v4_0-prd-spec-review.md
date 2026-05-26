# V4.0 PRD Spec Review

status: accepted-feasibility-review-no-major-mismatch

date: 2026-05-26

## Reviewed Sources

- `docs/active/agent_desktop_pet_prd_v3x.md`
- `docs/V4.x/v4_x-development-plan.md`
- `docs/V4.x/v4_x-acceptance-plan.md`
- `docs/V4.x/v4_x-current-gap-analysis.md`
- `docs/V4.x/v4_x-claim-matrix.md`
- `docs/active/development-plan.md`
- `docs/active/acceptance-plan.md`
- `docs/active/current-vs-target-gap.md`

## PRD-aligned Requirements

The PRD aligns with V4.0 on these points:

- V3.7 is the current recommended Codex exec monitoring path for wrapper-launched `codex exec --json`.
- V3.7 does not cover interactive Codex TUI or OS-level Codex window binding.
- V4.x is a separate future line for already-open Codex active window binding.
- V4.x should start with feasibility review.
- V4.x must not read raw terminal text, prompt text, command text, workspace path, or full local path.
- Forbidden claims remain forbidden, including `OS-level Codex window binding ready` and `all Codex workflows verified`.

## Closed Major Mismatch

| ID | Severity | PRD Text / Meaning | Current V4.0 Plan | Risk |
| --- | --- | --- | --- | --- |
| PRD-V4-001 | Major | PRD section 13.6 previously said V4.x may include productization asset packaging needed for release artifacts. | PRD now states asset, renderer, packaging, license / attribution, and release artifact asset integrity are V5.x or later productization work and cannot enter V4.0-V4.3 gates. | closed |

## Non-blocking Observations

| ID | Severity | Observation | Recommended Handling |
| --- | --- | --- | --- |
| PRD-V4-002 | Minor | PRD version title still says it applies to V1.0-V3.7, but later sections discuss V4.x and V5.x. | Rename or annotate PRD as active product baseline with post-V3.7 planning sections. |
| PRD-V4-003 | Minor | PRD says product is not an OS-level window recognition system, while V4.x explores OS-level discovery feasibility. | Keep wording but add that V4.x is a feasibility exception and may still no-go. |

## Closure Result

PRD-V4-001 is closed by revising PRD section 13.6 and 13.8:

- V4.x no longer includes asset, renderer, or productization packaging acceptance.
- V4.x remains OS-level Codex window/session binding feasibility.
- V5.x and later tracks own advanced pet experience and asset productization.

## Current PRD Review Decision

status: accepted-feasibility-review-no-major-mismatch

V4.0 feasibility review is complete with no major or critical PRD mismatch. V4.1 may be planned for Terminal.app and iTerm2 safe-field probe only. V4.1 implementation still requires separate development plan, acceptance plan, PRD review, audit closure, and no High false-green risk.
