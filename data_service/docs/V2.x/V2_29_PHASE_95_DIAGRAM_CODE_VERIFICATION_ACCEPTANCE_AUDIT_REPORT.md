# V2.29 Phase 95 验收审计报告：Diagram-to-Code Verification

审计日期：2026-06-10
阶段：V2.29 / Phase 95
结论：accepted，带性能观察项

## 1. 本阶段目标

Phase 95 将文档/图声明对齐到代码、配置、测试、runtime descriptor 证据，输出架构声明落地状态。

本阶段不生成 runtime call graph、data flow、control flow、type inference，也不把 token overlap only 标记为 accepted。

## 2. 实现范围

新增实现：

- `backend/data_service/code_assets/architecture_intent/diagram_verification.py`
- `backend/tests/test_v2_29_diagram_code_verification.py`

新增 artifact：

- `architecture/intent/verification/diagram_code_alignment.jsonl`
- `architecture/intent/verification/undocumented_code_facts.jsonl`
- `architecture/intent/verification/architecture_diff.json`
- `architecture/intent/verification/verification_summary.json`

## 3. 自动化测试

Focused suite：

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_25_architecture_source_model.py backend/tests/test_v2_26_diagram_to_claim_parser.py backend/tests/test_v2_27_code_proof_graph.py backend/tests/test_v2_28_intent_inference.py backend/tests/test_v2_29_diagram_code_verification.py
```

结果：

```text
7 passed
```

回归子集：

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_18_platform_console.py backend/tests/test_v2_19_artifact_contracts.py backend/tests/test_v2_20_tool_catalog.py backend/tests/test_v2_21_incremental_build.py backend/tests/test_v2_22_provider_plugins.py backend/tests/test_v2_23_platform_governance.py backend/tests/test_v2_24_ci_readiness.py backend/tests/test_v2_25_architecture_source_model.py backend/tests/test_v2_26_diagram_to_claim_parser.py backend/tests/test_v2_27_code_proof_graph.py backend/tests/test_v2_28_intent_inference.py backend/tests/test_v2_29_diagram_code_verification.py
```

结果：

```text
21 passed
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
Phase 93 proof graph
Phase 94 intent inference
Phase 95 diagram-to-code verification
readback validation
```

### data_service

| 指标 | 值 |
| --- | ---: |
| duration_seconds | 20.24 |
| file_count | 995 |
| verification_count | 11324 |
| accepted_count | 9028 |
| weak_match_count | 359 |
| missing_code_evidence_count | 1774 |
| conflict_count | 142 |
| stale_count | 21 |
| undocumented_code_fact_count | 153 |
| accepted_gate_violation_count | 0 |
| token_only_accepted_count | 0 |
| absolute_path_leak | false |

### HarnessOS

| 指标 | 值 |
| --- | ---: |
| duration_seconds | 148.59 |
| file_count | 2584 |
| verification_count | 6766 |
| accepted_count | 5337 |
| weak_match_count | 470 |
| missing_code_evidence_count | 715 |
| conflict_count | 214 |
| stale_count | 30 |
| undocumented_code_fact_count | 1322 |
| accepted_gate_violation_count | 0 |
| token_only_accepted_count | 0 |
| absolute_path_leak | false |

## 5. PRD 规格检视

| 规格项 | 审计结论 |
| --- | --- |
| accepted verification 必须有 document evidence | pass |
| accepted verification 必须有 code evidence | pass |
| token_overlap_only 不得 accepted | pass |
| confidence < 0.80 不得 accepted | pass |
| undocumented code facts 必须可见 | pass |
| weak/missing/conflict/stale 必须可见 | pass |
| runtime descriptor 不得作为 runtime observed | pass |
| 不输出 full call graph / data flow / control flow / type inference | pass |

## 6. False-Green 审计

| 风险 | 结果 |
| --- | --- |
| HarnessOS 未跑却通过 | 未发生 |
| token-only 被标记 accepted | 未发现 |
| accepted 缺少双边 evidence | 未发现 |
| accepted hard gate 违规 | 未发现 |
| undocumented code facts 被隐藏 | 未发现 |
| public payload 泄露绝对路径 | 未发现 |

## 7. 性能观察

HarnessOS 真实 E2E 用时约 148.59 秒，主要来自大仓库 source/claim/proof/verification 全链路构建。

这不阻塞 Phase 95 验收，但 Phase 96 报告生成和最终 closure 应继续记录大仓库耗时，后续若进入产品化增量构建，应把 verification 索引与缓存纳入优化项。

## 8. 出门结论

Phase 95 通过真实 data_service 与 HarnessOS E2E、focused tests、回归子集、PRD 规格检视和 false-green 审计。

可以进入 Phase 96：UX Report、Context Pack、Governance 与 Closure。
