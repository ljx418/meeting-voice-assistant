# Documentation Map

本文说明 `docs/` 下各类文档的用途和维护规则。

## 目录分层

```text
docs/
  active/      当前阶段执行文档：计划、验收、当前差距和配套 drawio
  blueprint/   长期蓝图文档：产品、架构、协议、状态机、窗口、风险
  reference/   用户和集成参考：Multi-Codex workflow、Agent guide、petctl recipes、未来扩展参考
  ops/         工程运维文档：开发环境、网络镜像、排障、本地分发
  V1.0/        V1.0 macOS-first MVP 版本归档
  V2.0/        V2.0 Developer Workflow Integration Release 基线文档
  V2.1/        Real Agent Integration Verification 当前版本文档
  V2.2/        MCP adapter 预研文档，不代表已实现
  V3.0/        Multi-instance Codex Working Partner System 已验收基线
  V3.1/        V3.1 稳定化、用户上手、runtime smoke、迁移备份阶段文档
  V3.2/        Agent Integration Readiness：MCP adapter、Claude hook、third-party contract v3
  V3.7/        Codex Exec JSONL Monitor：当前推荐 Codex exec 监听路径，wrapper-launched codex exec --json 状态映射
  V3.x/        V3.x 后续开发总计划、子阶段验收标准和最终收口计划
  V4.x/        OS-level Codex window/session binding feasibility planning
  V5.x/        Cat Renderer & Asset System：3D 化、动作资产和高级猫咪体验规划
```

## 推荐阅读路径

普通用户：

1. 根目录 `README.md`：快速启动、验证和文档入口。
2. `reference/multi-codex-workflow.md`：一只 Codex 窗口一只猫的实际使用流程。
3. `ops/troubleshooting.md`：启动、端口、token、petctl 常见问题。
4. `ops/macos-local-distribution.md`：macOS unsigned local app 构建和打开。
5. `V3.1/v3_1-local-app-migration-backup.md`：本地迁移、备份和恢复说明。

开发者：

1. `active/development-plan.md`：当前 V4.x active line 和开发边界。
2. `active/acceptance-plan.md`：当前 V4.x 验收门禁。
3. `V4.x/v4_x-development-plan.md`：OS-level Codex window/session binding feasibility planning。
4. `V3.x/v3_x-final-acceptance-report.md`：V3.x closed scoped baseline。
5. `blueprint/03-pet-event-protocol.md`：PetEvent 协议边界。
6. `reference/agent-integration-guide.md` 和 `reference/petctl-recipes.md`：agent 接入与命令 cookbook。

维护者 / 审计者：

1. `V3.0/v3_0-final-acceptance-report.md`：V3.0 ready 的最终依据。
2. `V3.0/v3_0-claim-matrix.md`：允许声明和禁止扩展。
3. `V3.0/v3_0-evidence-index.md`：证据索引。
4. `active/current-vs-target-gap.md` 与 `active/current-vs-target-gap.drawio`：当前 gap 和图。
5. `V3.1/v3_1-final-manual-acceptance-checklist.md`：V3.1 最终人工验收逐项检查表。
6. `V3.1/evidence/`：V3.1 各阶段 evidence。
7. `V3.2/v3_2-claim-matrix.md`：V3.2 集成声明边界。
8. `V3.2/evidence/`：V3.2 MCP / Claude hook / third-party contract evidence。
9. `V3.7/v3_7-final-acceptance-report.md`：V3.7 JSONL monitor scoped passed 的最终依据。
10. `V3.x/v3_x-evidence-index.md`：V3.x final evidence 索引。
11. `V3.x/v3_x-claim-matrix.md`：V3.x final claim 边界。
12. `V3.x/v3_x-final-acceptance-report.md`：V3.x final consolidation 收口报告。
13. `V4.x/v4_x-claim-matrix.md`：V4.x OS-level binding 规划声明边界。
14. `V5.x/v5_x-claim-matrix.md`：V5.x renderer / asset 规划声明边界。

历史阶段文档（`V1.0/`、`V2.0/`、`V2.1/`、`V2.2/`）主要用于审计和追溯。普通用户不需要阅读这些目录才能使用桌宠。

## active

`active/` 是当前开发阶段的执行事实源。

- `development-plan.md`：当前主线开发计划。
- `acceptance-plan.md`：当前主线验收计划。
- `current-vs-target-gap.md`：当前实现、目标状态和差距矩阵。
- `current-vs-target-gap.drawio`：与 gap markdown 同步维护的可视化图。

维护规则：

- 每个阶段完成后必须同步更新 `development-plan.md`、`acceptance-plan.md` 和 `current-vs-target-gap.md`。
- 更新 `current-vs-target-gap.md` 时必须同步更新 `current-vs-target-gap.drawio`。

## blueprint

`blueprint/` 是长期产品与技术合同。

- `00-product-experience.md`：产品体验北极星。
- `00-overview.md`：总体架构。
- `01-tech-stack.md`：技术选型。
- `02-monorepo-structure.md`：monorepo 结构。
- `03-pet-event-protocol.md`：PetEvent 协议。
- `04-cat-state-machine.md`：猫咪状态机。
- `05-desktop-window.md`：桌面窗口策略。
- `target-architecture.md`：目标架构。
- `10-risks-and-decisions.md`：风险与技术决策。

维护规则：

- 只有产品定位、架构边界、协议或长期技术决策变化时才更新。
- 不把阶段性验收日志写入 blueprint。

## reference

`reference/` 是用户接入、命令 cookbook 和未来扩展参考。

