# V2.16 Phase 77 验收审计报告：Semantic Provider Orchestrator

## 1. 审计结论

结论：Phase 77 通过。

本阶段完成 AST baseline Semantic Provider Orchestrator。系统可以把 V2.11 actionability facts 转换成带 provider provenance 的 semantic facts，并对 optional provider 缺失输出结构化 blocker。本报告不声明 tree-sitter / Jedi / LSP 真实 adapter 已完成。

## 2. 已实现能力

- 生成 `provider_facts.jsonl`。
- 生成 `merged_semantic_index.json`。
- 生成 `provider_conflicts.jsonl`。
- 每条 accepted definition fact 包含 provider、extractor、confidence、source file、line range、evidence refs。
- optional semantic providers 进入 provider blockers。
- HTTP / MCP / CLI 三端 build/read。
- forbidden claim scan：无 runtime call / data flow / control flow / type inference 声明。

## 3. 关键文件

实现：

- `backend/data_service/code_assets/coding_agent_v2_16/semantic_orchestrator.py`
- `backend/data_service/code_assets/coding_agent_v2_16/persistence.py`
- `backend/data_service/code_assets/coding_agent/service.py`
- `backend/app/api/v1/code_assets_coding_agent.py`
- `backend/data_service/mcp_code_coding_agent_tools.py`
- `backend/data_service/cli_code_coding_agent.py`

测试：

- `backend/tests/test_v2_16_semantic_orchestrator.py`
- `backend/tests/test_v2_16_provider_registry.py`
- `backend/tests/test_public_surface_guard.py`

## 4. 自动化验收结果

### 4.1 Focused + regression tests

命令：

```text
PYTHONPATH=backend pytest backend/tests/test_v2_16_provider_registry.py backend/tests/test_v2_16_semantic_orchestrator.py backend/tests/test_v2_11_coding_agent_actionability.py backend/tests/test_v2_12_safe_patch_planning.py backend/tests/test_v2_13_15_coding_agent_remaining.py backend/tests/test_public_surface_guard.py -q
```

结果：

```text
15 passed
```

### 4.2 真实 data_service 仓库 E2E

流程：

1. 在 `/private/tmp` 创建临时 workspace。
2. 导入当前 data_service 仓库。
3. 生成真实 snapshot。
4. 构建 provider registry。
5. 构建 semantic provider index。
6. 检查 artifact、fact count、provider blocker、forbidden claim、路径脱敏。

结果摘要：

```json
{
  "codebase_id": "codebase_data_service_real",
  "provider_fact_count": 1600,
  "accepted_fact_count": 1600,
  "provider_blocker_count": 3,
  "artifact": "workspace/assets/codebase/codebase_data_service_real/coding_agent/v2_16/semantic/merged_semantic_index.json"
}
```

### 4.3 格式检查

命令：

```text
git diff --check -- .
```

结果：通过。

## 5. PRD 规格检视

| 检视项 | 结论 |
| --- | --- |
| AST mandatory baseline 是否可用 | 通过 |
| optional provider unavailable 是否结构化表达 | 通过 |
| 是否伪造 tree-sitter / Jedi / LSP 成功 | 未发现 |
| 是否输出 full call graph / data flow / type inference | 未发现 |
| facts 是否有 provider / extractor / confidence / evidence | 通过 |
| HTTP / MCP / CLI parity 是否通过 | 通过 |
| public payload 是否泄露绝对路径 / secret | 未发现 |

## 6. 剩余风险

- 当前 provider facts 来源为 AST baseline。tree-sitter / Jedi / LSP 仍为 optional unavailable / unsupported，不得在用户输出中声明已接受。
- reference facts 是静态引用证据，不是 runtime call。
- 本报告不构成 V2.16 closure。

## 7. 审计意见

- Fatal findings：0
- Major findings：0
- Minor findings：0

Phase 77 可以关闭。允许进入 Phase 78 前置开发/验收/审计文档阶段。
