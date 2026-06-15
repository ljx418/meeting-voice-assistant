# V2.26 Phase 92 验收审计报告：Diagram-to-Claim Parser

## 1. 审计结论

结论：通过。

Phase 92 已完成 Diagram-to-Claim Parser，实现了 drawio、Mermaid/PlantUML 文本图和架构性 Markdown source block 到 document-side claim/relation 的结构化转换。

本阶段未生成 code fact，未执行 diagram-to-code verification，未声称 runtime call/data flow/control flow。

## 2. 实现范围

新增代码：

```text
backend/data_service/code_assets/architecture_intent/diagram_claims.py
backend/tests/test_v2_26_diagram_to_claim_parser.py
```

扩展代码：

```text
backend/data_service/code_assets/architecture_intent/paths.py
backend/data_service/code_assets/architecture_intent/source_model.py
backend/data_service/code_assets/architecture_intent/__init__.py
```

新增文档：

```text
docs/V2.x/V2_26_PHASE_92_DIAGRAM_TO_CLAIM_DEVELOPMENT_PLAN.md
docs/V2.x/V2_26_PHASE_92_DIAGRAM_TO_CLAIM_ACCEPTANCE_PLAN.md
docs/V2.x/V2_26_PHASE_92_DIAGRAM_TO_CLAIM_PRE_IMPLEMENTATION_AUDIT_REPORT.md
docs/V2.x/V2_26_PHASE_92_DIAGRAM_TO_CLAIM_ACCEPTANCE_AUDIT_REPORT.md
```

## 3. 输出 Artifact

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/claims/
  diagram_claims.jsonl
  diagram_relations.jsonl
  diagram_claim_summary.json
```

## 4. 自动化测试

命令：

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_25_architecture_source_model.py \
  backend/tests/test_v2_26_diagram_to_claim_parser.py
```

结果：

```text
4 passed
```

平台回归子集：

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_25_architecture_source_model.py \
  backend/tests/test_v2_26_diagram_to_claim_parser.py \
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
18 passed
```

## 5. 真实仓库 E2E

临时 workspace：

```text
[local temp workspace redacted]
```

### data_service

| 指标 | 结果 |
| --- | ---: |
| source_count | 968 |
| diagram_cell_count | 904 |
| claim_count | 11245 |
| relation_count | 460 |
| needs_review_count | 1849 |
| forbidden_relation_count | 0 |
| code_fact_claim_count | 0 |
| absolute_path_leak | false |

claim_type 覆盖：

```json
{
  "adapter": 124,
  "boundary": 180,
  "component": 133,
  "forbidden_claim": 117,
  "layer": 57,
  "milestone": 361,
  "non_goal": 19,
  "provider": 810,
  "public_interface": 2604,
  "quality_gate": 2666,
  "runtime": 366,
  "storage": 1902,
  "unknown": 1400,
  "workflow": 506
}
```

### HarnessOS

| 指标 | 结果 |
| --- | ---: |
| source_count | 2402 |
| diagram_cell_count | 1306 |
| claim_count | 6766 |
| relation_count | 494 |
| needs_review_count | 1144 |
| forbidden_relation_count | 0 |
| code_fact_claim_count | 0 |
| absolute_path_leak | false |

claim_type 覆盖：

```json
{
  "adapter": 78,
  "boundary": 190,
  "component": 30,
  "forbidden_claim": 201,
  "layer": 59,
  "milestone": 54,
  "non_goal": 19,
  "provider": 75,
  "public_interface": 379,
  "quality_gate": 1530,
  "runtime": 489,
  "storage": 562,
  "unknown": 661,
  "workflow": 2439
}
```

## 6. PRD 规格检视

| 检查项 | 结论 |
| --- | --- |
| 只生成 document-side claim/relation | Pass |
| 未生成 code fact | Pass |
| 未实现 diagram-to-code accepted verification | Pass |
| 未声称 runtime call/data flow/control flow | Pass |
| forbidden/non_goal 一等抽取 | Pass |
| data_service + HarnessOS 真实 E2E | Pass |

## 7. False-green Review

| 风险 | 结果 |
| --- | --- |
| drawio claim 被当 code fact | 未发生 |
| relation_type 使用 runtime_calls/data_flow/control_flow | 未发生 |
| raw path 泄露 | 未发生 |
| HarnessOS 未跑却通过 | 未发生 |
| 只有 summary 无 rows | 未发生 |

## 8. 后续进入 Phase 93 的前置要求

Phase 93 开始前必须产出：

```text
V2_27_PHASE_93_CODE_PROOF_GRAPH_DEVELOPMENT_PLAN.md
V2_27_PHASE_93_CODE_PROOF_GRAPH_ACCEPTANCE_PLAN.md
V2_27_PHASE_93_CODE_PROOF_GRAPH_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

并确认：

- Phase 91/92 artifacts 可读。
- Proof graph 不能把 document claim、import 或 test reference 误写成 runtime observed。
- forbidden edge scan 必须自动化。

## 9. 最终判定

```text
Phase 92 accepted.
No open fatal findings.
No open major findings.
Proceed to Phase 93 planning.
```
