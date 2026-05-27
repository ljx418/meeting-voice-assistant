# V3.x Development Plan

文档状态：closed / superseded by V4.x planning for OS-level binding

日期：2026-05-25

适用范围：V3.0 到 V3.x 收口阶段

## 目标

V3.x 的主线目标是把项目从“多实例 Codex 桌宠可用”推进到“Codex 窗口和桌宠一一绑定、Codex lifecycle 状态可映射、用户可诊断、证据可复跑、声明不 false-green”的稳定本地工作流。

当前 V3.x 已完成收口。历史推进顺序如下：

- V3.1 final acceptance passed。
- V3.2 final acceptance passed for scoped Agent Integration Readiness closure。
- V3.3 Codex window/session-to-pet binding passed for tested local macOS terminal scenarios；evidence: `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md`。
- V3.4 Codex hook wrapper fixture smoke passed；evidence: `docs/V3.4/evidence/codex-hook-fixture-smoke-2026-05-24.md`。
- V3.4 Codex hooks state mapping passed for tested local Codex hook scenarios；evidence: `docs/V3.4/evidence/codex-hook-real-lifecycle-smoke-2026-05-24.md`。

V3.x 当前没有剩余 active implementation work。Claude Code、MCP ready、第三方产品集成、Windows / cross-platform / USB / production signed release 仍不属于 V3.x 已验收能力。已打开 Codex 活动窗口 / OS-level binding 已进入 V4.x feasibility planning。

## V3.3 命名边界

`docs/V3.3/` 中仍保留早期 Claude Code Hook Real Verification 的失败证据和修复尝试文档。这些文件是 historical / superseded evidence，不是 active V3.3 目标，也不允许产生 Claude Code pass claim。

当前 active V3.3 final target 是 Codex window/session-to-pet binding，依据是：

- `docs/V3.3/v3_3-claim-matrix.md`
- `docs/V3.3/v3_3-codex-window-binding-design.md`
- `docs/V3.3/v3_3-final-acceptance-report.md`
- `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md`

后续 V3.x 文档中所有 completed V3.3 claim 只指 Codex window/session-to-pet binding。旧 Claude Code V3.3 claim 必须保持 not allowed / historical / superseded 语境。

## 当前允许声明

| Claim | Status | Evidence |
| --- | --- | --- |
| `V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.` | completed | `docs/V3.1/v3_1-final-acceptance-report.md` |
| `V3.2 MCP adapter minimal smoke passed for localhost bridge routing.` | completed | `docs/V3.2/evidence/mcp-adapter-smoke-2026-05-23.md` |
| `V3.2 third-party contract v3 smoke passed.` | completed | `docs/V3.2/evidence/third-party-contract-v3-smoke-2026-05-23.md` |
| `V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.` | completed | `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md` |
| `V3.4 Codex hook wrapper fixture smoke passed.` | completed | `docs/V3.4/evidence/codex-hook-fixture-smoke-2026-05-24.md` |
| `V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.` | completed | `docs/V3.4/evidence/codex-hook-real-lifecycle-smoke-2026-05-24.md` |
| `V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.` | completed | `docs/V3.5/evidence/hook-diagnostics-smoke-2026-05-25.md` |
| `V3.6 selected Codex workflow hook coverage smoke passed for tested local scenarios.` | historical blocked / deprecated active strategy | `docs/V3.6/v3_6-final-acceptance-report.md` |
| `V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.` | completed / current Codex exec monitoring strategy | `docs/V3.7/evidence/codex-exec-jsonl-monitor-smoke-2026-05-25.md` |
| `V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.` | passed | `docs/V3.x/v3_x-final-acceptance-report.md` |

## 禁止声明

以下声明在 V3.x 内仍禁止作为 ready / verified / production 结论出现，除非后续阶段另行建立真实验收证据并更新 claim matrix：

```text
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
all Codex workflows verified
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```

## 阶段总览

