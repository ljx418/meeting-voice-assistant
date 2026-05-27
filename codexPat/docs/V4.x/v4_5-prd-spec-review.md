# V4.5 PRD Spec Review

status: reviewed-no-major-mismatch-after-scoped-lifecycle

date: 2026-05-27

## PRD Requirement

The PRD goal is that one Codex session can correspond to one cat and the cat can reflect Codex workflow state.

## V4.5 Fit

V4.5 targets this requirement for managed Codex TUI sessions only:

```text
wrapper-launched Codex TUI -> trusted hooks -> one PetInstance.
```

## Current Result

V4.5 now has scoped real lifecycle evidence for a wrapper-launched Codex TUI session:

- `UserPromptSubmit -> thinking`
- `PreToolUse -> running`
- `Stop -> success`

`PermissionRequest` was not observed because the tested local policy did not emit it, so no permission-request claim is made.

## Drift Assessment

| Risk | Level | Mitigation |
| --- | --- | --- |
| Preflight mistaken for real hook lifecycle | Low | Evidence and final report now link separate real lifecycle smoke. |
| TUI claim made without `/hooks` trust | Low | Real run included `/hooks` review/trust before lifecycle validation. |
| Already-open TUI generalized as supported | Low | Scope remains wrapper-launched managed TUI only. |
| Terminal text parsing introduced | Low | Evidence uses sanitized PetInstance state, not terminal text parsing. |
| PermissionRequest generalized as passed | Low | Claim explicitly excludes it for this local run. |

## Conclusion

No major PRD mismatch remains for the scoped V4.5 acceptance. No High drift or false-green risk remains after excluding unobserved `PermissionRequest`.
