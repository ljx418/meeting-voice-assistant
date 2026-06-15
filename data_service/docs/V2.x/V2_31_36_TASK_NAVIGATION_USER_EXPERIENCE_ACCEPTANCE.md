# V2.31-V2.36 用户体验验收场景

## 1. 用户最终体验

本阶段结束后，用户不应该只看到一堆 JSON artifact，而应该能完成以下真实工作：

1. 输入一个开发任务。
2. 看到系统解释任务属于哪类改动。
3. 看到应该先读哪些文件、函数、接口、测试和文档。
4. 看到关键关系图：任务 -> capability -> surface -> handler/symbol -> tests -> guardrails。
5. 看到哪些内容可以跳过，以及为什么。
6. 把结果交给 Copilot 类 Agent，减少重复全仓阅读。
7. 对无法证明的关系看到 blocker，而不是伪造完整架构图。

## 2. 场景一：新增 MCP Tool

### 输入

```text
新增一个用于读取 task navigation report 的 MCP tool，并同步 CLI。
```

### 用户期望看到

- 任务分类：`mcp_tool + cli + report_read`。
- 必读文件：
  - MCP tool registry。
  - MCP dispatcher。
  - CLI command group。
  - report persistence/service。
  - public surface guard tests。
- 关系图：

```text
task -> mcp_tool capability -> MCP registry -> handler -> report service -> tests
```

- 推荐测试：
  - MCP contract。
  - CLI JSON output。
  - public surface guard。
- Token ledger：
  - included：核心 registry/service/test。
  - omitted：无关 frontend、ResearchNotebook provider、历史 docs。

## 3. 场景二：修改 HarnessOS Workflow Dispatch

### 输入

```text
修改 HarnessOS 中 mission workflow 的 dispatch 行为。
```

### 用户期望看到

- 系统尝试定位：
  - workflow manifest。
  - runtime adapter。
  - station/agent descriptor。
  - orchestration tests。
- 如果能证明：
  - 输出 accepted relationship 和 evidence line。
- 如果无法证明：
  - 输出 `dynamic_unresolved` blocker。
  - 说明缺少 manifest、runtime trace、registry 或 test reference。
- 明确不输出：
  - full runtime topology。
  - data flow。
  - control flow。

## 4. 场景三：审查 Patch 风险

### 输入

```text
这个 patch 修改了 snapshot service 和 public surface inventory。
```

### 用户期望看到

- 影响范围：
  - snapshot artifacts。
  - inventory artifacts。
  - public surface guard。
  - context pack / architecture intent consumers。
- 建议测试：
  - snapshot stability。
  - secret skip。
  - public surface golden samples。
  - MCP/HTTP/CLI parity。
- 架构风险：
  - 是否污染 source registry。
  - 是否修改旧大文件。
  - 是否新增无 evidence 的 summary。

## 5. 场景四：低 Token 预算 Agent Handoff

### 输入

```text
请生成 8k token 以内的任务上下文，给 Coding Agent 修改 provider health。
```

### 用户期望看到

- required_reads 被限制在关键 provider registry、health contract、error mapping、tests。
- optional_reads 包含相邻 provider implementation。
- skip_reads 明确列出被跳过的历史 docs 和无关 frontend。
- omitted_items 每项都有 reason。
- 如果 evidence 被裁剪，对应建议被降级为 needs_review 或 omitted。

## 6. 用户验收失败条件

以下用户体验不得验收通过：

- 用户只拿到 JSON，没有可读解释或图。
- 报告看起来完整，但关键关系没有 evidence。
- 系统为了展示好看，隐藏 HarnessOS blocker。
- Token ledger 没有解释 omitted items。
- 建议测试没有 reason。
- HTML/Mermaid 中出现 artifact 中不存在的结论。
