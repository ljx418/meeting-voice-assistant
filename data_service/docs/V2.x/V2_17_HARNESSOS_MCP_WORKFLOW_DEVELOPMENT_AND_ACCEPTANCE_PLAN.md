# V2.17 开发与验收计划：HarnessOS MCP 工作流接入审计

## 1. 阶段性质

V2.17 是特殊验收阶段，以审计、规格冻结和接入验收设计为主。

本阶段输出：

- PRD。
- 目标架构。
- 接入开发与验收计划。
- 审计报告。
- HTML 可视化验收报告。

## 2. 阶段拆分

| 子阶段 | 名称 | 目标 |
| --- | --- | --- |
| 83.1 | 当前能力盘点 | 确认 MCP tools、V2.16 closure、测试状态和 HarnessOS 路径。 |
| 83.2 | 工作流接入规格 | 定义 HarnessOS / data_service 职责边界和调用路径。 |
| 83.3 | 用户场景验收 | 定义 Workflow Agent、Coding Agent、Review Agent、人类维护者路径。 |
| 83.4 | 风险与安全门禁 | 定义 high-risk gate、runtime profile、patch preview、no-autonomous-apply。 |
| 83.5 | HTML 验收报告 | 生成高可读中文网页，包含图表、矩阵和结论。 |

## 3. 真实数据检查

本阶段使用真实本地信息：

| 检查项 | 结果 |
| --- | --- |
| data_service MCP registry | 当前 `all_tool_specs()` 返回 156 个 tools。 |
| `knowledge_code_*` tools | 99 个。 |
| `knowledge_code_architecture_*` tools | 57 个。 |
| V2.16 closure | `V2_16_PHASE_82_CLOSURE_AUDIT_REPORT.md` 记录 accepted。 |
| HarnessOS repo | `/Users/Zhuanz/Desktop/workspace/harnessOS` 存在。 |
| HarnessOS 文档 | 发现 README、AGENTS、CLAUDE、docs/design/V4.x、V9.x 等文档。 |

## 4. 接入验收矩阵

| 能力 | data_service 当前状态 | 接入 HarnessOS 状态 | 验收结论 |
| --- | --- | --- | --- |
| 项目导入与 snapshot | 已实现 | 可作为 MCP 前置步骤 | ready |
| 架构文档扫描 | 已实现 | 可扫描 HarnessOS docs/design | ready |
| 文档-代码对齐 | 已实现 | 可用于 HarnessOS 架构差异审计 | ready |
| Human report | 已实现 | 可作为 Review Agent 输入 | ready |
| Context pack | 已实现 | 可作为 Coding Agent 输入 | ready |
| Impact analysis | 已实现 | 可用于任务拆解 | ready |
| Safe patch plan | 已实现 | 可用于改动前计划 | ready |
| Patch preview | 已实现，只读 | 需要 HarnessOS 审批后才能继续 | gated |
| Runtime profile | 已实现 allowlist-only | 需要 HarnessOS profile 策略映射 | gated |
| Patch apply | blocked by default | 不应由 data_service 自动执行 | blocked |
| Git 操作 | out of scope | 必须由 HarnessOS 或人类处理 | blocked |
| Agent orchestration | out of scope | HarnessOS 自身职责 | not_data_service |

## 5. 用户场景验收

### 场景 A：HarnessOS 项目理解

输入：

```text
请读取 HarnessOS，说明它的工作流架构、关键文档、代码入口和风险。
```

期望：

- 输出项目摘要。
- 输出 docs/design 资产地图。
- 输出 target/current/diff 架构视图。
- 明确 accepted / needs_review / blocked。

通过标准：

- 不把文档 claim 当作代码 fact。
- 不输出无证据架构结论。

### 场景 B：Coding Agent 开发准备

输入：

```text
在 HarnessOS 中增加一个 workflow MCP 接入检查步骤。
```

期望：

- impact analysis。
- task plan。
- 相关文件和文档。
- 风险和测试建议。
- context pack。

通过标准：

- 每条建议有 evidence 或 needs_review。
- 低置信建议不显示为 ready。

### 场景 C：Review Agent 审查

输入：

```text
审查这个任务是否可以进入 patch preview。
```

期望：

- risk lane。
- blocker。
- runtime profile 建议。
- patch preview 只读。

通过标准：

- 未批准时 apply 必须 blocked。
- runtime 只能使用 allowlist profile。

### 场景 D：人类维护者验收

输入：

```text
这套 MCP 接入是否安全可靠？
```

期望：

- 职责边界图。
- 高风险动作清单。
- ready/gated/blocked 矩阵。
- 下一步接入步骤。

## 6. 高风险停止条件

如果出现以下情况，不能声称 MCP 接入 ready：

- MCP tool registry 无法读取。
- HarnessOS repo 不存在。
- HarnessOS 文档资产无法发现。
- context pack 无 evidence 或 needs_review。
- patch preview 修改源码。
- apply 未经审批可执行。
- runtime profile 接受任意命令。
- data_service 试图接管 HarnessOS orchestration。

## 7. 最小正式接入前验收

在 HarnessOS 真实接入前，还应补一轮 E2E：

1. HarnessOS 通过 MCP client 调用 data_service。
2. 调用 codebase import / snapshot / architecture build。
3. 生成 HarnessOS context pack。
4. 生成一个真实任务的 impact analysis。
5. 生成 patch preview，确认不修改源码。
6. 运行 allowlist runtime profile 或返回 structured blocker。
7. HarnessOS 工作流记录 data_service artifact refs。

## 8. 本阶段完成定义

V2.17 完成定义：

- 特殊阶段文档齐全。
- 验收规格清晰。
- 用户场景明确。
- HTML 报告可读。
- 明确结论：可作为 HarnessOS 项目智能 MCP 工具层接入，但不替代 HarnessOS 编排核心。

