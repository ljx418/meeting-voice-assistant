# V2.27 Phase 93 验收审计报告：Code Proof Graph

## 1. 审计结论

结论：通过。

Phase 93 已完成 Code Proof Graph，实现了 document claim、architecture source、code file、config fact、test fact、runtime descriptor 的 proof node/edge 建模。验收重点中的 forbidden edge scan、runtime descriptor 边界和真实仓库 E2E 均通过。

本阶段未实现 intent inference、diagram-to-code accepted verification、runtime observation 或 full call graph。

## 2. 实现范围

新增代码：

```text
backend/data_service/code_assets/architecture_intent/proof_graph.py
backend/tests/test_v2_27_code_proof_graph.py
```

扩展代码：

```text
backend/data_service/code_assets/architecture_intent/paths.py
backend/data_service/code_assets/architecture_intent/__init__.py
```

新增文档：

```text
docs/V2.x/V2_27_PHASE_93_CODE_PROOF_GRAPH_DEVELOPMENT_PLAN.md
docs/V2.x/V2_27_PHASE_93_CODE_PROOF_GRAPH_ACCEPTANCE_PLAN.md
docs/V2.x/V2_27_PHASE_93_CODE_PROOF_GRAPH_PRE_IMPLEMENTATION_AUDIT_REPORT.md
docs/V2.x/V2_27_PHASE_93_CODE_PROOF_GRAPH_ACCEPTANCE_AUDIT_REPORT.md
```

## 3. 输出 Artifact

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/proof_graph/
  proof_nodes.jsonl
  proof_edges.jsonl
  evidence_bundles.jsonl
  proof_graph_summary.json
```

## 4. 自动化测试

Focused tests：

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_25_architecture_source_model.py \
  backend/tests/test_v2_26_diagram_to_claim_parser.py \
  backend/tests/test_v2_27_code_proof_graph.py
```

结果：

```text
5 passed
```

平台回归子集：

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_25_architecture_source_model.py \
  backend/tests/test_v2_26_diagram_to_claim_parser.py \
  backend/tests/test_v2_27_code_proof_graph.py \
  backend/tests/test_v2_18_platform_console.py \
  backend/tests/test_v2_19_artifact_contracts.py \
  backend/tests/test_v2_20_tool_catalog.py \
  backend/tests/test_v2_21_incremental_build.py \
  backend/tests/test_v2_22_provider_plugins.py \
  backend/tests/test_v2_23_platform_governance.py \
  backend/tests/test_v2_24_ci_readiness.py
```

结果：

```text
19 passed
```

## 5. 真实仓库 E2E

临时 workspace：

```text
[local temp workspace redacted]
```

### data_service

| 指标 | 结果 |
| --- | ---: |
| proof_node_count | 12241 |
| proof_edge_count | 12241 |
| evidence_bundle_count | 11267 |
| forbidden_edge_count | 0 |
| runtime_observed_count | 0 |
| absolute_path_leak | false |

node_type_counts：

```json
{
  "architecture_source": 561,
  "code_file": 242,
  "config_fact": 32,
  "document_claim": 11267,
  "runtime_descriptor": 22,
  "test_fact": 117
}
```

### HarnessOS

| 指标 | 结果 |
| --- | ---: |
| proof_node_count | 9168 |
| proof_edge_count | 9168 |
| evidence_bundle_count | 6766 |
| forbidden_edge_count | 0 |
| runtime_observed_count | 0 |
| absolute_path_leak | false |

node_type_counts：

```json
{
  "architecture_source": 593,
  "code_file": 687,
  "config_fact": 129,
  "document_claim": 6766,
  "runtime_descriptor": 563,
  "test_fact": 430
}
```

## 6. PRD 规格检视

| 检查项 | 结论 |
| --- | --- |
| 只建立 proof graph | Pass |
| 未实现 intent inference | Pass |
| 未实现 diagram-to-code accepted verification | Pass |
| 未声称 full call graph/data flow/control flow/type inference | Pass |
| runtime_descriptor 未标 runtime_observed | Pass |
| data_service + HarnessOS 真实 E2E | Pass |

## 7. False-green Review

| 风险 | 结果 |
| --- | --- |
| forbidden edge 出现 | 未发生 |
| runtime descriptor 被当 observed runtime | 未发生 |
| proof graph 只有 summary 无 rows | 未发生 |
| public payload 路径泄露 | 未发生 |
| HarnessOS 未跑却通过 | 未发生 |

## 8. 后续进入 Phase 94 的前置要求

Phase 94 开始前必须产出：

```text
V2_28_PHASE_94_INTENT_INFERENCE_DEVELOPMENT_PLAN.md
V2_28_PHASE_94_INTENT_INFERENCE_ACCEPTANCE_PLAN.md
V2_28_PHASE_94_INTENT_INFERENCE_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

并确认：

- intent candidate 不是 accepted fact。
- 每条 intent 必须有 evidence bundle 或 needs_review。
- counter evidence 必须可见。
- LLM-only conclusion 不得 accepted。

## 9. 最终判定

```text
Phase 93 accepted.
No open fatal findings.
No open major findings.
Proceed to Phase 94 planning.
```
