# Development Plan

文档状态：active plan；V3.1 stabilization and onboarding release。

## Current Baseline

V3.1 从已验收的 V3.0 基线开始。

允许保留的核心声明：

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
V2.0 ready: local agent workflow integration and developer usability polish complete.
Third-party local HTTP contract smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
V3.1 planning ready: stabilization, onboarding, runtime smoke, and migration cleanup can start from the V3.0 accepted baseline.
```

V3.0 ready 的判断依据：

- `docs/V3.0/evidence/performance-hardening-final-acceptance-2026-05-20.md`
- `docs/V3.0/v3_0-final-visual-acceptance-checklist.md`
- `docs/V3.0/v3_0-final-acceptance-report.md`
- `docs/V3.0/v3_0-claim-matrix.md`

## V3.1 Product Goal

V3.1 是 V3.0 的稳定化与交付整理阶段。它不继续堆新功能，而是围绕多实例猫、Codex attach、Manager UI、用户启动流程、迁移说明和回归脚本做收口。

## Phase Plan

### Phase 1：V3.0 Release Freeze & Documentation Cleanup

状态：complete。

目标：

- 固化 V3.0 ready 证据链。
- 压缩 README 为快速入口。
- 更新 docs map，告诉用户读哪些文档、不读哪些历史文档。
- 清理 active / V3.0 / drawio 中过期的 pending、blocked、not-run 表述。

验收标准：

- README 只做快速入口，不复制完整历史阶段内容。
- `docs/README.md` 有普通用户、开发者、维护者阅读路径。
- V3.0 final acceptance report 存在，且与 evidence / claim matrix 一致。
- 不把 V3.1 写成 MCP、Windows、USB、3D 或 production release。

### Phase 2：Multi-Codex User Workflow Guide

状态：complete。

目标：

- 让新用户可以完成“一只 Codex 窗口一只猫”。

验收标准：

- `docs/reference/multi-codex-workflow.md` 覆盖 attach、`--print-env`、`notify --instance`、`list`、Manager UI 检查、常见错误和安全边界。
- 用户不需要理解 Rust/Tauri 内部实现即可完成 A/B 两只猫。
- 文档不暴露 token，不声明 OS-level Codex window binding。

### Phase 3：Manager UI Usability Polish

状态：complete。

目标：

- 让 Multi-pet Manager 对普通用户更可理解。

计划任务：

- 消除残余英文动作词。
- Rename / copy / detach 提供轻量反馈。
- default pet 标注为默认猫 / 旧路由。
- extra pet 标注为 Codex 实例猫 / 实例路由。
- currentState 在 Manager 中显示中文状态值。
- soft / hard limit 提示更用户化。
- 复制按钮只复制安全模板文本，不执行命令。

当前证据：

- `docs/V3.1/v3_1-manager-ui-polish.md`
- `docs/V3.1/evidence/manager-ui-polish-2026-05-20.md`

不做：

- 不执行 shell、petctl、curl、node。
- 不做通知中心式 UI。

### Phase 4：Runtime Regression Harness

状态：complete。

目标：

- 提供可重复执行的 V3 runtime smoke。

计划任务：

- 新增本地 smoke 脚本 `scripts/v3_1_runtime_smoke.mjs`。
- 覆盖 health、attach A/B、list、notify A/B、legacy default、unknown instance、invalid instance、invalid sound redaction、hard limit。
- 不打印 token，不破坏用户现有配置。
- 通过 `petctl detach --instance` 只清理本次脚本创建的 Smoke 实例。

当前证据：

- `docs/V3.1/v3_1-runtime-regression-harness.md`
- `docs/V3.1/evidence/runtime-regression-harness-2026-05-21.md`

### Phase 5：Local App Migration & Backup

状态：complete。

目标：

- 说明换目录、换机器、重新安装依赖时如何迁移。

计划任务：

- 以当前实现和实际路径为准确认 config 路径。
- 文档化项目目录、依赖、Rust cache、Tauri config、token/settings/pet instance registry。
- 明确 token/config 不应公开分享。
- 新增只读 `scripts/v3_1_config_audit.mjs`，输出脱敏 config 摘要。

当前证据：

- `docs/V3.1/v3_1-local-app-migration-backup.md`
- `docs/V3.1/evidence/local-app-migration-backup-2026-05-21.md`

### Phase 6：V3.1 Final Acceptance

状态：complete。

目标：

- 收口 V3.1 文档、用户流程、Manager polish、runtime smoke 和迁移说明。

当前证据：

- `docs/V3.1/v3_1-final-acceptance-report.md`

当前结果：

- 自动检查通过。
- runtime smoke 复跑通过。
- config audit 复跑通过。
- Manager UI evidence 已通过人工验收并记录为 `passed`。

final acceptance report `status: passed`，允许声明：

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
```

`docs/V3.1/v3_1-final-acceptance-report.md` 是上述声明的唯一依据。

## Explicit Non-goals

V3.1 不做：

- MCP server。
- Claude Code 完整验证。
- Windows ready / cross-platform ready。
- USB。
- Rive / Live2D / 3D。
- 照片自定义。
- 正式签名、公证、自动更新。
- OS 级 Codex 窗口句柄绑定。
- 通知中心式 UI。
- per-instance queue，除非另行立项。
