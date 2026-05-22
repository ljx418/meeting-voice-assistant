# Acceptance Plan

文档状态：active acceptance；V3.1 stabilization and onboarding release。

## Baseline Gate

V3.1 只能从 V3.0 final acceptance passed 的基线开始。

必须存在并通过：

- `docs/V3.0/evidence/performance-hardening-final-acceptance-2026-05-20.md`：`status: passed`。
- `docs/V3.0/v3_0-final-visual-acceptance-checklist.md`：operator result passed。
- `docs/V3.0/v3_0-final-acceptance-report.md`：记录 V3.0 ready scope。
- `docs/V3.0/v3_0-claim-matrix.md`：声明边界与 evidence 一致。

当前检查结果：baseline passed。

## Phase 1 Acceptance：Release Freeze & Docs Cleanup

通过标准：

- README 是快速入口，不复制完整历史阶段。
- `docs/README.md` 能告诉普通用户、开发者、维护者分别读哪些文档。
- V3.0 final acceptance report 存在。
- active / V3.0 / drawio 对 V3.0 ready 和禁止声明保持一致。
- 不声明 MCP、Windows、USB、3D、照片自定义或 production release。

当前结果：passed。

## Phase 2 Acceptance：Multi-Codex Workflow Guide

通过标准：

- `docs/reference/multi-codex-workflow.md` 存在。
- 文档能指导用户完成：
  - `attach codex`
  - `notify --instance`
  - `AGENT_DESKTOP_PET_INSTANCE_ID`
  - 两个 Codex session 分别对应两只猫
  - Manager UI 检查
- 常见错误和安全边界完整。
- 不暗示 OS-level window binding 或 all Codex workflows verified。

当前结果：passed。

## Phase 3 Acceptance：Manager UI Usability Polish

通过标准：

- Manager UI 中文文案可理解。
- Rename / copy / detach 有即时反馈。
- default 和 extra pet 的含义明确。
- currentState 值显示为中文。
- 重命名后卡片和猫窗口名字即时更新，不需要 reload。
- 移除使用“移除 / 确认移除”二次点击，不使用系统 confirm。
- 复制环境变量和通知命令只复制文本，不执行命令。
- 不显示 token、raw payload、metadata 全量或 workspace path。
- 不提供命令执行按钮。

验收证据：

- `docs/V3.1/evidence/manager-ui-polish-2026-05-20.md`

当前结果：passed。允许声明 `V3.1 Phase 3 complete: multi-pet manager usability polish ready.`。

## Phase 4 Acceptance：Runtime Regression Harness

通过标准：

- 一条本地 smoke 命令可覆盖 V3 runtime/API/CLI 链路。
- 脚本不打印 token。
- 脚本不破坏用户现有配置；临时实例会被清理，或明确记录不可清理项。
- 失败时输出具体 case。
- `DELETE /api/instances/:instanceId` 和 `petctl detach --instance` 只用于安全清理非 default 测试实例。
- 脚本不启动 GUI 自动视觉判断，不替代人工验收。

验收证据：

- `docs/V3.1/evidence/runtime-regression-harness-2026-05-21.md`

当前结果：passed。允许声明 `V3.1 Phase 4 complete: repeatable runtime regression smoke ready.`。

## Phase 5 Acceptance：Local App Migration & Backup

通过标准：

- 文档中的 config 路径来自当前实现或实际验证，不虚构。
- 用户知道迁移项目目录、依赖、Tauri config、token/settings/pet instance registry。
- 安全边界明确：token/config 不应公开分享。
- 不把 unsigned local app 写成正式发布。
- `node scripts/v3_1_config_audit.mjs` 和 `--json` 输出均脱敏。
- audit 不打印 token、raw settings、Authorization header、完整 `/Users/<name>/...` 路径或完整 workspace path。
- README 只保留入口，不复制完整迁移文档。

验收证据：

- `docs/V3.1/evidence/local-app-migration-backup-2026-05-21.md`

当前结果：passed。允许声明 `V3.1 Phase 5 complete: local app migration and backup guidance ready.`。

## Phase 6 Acceptance：V3.1 Final Acceptance

自动检查：

```bash
pnpm run doctor
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter desktop check
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop build
pnpm --filter desktop tauri build -b app
```

final acceptance report `status: passed`，允许声明：

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
```

当前结果：

- `docs/V3.1/v3_1-final-acceptance-report.md`：`status: passed`。
- 自动检查、runtime smoke 和 config audit 在 2026-05-22 复跑通过。
- Manager UI evidence 已通过人工验收。
- 当前允许声明 V3.1 ready，声明范围以 final acceptance report 为准。

## No False-Green

V3.1 仍不得声明：

```text
Windows ready
cross-platform ready
MCP ready
USB ready
production signed release ready
OS-level Codex window binding ready
all Codex workflows verified
Rive / Live2D / 3D ready
photo customization ready
per-instance queue ready
```
