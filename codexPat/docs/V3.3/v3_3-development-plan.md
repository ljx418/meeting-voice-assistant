# V3.3 Development Plan

文档状态：final；V3.3 scope reset to Codex window/session binding.

## Baseline

V3.3 从 V3.2 scoped final acceptance passed 开始，并继承：

```text
V3.2 final acceptance passed for scoped Agent Integration Readiness closure.
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
V3.2 third-party contract v3 smoke passed.
```

早期 V3.3 Claude Code hook 验证已失败。根据 2026-05-24 scope reset，本项目暂时放弃 Claude Code 适配要求；相关 evidence 保留为 historical / superseded，不再作为 V3.3 gate。

## Goal

V3.3 目标改为：让一个本地 Codex terminal window / session 稳定绑定一只猫，并保证该会话产生的状态事件只驱动对应猫。

本阶段采用 wrapper-first，不做不可审计的 OS 级窗口内容推断。`petctl codex launch` 负责：

- 创建或附着 Codex `PetInstance`。
- 注入 `AGENT_DESKTOP_PET_INSTANCE_ID`。
- 设置终端标题，便于人工区分窗口和猫。
- 在 Codex 子进程 lifecycle 中发送 `running`、`success`、`error`。
- 让会话内显式 `petctl notify` 默认路由到当前实例。

## Phase Plan

### Phase 1：Scope Freeze & Claim Boundary

状态：completed。

产物：

- `docs/V3.3/v3_3-claim-matrix.md`
- `docs/V3.3/v3_3-acceptance-plan.md`
- `docs/V3.3/v3_3-current-gap-analysis.md`
- `docs/V3.3/v3_3-codex-window-binding-design.md`

### Phase 2：petctl Codex Launch Wrapper

状态：completed。

实现：

- 新增 `petctl codex launch --name <name> -- <codex args...>`。
- 默认启动 `codex`，smoke 可通过 `--bin` 指定 fake Codex 命令。
- `--no-title` 只用于自动化 smoke，避免终端控制字符污染证据。
- wrapper 不打印 token、Authorization header、raw payload 或本地路径。

### Phase 3：Window/Session Binding Smoke

状态：completed。

产物：

- `scripts/v3_3_codex_window_binding_smoke.mjs`
- `docs/V3.3/evidence/codex-window-binding-smoke-2026-05-24.md`

最低验证：

- desktop health passed。
- session A 创建/绑定 cat A。
- session B 创建/绑定 cat B。
- session A final state 为 `success`。
- session B final state 为 `error`。
- session B 不改变 session A。
- session 内显式 `petctl notify` 使用 env instance route。
- evidence 不包含 token、Authorization、raw payload、config path、workspace path 或完整本地路径。

### Phase 4：Regression & Final Acceptance

状态：completed for V3.3 scoped gate。

本轮已执行：

```bash
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter @agent-desktop-pet/petctl build
node scripts/v3_3_codex_window_binding_smoke.mjs
```

完整 V3.1/V3.2/desktop regression gate 仍应在 release closure 前复跑。

## Explicit Non-goals

V3.3 不做、也不声明：

- Claude Code integration verified。
- Claude Code all workflows verified。
- MCP ready。
- Third-party agent integration verified。
- all Codex workflows verified。
- Windows ready / cross-platform ready。
- USB。
- production signed release。
- OS-level Codex window binding ready。
- per-instance queue ready。
