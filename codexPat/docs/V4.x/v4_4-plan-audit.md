# V4.4 Plan Audit

status: audit-closed-no-fatal-or-major-risk-before-implementation

date: 2026-05-27

## Reviewed Plans

- `docs/V4.x/v4_4-development-plan.md`
- `docs/V4.x/v4_4-acceptance-plan.md`
- `docs/V4.x/v4_4-prd-spec-review.md`

## Audit Findings

| Finding | Severity | Status |
| --- | --- | --- |
| Already-open Codex TUI cannot be monitored from OS discovery alone. | Major if claimed | Closed by managed-launch-only scope. |
| Hook mode may be unavailable if hook trust is not granted. | Major if silently passed | Closed by blocked-if-not-observed acceptance rule. |
| JSONL mode does not cover interactive TUI. | Major if generalized | Closed by separate exec and TUI claims. |
| V4.3 route-test must not become lifecycle evidence. | Major if generalized | Closed by explicit non-goal and claim matrix. |

## Drift / False-green Risk

Overall risk before implementation: Medium.

No High risk remains after scope reduction to project-managed sessions and trusted event sources.

## Go / No-go

Go for V4.4 implementation with these limits:

- implement a managed `codex session start` user entry.
- reuse existing V3.7 JSONL and V3.4 hook mechanisms.
- do not claim arbitrary already-open TUI monitoring.
- stop if real TUI hook evidence cannot be produced.