| 阶段 | 状态 | 目标 | 最终声明 |
| --- | --- | --- | --- |
| V3.0 | completed | 多实例基础、实例路由、Manager UI 基线 | V3.0 multi-instance baseline passed |
| V3.1 | completed | 稳定化、用户上手、runtime smoke、迁移指导 | V3.1 ready |
| V3.2 | completed | MCP adapter minimal bridge、third-party contract v3、集成证据边界 | scoped Agent Integration Readiness closure passed |
| V3.3 | completed | `petctl codex launch` 绑定 Codex session 与单个猫实例；旧 Claude Code V3.3 是 historical / superseded | Codex window/session-to-pet binding passed |
| V3.4 | completed | Codex hooks lifecycle 状态映射 | tested local Codex hook scenarios passed |
| V3.5 | completed | Hook UX diagnostics and recovery | hook diagnostics and recovery smoke passed |
| V3.6 | historical blocked / deprecated | Real Codex hook-only workflow coverage expansion | blocked on real `PostToolUse` failure evidence；不再作为 active strategy |
| V3.7 | completed / current strategy | Codex Exec JSONL Monitor；当前推荐 Codex exec 监听路径 | wrapper-launched `codex exec --json` JSONL monitor state mapping passed |
| V3.x Final | completed | 回归、文档、声明、证据收口 | V3.x scoped Codex local workflow acceptance passed |

## V3.5：Hook UX Diagnostics and Recovery

### 目标

把 V3.4 的 hook 能力从“可工作”补齐到“用户能发现、能诊断、能恢复”。本阶段不新增状态映射，不扩展 MCP，不做第三方 agent 产品集成。

### 开发内容

- 在 `petctl` 中补充 Codex hook 诊断命令或现有 doctor 输出，检查：
  - `.codex/hooks.json` 是否存在。
  - hook schema 是否符合当前项目支持的 Codex hooks schema，并记录 `codex-cli` version。
  - `scripts/codex-pet-hook.mjs` 是否存在且 `node --check` 通过。
  - 当前 shell 是否有 `AGENT_DESKTOP_PET_INSTANCE_ID`。
  - pet desktop bridge 是否可达。
  - token 是否存在但不打印。
- 补充 hook trust 指引：
  - `/hooks` review/trust 是普通路径。
  - `--dangerously-bypass-hook-trust` 只允许本地 smoke，不作为用户默认路径。
- 补充失败恢复指南：
  - `/hooks` 显示 Installed 0 / Active 0。
  - hook 没有触发。
  - 猫实例没有绑定。
  - token 缺失或 desktop app 未运行。
- 补充自动 smoke：
  - hook config parse smoke。
  - diagnostics redaction smoke。
  - missing instance env smoke。
  - desktop unavailable smoke。

### 验收标准

- `petctl` 或 doctor 能明确报告 hook config、hook wrapper、instance env、desktop health 四类状态。
- 诊断输出不包含 token、Authorization header、raw payload、本地完整路径、workspace path、config path。
- 错误场景输出可指导用户恢复，但不暗示已通过真实 lifecycle smoke。
- 复跑 V3.4 fixture smoke 通过。
- 复跑 `pnpm --filter @agent-desktop-pet/petctl check` 和 `pnpm --filter @agent-desktop-pet/petctl test` 通过。

### Claim Matrix

Allowed claim after acceptance:

```text
V3.5 Codex hook diagnostics and recovery smoke passed for tested local diagnostics scenarios.
```

Forbidden expansion remains the global V3.x forbidden claim list. V3.5 cannot claim new hook mappings, all Codex workflows, OS-level window binding, MCP ready, third-party product integration, or production readiness.

### 输出文档

- `docs/V3.5/v3_5-development-plan.md`
- `docs/V3.5/v3_5-acceptance-plan.md`
- `docs/V3.5/v3_5-current-gap-analysis.md`
- `docs/V3.5/v3_5-claim-matrix.md`
- `docs/V3.5/evidence/hook-diagnostics-smoke-YYYY-MM-DD.md`
- `docs/V3.5/v3_5-final-acceptance-report.md`

