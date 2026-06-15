# V2.35 Phase 101 Copilot Agent Integration Contracts Acceptance Audit Report

## 1. 审计结论

结论：通过。

Phase 101 已实现面向外部 Coding Agent 的 handoff 合同，支持 HTTP/MCP/CLI build/read 路径，并能把 Phase 97-100 的 task navigation、impact/test selection、module reading pack、token ledger 汇总为可交给 Copilot/Codex/Claude Code/generic agent 的开发交接包。

本阶段没有执行 recommended commands，没有自动改代码，没有声明 Phase 102 HTML UX / governance closure 完成。

## 2. 实现范围

新增/修改核心文件：

- `backend/data_service/code_assets/coding_agent_navigation/handoff.py`
- `backend/data_service/code_assets/coding_agent_navigation/handoff_persistence.py`
- `backend/data_service/code_assets/coding_agent_navigation/service.py`
- `backend/app/api/v1/code_assets_coding_agent.py`
- `backend/data_service/mcp_code_coding_agent_tools.py`
- `backend/data_service/cli_code_coding_agent.py`
- `backend/tests/test_v2_35_copilot_agent_handoff.py`
- `backend/tests/test_public_surface_guard.py`
- `frontend/src/data/mcpContract.ts`

Artifact layout：

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/
  handoff/{handoff_id}.json
```

## 3. 公共合同

HTTP：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/handoff/{handoff_id}
```

MCP：

```text
knowledge_code_agent_handoff
knowledge_code_agent_handoff_read
```

CLI：

```text
knowledge code coding-agent handoff
knowledge code coding-agent handoff-read
```

## 4. PRD 规格检视

| 规格项 | 验收结果 | 证据 |
| --- | --- | --- |
| 生成 handoff artifact | 通过 | `test_v2_35_copilot_agent_handoff.py` |
| handoff 引用 reading pack | 通过 | `reading_pack_ref` |
| handoff 引用 impact artifact | 通过 | `impact_ref` |
| 输出 recommended commands | 通过 | `recommended_commands` |
| 输出 guardrails | 通过 | `guardrails` |
| 输出 acceptance checks | 通过 | `acceptance_checks` |
| 每项有 evidence 或 needs_review | 通过 | 自动断言 |
| 证据为空时必须有 blocker | 通过 | `HANDOFF_EVIDENCE_UNAVAILABLE` |
| HTTP/MCP/CLI read parity | 通过 | focused test |
| 不泄露绝对路径 | 通过 | HTTP/MCP/CLI 与真实 E2E redaction check |

## 5. 自动化测试

执行命令：

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest backend/tests/test_v2_35_copilot_agent_handoff.py -q
```

结果：

```text
1 passed
```

回归命令：

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

结果：

```text
8 passed
```

MCP / public surface contract：

```bash
PYTHONPATH=backend /usr/bin/python3 -m pytest \
  backend/tests/test_data_service_mcp.py::test_data_service_mcp_tool_registry_contract \
  backend/tests/test_data_service_mcp.py::test_console_mcp_contract_snapshot_matches_registry \
  backend/tests/test_public_surface_guard.py::test_v16a_mcp_registry_matches_v15_public_surface_baseline -q
```

结果：

```text
2 passed, 1 skipped
```

skip 原因：本地 optional `mcp` package 未安装；registry contract 与 public surface guard 已通过。

## 6. 真实仓 E2E

复验工作区：

```text
/private/tmp/data_service_v235_phase101_real_matrix_rerun
```

### data_service

| 任务 | evidence_refs | blockers | artifact_refs |
| --- | ---: | --- | ---: |
| 新增 MCP tool 并同步 HTTP API 与 CLI | 60 | none | 6 |
| 修改 codebase snapshot 扫描策略并补测试 | 12 | none | 6 |
| 优化架构报告 HTML 可读性 | 41 | none | 6 |
| 接入 provider adapter 错误码映射 | 6 | none | 6 |
| 调整 quality governance read-time overlay | 82 | none | 6 |

### HarnessOS

| 任务 | evidence_refs | blockers | artifact_refs |
| --- | ---: | --- | ---: |
| 调整 workflow dispatch 路由并补运行时测试 | 0 | `HANDOFF_EVIDENCE_UNAVAILABLE` | 6 |
| 修改 station agent descriptor 读取逻辑 | 1 | none | 6 |
| 定位 mission TUI 入口与工作流调用关系 | 1 | none | 6 |

## 7. False-Green 修复记录

首次真实 E2E 中发现 HarnessOS 的一个任务 `evidence_refs=0` 但 handoff 没有 blocker。按验收规则，这属于虚假验收风险。

修复：

- 当 handoff 顶层 `evidence_refs` 为空时，自动添加 `HANDOFF_EVIDENCE_UNAVAILABLE` blocker。
- 重新运行 Phase 101 focused test。
- 重新运行真实仓 E2E，确认该任务现在以结构化 blocker 呈现。

该风险已闭环。

## 8. 架构审计

- 未修改 `backend/app/api/v1/data_service.py`。
- 未修改 `backend/data_service/service.py`。
- Phase 101 核心逻辑位于 `backend/data_service/code_assets/coding_agent_navigation/`。
- HTTP/MCP/CLI 层仅负责参数转换和 envelope 输出。
- handoff 不执行命令、不改代码。
- 未声称 full call graph、runtime topology、data flow、type inference。

## 9. Open Findings

无 fatal 或 major finding。

Minor：

- HarnessOS 的 workflow dispatch handoff 仍缺少 retained evidence，已通过 blocker 暴露。后续 Phase 102 HTML UX 报告应把这类 blocker 用更直观方式展示给人类审阅。

## 10. 出门条件

Phase 101 出门条件满足：

- 自动化测试通过。
- 合同测试通过。
- 真实仓 E2E 通过。
- false-green 风险已修复并复验。
- coverage matrix 已更新。

可以进入 Phase 102 pre-implementation planning/audit。
