# V4.3 Plan Audit

status: audit-passed

date: 2026-05-27

## Audit Scope

This audit checks whether V4.3 may enter implementation under the stage rule:

```text
Before implementation, create development and acceptance plans from the PRD, complete PRD review, close audit findings, and stop if critical/major drift or High false-green risk appears.
```

## Audit Findings

| ID | Severity | Finding | Required Action | Status |
| --- | --- | --- | --- | --- |
| AUDIT-V4.3-001 | Medium | Manual route-test could be counted as lifecycle routing. | Keep command, metadata, evidence, and claim manual/test-only. | closed |
| AUDIT-V4.3-002 | Medium | Unknown binding could route default. | Require explicit binding lookup and no fallback. | closed |
| AUDIT-V4.3-003 | Medium | Stale candidate could route to wrong pet. | Revalidate binding before delivery. | closed |
| AUDIT-V4.3-004 | Medium | Missing PetInstance could still produce success. | Check instance list before sending event. | closed |

No critical or major findings remain open.

## False-green Risk Assessment

| Risk | Level | Mitigation |
| --- | --- | --- |
| Route-test counted as lifecycle monitoring | Medium | Manual route-test metadata and scoped claim. |
| Default fallback | Medium | Explicitly forbidden and tested. |
| Stale binding route | Medium | Binding revalidation required. |
| Sensitive field leakage | Medium | Binding store/output use sanitized summaries only. |

Overall risk: Medium.

No High false-green risk remains after the current scope restrictions.

## Implementation Decision

go / no-go: go for V4.3 implementation.

Allowed implementation:

- `petctl codex route test --binding <bindingId> --level <level> --json`.
- binding lookup and revalidation.
- manual PetEvent delivery to `/api/instances/:instanceId/events`.
- safe failure for stale/missing/mismatched bindings.

Not allowed:

- lifecycle monitoring.
- direct UI control.
- default fallback.
- iTerm2 / VS Code / Warp / Ghostty support.
- OS-level binding ready claim.
