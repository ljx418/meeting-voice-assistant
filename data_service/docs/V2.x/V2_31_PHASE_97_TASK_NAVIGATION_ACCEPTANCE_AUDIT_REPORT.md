# V2.31 Phase 97 验收审计报告：Task-Aware Navigation Index

审计日期：2026-06-10
阶段：V2.31 / Phase 97
结论：**通过，允许进入 Phase 98 pre-implementation planning。**

本阶段完成 task-aware navigation index 的最小闭环：基于已存在的 snapshot、public surface、symbol、evidence artifacts，生成任务导航索引，并通过 HTTP/MCP/CLI 让 Coding Agent 针对任务获取候选 surface、symbol、test、doc 和 config。

## 1. 实现范围

新增 focused package：

```text
backend/data_service/code_assets/coding_agent_navigation/
```

新增能力：

- 构建 `coding_agent/task_navigation/navigation_index.json`。
- 根据开发任务生成 `coding_agent/task_navigation/task_queries/{task_id}.json`。
- 支持 task taxonomy：`mcp_tool`、`api`、`cli`、`workflow`、`provider`、`snapshot`、`governance`、`descriptor`、`entrypoint`、`bugfix`、`test`、`docs`、`architecture_review`、`unknown`。
- 候选项覆盖 surface、symbol、test、doc、config、entrypoint。
- candidate 必须有 `evidence_refs` 或 `needs_review`。
- 没有 accepted evidence 时返回 structured blocker，不伪装为 accepted。

新增公共入口：

```text
HTTP:
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/{task_id}

MCP:
knowledge_code_task_navigation_build
knowledge_code_task_navigation_read
knowledge_code_task_navigation_prepare
knowledge_code_task_navigation_query_read

CLI:
knowledge code coding-agent task-navigation-build
knowledge code coding-agent task-navigation
knowledge code coding-agent task-navigation-read
```

## 2. 真实仓库 E2E 验收

验收命令使用真实仓库：

- `/Users/Zhuanz/Desktop/workspace/data_service`
- `/Users/Zhuanz/Desktop/workspace/harnessOS`

验收 workspace：

```text
/private/tmp/data_service_v231_phase97_real_matrix
```

### data_service 结果

| 任务 | task_type | matched | accepted | needs_review | blockers | 结论 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 新增 MCP tool 并同步 HTTP/CLI | mcp_tool | 25 | 23 | 2 | 0 | accepted |
| 修改 codebase snapshot | snapshot | 25 | 12 | 13 | 0 | accepted |
| 新增 architecture report 字段 | architecture_review | 25 | 25 | 0 | 0 | accepted |
| 修改 provider adapter | provider | 25 | 0 | 25 | 1 | structured blocker |
| 调整 quality governance | governance | 25 | 25 | 0 | 0 | accepted |

data_service 索引摘要：

```text
snapshot_id: snap_46327b75cc183bfa40f8
candidate_count: 5888
surface_candidate_count: 507
symbol_candidate_count: 4596
```

### HarnessOS 结果

| 任务 | task_type | matched | accepted | needs_review | blockers | 结论 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 修改 workflow dispatch | workflow | 25 | 0 | 25 | 1 | structured blocker |
| 新增 station agent descriptor | descriptor | 25 | 0 | 25 | 1 | structured blocker |
| 审查 mission TUI entrypoint | entrypoint | 25 | 0 | 25 | 1 | structured blocker |

HarnessOS 索引摘要：

```text
snapshot_id: snap_7d6e4b8e03a8da79a847
candidate_count: 10391
surface_candidate_count: 186
symbol_candidate_count: 8299
```

HarnessOS 本阶段结论：**通过 structured blocker 验收，不声称 accepted line-level navigation evidence。** 这是符合 Phase 97 验收计划的结果，因为当前阶段只要求返回 accepted candidates 或 blocker，不能伪造 accepted relation。

## 3. 自动化测试结果

```text
PYTHONPATH=backend /usr/bin/python3 -m pytest backend/tests/test_v2_31_task_navigation.py -q
1 passed

PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_v2_31_task_navigation.py \
  backend/tests/test_v2_11_coding_agent_actionability.py \
  backend/tests/test_v2_16_large_project_advisor.py -q
4 passed

PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_data_service_mcp.py::test_data_service_mcp_tool_registry_contract \
  backend/tests/test_data_service_mcp.py::test_console_mcp_contract_snapshot_matches_registry \
  backend/tests/test_public_surface_guard.py::test_v16a_mcp_registry_matches_v15_public_surface_baseline -q
2 passed, 1 skipped
```

跳过项说明：`test_data_service_mcp_tool_registry_contract` 依赖可选 `mcp` 包，本地环境未安装该包，因此按既有测试设计跳过。前端 MCP contract snapshot 与 public surface guard 均通过。

格式检查：

```text
git diff --check -- Phase 97 touched files
passed
```

## 4. PRD / 规格检视

| 检查项 | 结果 |
| --- | --- |
| 只构建 task navigation，不提前实现 Phase 98 relationship graph | pass |
| 不输出 `relationships.jsonl`、impact analysis、token ledger、handoff | pass |
| 输入 facts 来自 V2.0-V2.30 artifacts，不改写上游 artifacts | pass |
| candidate 有 evidence 或 needs_review | pass |
| 无 accepted evidence 时返回 blocker | pass |
| HTTP/MCP/CLI 均可访问 | pass |
| public payload 无绝对路径泄露 | pass |

## 5. False-Green 审计

本阶段发现并修复一项假通过风险：

```text
问题：HarnessOS 任务能返回候选，但 accepted_count=0 且 blocker_count=0。
风险：弱匹配结果可能被误读为可执行导航成功。
修复：当 selected candidates 存在但 accepted_count=0 时，输出 TASK_NAVIGATION_ACCEPTED_EVIDENCE_UNAVAILABLE blocker。
```

修复后，HarnessOS 三个任务均返回结构化 blocker，没有伪造 accepted evidence。

## 6. Open Findings

| finding | severity | 状态 |
| --- | --- | --- |
| HarnessOS 缺 accepted line-level task navigation evidence | minor / expected blocker | defer to Phase 98+ relationship/evidence hardening |
| provider adapter 任务在 data_service 中缺 accepted evidence | minor / expected blocker | defer to Phase 98+ relationship and impact phases |

无 open fatal / major finding。

## 7. 出门结论

Phase 97 完成以下出门条件：

- Focused tests 通过。
- data_service 5 个真实任务完成验收。
- HarnessOS 3 个真实任务返回 structured blocker。
- HTTP/MCP/CLI 入口完成最小验收。
- PRD/spec review 无重大偏差。
- False-green 风险已闭环。

结论：**Phase 97 accepted。可以进入 Phase 98 的开发计划、验收计划和预实施审计。**
