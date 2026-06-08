# V2.17 特殊验收 PRD：HarnessOS MCP 工作流接入审计

## 1. 阶段定位

V2.17 是一个特殊验收阶段，不新增自动改代码能力，目标是审计并定义：

> `data_service` 能否作为 HarnessOS 多 Agent 联合开发工作流中的项目智能 MCP 工具层。

本阶段不把 `data_service` 变成 HarnessOS 的工作流编排器，也不替代 HarnessOS 的 agent orchestration、权限审批、任务队列、状态机或真实执行平台。

## 2. 背景

当前 `data_service` 已完成 V2.0-V2.16 主线能力：

- 本地 codebase registry、snapshot、public surface、symbol、evidence。
- DevWiki、Code Graph、Quality Governance、Architecture views。
- 文档资产治理、文档-代码对齐、目标/当前/差异架构报告。
- 大项目抽象、pattern evidence、review queue、human report。
- Coding Agent actionability、impact analysis、task plan、safe patch plan。
- runtime profiles、runtime evidence、incremental diff、drift timeline。
- Workbench / Workbench v2、large-project advisor、human-gated patch sandbox。
- MCP registry 当前可见 156 个 tools，其中 `knowledge_code_*` 99 个，`knowledge_code_architecture_*` 57 个。

HarnessOS 是一个多 Agent / workflow orchestration 方向的大项目，包含多版本设计文档、运行时边界、安全策略、workflow spec、agent executor、controlled runtime、terminal sandbox、governance 等内容。它需要一个外部项目智能工具层帮助 Agent 在执行任务前理解项目、抽取证据、生成上下文和做风险审计。

## 3. 核心目标

V2.17 的目标是形成一个可审计结论：

```text
data_service 是否可以作为 HarnessOS 工作流 MCP 接入工具；
如果可以，接入后承担哪些职责；
哪些能力已具备；
哪些能力必须由 HarnessOS 自身承担；
哪些验收门槛必须通过后才能进入真实多 Agent 工作流。
```

## 4. In Scope

1. HarnessOS MCP 接入角色定义。
2. data_service 当前能力清单与 MCP 工具映射。
3. HarnessOS 真实仓库存在性和文档资产可见性确认。
4. 多 Agent 工作流中的工具调用路径设计。
5. 用户场景与用户体验验收。
6. 接入验收矩阵。
7. 安全边界、human gate、runtime profile、patch preview 风险界定。
8. HTML 可视化验收报告。

## 5. Out of Scope

本阶段不实现或不承诺：

- HarnessOS 的多 Agent 编排核心。
- 自动分配 Agent、自动推进 workflow state。
- 任意 shell command runner。
- 自动修改源码并提交远端。
- 自动 PR / merge。
- full call graph、data flow、control flow、type inference。
- 从代码中完整恢复人类设计意图。
- 对 HarnessOS workflow spec 的强绑定或项目专用 hardcoding。

## 6. 目标用户

| 用户 | 目标 |
| --- | --- |
| HarnessOS Workflow Agent | 在执行任务前调用项目智能 MCP，获得项目事实、证据、上下文和风险。 |
| Coding Agent | 获取任务计划、候选文件、相关 public surface、测试建议和 patch preview。 |
| Review Agent | 审查 evidence、relationship、ranking、blocker 和 runtime result。 |
| Documentation Agent | 读取文档声明、文档-代码差异和 architecture context pack。 |
| 人类维护者 | 判断是否允许进入高风险动作，例如 patch apply、真实运行、git 操作。 |

## 7. 目标体验

### 7.1 体验路径

```text
HarnessOS 工作流发起任务
  -> 调用 data_service MCP 导入/读取 HarnessOS codebase
  -> 构建或读取 snapshot / architecture / docs / evidence
  -> 生成 task plan / impact analysis / context pack
  -> Coding Agent 读取上下文并提出方案
  -> Review Agent 检查 evidence、risk、blocker
  -> data_service 生成 patch preview / runtime profile 建议
  -> HarnessOS 自己决定是否进入人工审批或后续执行
```

### 7.2 用户能看到什么

- HarnessOS 项目入口和文档资产地图。
- 哪些能力是从代码证据得出，哪些只是文档声明。
- 多 Agent 工作流任务需要关注的文件、模块、测试和风险。
- 可传给 Coding Agent 的 context pack。
- 可传给 Review Agent 的 evidence / blocker / ranking。
- runtime profile 是否允许运行、运行结果是什么。
- patch preview 是否只读、是否需要人工审批。

## 8. 功能规格

### 8.1 MCP 工具层角色

data_service 作为 MCP 工具层时提供：

- `knowledge_codebase_*`：项目登记、snapshot、describe、archive。
- `knowledge_code_architecture_*`：架构、文档、graph、evidence、report、context pack。
- `knowledge_code_*`：symbol、quality、actionability、impact、task plan、patch plan、runtime、workbench。

### 8.2 HarnessOS 工作流边界

HarnessOS 仍负责：

- Agent 编排和调度。
- workflow state。
- human approval。
- 权限模型。
- 执行队列。
- 任务生命周期。
- 真实代码修改/提交策略。

data_service 只负责：

- 项目事实和证据。
- 上下文准备。
- 风险和 blocker。
- patch preview 和 rollback artifact。
- allowlist runtime profile。
- 给 Agent 消费的 MCP contract。

### 8.3 成功判定

本阶段通过的含义：

```text
data_service 可以作为 HarnessOS 工作流的项目智能 MCP 工具层接入。
```

本阶段不意味着：

```text
HarnessOS 多 Agent 执行闭环已经由 data_service 完成。
```

## 9. 验收定义

V2.17 完成必须满足：

1. 文档说明清楚 data_service 和 HarnessOS 的职责边界。
2. MCP 工具清单真实来自当前 registry。
3. HarnessOS repo 路径真实存在，并能发现设计文档。
4. 工作流接入路径明确。
5. 用户场景明确，至少覆盖项目理解、Coding Agent 准备、Review Agent 审查、安全 patch preview。
6. 验收矩阵明确区分 accepted、ready、gated、blocked。
7. 高风险动作默认需要 HarnessOS 或人类审批。
8. HTML 报告可读，含架构图、工作流图、能力矩阵、风险图和验收门槛。

