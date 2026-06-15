# V2.28 Phase 94 验收审计报告：Intent Inference Engine

审计日期：2026-06-10
阶段：V2.28 / Phase 94
结论：accepted，带明确边界

## 1. 本阶段目标

Phase 94 在 Phase 91 source model、Phase 92 diagram/document claims、Phase 93 code proof graph 之上生成证据支撑的 architecture intent candidates。

本阶段不声称完整恢复人类设计意图，不调用外部 LLM，不把 inferred intent 当成无条件 accepted architecture fact。

## 2. 实现范围

新增实现：

- `backend/data_service/code_assets/architecture_intent/intent_inference.py`
- `backend/tests/test_v2_28_intent_inference.py`

新增 artifact：

- `architecture/intent/intent/intent_candidates.jsonl`
- `architecture/intent/intent/counter_evidence.jsonl`
- `architecture/intent/intent/intent_summary.json`

支持 intent type：

- `capability`
- `module_boundary`
- `workflow`
- `governance`
- `runtime`
- `storage`
- `public_surface_strategy`
- `provider_strategy`
- `quality_strategy`

## 3. 自动化测试

命令：

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_25_architecture_source_model.py backend/tests/test_v2_26_diagram_to_claim_parser.py backend/tests/test_v2_27_code_proof_graph.py backend/tests/test_v2_28_intent_inference.py
```

结果：

```text
6 passed
```

回归子集：

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_18_platform_console.py backend/tests/test_v2_19_artifact_contracts.py backend/tests/test_v2_20_tool_catalog.py backend/tests/test_v2_21_incremental_build.py backend/tests/test_v2_22_provider_plugins.py backend/tests/test_v2_23_platform_governance.py backend/tests/test_v2_24_ci_readiness.py backend/tests/test_v2_25_architecture_source_model.py backend/tests/test_v2_26_diagram_to_claim_parser.py backend/tests/test_v2_27_code_proof_graph.py backend/tests/test_v2_28_intent_inference.py
```

结果：

```text
20 passed
```

## 4. 真实仓库 E2E

环境：

```text
DATA_SERVICE_ALLOWED_CODEBASE_ROOTS=/Users/Zhuanz/Desktop/workspace
DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS=/private/tmp
```

执行链路：

```text
import codebase
snapshot
Phase 91 source model
Phase 92 diagram/document claims
Phase 93 code proof graph
Phase 94 intent inference
readback validation
```

### data_service

| 指标 | 值 |
| --- | ---: |
| file_count | 989 |
| source_count | 980 |
| claim_count | 11279 |
| proof_node_count | 12259 |
| evidence_bundle_count | 11279 |
| intent_candidate_count | 9 |
| counter_evidence_count | 10 |

Intent status：

```json
{
  "accepted": 8,
  "inferred": 1
}
```

Counter evidence codes：

```text
DESIGN_INTENT_NOT_FULLY_OBSERVABLE
RUNTIME_DESCRIPTOR_NOT_RUNTIME_OBSERVED
```

### HarnessOS

| 指标 | 值 |
| --- | ---: |
| file_count | 2584 |
| source_count | 2402 |
| claim_count | 6766 |
| proof_node_count | 9168 |
| evidence_bundle_count | 6766 |
| intent_candidate_count | 9 |
| counter_evidence_count | 10 |

Intent status：

```json
{
  "accepted": 8,
  "inferred": 1
}
```

Counter evidence codes：

```text
DESIGN_INTENT_NOT_FULLY_OBSERVABLE
RUNTIME_DESCRIPTOR_NOT_RUNTIME_OBSERVED
```

## 5. PRD 规格检视

| 规格项 | 审计结论 |
| --- | --- |
| intent candidate 必须有 evidence bundle 或 needs_review | pass |
| counter evidence 必须可见 | pass |
| 不能全部 accepted | pass |
| 不能声称完整设计意图恢复 | pass，通过 `DESIGN_INTENT_NOT_FULLY_OBSERVABLE` 显式限制 |
| runtime descriptor 不能当 runtime observed | pass，通过 `RUNTIME_DESCRIPTOR_NOT_RUNTIME_OBSERVED` 显式限制 |
| 不调用外部 LLM | pass |
| 不泄露绝对路径 | pass |

## 6. False-Green 审计

| 风险 | 结果 |
| --- | --- |
| LLM-only conclusion marked accepted | 未发现 |
| 所有 intent 都 accepted | 未发生 |
| recommendation 无 evidence 且无 needs_review | 未发现 |
| HarnessOS 未跑却通过 | 未发生，HarnessOS 已执行真实 E2E |
| public payload 泄露 `/Users/`、`/private/tmp`、`/private/var`、`/var/folders` | 未发现 |
| runtime descriptor 被写成 runtime observation | 未发现 |

## 7. 已知边界

- Phase 94 是 evidence-backed inference，不是 full architecture intent recovery。
- accepted intent 表示“文档声明和 proof graph 支撑的高置信候选”，不表示人类设计意图已被完整证明。
- HarnessOS 已产生候选意图，但仍需 Phase 95 做 diagram-to-code verification 才能判断设计图与代码事实的偏差。

## 8. 出门结论

Phase 94 通过真实 data_service 与 HarnessOS E2E、focused tests、回归子集、PRD 规格检视和 false-green 审计。

可以进入 Phase 95：Diagram-to-Code Verification。
