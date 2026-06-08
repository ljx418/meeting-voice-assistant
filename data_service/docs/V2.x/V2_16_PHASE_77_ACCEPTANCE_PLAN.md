# V2.16 Phase 77 验收计划：Semantic Provider Orchestrator

## 1. 验收目标

证明系统能把 AST baseline 事实转换成带 provider provenance 的语义事实，同时不会把 optional provider 的缺失伪装成成功。

## 2. 必测断言

- `provider_facts.jsonl` 存在且非空。
- `merged_semantic_index.json` 存在且 summary 非空。
- `provider_conflicts.jsonl` 存在。
- 每条 accepted fact 有：
  - `provider_id`
  - `extractor`
  - `confidence`
  - `source_file`
  - `line_range`
  - `evidence_refs`
- optional provider unavailable/unsupported 进入 `provider_blockers`。
- 不出现 `runtime_call`、`data_flow`、`control_flow`、`type_inferred` 等 forbidden claim。

## 3. 三端验收

HTTP / MCP / CLI 必须在以下字段一致：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `summary`
- artifact refs count
- provider blocker count

## 4. 真实数据验收

- 使用当前 data_service 仓库执行 service-level E2E。
- 验证 AST facts 真实来自 snapshot/actionability。
- public payload 不泄露 repo/workspace 绝对路径。

## 5. 打回条件

- AST facts 为空。
- optional provider 缺失被标 accepted。
- token/字符串重叠被当成语义证据。
- 输出 full call graph/data flow/type inference 声明。
