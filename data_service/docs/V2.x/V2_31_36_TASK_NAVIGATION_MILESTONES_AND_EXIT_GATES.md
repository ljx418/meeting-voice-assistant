# V2.31-V2.36 项目里程碑与出门条件

## 1. 项目宏观里程碑

| 里程碑 | 阶段 | 目标体验 |
| --- | --- | --- |
| M1 | V2.31 | Agent 输入任务后能拿到相关 capability/surface/symbol/test/doc 候选。 |
| M2 | V2.32 | 系统能展示轻量调用、引用、handler dispatch、registry、test 关系，并清楚标注边界。 |
| M3 | V2.33 | 系统能给出影响范围、测试建议和架构边界风险。 |
| M4 | V2.34 | 系统能生成最小阅读包和 token ledger。 |
| M5 | V2.35 | Copilot 类 Agent 能通过 HTTP/MCP/CLI 获取任务上下文、影响分析和 handoff。 |
| M6 | V2.36 | 人类可以通过 HTML/Mermaid 报告验收任务导航质量，并把结果纳入治理。 |

## 2. 全局出门门槛

- data_service 真实任务验收通过。
- HarnessOS 大项目验收通过或输出 structured blocker。
- 无 accepted relationship 缺 evidence。
- 无 public path leak。
- 无 open fatal/major。
- 全量 backend tests 通过或记录环境性非产品阻塞；产品相关测试不得跳过。
- Coverage matrix 每个 accepted row 必须有 test command、artifact path、E2E result、audit report。

## 3. 用户场景验收

### 场景 A：新增 MCP tool

用户输入：

```text
新增一个 architecture intent MCP read tool。
```

期望输出：

- 应读 MCP registry、tool handler、CLI parser、HTTP route、相关 tests。
- 不建议全仓阅读。
- 输出复用 pattern：已有 code platform / architecture intent tools。
- 推荐测试：MCP registry、public surface guard、CLI inventory。

### 场景 B：修改大项目 workflow

用户输入：

```text
修改 HarnessOS 某个 workflow dispatch 行为。
```

期望输出：

- 如果能定位 workflow manifest / runtime adapter / tests，给出 evidence。
- 如果无法确定运行时调用关系，输出 blocker。
- 不允许伪造完整 runtime topology。

### 场景 C：代码审查

用户输入 patch summary。

期望输出：

- 可能影响的 public surface。
- 可能失效的架构 claim。
- 建议跑哪些测试。
- 哪些风险需要人工 review。

### 场景 D：Copilot Agent Handoff

用户输入：

```text
给 Copilot Agent 一个 16k token 内的任务包。
```

期望输出：

- `required_reads` 控制在预算内。
- `recommended_next_steps` 可执行。
- `acceptance_checks` 明确。
- `omitted_items` 解释为什么未纳入。
- 每条关键建议有 evidence 或 `needs_review`。

## 4. 阶段停止条件

任一阶段出现以下情况必须停止并回到计划/审计：

- relationship artifact 出现 forbidden type。
- accepted row 无 evidence。
- HarnessOS blocker 被写成成功关系。
- Token ledger 裁剪 evidence 后仍保留高置信建议。
- HTTP/MCP/CLI public contract 不一致。
- 旧大文件吸收本阶段核心逻辑。
