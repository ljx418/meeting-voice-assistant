# V4.1 PRD Spec Review

status: no-major-mismatch

date: 2026-05-26

## Reviewed Sources

- `docs/active/agent_desktop_pet_prd_v3x.md`
- `docs/V4.x/v4_0-os-binding-feasibility-review.md`
- `docs/V4.x/v4_1-development-plan.md`
- `docs/V4.x/v4_1-acceptance-plan.md`
- `docs/V4.x/v4_x-claim-matrix.md`

## PRD Alignment

V4.1 aligns with PRD because:

- PRD says V4.x starts with feasibility and must not claim ready.
- PRD says V4.x must distinguish candidate discovery from Codex lifecycle state event source.
- PRD says V4.x must not read raw terminal text, prompt text, command text, workspace path, or full local path.
- V4.1 Node-wrapper process args inspection is restricted to same-TTY candidate PID classification and does not emit raw args or local paths.
- PRD excludes asset, renderer, and productization work from V4.x.
- V4.0 explicitly scopes V4.1 to Terminal.app and iTerm2 safe-field probe planning.

## Scope Check

| Area | V4.1 Plan | PRD Result |
| --- | --- | --- |
| Terminal.app safe-field probe | planned | aligned |
| iTerm2 safe-field probe | planned | aligned |
| VS Code terminal | deferred | aligned with V4.0 risk decision |
| Warp | deferred/no-go | aligned with V4.0 risk decision |
| Ghostty | deferred | aligned with V4.0 risk decision |
| binding UX | excluded | aligned |
| selected-terminal routing | excluded | aligned |
| lifecycle state monitoring | excluded | aligned |
| asset/productization work | excluded | aligned |

## Findings

| ID | Severity | Finding | Status |
| --- | --- | --- | --- |
| PRD-V4.1-001 | Medium | A future probe may be misread as already-open Codex auto-detection ready. The acceptance plan must keep probe-only language. | mitigated |
| PRD-V4.1-002 | Medium | Terminal.app/iTerm2 evidence may be overgeneralized to all terminals. The acceptance plan requires per-terminal claims. | mitigated |
| PRD-V4.1-003 | Medium | Probe output could accidentally include window titles or session names containing local paths. The plan requires redacted summaries only. | mitigated |
| PRD-V4.1-004 | Medium | Node-packaged Codex detection could leak raw process args or overmatch ordinary Node sessions. Implementation must keep args classifier-only and require Codex-specific signatures. | mitigated |

No critical or major PRD mismatch found.

## Decision

status: go-for-v4-1-plan-audit

V4.1 may proceed to plan audit. V4.1 implementation still must not start until audit findings are closed and false-green risk is not High.
