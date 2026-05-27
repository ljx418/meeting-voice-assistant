# V4.5 Final Acceptance Report

status: passed-scoped

date: 2026-05-27

## Scope

V4.5 is intended to validate managed Codex TUI hook state mapping for wrapper-launched Codex TUI sessions.

## Current Decision

V4.5 wrapper preflight passed. Real Codex TUI hook lifecycle acceptance also passed for the tested local wrapper-launched scenario, scoped to `UserPromptSubmit`, `PreToolUse`, and `Stop`.

`PermissionRequest` was not observed in the local run because the tested Codex policy did not emit a permission request. No permission-request claim is made.

## Completed Gates

| Gate | Result |
| --- | --- |
| development plan | completed |
| acceptance plan | completed |
| PRD spec review | no major mismatch before preflight |
| plan audit | no High risk for preflight |
| petctl check | passed |
| petctl test | passed, 47 tests |
| petctl build | passed |
| V4.4 managed exec JSONL regression | passed |
| V4.5 managed TUI wrapper preflight | passed |
| real Codex TUI hook lifecycle | passed scoped |

## Real Lifecycle Evidence

| Gate | Result |
| --- | --- |
| `/hooks` trust reviewed before real lifecycle run | passed |
| `UserPromptSubmit -> thinking` | passed |
| `PreToolUse -> running` | passed |
| `Stop -> success` | passed |
| Default PetInstance unchanged | passed |
| Unrelated PetInstances unchanged | passed |
| `PermissionRequest -> need_input` | not observed; local policy did not emit permission request |

Evidence: `docs/V4.x/evidence/v4_5-managed-tui-hook-lifecycle-smoke-2026-05-27.md`

## Security Scan

The evidence is sanitized and does not include raw hook payloads, prompt text, tool command text, terminal screen contents, transcript paths, tokens, authorization headers, config paths, workspace paths, or full local paths.

## Claim Scan

Allowed current scoped claim:

```text
V4.5 managed Codex TUI hook state mapping passed for UserPromptSubmit, PreToolUse, and Stop in tested local wrapper-launched scenario; PermissionRequest remains blocked by local policy.
```

Forbidden as ready / passed:

```text
V4.5 managed Codex TUI hook state mapping passed
V4.5 managed Codex TUI lifecycle acceptance passed
interactive Codex TUI monitoring ready
already-open Codex window auto-monitoring ready
OS-level Codex window binding ready
all Codex workflows verified
```

## PRD Spec Review

No major PRD mismatch remains for the scoped V4.5 result: one wrapper-launched Codex TUI session can correspond to one PetInstance and drive that PetInstance through observed hook-backed states. The claim remains scoped and does not cover already-open Codex windows, OS-level binding, interactive TUI monitoring readiness, or all Codex workflows.

## Drift And False-Green Risk

| Risk | Level | Decision |
| --- | --- | --- |
| PermissionRequest not observed but claimed passed | Low | Claim excludes PermissionRequest and records local-policy non-observation. |
| Preflight confused with lifecycle evidence | Low | Final report links separate real lifecycle evidence. |
| Wrapper-launched TUI generalized to already-open TUI | Low | Forbidden claims remain explicit. |

No High risk remains for the scoped V4.5 acceptance.
