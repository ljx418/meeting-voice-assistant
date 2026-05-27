# V4.6 PRD Spec Review

status: reviewed-no-major-mismatch

date: 2026-05-27

## PRD Fit

The PRD requires users to understand how a managed Codex session connects to one PetInstance and how to avoid silent or misleading acceptance. V4.6 supports that by adding explicit diagnostics before managed TUI hook startup and by exposing `petctl codex doctor`.

## Boundary

V4.6 does not claim new state mapping. It only improves startup diagnostics and user instructions.

## Drift Review

| PRD Risk | Level | Result |
| --- | --- | --- |
| Product appears to support already-open TUI monitoring | Low | Claims remain wrapper-launched only. |
| Diagnostics become a false-green lifecycle substitute | Low | Lifecycle evidence remains separate in V4.5. |
| Sensitive local data appears in diagnostic output | Low | Evidence uses sanitized diagnostic names and reason codes only. |

No major PRD mismatch remains.
