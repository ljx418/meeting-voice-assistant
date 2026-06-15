# V2.30 Phase 96B 验收计划：Architecture Intent 公共合同

阶段：V2.30 / Phase 96B
验收类型：真实仓库 E2E + HTTP/MCP/CLI contract parity + PRD 规格检视。

## 1. 必测场景

### 1.1 data_service E2E

1. 导入真实 data_service 仓库。
2. 生成 snapshot。
3. 通过 HTTP build architecture intent pipeline。
4. 通过 HTTP/MCP/CLI 分别读取 report、context-pack、verification、proof-graph。
5. 比较三端稳定字段：
   - schema_version
   - workspace_id
   - codebase_id
   - snapshot_id
   - artifact_refs count
   - report node count
   - verification count
   - context recommendation count
6. 通过 HTTP/MCP/CLI 执行 confirm/revoke，并验证 read-time overlay 生效。

### 1.2 HarnessOS E2E

1. 使用真实 HarnessOS 仓库。
2. 跑同样 build/read 流程。
3. 如果 accepted evidence 不足，必须输出 structured blocker，而不是 mock 成功。

## 2. 安全与真实性断言

- public JSON / HTML / Markdown / Mermaid 不得包含本机绝对路径前缀：
  - `/Users/`
  - `/private/var`
  - `/var/folders`
- public payload 不得包含 key、token、secret、Authorization、traceback。
- HTTP/MCP/CLI 任一端失败，不能将公共合同标记 accepted。
- confirm/revoke 前后 Phase 91-95 artifact hash 必须不变。
- `token_overlap_only` 不能出现在 accepted verification。

## 3. 自动化测试要求

新增测试：

```text
backend/tests/test_v2_30_architecture_intent_public_contracts.py
```

测试覆盖：

- MCP tool specs 注册。
- CLI parser 输出合法 JSON。
- HTTP endpoint success/error envelope。
- 三端 read parity。
- governance confirm/revoke overlay。
- no path leak / no unpersisted fact。

## 4. 回归测试

至少运行：

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests/test_v2_25_architecture_source_model.py backend/tests/test_v2_26_diagram_to_claim_parser.py backend/tests/test_v2_27_code_proof_graph.py backend/tests/test_v2_28_intent_inference.py backend/tests/test_v2_29_diagram_code_verification.py backend/tests/test_v2_30_architecture_intent_report_context_governance.py backend/tests/test_v2_30_architecture_intent_public_contracts.py
```

最终收口前运行：

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests
```

## 5. PRD 规格检视

验收后必须更新：

- `V2_25_30_ARCHITECTURE_INTENT_FULL_COVERAGE_MATRIX.md`
- `V2_30_PHASE_96_REPORT_CONTEXT_GOVERNANCE_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_25_30_ARCHITECTURE_INTENT_CLOSURE_AUDIT_REPORT.md`

公共合同 row 只有在 HTTP/MCP/CLI 三端均通过真实仓库验收后，才能从 `not_implemented` 改为 `accepted`。
