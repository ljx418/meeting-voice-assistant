# V4.0 Plan Audit

status: accepted-feasibility-review

date: 2026-05-26

## Audit Scope

This audit checks whether V4.0 can enter implementation under the project rule:

```text
Before the next phase starts, define acceptance criteria and development plan from the PRD, summarize them as standalone documents, review audit opinions, and close all critical/major drift or false-green risks.
```

## Audit Result

V4.0 planning documents exist:

- `docs/V4.x/v4_0-development-plan.md`
- `docs/V4.x/v4_0-acceptance-plan.md`
- `docs/V4.x/v4_0-prd-spec-review.md`
- `docs/V4.x/v4_0-plan-audit.md`

V4.0 feasibility review is complete. This does not permit active window probe, Accessibility / Automation implementation, binding UX, or selected-terminal routing without a separate V4.1 plan, acceptance plan, PRD review, and audit closure.

## Audit Findings

| ID | Severity | Finding | Required Action | Status |
| --- | --- | --- | --- | --- |
| AUDIT-V4-001 | Major | PRD allowed V4.x productization asset packaging, while current V4.0-V4.3 plan excludes asset/productization acceptance gates. | PRD revised to move asset/productization packaging out of V4.x and into V5.x or later productization track. | closed |
| AUDIT-V4-002 | Medium | V4.0 feasibility could be misread as readiness if the claim matrix is not checked after every subphase. | Run claim scan after each V4.0 subphase. | planned |
| AUDIT-V4-003 | Medium | Terminal discovery could be mistaken for lifecycle monitoring. | Keep event source analysis as a required V4.0 output. | planned |
| AUDIT-V4-004 | Medium | Already-running session may not allow env injection or event ownership proof. | Require wrapper relaunch fallback in feasibility report if no safe route exists. | planned |
| AUDIT-V4-005 | Medium | V4.3 routing from OS-level discovery alone lacks event ownership proof. | Mark V4.3 no-go unless a future phase proves a safe route key and event source. | closed |

## False-green Risk Assessment

| Risk | Level | Reason |
| --- | --- | --- |
| Scope drift into asset/productization work | Low | PRD now excludes asset/productization packaging from V4.0-V4.3. |
| Window discovery counted as TUI monitoring | Medium | Discovery can identify candidates but does not produce lifecycle events; V4.0 event source analysis remains required. |
| Single terminal candidate treated as general OS-level support | Medium | Terminal apps differ significantly and each needs scoped evidence. |
| V3.7 evidence reused as OS-level evidence | Medium | V3.7 remains baseline but cannot prove already-open window binding. |
| V4.3 routing from discovery alone | Medium | V4.0 marks this no-go unless future event ownership proof exists. |

Overall risk: Medium.

## Development Decision

go / no-go: V4.0 accepted as feasibility review; go only for V4.1 planning, not implementation.

Allowed now:

- documentation-only V4.0 feasibility planning.
- V4.0 feasibility report.
- terminal matrix.
- permission/privacy model.
- state event source analysis.
- go/no-go decision.
- V4.1 development and acceptance planning.

Not allowed now:

- active window probe.
- Accessibility / Automation implementation.
- shell helper implementation.
- user-confirmed binding UX implementation.
- selected-terminal routing implementation.
- any passed V4.0 final acceptance claim before the feasibility report is complete.
- V4.1 implementation before V4.1 audit closure.

## Required Closure Before Implementation

1. Create V4.1 development and acceptance plans for Terminal.app and iTerm2 safe-field probe only.
2. Re-run PRD spec review and confirm no new major/critical mismatch.
3. Re-run false-green risk assessment and confirm no High risk remains.
4. Run claim/security scans.
5. Only then decide whether V4.1 active window probe implementation may start.
