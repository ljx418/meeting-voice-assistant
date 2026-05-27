# V3.3-Fix v1.1 Development Plan

文档状态：active。

## Baseline

V3.3 final acceptance failed on 2026-05-23.

Root failed condition:

- Claude Code version: `2.1.114 (Claude Code)`.
- Non-interactive Claude Code run completed.
- Real interactive permission and idle probes were attempted.
- No real Claude Code `Notification` hook event produced an accepted `need_input`.
- Default pet remained `idle`.

## Goal

Find whether the failure is caused by hook settings not loading, tested trigger scenarios not emitting Notification, or local Claude Code behavior that blocks this claim.

The only pass claim still gated by evidence is:

```text
V3.3 Claude Code hook Notification -> need_input smoke passed for tested local Claude Code hook scenario.
```

## Phase 1：Root Cause Freeze

Status: completed.

Confirmed root-cause candidates:

| Candidate | Current Evidence | Status |
| --- | --- | --- |
| Desktop bridge unavailable | V3.3 and V3.2 regression smokes reached bridge | unlikely |
| petctl/hook wrapper invalid | wrapper and redaction path validated outside acceptance; regressions passed | unlikely |
| Hook settings not loaded | not isolated in V3.3 | Phase 2 target |
| Notification trigger not emitted | V3.3 permission and idle probes did not emit accepted event | likely |
| Claude Code version/provider behavior | possible; local docs list Notification matchers but observed runs did not emit them | Phase 3 target |

Next-phase audit:

- Phase 2 must only prove hook config loading.
- Phase 2 must not write a Claude Code `need_input` event through `petctl`.
- If config load fails, Phase 3 must be revised to fix settings loading first.

## Phase 2：Hook Config Load Verification

Status: completed.

Implement a config-load probe that uses a temporary Claude settings file and a harmless hook event that is expected to run reliably. The probe writes a non-sensitive marker to a temporary file and reports only a redacted summary.

Allowed outcome labels:

- `loaded`
- `not-loaded`
- `blocked`
- `failed`

No pass claim may be made from config-load evidence.

Result:

- Temporary `--settings` hook loading passed.
- `SessionStart` lifecycle executed a harmless hook marker.
- Evidence: `docs/V3.3/evidence/claude-code-hook-config-load-2026-05-23.md`.

Next-phase audit:

- Settings loading is not the current blocker.
- Phase 3 must focus on Notification matcher emission.
- Do not broaden Phase 3 into MCP, third-party integration, or direct wrapper acceptance.

## Phase 3：Notification Trigger Matrix

Status: completed; failed to find an accepted Notification trigger.

Test real Claude Code Notification trigger scenarios:

- `permission_prompt`
- `idle_prompt`
- `elicitation_dialog`, only if safely triggerable
- `auth_success`, only if safely triggerable and never credential-bearing

Each scenario must distinguish:

- Claude Code process/session ran.
- Notification lifecycle event was observed.
- Hook command executed.
- Diagnostics accepted `sourceId=claude-code.local`, `level=need_input`.
- Target pet entered `need_input`.

Result:

- Evidence: `docs/V3.3/evidence/claude-code-notification-trigger-matrix-2026-05-23.md`.
- Matrix: `docs/V3.3/v3_3-notification-trigger-matrix.md`.
- `permission_prompt` ran with real Claude Code but did not emit Notification, did not execute hook marker, and did not create accepted `need_input`.
- Follow-up team probe removed `matcher` entirely from Notification config; Bash, Write, and manual idle variants still did not emit Notification.
- Other matchers were not accepted because they require unsafe credential changes, unavailable local MCP elicitation, or tty-only idle behavior already manually probed in V3.3.

Next-phase audit:

- Phase 4 must be blocker/failed declaration.
- No code path may directly call the hook wrapper as acceptance.
- Re-acceptance may only pass if a later real Notification trigger appears.

## Phase 4：Minimal Fix or Blocker Declaration

Status: completed.

If config loading is the issue, fix only settings loading or smoke invocation.

If Notification is not emitted despite loaded settings, declare failed or blocked with evidence. Do not replace Notification acceptance with direct wrapper execution.

Result:

- No minimal product fix is justified because settings loading passed.
- Current blocker is real Claude Code Notification emission in the tested local scenario.
- Matcher syntax is no longer the primary blocker after the no-matcher probe.
- Claim matrix and gap analysis were updated.

Next-phase audit:

- Phase 5 final report must be `failed`, not `passed`, unless a new real Notification trigger is observed during final smoke.
- V3.1/V3.2 regressions still need to be rerun to prove no collateral regression.

## Phase 5：Re-Acceptance

Status: completed; failed.

Run V3.3 hook smoke plus V3.1/V3.2 regression smokes and automatic checks. The final result is `passed` only if real Claude Code `Notification -> need_input` is accepted and visible in target pet state.

Result:

- Re-acceptance report: `docs/V3.3/v3_3-re-acceptance-report.md`.
- V3.3 hook smoke failed for the same root condition: no Notification, no accepted `need_input`, target pet `idle`.
- V3.1 runtime smoke passed.
- V3.2 MCP adapter smoke passed.
- V3.2 third-party contract smoke passed.
- Automatic checks and bundle build passed.
- Final status remains `failed`.

## Forbidden Claims

```text
Claude Code integration verified
Claude Code all workflows verified
MCP ready
Third-party agent integration verified
all Codex workflows verified
Windows ready
cross-platform ready
USB ready
production signed release ready
OS-level Codex window binding ready
per-instance queue ready
```
