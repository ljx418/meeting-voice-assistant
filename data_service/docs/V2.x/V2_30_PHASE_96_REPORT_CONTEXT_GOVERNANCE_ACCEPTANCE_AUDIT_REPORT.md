# V2.30 Phase 96 验收审计报告：Report、Context、Governance 与 Closure

审计日期：2026-06-10
阶段：V2.30 / Phase 96
结论：artifact/readback/test closure accepted；公共 HTTP/MCP/CLI 已由 Phase 96B 补齐并 accepted

## 1. 本阶段目标

Phase 96 生成 V2.25-V2.30 的用户可读出口与治理闭环：

- HTML 架构意图报告。
- Mermaid 关键关系图。
- Architecture Context Pack v4。
- Human confirmation / revoke governance overlay。
- Closure coverage matrix 更新。

## 2. 实现范围

新增实现：

- `backend/data_service/code_assets/architecture_intent/report.py`
- `backend/data_service/code_assets/architecture_intent/context_pack.py`
- `backend/data_service/code_assets/architecture_intent/governance.py`
- `backend/tests/test_v2_30_architecture_intent_report_context_governance.py`

新增 artifact：

- `architecture/intent/report/architecture_intent_report.json`
- `architecture/intent/report/architecture_intent_report.html`
- `architecture/intent/report/architecture_intent_diff.mmd`
- `architecture/intent/context/architecture_context_pack_v4.json`
- `architecture/intent/context/architecture_context_pack_v4.md`
- `architecture/intent/governance/confirmed_facts.jsonl`
- `architecture/intent/governance/governance_events.jsonl`
- `architecture/intent/governance/governance_summary.json`

Phase 96B 后续补齐：

- HTTP/MCP/CLI public contract routes/tools/commands 已实现并通过真实仓库 E2E。

## 3. 自动化测试

Focused test：

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_30_architecture_intent_report_context_governance.py
```

结果：

```text
1 passed
```

回归子集：

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_18_platform_console.py backend/tests/test_v2_19_artifact_contracts.py backend/tests/test_v2_20_tool_catalog.py backend/tests/test_v2_21_incremental_build.py backend/tests/test_v2_22_provider_plugins.py backend/tests/test_v2_23_platform_governance.py backend/tests/test_v2_24_ci_readiness.py backend/tests/test_v2_25_architecture_source_model.py backend/tests/test_v2_26_diagram_to_claim_parser.py backend/tests/test_v2_27_code_proof_graph.py backend/tests/test_v2_28_intent_inference.py backend/tests/test_v2_29_diagram_code_verification.py backend/tests/test_v2_30_architecture_intent_report_context_governance.py
```

结果：

```text
22 passed
```

全量后端测试：

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests
```

结果：

```text
479 passed, 617 warnings in 229.24s
```

## 4. 真实仓库 E2E

### data_service

| 指标 | 值 |
| --- | ---: |
| duration_seconds | 21.8 |
| file_count | 1003 |
| verification_count | 11362 |
| accepted_count | 9040 |
| context_recommendation_count | 8 |
| report_node_count | 69 |
| html_size | 7912 |
| mermaid_size | 2926 |
| all_sections_present | true |
| confirm_count_before_revoke | 1 |
| confirm_count_after_revoke | 0 |
| hash_gate_pass | true |
| recommendations_without_evidence_or_review | 0 |
| absolute_path_leak | false |

### HarnessOS

| 指标 | 值 |
| --- | ---: |
| duration_seconds | 171.45 |
| file_count | 2584 |
| verification_count | 6766 |
| accepted_count | 5337 |
| context_recommendation_count | 8 |
| report_node_count | 69 |
| html_size | 7539 |
| mermaid_size | 2926 |
| all_sections_present | true |
| confirm_count_before_revoke | 1 |
| confirm_count_after_revoke | 0 |
| hash_gate_pass | true |
| recommendations_without_evidence_or_review | 0 |
| absolute_path_leak | false |

## 5. PRD 规格检视

| 规格项 | 审计结论 |
| --- | --- |
| HTML 报告非 raw JSON | pass |
| HTML 包含 8 个要求区块 | pass |
| Mermaid 非空且从 report JSON 节点渲染 | pass |
| Context Pack recommendations 有 evidence 或 needs_review | pass |
| confirm/revoke 不修改 Phase 91-95 原始 artifact | pass |
| no absolute path leak | pass |
| HTTP/MCP/CLI 公共合同 | Phase 96B accepted |

## 6. False-Green 审计

| 风险 | 结果 |
| --- | --- |
| HTML 只是 JSON dump | 未发生 |
| Mermaid 引入 artifact 外新事实 | 未发现 |
| Context Pack 保留无证据建议 | 未发现 |
| confirm/revoke 改写原始 artifact | 未发生 |
| public payload 泄露绝对路径 | 未发现 |
| 未实现 HTTP/MCP/CLI 却标记 accepted | 未发生；Phase 96B 实现和验收后才标记 accepted |

## 7. 出门结论

Phase 96 的 artifact/readback/test closure 通过。

Phase 96B 已补齐公共 HTTP/MCP/CLI 暴露。V2.25-V2.30 当前完成了核心架构意图、图到代码验证、报告、上下文包、治理 overlay 和 Agent-callable public surface。
