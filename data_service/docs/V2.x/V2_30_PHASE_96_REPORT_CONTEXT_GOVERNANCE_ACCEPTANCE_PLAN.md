# V2.30 Phase 96 验收计划：Report、Context、Governance 与 Closure

## 1. 自动化测试

新增并通过：

```text
backend/tests/test_v2_30_architecture_intent_report_context_governance.py
```

覆盖：

- report JSON / HTML / Mermaid 落盘。
- HTML 包含 8 个要求区块，不是 raw JSON。
- Mermaid node id 来自 persisted report JSON。
- Mermaid/HTML 不泄露绝对路径。
- Context Pack JSON/Markdown 落盘。
- recommendation 有 evidence_refs 或 needs_review。
- confirm/revoke 写入 governance events。
- confirm/revoke 不修改 Phase 91-95 artifact hash。

## 2. 回归测试

必须通过：

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_18_platform_console.py \
  backend/tests/test_v2_19_artifact_contracts.py \
  backend/tests/test_v2_20_tool_catalog.py \
  backend/tests/test_v2_21_incremental_build.py \
  backend/tests/test_v2_22_provider_plugins.py \
  backend/tests/test_v2_23_platform_governance.py \
  backend/tests/test_v2_24_ci_readiness.py \
  backend/tests/test_v2_25_architecture_source_model.py \
  backend/tests/test_v2_26_diagram_to_claim_parser.py \
  backend/tests/test_v2_27_code_proof_graph.py \
  backend/tests/test_v2_28_intent_inference.py \
  backend/tests/test_v2_29_diagram_code_verification.py \
  backend/tests/test_v2_30_architecture_intent_report_context_governance.py
```

## 3. 真实仓库 E2E

使用：

- `/Users/Zhuanz/Desktop/workspace/data_service`
- `/Users/Zhuanz/Desktop/workspace/harnessOS`

执行：

```text
Phase 91 -> 92 -> 93 -> 94 -> 95 -> 96
```

验收：

- report sections 全部存在。
- HTML 文件大小 > 0。
- Mermaid 文件非空。
- Context Pack 模式至少覆盖 `architecture_review`。
- governance confirm/revoke 行为可验证。
- no absolute path leak。

## 4. PRD 规格检视

- 报告必须清晰区分 target/current/inferred/confirmed/diff。
- 不得新增 artifact 中不存在的事实。
- 不得把 inferred intent 当 confirmed。
- Context Pack 不得保留无证据建议。
- Governance overlay 只能 read-time 生效。

## 5. False-Green 拒绝条件

- HTML 只是 JSON dump。
- Mermaid 节点不是 persisted report JSON 节点。
- confirm/revoke 改写原始 artifact。
- recommendations 无 evidence 且无 needs_review。
- public payload 泄露绝对路径。
- coverage matrix 仍有未解释 planned 行却声明 closure。

## 6. 出门报告

必须产出：

- `V2_30_PHASE_96_REPORT_CONTEXT_GOVERNANCE_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_25_30_ARCHITECTURE_INTENT_CLOSURE_AUDIT_REPORT.md`
- 更新 `V2_25_30_ARCHITECTURE_INTENT_FULL_COVERAGE_MATRIX.md`
