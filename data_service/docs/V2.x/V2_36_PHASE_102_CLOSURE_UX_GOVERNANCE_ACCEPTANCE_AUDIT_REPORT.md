# V2.36 Phase 102 Closure, UX Report & Governance Acceptance Audit Report

## 1. 审计结论

结论：通过，状态为 `accepted_with_blockers`。

Phase 102 已实现 V2.36 task navigation closure bundle，包括：

- closure JSON report
- HTML 用户报告
- Mermaid 任务关系图
- coverage matrix artifact
- governance target summary
- closure audit artifact
- HTTP/MCP/CLI read/build/view 合同

本阶段显式展示 blocker，不把 blocker 隐藏为 accepted。

修复后复验补充结论：

- accepted relationship 必须具备 repo-relative path、line_range、evidence_refs；缺任一项会降级为 `needs_review`。
- Public Surface Inventory 不再从运行中的 data_service registry 注入 MCP tools 到外部项目，只解析目标仓库生产源码中的 MCP `TOOL_SPECS`。
- 没有确定性 public surface 的大型项目不再硬失败，而是输出结构化 blocker 并继续生成模块/符号/测试/文档层面的导航与关系产物。

## 2. 实现范围

新增/修改核心文件：

- `backend/data_service/code_assets/coding_agent_navigation/closure_report.py`
- `backend/data_service/code_assets/coding_agent_navigation/closure_persistence.py`
- `backend/data_service/code_assets/coding_agent_navigation/service.py`
- `backend/app/api/v1/code_assets_coding_agent.py`
- `backend/data_service/mcp_code_coding_agent_tools.py`
- `backend/data_service/cli_code_coding_agent.py`
- `backend/tests/test_v2_36_task_navigation_closure.py`
- `backend/tests/test_public_surface_guard.py`
- `frontend/src/data/mcpContract.ts`

Artifact layout：

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/
  reports/task_navigation_report.json
  reports/task_navigation_report.html
  reports/task_navigation_graph.mmd
  coverage_matrix.json
  governance_targets.json
  closure_audit_report.json
```

## 3. 自动化测试

Focused：

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest backend/tests/test_v2_36_task_navigation_closure.py -q
```

结果：

```text
1 passed
```

Regression：

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_v2_31_task_navigation.py \
  backend/tests/test_v2_32_lightweight_relationship_graph.py \
  backend/tests/test_v2_33_change_impact_test_selection.py \
  backend/tests/test_v2_34_module_reading_pack.py \
  backend/tests/test_v2_35_copilot_agent_handoff.py \
  backend/tests/test_v2_36_task_navigation_closure.py \
  backend/tests/test_v2_11_coding_agent_actionability.py \
  backend/tests/test_v2_16_large_project_advisor.py -q
```

结果：

```text
9 passed
```

Contract：

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_data_service_mcp.py::test_data_service_mcp_tool_registry_contract \
  backend/tests/test_data_service_mcp.py::test_console_mcp_contract_snapshot_matches_registry \
  backend/tests/test_public_surface_guard.py::test_v16a_mcp_registry_matches_v15_public_surface_baseline -q
```

结果：

```text
3 passed
```

修复后 focused + regression：

```bash
PYTHONPATH=backend python3 -m pytest \
  backend/tests/test_v2_31_task_navigation.py \
  backend/tests/test_v2_codebase_inventory.py \
  backend/tests/test_v2_32_lightweight_relationship_graph.py \
  backend/tests/test_v2_34_module_reading_pack.py -q
```

结果：

```text
7 passed
```

修复后 V2.31-V2.36 主线回归：

```bash
PYTHONPATH=backend python3 -m pytest \
  backend/tests/test_v2_31_task_navigation.py \
  backend/tests/test_v2_32_lightweight_relationship_graph.py \
  backend/tests/test_v2_33_change_impact_test_selection.py \
  backend/tests/test_v2_34_module_reading_pack.py \
  backend/tests/test_v2_35_copilot_agent_handoff.py \
  backend/tests/test_v2_36_task_navigation_closure.py \
  backend/tests/test_v2_11_coding_agent_actionability.py \
  backend/tests/test_v2_16_large_project_advisor.py \
  backend/tests/test_v2_codebase_inventory.py -q
```

结果：

```text
13 passed
```

## 4. 真实仓 E2E

工作区：

```text
/private/tmp/data_service_v236_phase102_real_matrix
```

### data_service

