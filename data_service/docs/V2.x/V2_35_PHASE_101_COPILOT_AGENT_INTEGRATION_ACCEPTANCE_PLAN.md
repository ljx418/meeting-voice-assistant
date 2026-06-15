# V2.35 Phase 101 Copilot Agent Integration Contracts Acceptance Plan

## 1. 验收目标

验证 Phase 101 的 handoff 合同可被外部 Coding Agent 稳定消费，并且 HTTP/MCP/CLI 三端输出一致。

## 2. 必须通过的自动化测试

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest backend/tests/test_v2_35_copilot_agent_handoff.py -q
```

回归：

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_v2_31_task_navigation.py \
  backend/tests/test_v2_32_lightweight_relationship_graph.py \
  backend/tests/test_v2_33_change_impact_test_selection.py \
  backend/tests/test_v2_34_module_reading_pack.py \
  backend/tests/test_v2_35_copilot_agent_handoff.py \
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

- HTTP `POST /coding-agent/handoff` 可创建 handoff。
- HTTP `GET /coding-agent/handoff/{handoff_id}` 可回读。
- MCP `knowledge_code_agent_handoff_read` 可回读同一 handoff。
- CLI `handoff-read` 输出合法 JSON。
- handoff 包含 reading pack ref、impact ref、recommended commands、guardrails、acceptance checks。
- 每个 recommended command / guardrail / acceptance check 必须有 evidence 或 needs_review。
- public payload 不泄露绝对路径。

## 4. 真实仓 E2E

真实项目：

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

任务矩阵：

data_service：

1. 新增 MCP tool 并同步 HTTP API 与 CLI。
2. 修改 codebase snapshot 扫描策略并补测试。
3. 优化架构报告 HTML 可读性。
4. 接入 provider adapter 错误码映射。
5. 调整 quality governance read-time overlay。

HarnessOS：

1. 调整 workflow dispatch 路由并补运行时测试。
2. 修改 station agent descriptor 读取逻辑。
3. 定位 mission TUI 入口与工作流调用关系。

每个任务必须生成 handoff，或输出结构化 blocker。不能将 missing evidence 视为 accepted。

## 5. False-Green Rejection

以下情况拒绝验收：

- handoff 未落盘。
- handoff 引用了不存在的 reading pack。
- handoff 引用了不存在的 impact artifact。
- recommended commands 缺 evidence 且未标 `needs_review`。
- CLI 输出不是 JSON。
- HTTP/MCP/CLI stable fields 不一致。
- public payload 包含绝对路径。
- 只使用 mock fixture，不跑真实仓。

## 6. PRD 规格检视

通过后更新：

- `V2_31_36_TASK_NAVIGATION_FULL_COVERAGE_MATRIX.md`
- `V2_35_PHASE_101_COPILOT_AGENT_INTEGRATION_ACCEPTANCE_AUDIT_REPORT.md`

不能更新 Phase 102 closure rows。
