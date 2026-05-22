# Current vs Target Gap

文档状态：active gap；V3.1 stabilization and onboarding release。  
配套图：`current-vs-target-gap.drawio`。

## Current State

当前已完成并验收：

- macOS-first MVP：Tauri 桌面猫、透明窗口、拖拽、托盘、设置页。
- PetEvent / HTTP API / diagnostics / `petctl notify` / safe sound。
- V2.0 workflow templates、recipes、shell/Node 示例、settings diagnostics polish、CSS cat polish、macOS local distribution docs。
- V2.1-A third-party local HTTP contract smoke passed。
- V2.1-B Codex local workflow integration verified for tested local Codex CLI smoke scenarios。
- V3.0 multi-instance Codex workflow final acceptance passed for tested local Codex session scenarios。

当前 V3.1 主线是稳定化与交付整理：文档收口、用户上手、多 Codex workflow guide、Manager polish、runtime smoke 和本地迁移说明。

## Implemented Baseline Checklist

| Version / phase | Implemented capability | Evidence / notes |
| --- | --- | --- |
| ✅ V1.0 / macOS-first MVP | Tauri 桌面壳、透明无边框置顶窗口、拖拽、位置持久化、系统托盘、设置页。 | macOS-first MVP 已验收；Windows 不在 V1.0 验收范围内。 |
| ✅ V1.0 / Local Event Bridge | PetEvent JSON Schema、本地 HTTP API、token、白名单、rate limit、diagnostics、rejected reason sanitization。 | HTTP / diagnostics smoke 已通过。 |
| ✅ V1.0 / CLI & Sound | `petctl notify`、JSON stdin、内置安全声音白名单、静音、cooldown。 | CLI smoke 与 safe sound smoke 已通过。 |
| ✅ V2.0 Final Acceptance | Developer workflow polish。 | `docs/V2.0/v2_0-final-acceptance-report.md` passed。 |
| ✅ V2.1-A | Third-party local HTTP contract smoke passed。 | 不代表真实第三方产品集成 verified。 |
| ✅ V2.1-B | Codex local workflow integration verified for tested local Codex CLI smoke scenarios。 | 不代表所有 Codex workflow、MCP 或 cross-platform。 |
| ✅ V3.0 Final Acceptance | Multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios。 | `docs/V3.0/v3_0-final-acceptance-report.md` and evidence passed。 |
| ✅ V3.1 Phase 1 | V3.0 Release Freeze & Documentation Cleanup。 | complete。 |
| ✅ V3.1 Phase 2 | Multi-Codex User Workflow Guide。 | complete。 |
| ✅ V3.1 Final Acceptance | Stabilization, onboarding, Manager polish, runtime smoke and migration guidance。 | `docs/V3.1/v3_1-final-acceptance-report.md` passed。 |

## Target State

V3.1 目标：

- README 是快速入口，不复制完整历史阶段内容。
- docs map 明确普通用户、开发者、维护者分别该读哪些文档。
- multi-codex workflow guide 能让新用户完成“一只 Codex 窗口一只猫”。
- Manager UI 更易理解。
- runtime smoke 可重复执行且不泄露 token、不破坏用户配置。
- migration 文档基于真实 config 路径，不虚构。

## Gap Matrix

| Gap | Current | Target | Status |
| --- | --- | --- | --- |
| V3.0 release evidence | V3.0 final checklist and evidence passed。 | Final acceptance report 作为统一入口。 | ✅ V3.1 Phase 1 |
| README / docs map | README 快速入口和 docs map 已收口。 | README 快速入口；docs map 按角色导读。 | ✅ V3.1 Phase 1 |
| Multi-Codex onboarding | V3.0 能力已实现，workflow guide 已存在。 | 新用户按文档完成 A/B Codex session 各一只猫。 | ✅ V3.1 Phase 2 |
| Manager UI usability | 文案、反馈、复制安全和布局 polish 已实现并通过人工验收。 | 自动检查和人工验收通过后冻结。 | ✅ V3.1 Phase 3 |
| Runtime smoke | 脚本与最小清理能力已实现并通过。 | 一条脚本可重复验证核心 runtime 链路。 | ✅ V3.1 Phase 4 |
| Migration / backup | 只读 config audit 和迁移备份文档已实现并通过。 | 明确真实 config 路径和迁移策略。 | ✅ V3.1 Phase 5 |
| V3.1 final acceptance | 自动检查、runtime smoke、config audit 和 Manager UI 人工验收均已通过。 | final acceptance report passed 后允许 V3.1 ready。 | ✅ V3.1 ready |

## Allowed Current Claims

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
V2.0 ready: local agent workflow integration and developer usability polish complete.
Third-party local HTTP contract smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
V3.1 planning ready: stabilization, onboarding, runtime smoke, and migration cleanup can start from the V3.0 accepted baseline.
V3.1 Phase 4 complete: repeatable runtime regression smoke ready.
V3.1 Phase 5 complete: local app migration and backup guidance ready.
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
```

当前 final acceptance：

```text
V3.1 final acceptance passed.
```

## Forbidden Current Claims

```text
all Codex workflows verified
unqualified multi-instance Codex verified beyond tested local scenarios
per-instance queue ready
OS-level Codex window binding ready
Claude Code integration verified
Third-party agent integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
Rive/Live2D/3D ready
photo customization ready
user asset upload ready
remote asset download ready
custom asset pack import ready
production signed release ready
auto update ready
```