| 字段 | 结果 |
| --- | --- |
| workspace_id | `phase102-data_service` |
| codebase_id | `phase102_data_service` |
| closure_status | `accepted_with_blockers` |
| blocker_count | 827 |
| node_count | 5 |
| coverage_rows | 6 |
| governance_targets | 828 |

### HarnessOS

| 字段 | 结果 |
| --- | --- |
| workspace_id | `phase102-harnessos` |
| codebase_id | `phase102_harnessos` |
| closure_status | `accepted_with_blockers` |
| handoff_blockers | `HANDOFF_EVIDENCE_UNAVAILABLE` |
| blocker_count | 788 |
| node_count | 5 |
| coverage_rows | 6 |
| governance_targets | 789 |

## 4.1 修复后大型项目复验

工作区：

```text
/private/tmp/data_service_v236_postfix_large_projects_rerun2
```

| 项目 | 文件数 | closure_status | surface_types | relationship_count | accepted relationship audit |
| --- | ---: | --- | --- | ---: | --- |
| data_service | 1074 | accepted_with_blockers | cli/http/mcp/frontend/api_client | 9143 | accepted=9053, missing line/evidence/path=0/0/0 |
| HarnessOS | 2676 | accepted_with_blockers | none | 10363 | accepted=10196, missing line/evidence/path=0/0/0 |
| codexPat | 998 | accepted_with_blockers | none | 73 | accepted=73, missing line/evidence/path=0/0/0 |

复验 artifact：

```text
/private/tmp/data_service_v236_postfix_large_projects_rerun2/v236_postfix_large_project_acceptance.json
/private/tmp/data_service_v236_postfix_large_projects_rerun2/v236_postfix_architecture_overview_index.json
```

生成的项目架构概览：

```text
/private/tmp/data_service_v236_postfix_large_projects_rerun2/v236-postfix-data_service/assets/codebase/v236_postfix_data_service/coding_agent/task_navigation/reports/project_architecture_overview.html
/private/tmp/data_service_v236_postfix_large_projects_rerun2/v236-postfix-harnessos/assets/codebase/v236_postfix_harnessos/coding_agent/task_navigation/reports/project_architecture_overview.html
/private/tmp/data_service_v236_postfix_large_projects_rerun2/v236-postfix-codexpat/assets/codebase/v236_postfix_codexpat/coding_agent/task_navigation/reports/project_architecture_overview.html
```

## 5. PRD 规格检视

| 规格项 | 结果 |
| --- | --- |
| HTML 用户报告 | 通过 |
| Mermaid 任务关系图 | 通过 |
| coverage matrix artifact | 通过 |
| governance targets | 通过 |
| blocker 可见 | 通过 |
| Mermaid node id 追踪到 JSON nodes | 通过 |
| HTML 无 `<script` | 通过 |
| public payload 无绝对路径 | 通过 |
| 不声明 runtime call graph | 通过 |

## 6. False-Green 审计

| 风险 | 结论 |
| --- | --- |
| HTML 硬编码未持久化事实 | 未发现，HTML 从 closure JSON 渲染 |
| Mermaid 引入不存在节点 | 未发现，focused test 强制 node id 存在 |
| HarnessOS blocker 被隐藏 | 未发现，`HANDOFF_EVIDENCE_UNAVAILABLE` 与 blocker_count 可见 |
| closure 把 blocker 写成 accepted | 未发生，状态为 `accepted_with_blockers` |
| 只跑 mock fixture | 未发生，已跑 data_service 和 HarnessOS |
| 绝对路径泄露 | 未发现 |
| 外部项目被注入 data_service MCP tools | 已修复并复验，HarnessOS/codexPat `surface_types` 为空 |
| accepted relationship 缺证据仍被接受 | 已修复并复验，三项目缺 line/evidence/path 均为 0 |

## 7. 架构审计

- 未修改 `backend/app/api/v1/data_service.py`。
- 未修改 `backend/data_service/service.py`。
- 核心逻辑位于 `coding_agent_navigation` focused modules。
- HTTP/MCP/CLI 层为薄封装。
- 未写入 source registry。
- 未改写目标项目代码。
- 未执行 recommended commands。

## 8. Open Findings

无 fatal 或 major finding。

Minor：

- closure report 当前为摘要级 HTML，不替代完整交互式工作台。
- data_service/HarnessOS 存在大量 relationship blockers，说明大项目仍需要后续阶段继续提升证据覆盖和阅读体验。

## 9. 出门条件

Phase 102 出门条件满足，可以宣布 V2.31-V2.36 Task Navigation 主线完成，最终状态为：

```text
accepted_with_blockers
```
