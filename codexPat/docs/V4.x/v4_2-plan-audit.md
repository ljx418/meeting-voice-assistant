# V4.2 Plan Audit

status: audit-passed

date: 2026-05-26

## Audit Scope

This audit checks whether V4.2 may enter implementation under the stage rule:

```text
Before implementation, create development and acceptance plans from the PRD, complete PRD review, close audit findings, and stop if critical/major drift or High false-green risk appears.
```

## Audit Findings

| ID | Severity | Finding | Required Action | Status |
| --- | --- | --- | --- | --- |
| AUDIT-V4.2-001 | Medium | A one-step bind command could create a silent binding. | Use preview / confirm; missing explicit confirmation returns `confirmation_required` if a one-step path exists. | closed |
| AUDIT-V4.2-002 | Medium | A binding could become stale after preview. | Add candidate TTL, `lastValidatedAt`, `expiresAt`, and revalidation before confirm. | closed |
| AUDIT-V4.2-003 | Medium | Binding could be mistaken for lifecycle monitoring. | V4.2 forbids PetEvent emission and state routing. | closed |
| AUDIT-V4.2-004 | Medium | Evidence could leak local machine details. | Store and print only sanitized summaries; scan evidence. | closed |

No critical or major findings remain open.

## False-green Risk Assessment

| Risk | Level | Mitigation |
| --- | --- | --- |
| Binding counted as OS-level ready | Medium | Claim says Terminal.app candidate-to-PetInstance UX only. |
| Binding counted as lifecycle monitoring | Medium | No PetEvent and no state routing in V4.2. |
| Stale candidate accepted | Medium | TTL and revalidation required. |
| Sensitive field leakage | Medium | Sanitized store/output and evidence scan. |
| iTerm2/all-terminal generalization | Medium | Terminal.app-only claim. |

Overall risk: Medium.

No High false-green risk remains after the current scope restrictions.

## Implementation Decision

go / no-go: go for V4.2 implementation.

Allowed implementation:

- `petctl codex bind active-window --terminal terminal --preview --json`
- `petctl codex bind confirm --candidate <candidateId> --name "<cat name>" --json`
- sanitized candidate and binding records with TTL/stale status.
- confirm flow that creates/links PetInstance through existing `/api/instances`.

Not allowed:

- PetEvent emission.
- `/api/events` or `/api/instances/:id/events` calls.
- lifecycle monitoring.
- iTerm2 / VS Code / Warp / Ghostty support.
- OS-level binding ready claim.
