# Documentation Map

本文说明 `docs/` 下各类文档的用途和维护规则。

## 目录分层

```text
docs/
  active/      当前阶段执行文档：计划、验收、当前差距和配套 drawio
  blueprint/   长期蓝图文档：产品、架构、协议、状态机、窗口、风险
  reference/   后续参考设计：Cat Pack、Integrations、USB、Post-MVP roadmap
  ops/         工程运维文档：开发环境、网络镜像、排障、本地分发
  V1.0/        V1.0 macOS-first MVP 版本归档
  V2.0/        V2.0 Developer Workflow Integration Release 基线文档
  V2.1/        Real Agent Integration Verification 当前版本文档
  V2.2/        MCP adapter 预研文档，不代表已实现
```

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

`reference/` 是 Post-MVP 或未来扩展参考。

- `06-cat-pack.md`：猫咪资产包设计。
- `07-integrations.md`：petctl、MCP、Skill 接入参考。
- `agent-integration-guide.md`：V2.0 本地 Agent 工作流接入指南。
- `petctl-recipes.md`：V2.0 `petctl notify` 命令 cookbook。
- `third-party-agent-contract.md`：V2.1 third-party local agent HTTP contract。
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

维护规则：

- 新版本开始时复制或整理活动文档形成该版本基线。
- 版本完成后归档，不再把持续变动内容直接写入旧版本目录。
