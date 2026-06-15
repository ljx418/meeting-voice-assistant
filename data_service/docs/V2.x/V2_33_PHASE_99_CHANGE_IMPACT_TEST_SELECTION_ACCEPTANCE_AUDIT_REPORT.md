# V2.33 Phase 99 验收审计报告：Change Impact & Test Selection

审计日期：2026-06-10
阶段：V2.33 / Phase 99
结论：**通过，允许进入 Phase 100 pre-implementation planning。**

本阶段完成基于 task navigation 和 lightweight relationships 的影响分析与测试建议。输出用于 Coding Agent 在开发前快速判断必改范围、可能相关测试和风险。

## 1. 实现范围

新增 focused modules：

```text
backend/data_service/code_assets/coding_agent_navigation/impact_analysis.py
backend/data_service/code_assets/coding_agent_navigation/impact_persistence.py
```

新增 artifacts：

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/impacts/{task_id}.json
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/test_selection/{task_id}.json
```

新增公共入口：

```text
HTTP:
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact-v2/{task_id}

MCP:
knowledge_code_task_impact_analyze
knowledge_code_task_impact_read

CLI:
knowledge code coding-agent impact-v2
knowledge code coding-agent impact-v2-read
```

说明：保留既有 V2.11 `/coding-agent/impact`，Phase 99 使用 `impact-v2`，避免 contract drift。

## 2. 真实仓库 E2E 验收

验收 workspace：

```text
/private/tmp/data_service_v233_phase99_real_matrix
```

### data_service

| 任务 | task_type | impacted_total | suggested_tests | blockers | risks | 结论 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 新增 MCP tool 并同步 HTTP/CLI | mcp_tool | 1748 | 40 | 0 | 40 | accepted |
| 修改 codebase snapshot | snapshot | 514 | 40 | 0 | 40 | accepted |
| 新增 architecture report 字段 | architecture_review | 1319 | 40 | 0 | 34 | accepted |
| 修改 provider adapter | provider | 2098 | 40 | 0 | 40 | accepted |
| 调整 quality governance | governance | 251 | 40 | 0 | 24 | accepted |

### HarnessOS

| 任务 | task_type | impacted_total | suggested_tests | blockers | risks | 结论 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 修改 workflow dispatch | workflow | 49 | 40 | 0 | 40 | accepted |
| 新增 station agent descriptor | descriptor | 40 | 40 | 0 | 40 | accepted |
| 审查 mission TUI entrypoint | entrypoint | 71 | 40 | 0 | 40 | accepted |

HarnessOS 结论：Phase 99 已能基于 Phase 98 relationships 给出 impact/test selection，但 suggested tests 中大量项目仍可能带 `needs_review`，不等价于已证明的运行时覆盖关系。

## 3. 自动化测试结果

```text
PYTHONPATH=backend /usr/bin/python3 -m pytest backend/tests/test_v2_33_change_impact_test_selection.py -q
1 passed

PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_v2_31_task_navigation.py \
  backend/tests/test_v2_32_lightweight_relationship_graph.py \
  backend/tests/test_v2_33_change_impact_test_selection.py \
  backend/tests/test_v2_11_coding_agent_actionability.py \
  backend/tests/test_v2_16_large_project_advisor.py -q
6 passed

PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_data_service_mcp.py::test_data_service_mcp_tool_registry_contract \
  backend/tests/test_data_service_mcp.py::test_console_mcp_contract_snapshot_matches_registry \
  backend/tests/test_public_surface_guard.py::test_v16a_mcp_registry_matches_v15_public_surface_baseline -q
2 passed, 1 skipped
```

跳过项说明：MCP registry contract test 依赖可选 `mcp` 包，本地未安装，按既有测试设计跳过。前端 MCP contract snapshot 和 public surface guard 均通过。

格式检查：

```text
git diff --check -- Phase 97/98/99 touched files
passed
```

## 4. PRD / 规格检视

| 检查项 | 结果 |
| --- | --- |
| 输出 impacted files/symbols/surfaces/docs/tests | pass |
| suggested_tests 有 reason | pass |
| suggested_tests 有 evidence_refs 或 needs_review | pass |
| 不把 import/static relation 写成 runtime impact | pass |
| 不自动执行测试、不修改代码 | pass |
| data_service 与 HarnessOS 使用真实仓库 | pass |
| HTTP/MCP/CLI 可用 | pass |
| public payload 无绝对路径泄露 | pass |

## 5. False-Green 审计

本阶段发现并修复一项接口偏差：

```text
问题：最初使用 /coding-agent/impact，与既有 V2.11 impact route 冲突。
修复：Phase 99 改为 /coding-agent/impact-v2，保留旧 contract 不变。
```

本阶段发现并修复一项 artifact 规格缺口：

```text
问题：impact summary 缺少 impacted_doc_count，文档类影响无法被验收脚本正确统计。
修复：summary 增加 impacted_doc_count，验收统计纳入 docs。
```

## 6. Open Findings

| finding | severity | 状态 |
| --- | --- | --- |
| suggested tests 数量较多，部分为 needs_review | minor / expected | Phase 100 token ledger 和 reading pack 继续裁剪 |
| impact 表示 likely impact，不是 runtime proof | expected limitation | 已通过 reason/risk/semantic limits 约束 |

无 open fatal / major finding。

## 7. 出门结论

Phase 99 完成：

- impact/test selection artifacts 落盘并可回读。
- data_service 5 个真实任务通过。
- HarnessOS 3 个真实任务通过。
- HTTP/MCP/CLI contract 通过。
- PRD/spec/false-green review 通过。

结论：**Phase 99 accepted。可以进入 Phase 100 开发计划、验收计划和预实施审计。**
