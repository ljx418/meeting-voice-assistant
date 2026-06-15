# V2.35 Phase 101 Copilot Agent Integration Contracts Development Plan

## 1. 阶段目标

Phase 101 在 Phase 97-100 已验收的 task navigation、relationship graph、impact/test selection、module reading pack 基础上，补齐面向外部 Coding Agent 的 handoff 合同。

目标是让 Copilot/Codex/Claude Code/generic agent 可以一次读取：

- task interpretation
- reading pack reference
- impact reference
- suggested tests
- recommended commands
- guardrails
- acceptance checks
- evidence / needs_review

本阶段不做自动改代码、不执行测试命令、不生成 HTML UX report、不声明最终 V2.31-V2.36 closure。

## 2. 开发范围

新增 focused modules：

```text
backend/data_service/code_assets/coding_agent_navigation/
  handoff.py
  handoff_persistence.py
```

扩展薄接口：

```text
backend/data_service/code_assets/coding_agent_navigation/service.py
backend/app/api/v1/code_assets_coding_agent.py
backend/data_service/mcp_code_coding_agent_tools.py
backend/data_service/cli_code_coding_agent.py
frontend/src/data/mcpContract.ts
backend/tests/test_public_surface_guard.py
```

新增测试：

```text
backend/tests/test_v2_35_copilot_agent_handoff.py
```

## 3. Artifact 设计

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/
  handoff/{handoff_id}.json
```

最小字段：

```json
{
  "schema_version": "v2.35",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "handoff_id": "string",
  "task_id": "string",
  "target_agent": "copilot | codex | claude_code | generic",
  "reading_pack_ref": "coding-agent://...",
  "impact_ref": "coding-agent://...",
  "recommended_commands": [],
  "guardrails": [],
  "acceptance_checks": [],
  "evidence_refs": [],
  "needs_review": [],
  "blockers": [],
  "artifact_refs": []
}
```

## 4. API / MCP / CLI

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

## 5. 开发步骤

1. 实现 `handoff.py`：从 reading pack、impact、test selection 生成 handoff payload。
2. 实现 `handoff_persistence.py`：落盘和回读 handoff artifact。
3. 扩展 service：支持基于 `pack_id` 或 `task/task_id` 创建 handoff。
4. 扩展 HTTP/MCP/CLI：保持 envelope parity。
5. 扩展 public surface guard 和 frontend MCP contract。
6. 新增 focused tests 和 real repo E2E。

## 6. 不做事项

- 不执行 recommended commands。
- 不自动修改代码。
- 不把 heuristic relationship 写成 runtime call。
- 不把 handoff 当成最终开发计划批准。
- 不输出绝对路径。

## 7. 出门条件

- Focused tests pass。
- V2.31-V2.35 regression pass。
- MCP/public surface contract pass。
- data_service 5 个真实任务 handoff 通过。
- HarnessOS 3 个真实任务 handoff 通过或结构化 blocker。
- PRD/spec review 通过。
- false-green audit 无 fatal/major。