## V3.6：Real Codex Workflow Coverage Expansion（historical blocked / deprecated）

### 目标

扩大真实 Codex workflow 的覆盖面，验证 hooks 在更多日常 Codex 场景中仍能驱动正确猫状态。本阶段仍不声称 all Codex workflows verified。

Current strategy update: V3.6 hook-only monitoring is deprecated as the active Codex monitoring strategy. It remains historical blocked evidence because real `PostToolUse` payloads did not expose stable failure fields. Current Codex exec monitoring uses V3.7 JSONL monitor instead.

### 开发内容

- 设计最小真实场景矩阵：
  - 普通回答：`UserPromptSubmit -> thinking`，`Stop` 作为 turn completion marker；仅在本轮无 error / warning 且验收通过时允许进入 `success`，否则回 `idle` 或保持当前非成功状态。
  - 工具执行成功：`PreToolUse -> running`，`PostToolUse success`，`Stop` 作为 turn completion marker；仅在本轮无 error / warning 且验收通过时允许进入 `success`，否则回 `idle` 或保持当前非成功状态。
  - 权限请求：`PermissionRequest -> need_input`。
  - 工具失败：`PostToolUse failure -> error`。
  - 上下文压缩：`PreCompact`、`PostCompact` 仅记录诊断或状态 marker，不声明思考精确映射。
  - 子代理：`SubagentStart`、`SubagentStop` 如当前 Codex 版本可触发，则记录；不可触发则 deferred。
- 建立真实场景 evidence 模板，记录：
  - Codex version。
  - hook config loaded。
  - route instance id 是否存在但脱敏。
  - operator visual acceptance。
  - 不记录 prompt 原文和 raw hook payload。
- 补充 smoke 脚本或人工验收脚本，帮助操作者逐项触发场景。

### 验收标准

- 至少完成普通回答、工具成功、权限请求、工具失败四类真实 lifecycle 验收。
- 每类验收均能看到对应桌宠状态变化，且 evidence 记录 operator acceptance。
- evidence 不包含 token、Authorization header、raw payload、tool input command、完整本地路径、workspace path。
- `Stop` 不能无条件映射 `success`；必须验证 `PostToolUse failure -> error` 不会被后续 `Stop` false-green 覆盖。
- 如果 `PreCompact/PostCompact/SubagentStart/SubagentStop` 无法稳定触发，必须明确 deferred，不阻塞 V3.6 scoped pass。
- 复跑 V3.1 runtime smoke、V3.3 binding smoke、V3.4 hook fixture smoke。

### Claim Matrix

Allowed claim after acceptance:

```text
V3.6 selected Codex workflow hook coverage smoke passed for tested local scenarios.
```

Forbidden expansion remains the global V3.x forbidden claim list. V3.6 cannot claim exact Codex internal reasoning state, `ModelThinkingStart` / `ModelThinkingEnd`, all Codex workflows, OS-level window binding, or Claude Code integration.

### 输出文档

- `docs/V3.6/v3_6-development-plan.md`
- `docs/V3.6/v3_6-acceptance-plan.md`
- `docs/V3.6/v3_6-workflow-coverage-matrix.md`
- `docs/V3.6/v3_6-claim-matrix.md`
- `docs/V3.6/evidence/codex-real-workflow-smoke-YYYY-MM-DD.md`
- `docs/V3.6/v3_6-final-acceptance-report.md`

## V3.7：Codex Exec JSONL Monitor

### 目标

把 `codex exec --json` 的结构化 JSONL stdout 作为 project-owned monitor source，用于 wrapper-launched Codex exec sessions 的状态映射，尤其是失败/error 映射。

V3.7 不把 V3.6 改写为 passed。V3.6 仍是 historical blocked evidence：`V3.6 final acceptance blocked on real PostToolUse failure evidence.`

V3.7 现在是当前推荐的 Codex exec 监听方案，适用于 wrapper-launched `codex exec --json`。

### 开发内容

- 为 `petctl codex launch` 增加 `--monitor none|jsonl`，默认 `none` 保持现有行为。
- 推荐命令：