- `06-cat-pack.md`：猫咪资产包设计。
- `07-integrations.md`：petctl、MCP、Skill 接入参考。
- `multi-codex-workflow.md`：V3.1 用户流程文档，说明一只 Codex 窗口一只猫。
- `agent-integration-guide.md`：V2.0 本地 Agent 工作流接入指南。
- `petctl-recipes.md`：V2.0 `petctl notify` 命令 cookbook。
- `third-party-agent-contract.md`：V3.2 third-party local agent HTTP + multi-instance contract。
- `08-hardware-light.md`：USB 氛围灯协议参考。
- `post-mvp-roadmap.md`：MVP 之后路线图。

维护规则：

- 可以记录未来方案，但不能作为当前版本已实现能力。
- 如果某项能力进入当前版本开发，应迁移或同步到 `active/` 和对应版本目录。

## ops

`ops/` 是开发、分发和排障相关文档。

- `developer-setup.md`：开发环境配置。
- `network-mirrors.md`：网络镜像和下载加速。
- `troubleshooting.md`：doctor、petctl、端口、unsigned app 常见问题。
- `macos-local-distribution.md`：macOS local unsigned app 构建、首次打开和迁移。
- `release-and-distribution.md`：发布、打包、分发和声明边界。

维护规则：

- 开发环境、构建命令、下载镜像、分发策略变化时更新。
- 不在 ops 中声明未验收的平台 ready。

## version folders

版本目录是历史基线和阶段基线：

- `V1.0/`：macOS-first MVP 归档，除非发现归档错误，否则不改。
- `V2.0/`：Developer Workflow Integration Release 基线和计划。
- `V2.0/v2_0-final-acceptance-report.md`：V2.0 ready 的判断依据，记录最终自动检查、macOS smoke、人工验收和声明边界。
- `V2.1/`：真实 Codex / Claude Code / third-party agent 接入验证计划、证据模板和 gap。
- `V2.2/`：MCP adapter 预研，不创建 `packages/pet-mcp`，不声明 MCP ready。
- `V3.0/`：多实例 Codex 工作伙伴系统已验收基线；`v3_0-final-acceptance-report.md` 是 V3.0 ready 的最终依据；Claude Code、MCP、Windows、USB、3D、照片自定义和 production signing 当前是 deferred backlog，不是 V3.0 已实现能力。
- `V3.1/`：V3.0 之后的稳定化和用户上手阶段；包含 Manager polish、runtime regression harness、local app migration and backup 文档及 evidence。
- `V3.1/v3_1-final-manual-acceptance-checklist.md`：V3.1 final acceptance 的人工验收步骤，用于补齐 Manager UI operator acceptance。
- `V3.1/v3_1-final-acceptance-report.md`：V3.1 final acceptance 的收口报告；当前为 passed，是 V3.1 ready 声明依据。
- `V3.2/`：Agent Integration Readiness 阶段；包含 MCP adapter 最小实现计划、Claude Code hook deferred、third-party contract v3、claim matrix 和 evidence index。V3.2 不代表 `MCP ready`、`Claude Code integration verified` 或 `Third-party agent integration verified`。
- `V3.3/`：Codex window/session-to-pet binding 阶段；早期 Claude Code hook 尝试保留为 historical / superseded，当前 V3.3 final acceptance 依据是 `petctl codex launch` wrapper-first binding smoke。V3.3 不代表 `OS-level Codex window binding ready`、`all Codex workflows verified` 或 `Claude Code integration verified`。
- `V3.4/`：Codex Hooks State Mapping 阶段；包含 `.codex/hooks.json`、`scripts/codex-pet-hook.mjs`、fixture smoke 和 real lifecycle smoke gate。当前 scoped final acceptance 已 passed，依据是 fixture smoke、Codex `/hooks` review/trust 和 operator-confirmed real lifecycle state sync。
- `V3.5/`：Codex hook diagnostics and recovery 阶段；`petctl codex doctor` 和 diagnostics smoke passed。
- `V3.6/`：Real Codex Workflow Coverage Expansion 阶段；当前作为 historical blocked evidence 保留，原因是真实 `PostToolUse` failure hook payload 无稳定 failure fields；hook-only 路线已从 active strategy 中废弃。
- `V3.7/`：Codex Exec JSONL Monitor 阶段；project-owned structured monitor for wrapper-launched `codex exec --json`，当前 scoped final acceptance passed，并作为当前推荐 Codex exec 监听路径。V3.7 不代表 V3.6 hook-only passed、official `PostToolUse` failure hook evidence passed、interactive Codex TUI coverage 或 OS-level window binding。
- `V3.x/`：V3.x 后续开发总计划和 final consolidation；当前包含 `v3_x-development-plan.md`、`v3_x-evidence-index.md`、`v3_x-claim-matrix.md`、`v3_x-final-acceptance-report.md` 和 `v3_x-codex-monitoring-strategy.md`，用于审计 V3.5 hook diagnostics、V3.6 historical blocked boundary、V3.7 JSONL monitor 和 V3.x final consolidation。
- `V4.x/`：已打开 Codex 活动窗口 / OS-level session binding 的 feasibility planning。V4.x 当前不代表 `OS-level Codex window binding ready`，只能声明 planned for feasibility review。
- `V5.x/`：Cat Renderer & Asset System 规划；承接高质量 2D、GLTF/Three.js 3D、动作资产、renderer plugin 和后续自定义资产包导入。V5.x 当前不代表 `Rive / Live2D / 3D ready`。

维护规则：

- 新版本开始时复制或整理活动文档形成该版本基线。
- 版本完成后归档，不再把持续变动内容直接写入旧版本目录。
