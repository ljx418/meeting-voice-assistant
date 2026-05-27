# V4.4 PRD Spec Review

status: reviewed-no-major-mismatch-before-implementation

date: 2026-05-27

## PRD Requirement

The PRD states that a user should be able to associate a Codex session with a single cat and perceive Codex workflow state through that cat.

## Current Gap

V4.3 proves:

- Terminal.app Codex candidate discovery.
- user-confirmed candidate-to-PetInstance binding.
- explicit manual route-test to the bound pet.

V4.3 does not prove automatic Codex lifecycle or streaming state monitoring.

## V4.4 Alignment

V4.4 aligns with the PRD by requiring project-managed session launch:

```text
wrapper launch -> instance id injection -> trusted event source -> PetEvent route.
```

This is the first path in V4.x that can support the user-facing expectation that one Codex session drives one cat's state automatically.

## Boundary

V4.4 intentionally does not support arbitrary already-open Codex TUI windows because OS discovery cannot provide a trusted lifecycle event stream.

## Drift Assessment

| Risk | Level | Mitigation |
| --- | --- | --- |
| Treating V4.3 binding as automatic monitoring | High | V4.4 uses managed launch only and documents V4.3 as manual route-test only. |
| Claiming all interactive TUI workflows | High | TUI hooks require real trusted lifecycle evidence and remain scoped. |
| JSONL monitor treated as TUI monitoring | Medium | Claims distinguish managed exec JSONL from managed TUI hooks. |
| Sensitive evidence leakage | Medium | Evidence records event type and mapped state only. |

## Audit Conclusion

No fatal or major PRD mismatch is introduced by V4.4 if implementation remains wrapper-launched and scoped to trusted JSONL/hooks event sources.