```bash
petctl codex launch --monitor jsonl --name "<cat>" -- codex exec --json "<prompt>"
```

- 复用现有 PetInstance 绑定和 `AGENT_DESKTOP_PET_INSTANCE_ID` 注入。
- `--monitor jsonl` 读取 child stdout JSONL，只解析结构化 `event.type` / `type` 和安全字段名。
- 通过现有 `notify()` 写入目标猫，仍走 PetEvent / HTTP / Event Bridge。
- 不记录 raw JSONL、prompt 原文、tool command 原文、token、Authorization、`transcript_path`、完整本地路径、workspace path、config path。

初始映射：

| JSONL event type | State |
| --- | --- |
| `thread.started` | marker / idle |
| `turn.started` | thinking |
| `item.started` | running |
| `item.completed` | marker / keep current |
| `turn.completed` | success only if no current-turn error |
| `turn.failed` | error |
| `error` | error |

### 验收标准

- simple answer 映射 `thinking -> success / idle`。
- tool success 映射 `running -> success`。
- tool failure 必须从 structured JSONL 中观察到 `turn.failed` 或 `error`，并映射到 `error`。
- 如果 JSONL 没有结构化 failure signal，V3.7 status 必须为 blocked，不得 fallback 到文本解析。
- evidence 不包含 token、Authorization、raw JSONL、prompt 原文、tool command 原文、`transcript_path`、完整本地路径、workspace path、config path。
- 复跑 V3.1、V3.2、V3.3、V3.4 regression smoke 和自动检查。

### Claim Matrix

Allowed claim after acceptance:

```text
V3.7 Codex exec JSONL monitor state mapping passed for tested local wrapper-launched codex exec --json scenarios.
```

Forbidden expansion remains the global V3.x forbidden claim list. V3.7 cannot claim V3.6 hook-only acceptance, official `PostToolUse` failure hook evidence, arbitrary OS-level Codex window discovery, interactive Codex TUI coverage, all Codex workflows, production release readiness, Windows readiness, cross-platform readiness, or per-instance queue readiness.

### 输出文档

- `docs/V3.7/v3_7-development-plan.md`
- `docs/V3.7/v3_7-acceptance-plan.md`
- `docs/V3.7/v3_7-claim-matrix.md`
- `docs/V3.7/evidence/codex-exec-jsonl-monitor-smoke-YYYY-MM-DD.md`
- `docs/V3.7/v3_7-final-acceptance-report.md`
- `docs/V3.x/v3_x-codex-monitoring-strategy.md`

## V3.x Final Consolidation

### 目标

把 V3.1 到 V3.7 的证据、声明和用户文档统一收口，形成 V3.x scoped Codex local workflow acceptance。该阶段只做回归、文档、证据索引、claim scan 和安全扫描，不新增功能。

### 开发内容

- 汇总 evidence index：
  - V3.1 runtime smoke。
  - V3.2 MCP adapter minimal smoke。
  - V3.2 third-party contract v3 smoke。
  - V3.3 Codex window/session binding smoke。
  - V3.4 Codex hook fixture smoke。
  - V3.4 real Codex hook lifecycle evidence；该 gate 依赖真实 Codex `/hooks` review/trust 和 operator acceptance，不能用 fixture smoke 替代。
  - V3.5 hook diagnostics smoke。
  - V3.6 blocked final acceptance report。
  - V3.7 Codex exec JSONL monitor smoke。
- 同步用户文档：
  - `README.md`
  - `docs/README.md`
  - `docs/reference/multi-codex-workflow.md`
  - `docs/reference/07-integrations.md`
  - `docs/ops/troubleshooting.md`
- 执行 security redaction scan。
- 执行 claim consistency scan。
- 执行 git artifact check。

### 验收标准

