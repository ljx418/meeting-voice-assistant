# V2.25-V2.30 用户体验与场景验收

## 1. 目标体验

本阶段结束后，用户应能把一个大型项目交给 data_service，然后得到一份“架构理解与落地验证报告”。报告不只是列文件和 raw JSON，而是用图表和解释回答：

- 设计文档想让系统长什么样？
- 当前代码实际长什么样？
- 哪些目标架构节点已经落地？
- 哪些只是文档愿景或低置信推断？
- 哪些代码能力没有文档说明？
- 哪些偏差需要维护者确认？

## 2. 用户场景

### 场景 A：Tech Lead 审查目标架构是否落地

用户输入：项目路径和目标架构 drawio。

用户看到：

- 架构图节点列表。
- 每个节点对应的代码证据、配置证据、测试证据。
- `accepted / weak_match / missing_code_evidence / conflict / stale` 状态。
- 需要人工确认的节点。

验收门槛：

- 至少一个目标架构图节点可以追踪到代码 evidence。
- 缺失节点不会被伪装为 accepted。

### 场景 B：Coding Agent 准备修改一个工作流

用户输入：开发任务，例如“修改 HarnessOS station binding 流程”。

用户看到：

- 相关 architecture intent candidate。
- 可能涉及的 workflow/module/config/test。
- 图中设计关系与代码证据关系的差异。
- 下一步建议和需要人工确认的问题。

验收门槛：

- 每条建议有 evidence 或 needs_review。
- 小 token budget 下不能保留无证据建议。

### 场景 C：文档维护者检查架构文档质量

用户输入：项目文档目录。

用户看到：

- 哪些文档是 target、plan、audit、historical。
- 哪些目标架构图过期。
- 哪些 claim 没有代码证据。
- 哪些代码事实没有文档覆盖。

验收门槛：

- 历史文档不被误判为当前目标。
- stale / superseded 文档可见。

### 场景 D：维护者确认或驳回系统推断

用户操作：

- 对某条 intent candidate 点击 confirm / reject / needs_review。
- 生成 governance overlay。
- 后续 report 读取时显示 applied_rules。

验收门槛：

- confirm/revoke 不修改原始 artifacts。
- source artifact hash 不变。

## 3. 报告可读性要求

HTML 报告必须包含：

- 架构总览图。
- target/current/inferred/confirmed/diff 五区块。
- diagram-to-code 状态板。
- proof graph 摘要。
- 风险和 blocker。
- 推荐下一步。

不允许：

- 只输出 raw JSON。
- 只给表格没有解释。
- 隐藏 weak/missing/conflict。
- 图中节点无法追溯到 artifact。
