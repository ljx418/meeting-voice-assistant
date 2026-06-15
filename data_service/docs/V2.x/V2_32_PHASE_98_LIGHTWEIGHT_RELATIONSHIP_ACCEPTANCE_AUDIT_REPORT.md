# V2.32 Phase 98 验收审计报告：Lightweight Relationship Graph

审计日期：2026-06-10
阶段：V2.32 / Phase 98
结论：**通过，允许进入 Phase 99 pre-implementation planning。**

本阶段完成轻量关系层的最小闭环：基于 surfaces、symbols、imports、mappings、evidence 和 Phase 97 navigation index，生成浅层关系图，并通过 HTTP/MCP/CLI 读取。

## 1. 实现范围

新增 focused modules：

```text
backend/data_service/code_assets/coding_agent_navigation/relationship_graph.py
backend/data_service/code_assets/coding_agent_navigation/relationship_persistence.py
```

新增 artifacts：

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/relationship_graph.json
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/relationships.jsonl
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/relationship_blockers.jsonl
```

新增公共入口：

```text
HTTP:
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships

MCP:
knowledge_code_task_relationships_build
knowledge_code_task_relationships_read

CLI:
knowledge code coding-agent relationships-build
knowledge code coding-agent relationships
```

## 2. 关系类型

本阶段已生成并验收：

- `surface_handled_by`
- `registry_declared`
- `config_declared`
- `module_imports_module`
- `direct_call_ast`
- `test_references_symbol`
- `capability_related_to_surface`

语义边界：

- `module_imports_module` 仅表示 static import，不代表 runtime call。
- `direct_call_ast` 仅表示同文件 AST 语法直连，不代表完整调用图。
- attribute / dynamic call 进入 blocker，不标 accepted。

## 3. 真实仓库 E2E 验收

验收 workspace：

```text
/private/tmp/data_service_v232_phase98_real_matrix
```

### data_service

```text
snapshot_id: snap_5ed0484f4aec6a67b290
relationship_count: 8933
accepted_count: 8845
needs_review_count: 88
blocked_count: 18284
forbidden_relationship_count: 0
```

relationship type counts：

```text
capability_related_to_surface: 604
config_declared: 8
direct_call_ast: 4592
module_imports_module: 2624
registry_declared: 511
surface_handled_by: 506
test_references_symbol: 88
```

### HarnessOS

```text
snapshot_id: snap_768a01fc0dbd1f46f26e
relationship_count: 10648
accepted_count: 10293
needs_review_count: 355
blocked_count: 13017
forbidden_relationship_count: 0
```

relationship type counts：

```text
capability_related_to_surface: 101
config_declared: 46
direct_call_ast: 4985
module_imports_module: 5161
registry_declared: 188
test_references_symbol: 167
```

HarnessOS 结论：本阶段已能生成 accepted lightweight relationships，同时保留 dynamic / attribute unresolved blockers。未声称完整工作流运行时拓扑。

## 4. 自动化测试结果

```text
PYTHONPATH=backend /usr/bin/python3 -m pytest backend/tests/test_v2_32_lightweight_relationship_graph.py -q
1 passed

PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_v2_31_task_navigation.py \
  backend/tests/test_v2_32_lightweight_relationship_graph.py \
  backend/tests/test_v2_11_coding_agent_actionability.py \
  backend/tests/test_v2_16_large_project_advisor.py -q
5 passed

PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_data_service_mcp.py::test_data_service_mcp_tool_registry_contract \
  backend/tests/test_data_service_mcp.py::test_console_mcp_contract_snapshot_matches_registry \
  backend/tests/test_public_surface_guard.py::test_v16a_mcp_registry_matches_v15_public_surface_baseline -q
2 passed, 1 skipped
```

跳过项说明：MCP registry contract test 依赖可选 `mcp` 包，本地未安装，按既有测试设计跳过。前端 contract snapshot 和 public surface guard 均通过。

格式检查：

```text
git diff --check -- Phase 97/98 touched files
passed
```

## 5. PRD / 规格检视

| 检查项 | 结果 |
| --- | --- |
| 不输出 forbidden relationship type | pass |
| 不把 import 写成 runtime call | pass |
| 不声称 full call graph | pass |
| direct AST relation 标注 direct_syntax 和 caveat | pass |
| dynamic / attribute call 输出 blocker | pass |
| data_service 和 HarnessOS 均使用真实仓库 | pass |
| HTTP/MCP/CLI 均可读取 | pass |
| public payload 无绝对路径泄露 | pass |

## 6. False-Green 审计

本阶段重点防止以下假通过：

- import dependency 被当作 runtime call。
- AST 直连被当作完整调用图。
- dynamic dispatch 被伪装成 accepted。
- 空 graph 返回 success。
- HarnessOS 特化规则伪造关系。

审计结果：无上述问题。所有 dynamic / attribute 相关不可解析关系进入 blocker。

## 7. Open Findings

| finding | severity | 状态 |
| --- | --- | --- |
| attribute / dynamic call blocker 数量较大 | minor / expected | 进入 Phase 99 impact/test selection 时继续作为 unresolved impact 输入 |
| `direct_call_ast` 仍不是 runtime call | expected limitation | 已在 `needs_review` 和 `semantic_limit` 中标注 |

无 open fatal / major finding。

## 8. 出门结论

Phase 98 完成：

- relationship graph artifacts 落盘并可回读。
- data_service / HarnessOS 真实 E2E 通过。
- forbidden relationship count = 0。
- HTTP/MCP/CLI contract 通过。
- PRD/spec/false-green review 通过。

结论：**Phase 98 accepted。可以进入 Phase 99 开发计划、验收计划和预实施审计。**
