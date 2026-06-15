# V2.32 Phase 98 验收计划：Lightweight Relationship Graph

阶段：V2.32 / Phase 98
目标：验证轻量关系层能支撑后续影响分析，但不会虚假声称完整调用图或运行时拓扑。

## 1. 自动化验收

必须新增或扩展测试：

```text
backend/tests/test_v2_32_lightweight_relationship_graph.py
```

覆盖：

- relationship graph build/read。
- HTTP/MCP/CLI smoke。
- artifact disk inspection。
- forbidden relationship scanner。
- line range truth sampling。
- no absolute path leak。

## 2. data_service 真实仓库验收

真实仓库：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

必须验证：

- relationship artifact 非空。
- 至少包含 `surface_handled_by`、`module_imports_module`、`capability_related_to_surface`。
- 若存在 direct AST relation，line range 必须能回读真实源码。
- `module_imports_module` 不得写成 runtime call。
- forbidden relationship count = 0。

## 3. HarnessOS 真实仓库验收

真实仓库：

```text
/Users/Zhuanz/Desktop/workspace/harnessOS
```

必须验证：

- extractor 尝试 workflow / registry / entrypoint / tests 通用 pattern。
- 输出 accepted relationship 或 structured blocker。
- 若 dynamic dispatch 无法解析，必须输出 `dynamic_unresolved` blocker。
- 不允许写 HarnessOS 专用硬编码规则作为 accepted relation。

## 4. Truth Sampling

至少抽样 30 条 relationship：

- path 存在。
- line_range 在文件范围内。
- snippet 包含 source 或 target hint。
- evidence_refs 可追踪。

如果 accepted relationship 不足 30 条，必须抽样全部 accepted relation，并记录不足原因。

## 5. Public Contract

HTTP/MCP/CLI 必须输出一致的稳定字段：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- relationship count
- blocker count
- forbidden relationship count
- artifact_refs
- warnings / unresolved

## 6. False-Green Rejection

以下情况不得通过：

- 出现 `full_call_graph`、`runtime_call_accepted`、`data_flow`、`control_flow`、`runtime_topology`、`type_inferred`。
- `module_imports_module` 被解释为 runtime call。
- dynamic dispatch 无证据却 marked accepted。
- 只生成空 graph 仍返回 success。
- public payload 泄露 `/Users/`、`/private/var` 或 secret。
- HarnessOS 缺 accepted relation 但没有 structured blocker。

## 7. 出门条件

- Focused tests 通过。
- data_service E2E 通过。
- HarnessOS E2E accepted 或 blocker 通过。
- PRD/spec review 无 fatal/major。
- Phase 98 acceptance audit report 落盘。
