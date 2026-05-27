# V3.6 Development Plan

文档状态：historical blocked；deprecated active strategy

日期：2026-05-25

## Goal

V3.6 attempts selected real Codex workflow coverage expansion for the existing hook state mapping. It must not claim all Codex workflows, exact internal reasoning state, or OS-level window binding.

Strategy update on 2026-05-26: V3.6 hook-only monitoring is deprecated as the active Codex monitoring strategy. V3.7 JSONL monitor is the current recommended path for supported wrapper-launched `codex exec --json` sessions.

V3.6 的目标不是增加新集成，而是验证 V3.4 hooks 在更多真实 Codex workflow 中是否能稳定驱动桌宠状态。最低目标原本包括：

- simple answer：`UserPromptSubmit -> thinking`，clean `Stop -> success`。
- tool success：`PreToolUse -> running`，clean `Stop -> success`。
- tool failure：`PostToolUse failure -> error`，后续 `Stop` 不得覆盖 `error`。
- PermissionRequest：`PermissionRequest -> need_input`，如果本地 Codex 非交互模式无法稳定触发，则必须明确 blocked / deferred。

## Implemented So Far

- Hardened `scripts/codex-pet-hook.mjs` so `Stop` is treated as a turn completion marker.
- Added turn issue tracking so `PostToolUse failure -> error` is not overwritten by a later `Stop`.
- Verified that the observed real `PostToolUse` schema with no result field is treated as no-op instead of fabricating an error from `tool_input`.
- Added safe debug summaries that record field names/status summaries only when explicitly enabled.
- Re-ran V3.4 fixture regression and confirmed:
  - observed-shape `PostToolUse` without result fields does not change state.
  - `PostToolUse failure -> error`.
  - `Stop after failure -> error`.
  - clean new turn can later reach `success`.

## Real Workflow Attempt

Executed real local `codex exec` scenarios through `petctl codex launch`:

- simple answer turn.
- shell tool success.
- shell tool failure.

The simple answer and tool success scenarios completed and routed to bound cat instances. The shell failure scenario produced a failed command in Codex output, but the local `PostToolUse` hook payload did not include a stable exit code/status/result field. The hook wrapper therefore cannot safely map that real failure to `error` without parsing terminal output or treating `transcript_path` as an interface.

## Current Acceptance Status

| Gate | Status | Notes |
| --- | --- | --- |
| simple answer real workflow | passed | Real `codex exec` child session completed and target pet reached `success`. |
| tool success real workflow | passed | Real shell tool success completed and target pet reached `success`. |
| tool failure real workflow | blocked | Codex output showed command failure, but `PostToolUse` hook payload did not expose stable failure fields. |
| `Stop` false-green guard | passed in fixture | Fixture verifies failure state is not overwritten by `Stop`. |
| PermissionRequest | not-run | Non-interactive Codex path did not provide a stable approval prompt scenario in this pass. |
| V3.1 runtime smoke | passed | Regression rerun passed. |
| V3.3 binding smoke | passed | Regression rerun passed. |
| V3.4 fixture smoke | passed | Regression rerun passed after Stop hardening. |
| petctl check/test | passed | Type check and unit tests passed. |

## Blocker Details

The safe debug summary for the failing real `PostToolUse` hook exposed only field categories equivalent to:

```text
cwd, hook_event_name, model, permission_mode, session_id, tool_input
```

It did not expose stable failure fields such as:

```text
exitCode, exit_code, status, success, error, result
```

Because V3.x explicitly forbids parsing terminal text and treating `transcript_path` as a stable interface, the failed command observed in Codex output cannot be used as hook evidence.

## Risk Assessment

| Risk | Level | Notes |
| --- | --- | --- |
| Development plan drift | Low | Work stayed within V3.6 workflow coverage and Stop false-green hardening. |
| False-green acceptance | High | Passing V3.6 would require using fixture evidence or terminal output as substitute for real `PostToolUse` failure evidence. |
| Claim expansion | High | `selected workflow coverage passed` would overstate the current evidence. |
| Security redaction | Low | Debug summary records field names only and the temporary debug file was removed. |
| Regression coverage | Low | V3.1, V3.3, V3.4 fixture, and petctl checks passed. |

overall risk: High

go / no-go: no-go

## Decision

V3.6 is historical blocked evidence. Do not continue trying to pass V3.6 hook-only acceptance unless a future Codex hook payload exposes stable failure evidence and the V3.6 acceptance plan is explicitly revived, revised, and re-audited.

## Options for Review

1. Keep V3.6 blocked and wait for Codex hook payload support for stable failure fields.
2. Revise V3.6 scope to exclude real tool failure mapping and downgrade the claim to simple answer + tool success only. This requires ChatGPT audit because it weakens the original acceptance target.
3. Add a project-owned wrapper around tool execution to emit failure events. This would be a new capability and should be planned as a new stage, not silently added to V3.6.

Recommended current decision: keep V3.6 as historical blocked evidence and use V3.7 JSONL monitor as the active Codex exec monitoring path.

## Expanded Fix Attempt Result

On 2026-05-25, an additional blocker resolution pass checked three possible fixes:

- Codex hook schema/config angle: no supported local `codex-cli 0.131.0` flag or project hook schema option was found that makes real `PostToolUse` stdin expose stable failure result fields.
- Structured `codex exec --json` angle: implemented as V3.7 project-owned JSONL monitor. It supersedes V3.6 as the active strategy for supported wrapper-launched Codex exec monitoring, but it still is not valid V3.6 hook-only evidence.
- Acceptance/claim angle: V3.6 cannot be passed without scope revision because the required real tool failure gate remains blocked.

No further implementation is recommended inside V3.6 beyond the already-completed Stop false-green guard and future-compatible failure field detection.