- 全部阶段 final report 均为 passed，或明确 blocked/deferred 且没有越权声明。
- V3.4 real hook lifecycle smoke 必须复核；如果当前环境无法完成 Codex `/hooks` review/trust 或真实 lifecycle operator acceptance，V3.x Final 必须标记 blocked。
- 自动检查无 hard failure。
- evidence 和 smoke 输出不包含：
  - token
  - Authorization header
  - raw payload
  - full `/Users/...` path
  - config path
  - workspace path
  - invalid sound 原文
  - `api-token.json`
- forbidden claims 只出现在 forbidden / deferred / not-ready 语境。
- `git status --short` 确认 `dist/`、`target/`、`node_modules/` 等生成物不进入提交范围。

### 必跑回归命令

```bash
node scripts/v3_1_runtime_smoke.mjs
node scripts/v3_2_mcp_adapter_smoke.mjs
node scripts/v3_2_third_party_contract_smoke.mjs
node scripts/v3_3_codex_window_binding_smoke.mjs
node scripts/v3_4_codex_hook_fixture_smoke.mjs
pnpm run doctor
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/pet-mcp check
pnpm --filter @agent-desktop-pet/pet-mcp test
pnpm --filter desktop check
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop build
pnpm --filter desktop tauri build -b app
git status --short
```

V3.4 real lifecycle is reviewed through `docs/V3.4/evidence/codex-hook-real-lifecycle-smoke-2026-05-24.md` and `docs/V3.4/v3_4-final-acceptance-report.md`. The local helper `scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs` intentionally blocks without a trusted manual lifecycle run; this is a no-false-green guard rather than an automatic pass/fail regression.

### 输出文档

- `docs/V3.x/v3_x-evidence-index.md`
- `docs/V3.x/v3_x-claim-matrix.md`
- `docs/V3.x/v3_x-final-acceptance-report.md`

### Claim Matrix

Allowed claim after acceptance:

```text
V3.x scoped Codex local workflow acceptance passed with documented evidence and claim boundaries.
```

Forbidden expansion remains the global V3.x forbidden claim list. V3.x Final cannot add features and cannot upgrade scoped local Codex workflow evidence into MCP ready, third-party integration verified, Claude Code integration verified, cross-platform readiness, production signed release readiness, all Codex workflows verified, or OS-level Codex window binding ready.

## 下一阶段执行顺序

1. V3.5：已完成 hook diagnostics。
2. V3.6：已保留为 historical blocked evidence，hook-only strategy 不再作为 active strategy。
3. V3.7：已完成 Codex exec JSONL monitor，并作为当前推荐 Codex exec 监听方案。
4. V3.x Final：已完成回归和收口。

每个阶段完成后必须先审计下一阶段计划：

- 对照当前已实现能力修正下一阶段 scope。
- 对照 forbidden claims 修正 claim matrix。
- 对照失败或 deferred 项调整验收标准。
- 如果下一阶段计划和当前事实存在重大偏移，先修正文档，再继续开发。

## 阶段推进 Gate

每个子阶段完成后，进入下一阶段前必须按顺序完成：

1. 当前阶段验收：更新 final acceptance report、evidence、claim matrix 和必要的用户文档。
2. 下一阶段开发计划审计：确认下一阶段 scope、验收标准、allowed claim、forbidden expansion 与当前事实一致。
3. 开发计划漂移和虚假验收风险评估：在当前阶段 final report 或下一阶段 development plan 中记录风险等级和处理结论。

风险评估必须至少覆盖：

- 开发计划漂移风险：实现内容是否偏离原阶段目标，是否引入了未计划的新能力、跨阶段依赖或未审计接口。
- 虚假验收风险：evidence 是否可复跑，是否用 fixture / mock 冒充真实 lifecycle，是否存在 blocked/deferred 项被写成 passed。
- Claim 扩张风险：allowed claim 是否被写成 broader ready / verified / production claim。
- Security redaction 风险：是否可能泄露 token、Authorization header、raw payload、本地完整路径、workspace path 或配置路径。
- 回归覆盖风险：下一阶段是否依赖尚未复跑或尚未通过的 smoke / check。

风险等级定义：

