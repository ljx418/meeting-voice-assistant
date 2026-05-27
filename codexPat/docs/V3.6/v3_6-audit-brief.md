# V3.6 Audit Brief

文档状态：historical audit brief；V3.6 hook-only strategy deprecated

日期：2026-05-25

## 当前相关项目

| Area | Status | Audit files |
| --- | --- | --- |
| V3.x 总计划 | V3.6 historical blocked；V3.7 current strategy | `docs/V3.x/v3_x-development-plan.md`, `docs/V3.x/v3_x-codex-monitoring-strategy.md` |
| Active gap | 已更新到 V3.x 当前状态 | `docs/active/current-vs-target-gap.md`, `docs/active/current-vs-target-gap.drawio` |
| V3.5 diagnostics | passed | `docs/V3.5/v3_5-final-acceptance-report.md`, `scripts/v3_5_hook_diagnostics_smoke.mjs` |
| V3.6 workflow coverage | historical blocked / deprecated active strategy | `docs/V3.6/v3_6-development-plan.md`, `docs/V3.6/v3_6-final-acceptance-report.md` |
| V3.6 evidence | blocked on real failure payload | `docs/V3.6/evidence/codex-real-workflow-smoke-2026-05-25.md` |
| Hook wrapper | Stop false-green guard implemented | `scripts/codex-pet-hook.mjs` |
| petctl diagnostics | `petctl codex doctor` implemented | `packages/petctl/src/codex-doctor.ts`, `packages/petctl/src/args.ts`, `packages/petctl/src/cli.ts`, `packages/petctl/src/output.ts` |

## 审计结果摘要

V3.5 passed:

- `petctl codex doctor` reports hook config, hook wrapper, instance env, token source, Codex CLI, and desktop health diagnostics.
- Diagnostics smoke passed.
- Redaction scan passed.

V3.6 partial implementation:

- `Stop` is now treated as a turn completion marker.
- Observed-shape `PostToolUse` payloads without result fields are verified as no-op; the hook does not infer failure from `tool_input`.
- Fixture regression verifies `PostToolUse failure -> error` and `Stop after failure -> error`.
- Real simple answer workflow passed.
- Real tool success workflow passed.

V3.6 blocker:

- Real tool failure workflow produced a failed shell command in Codex output.
- The local `PostToolUse` hook payload did not expose stable failure fields.
- Safe field summary showed categories equivalent to:

```text
cwd, hook_event_name, model, permission_mode, session_id, tool_input
```

- Missing stable fields:

```text
exitCode, exit_code, status, success, error, result
```

Therefore V3.6 is blocked because the project rules forbid:

- parsing terminal text as a state interface.
- treating `transcript_path` as a stable interface.
- using fixture evidence as a substitute for real lifecycle evidence.

## Team Blocker Resolution Attempt

本轮按“激活团队尝试解决 V3.6 阻塞项”追加了三条排查线：

| Track | Question | Result |
| --- | --- | --- |
| Hook schema / config | 当前 `codex-cli 0.131.0` 是否存在配置、flag 或 schema 写法，让真实 `PostToolUse` stdin 暴露 exit/status/result？ | No valid fix found. 本地 `codex exec --help` 只暴露 hook trust / config / JSONL 输出等通用参数，没有发现可启用 `tool_response` 的稳定 hook 配置。 |
| Structured `codex exec --json` monitor | 能否监听 `codex exec --json` 子进程 JSONL，把工具失败映射到桌宠 `error`？ | Requires scope change. 这是结构化 stdout 监控，不是 hook stdin 证据；在当前 V3.6 “official hooks only / 不解析终端输出”边界内不能作为通过证据。 |
| Constraint audit | 是否能在不放宽边界的情况下声明 V3.6 passed？ | No. 只能保持 blocked，或正式修订 V3.6 scope 并降级 claim。 |

结论：

- 当前没有可落地的 V3.6 hook-only 修复。
- `scripts/codex-pet-hook.mjs` 已为未来稳定 failure fields 做好兼容：如果后续真实 payload 出现 `exitCode`、`exit_code`、`status=error/failed/failure`、`success=false`、`error`、`result`、`tool_result`、`tool_response` 等字段，现有检测逻辑可以映射到 `error`。
- 不能用 `codex exec --json` monitor、terminal output、transcript 或 fixture smoke 替代真实 `PostToolUse` failure evidence。
- 若要继续推进，必须二选一：
  - 保持 V3.6 blocked，等待 Codex hook payload 支持稳定 failure evidence。
  - 新开一个经审计的 scope-change 阶段，设计“项目自有 Codex exec structured monitor / wrapper”，并给出不同于 V3.6 的弱声明。

2026-05-26 strategy update: the second path has been implemented as V3.7 Codex Exec JSONL Monitor. V3.6 remains historical blocked evidence and is deprecated as the active strategy.

## Risk Assessment

| Risk | Level | Audit result |
| --- | --- | --- |
| Development plan drift | Low | Work stayed within V3.6 coverage and Stop false-green hardening. |
| False-green acceptance | High | Passing V3.6 would require accepting fixture or terminal output as real failure evidence. |
| Claim expansion | High | `V3.6 selected workflow coverage passed` would overstate evidence. |
| Security redaction | Low | Debug summary recorded field names only; temporary debug file was removed. |
| Regression coverage | Low | V3.1, V3.3, V3.4 fixture, and petctl checks passed. |

overall risk: High

go / no-go: no-go

## Current Allowed Claims

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
V3.2 third-party contract v3 smoke passed.
V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.
V3.4 Codex hook wrapper fixture smoke passed.
V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.
V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.
V3.6 final acceptance blocked on real PostToolUse failure evidence.
V3.6 hook-only monitoring is deprecated as an active strategy and superseded by V3.7 JSONL monitoring for supported wrapper-launched codex exec --json sessions.
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
```

## Forbidden Claims

```text
V3.6 selected Codex workflow hook coverage smoke passed for tested local scenarios
V3.7 Manager UI binding visibility acceptance passed
all Codex workflows verified
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```

## Audit Questions

1. Is V3.6 correctly blocked instead of passed?
2. Is it valid to reject terminal output as evidence for hook failure mapping?
3. Is the `Stop` false-green guard sufficient at fixture level while real failure remains historical blocked?
4. Is it correct to deprecate V3.6 hook-only monitoring as the active strategy?
5. Is V3.7 JSONL monitoring an acceptable current Codex exec monitoring path for wrapper-launched `codex exec --json`?
6. Are the V3.7 boundaries explicit enough: no interactive TUI, no OS-level binding, no official hook evidence claim?
7. Does the active gap markdown and drawio now match the same current state?
