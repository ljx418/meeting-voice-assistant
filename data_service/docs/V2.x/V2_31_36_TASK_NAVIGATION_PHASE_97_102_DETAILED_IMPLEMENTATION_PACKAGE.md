# V2.31-V2.36 Phase 97-102 详细实施与验收包

## 1. 文档定位

本文档把 V2.31-V2.36 的总控 PRD、目标架构、公共合同和验收矩阵拆成可执行阶段包。每个阶段开始前仍必须生成独立的 development plan、acceptance plan、pre-implementation audit；本文档用于保证后续自动化开发不偏离总规格。

## 2. 全局输入和不可变边界

### 2.1 只读输入

V2.31-V2.36 只读消费以下既有 artifacts：

- V2.0-V2.7：snapshot、inventory、symbols、evidence、DevWiki、Code Graph、Quality、doc-code alignment。
- V2.8-V2.10：visual reports、relationship hardening、adapter/rule specs。
- V2.11-V2.16：Coding Agent actionability、safe patch plan、runtime evidence、incremental intelligence、workbench、agent context。
- V2.18-V2.24：platform console、artifact contract、tool catalog、incremental build、provider SDK、governance、CI readiness。
- V2.25-V2.30：architecture source model、diagram claims、proof graph、intent inference、diagram-code verification、public contracts。

### 2.2 不可变规则

- 不静默改写上游 artifacts。
- 不修改目标项目代码。
- 不声明 full call graph、runtime topology、data flow、control flow、type inference。
- 不把 `import_dependency`、`heuristic_related`、`token_overlap` 写成 deterministic runtime call。
- HarnessOS 只能作为泛化验收样例，不能成为硬编码规则来源。

## 3. Phase 97 / V2.31：Task-Aware Navigation Index

### 3.1 开发设计

模块建议：

```text
backend/data_service/code_assets/coding_agent_navigation/
  task_taxonomy.py
  navigation_index.py
  task_query.py
  evidence_selector.py
  persistence.py
```

核心流程：

```text
task text
  -> task taxonomy classification
  -> capability / surface / symbol / test / doc candidate search
  -> rank candidates by evidence strength and task fit
  -> persist task query artifact
```

### 3.2 产物

```text
coding_agent/task_navigation/navigation_index.json
coding_agent/task_navigation/task_queries/{task_id}.json
```

### 3.3 验收

- data_service 5 个真实任务返回非空 ranked candidates。
- HarnessOS 3 个真实任务返回 accepted candidates 或 structured blocker。
- 每个 candidate 有 evidence、needs_review 或 blocker。
- 不能只靠 token overlap 标 accepted。

## 4. Phase 98 / V2.32：Lightweight Call & Impact Graph

### 4.1 开发设计

模块建议：

```text
relationship_extractors/
  python_ast_calls.py
  imports.py
  handler_dispatch.py
  registry_declarations.py
  config_declarations.py
  test_references.py
  forbidden_scanner.py
```

关系类型必须使用公共合同中的枚举。

### 4.2 产物

```text
coding_agent/task_navigation/relationship_graph.json
coding_agent/task_navigation/relationships.jsonl
coding_agent/task_navigation/relationship_blockers.jsonl
```

### 4.3 验收

- `forbidden_relationship_count == 0`。
- `direct_call_ast` 必须能回读真实 AST source line。
- `module_imports_module` 不得写成 runtime call。
- 抽样至少 30 条 line range 真实性。
- HarnessOS 若 dynamic dispatch 无法解析，必须输出 `dynamic_unresolved` blocker。

## 5. Phase 99 / V2.33：Change Impact & Test Selection

### 5.1 开发设计

输入可以是：

- task_id
- file path
- symbol_id
- surface_id
- capability_id

输出必须区分：

- direct impact
- reference impact
- test impact
- doc impact
- architecture guardrail impact
- unresolved impact

### 5.2 产物

```text
coding_agent/task_navigation/impacts/{task_id}.json
coding_agent/task_navigation/test_selection/{task_id}.json
```

### 5.3 验收

- data_service 5 个真实任务均有 impacted files/symbols/tests。
- 每个 suggested test 有 reason 和 evidence_refs 或 needs_review。
- fatal/major guardrail 不被 ranking 隐藏。
- HarnessOS 无法定位 test 时必须说明 missing evidence type。

## 6. Phase 100 / V2.34：Module Reading Pack & Token Ledger

### 6.1 开发设计

阅读包必须输出：

- required_reads
- optional_reads
- skip_reads
- reuse_patterns
- recommended_next_steps
- token_ledger
- omitted_items

Token 裁剪策略：

1. 保留 high-priority evidence。
2. 合并重复文件和重复 symbol。
3. 删除低优先级建议。
4. 如果 evidence 被裁剪，对应建议必须降级为 needs_review 或 omitted。

### 6.2 产物

```text
coding_agent/task_navigation/reading_packs/{pack_id}.json
coding_agent/task_navigation/reading_packs/{pack_id}.md
coding_agent/task_navigation/token_ledgers/{pack_id}.json
```

### 6.3 验收

- 5 个 data_service 任务证明阅读包小于 naive all-related files。
- 小 token budget 下无 evidence-less high-confidence recommendation。
- omitted_items 每项都有 reason。

## 7. Phase 101 / V2.35：Copilot Agent Integration Contracts

### 7.1 开发设计

暴露 HTTP/MCP/CLI：

- task navigation
- impact analysis
- module reading pack
- test recommendations
- reuse patterns
- agent handoff

接口层只做参数校验和转发，核心逻辑在 focused modules。

### 7.2 产物

```text
coding_agent/task_navigation/handoff/{handoff_id}.json
tool catalog entries
public surface inventory entries
```

### 7.3 验收

- HTTP/MCP/CLI success 和 error envelope parity。
- CLI 输出合法 JSON。
- MCP tool specs 出现在 tool catalog。
- public surface guard 通过。

## 8. Phase 102 / V2.36：Closure, UX Report & Governance

### 8.1 开发设计

收口输出：

- HTML 用户报告。
- Mermaid 任务关系图。
- coverage matrix。
- governance feedback targets。
- data_service + HarnessOS benchmark summary。

### 8.2 产物

```text
coding_agent/task_navigation/reports/task_navigation_report.html
coding_agent/task_navigation/reports/task_navigation_graph.mmd
coding_agent/task_navigation/coverage_matrix.json
coding_agent/task_navigation/closure_audit_report.json
```

### 8.3 验收

- HTML 展示任务解释、必读模块、关系图、影响范围、测试建议、风险、token ledger、blocker。
- Mermaid 每个 node id 可回溯 persisted artifact。
- data_service + HarnessOS E2E 完整。
- full backend regression 通过或仅记录环境性非产品阻塞。

## 9. 全局自动化测试建议

后续实现必须至少新增或扩展以下测试：

```text
test_v2_31_task_navigation_index.py
test_v2_32_lightweight_relationship_graph.py
test_v2_33_change_impact_test_selection.py
test_v2_34_module_reading_pack_token_ledger.py
test_v2_35_copilot_agent_contracts.py
test_v2_36_task_navigation_closure.py
```

## 10. 阶段完成判定

任何阶段不得仅凭单元测试通过验收。必须同时满足：

- artifact 落盘。
- artifact 读回。
- 真实仓库 E2E。
- public payload redaction。
- PRD/spec review。
- false-green review。
- acceptance audit。