| Level | Meaning | Required action |
| --- | --- | --- |
| Low | 风险已被 evidence、自动检查或明确文档边界覆盖。 | 可以进入下一阶段。 |
| Medium | 存在非阻塞风险，但已有明确缓解措施和 owner。 | 可以进入下一阶段，但必须记录缓解项。 |
| High | 存在计划漂移、false-green、越权 claim、关键 evidence 缺失或安全泄露风险。 | 不得进入下一阶段，必须先修正计划、实现或 evidence。 |

阶段推进规则：

- 如果风险评估没有 High，可以继续执行下一开发阶段计划。
- 如果任一风险为 High，下一阶段 no-go；必须先修正风险来源并重新评估。
- 不允许通过降低验收标准来移除 High；只能通过补证据、改实现、收窄 claim 或明确 blocked/deferred 来解除。
- 风险评估结果必须包含 `overall risk: Low / Medium / High` 和 `go / no-go`。

## ChatGPT 审计文件路径

建议把以下路径交给 ChatGPT 逐项审计：

```text
docs/V3.x/v3_x-development-plan.md
docs/V3.1/v3_1-final-acceptance-report.md
docs/V3.1/v3_1-runtime-regression-harness.md
docs/V3.2/v3_2-development-plan.md
docs/V3.2/v3_2-acceptance-plan.md
docs/V3.2/v3_2-claim-matrix.md
docs/V3.2/v3_2-final-acceptance-report.md
docs/V3.2/evidence/mcp-adapter-smoke-2026-05-23.md
docs/V3.2/evidence/third-party-contract-v3-smoke-2026-05-23.md
docs/V3.3/v3_3-development-plan.md
docs/V3.3/v3_3-acceptance-plan.md
docs/V3.3/v3_3-codex-window-binding-design.md
docs/V3.3/v3_3-final-acceptance-report.md
docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md
docs/V3.4/v3_4-development-plan.md
docs/V3.4/v3_4-acceptance-plan.md
docs/V3.4/v3_4-codex-hooks-design.md
docs/V3.4/v3_4-claim-matrix.md
docs/V3.4/v3_4-final-acceptance-report.md
docs/V3.4/v3_4-real-hook-manual-validation.zh.md
docs/V3.4/evidence/codex-hook-fixture-smoke-2026-05-24.md
docs/V3.4/evidence/codex-hook-real-lifecycle-smoke-2026-05-24.md
docs/V3.4/evidence/codex-hook-redaction-scan-2026-05-24.md
docs/reference/07-integrations.md
docs/reference/multi-codex-workflow.md
docs/reference/third-party-agent-contract.md
docs/ops/troubleshooting.md
README.md
docs/README.md
.codex/hooks.json
scripts/codex-pet-hook.mjs
scripts/v3_4_codex_hook_fixture_smoke.mjs
scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs
packages/petctl/src/codex-launch.ts
packages/petctl/src/args.ts
packages/petctl/src/cli.ts
packages/petctl/src/petctl.test.ts
```

## ChatGPT 审计问题

建议审计时逐项询问：

1. V3.x 已完成阶段是否严格建立在 V3.1-V3.4 已验收事实之上？
2. V3.5、V3.6、V3.7 的 scope 是否存在功能扩张或 false-green 风险？
3. 每个阶段的验收标准是否可执行、可复跑、可审计？
4. 禁止声明是否覆盖了当前项目尚未真实验证的能力？
5. Codex hook mapping 是否正确承认“不等于内部推理精确状态”的边界？
6. OS-level arbitrary window binding 是否被正确排除在 V3.x 已验收声明之外？
7. evidence 文件是否足以支撑每条 allowed claim？
8. security redaction scan 是否覆盖 token、Authorization、raw payload、本地路径和 workspace path？
9. 文档路径是否足够让审计者从计划追溯到实现和证据？
10. V3.x Final 是否只做收口，不再引入新能力？
11. 每个阶段完成后的开发计划漂移和虚假验收风险评估是否存在 High；如果存在，是否正确阻断了下一阶段？
