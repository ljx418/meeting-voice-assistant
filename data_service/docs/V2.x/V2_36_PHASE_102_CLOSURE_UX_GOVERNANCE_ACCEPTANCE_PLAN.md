# V2.36 Phase 102 Closure, UX Report & Governance Acceptance Plan

## 1. 验收目标

验证 V2.36 能把 V2.31-V2.35 的任务导航能力收口为可读、可审计、可回放的最终报告。

## 2. 自动化测试

Focused：

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest backend/tests/test_v2_36_task_navigation_closure.py -q
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

Contract：

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_data_service_mcp.py::test_data_service_mcp_tool_registry_contract \
  backend/tests/test_data_service_mcp.py::test_console_mcp_contract_snapshot_matches_registry \
  backend/tests/test_public_surface_guard.py::test_v16a_mcp_registry_matches_v15_public_surface_baseline -q
```

## 3. 功能验收

- closure JSON artifact 落盘。
- HTML artifact 落盘并可回读。
- Mermaid artifact 落盘并可回读。
- coverage matrix artifact 落盘。
- governance target summary artifact 落盘。
- closure audit artifact 落盘。
- HTTP/MCP/CLI 三端可读。
- HTML/Mermaid 不包含绝对路径。
- HTML 不包含未转义 `<script`。
- Mermaid node ids 与 report JSON nodes 对齐。

## 4. 真实仓 E2E

真实项目：

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

必须对每个项目完成：

1. codebase import。
2. snapshot。
3. inventory。
4. symbols。
5. trace。
6. task navigation。
7. relationship graph。
8. impact / test selection。
9. reading pack。
10. handoff。
11. closure report。

## 5. False-Green Rejection

以下情况拒绝验收：

- HTML 从模板硬编码，不来自 persisted JSON。
- Mermaid 引入 JSON 中不存在的节点。
- HarnessOS low-evidence blocker 被隐藏。
- closure 把 blocker 写成 accepted。
- public payload 包含绝对路径。
- governance target 指向不存在 artifact。
- 只跑 mock fixture，不跑真实仓。

## 6. PRD 规格检视

验收通过后更新：

- `V2_31_36_TASK_NAVIGATION_FULL_COVERAGE_MATRIX.md`
- `V2_36_PHASE_102_CLOSURE_UX_GOVERNANCE_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_31_36_TASK_NAVIGATION_CLOSURE_AUDIT_REPORT.md`
