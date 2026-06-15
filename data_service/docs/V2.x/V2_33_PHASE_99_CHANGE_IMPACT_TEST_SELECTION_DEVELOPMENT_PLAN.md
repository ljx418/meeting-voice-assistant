# V2.33 Phase 99 开发计划：Change Impact & Test Selection

阶段：V2.33 / Phase 99
前置阶段：Phase 97、Phase 98 accepted
目标：基于 task navigation 与 lightweight relationships，为 Coding Agent 输出任务影响范围、测试建议、风险和 blocker。

## 1. 阶段目标

Phase 99 输入一个 task 或 Phase 97 `task_id`，输出：

- impacted files
- impacted symbols
- impacted surfaces
- impacted docs
- impacted tests
- architecture guardrails
- risk items
- suggested tests
- unresolved impact blockers

Phase 99 不做：

- 真实运行时影响证明。
- 完整调用图。
- data flow / control flow。
- 自动修改代码。
- 自动执行测试。

## 2. 输入

```text
coding_agent/task_navigation/navigation_index.json
coding_agent/task_navigation/task_queries/{task_id}.json
coding_agent/task_navigation/relationship_graph.json
coding_agent/task_navigation/relationships.jsonl
snapshot files / surfaces / symbols / evidence
```

如果 task query 或 relationship graph 缺失，允许自动构建上游 Phase 97/98 产物；若必需 artifacts 缺失，必须返回 structured blocker。

## 3. 输出

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/impacts/{task_id}.json
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/test_selection/{task_id}.json
```

## 4. 实现设计

新增 focused modules：

```text
backend/data_service/code_assets/coding_agent_navigation/impact_analysis.py
backend/data_service/code_assets/coding_agent_navigation/impact_persistence.py
```

最小挂载：

- HTTP：`code_assets_coding_agent.py`
- MCP：`mcp_code_coding_agent_tools.py`
- CLI：`cli_code_coding_agent.py`

公共路径：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2/{task_id}
```

说明：已有 V2.11 `/coding-agent/impact` 保持不变，Phase 99 使用 `impact-v2` 避免 contract drift。

## 5. 分析策略

### 5.1 Impact scoring

来源：

- Phase 97 matched candidates。
- Phase 98 relationships。
- test reference relationships。
- path/name/capability overlap。

Impact 类型：

- `direct_task_match`
- `relationship_neighbor`
- `surface_impact`
- `symbol_impact`
- `test_impact`
- `doc_impact`
- `guardrail_impact`
- `unresolved_impact`

### 5.2 Test selection

测试建议必须包含：

- test_ref
- path
- reason
- confidence
- evidence_refs 或 needs_review
- linked impact refs

如果无法定位 test，必须返回 blocker，例如：

```text
TEST_EVIDENCE_UNAVAILABLE
TEST_REFERENCE_UNRESOLVED
```

## 6. 风险控制

| 风险 | 控制 |
| --- | --- |
| import relation 被当作 runtime impact | impact reason 必须写 `static_reference` |
| 没有 test 仍返回空成功 | 输出 `TEST_EVIDENCE_UNAVAILABLE` blocker |
| weak candidate 影响被写成 accepted | 低置信度保留 `needs_review` |
| major/fatal guardrail 被隐藏 | risk items 必须 pin 到输出 |

## 7. 完成定义

- data_service 5 个真实任务均有 impact artifact。
- 每个 suggested test 有 reason 和 evidence 或 needs_review。
- HarnessOS 输出 accepted impact 或 structured blocker。
- HTTP/MCP/CLI read/build 一致。
- PRD/spec/false-green audit 无 fatal/major。
