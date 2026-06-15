# V2.25-V2.30 Full PRD Coverage Matrix

## 1. 状态定义

| 状态 | 含义 |
| --- | --- |
| planned | 已规划，尚未实现。 |
| implemented | 已实现，尚未完成验收。 |
| accepted | 已通过真实仓库 E2E 和审计。 |
| conditionally_accepted | 有明确限制条件的通过。 |
| provider_or_runtime_unavailable | 依赖环境不可用，但返回结构化状态。 |
| not_implemented | 未实现。 |
| out_of_scope | 明确不属于本阶段。 |

## 2. Coverage Matrix

| PRD 能力 | Phase | Artifact / API | 验收证据要求 | 当前状态 |
| --- | --- | --- | --- | --- |
| Architecture Source Model | 91 | architecture_sources.jsonl | data_service source_count=962；HarnessOS source_count=2402；repo-relative path；authority_role 存在。 | accepted |
| Diagram Cell / Source Block | 91 | diagram_cells.jsonl / source_blocks.jsonl | data_service diagram_cell_count=904/source_block_count=28095；HarnessOS diagram_cell_count=1306/source_block_count=15779。 | accepted |
| Document authority / stale policy | 91 | architecture_source_summary.json | authority_role_counts 已输出；historical/target/plan/acceptance/audit/implementation 可区分。 | accepted |
| Diagram-to-Claim Parser | 92 | diagram_claims.jsonl | data_service claim_count=11245；HarnessOS claim_count=6766；claim_type、locator、confidence、needs_review 完整。 | accepted |
| Diagram Relation Parser | 92 | diagram_relations.jsonl | data_service relation_count=460；HarnessOS relation_count=494；forbidden_relation_count=0。 | accepted |
| Unsupported diagram blocker | 92 | diagram_claim_summary.json | 模糊/未标注关系进入 needs_review；Phase 92 未将 unsupported relation 伪装为 accepted。 | accepted |
| Code Proof Graph | 93 | proof_nodes.jsonl / proof_edges.jsonl | data_service proof_node_count=12241/proof_edge_count=12241；HarnessOS proof_node_count=9168/proof_edge_count=9168。 | accepted |
| Config/Test evidence | 93 | proof graph | data_service config_fact=32/test_fact=117；HarnessOS config_fact=129/test_fact=430。 | accepted |
| Runtime descriptor boundary | 93 | proof graph | runtime_observed_count=0；forbidden_edge_count=0；runtime_descriptor 仅 descriptor_only。 | accepted |
| Intent Candidates | 94 | intent_candidates.jsonl | data_service intent_candidate_count=9；HarnessOS intent_candidate_count=9；每条 recommendation 有 evidence 或 needs_review。 | accepted |
| Counter Evidence | 94 | counter_evidence.jsonl | data_service counter_evidence_count=10；HarnessOS counter_evidence_count=10；包含 DESIGN_INTENT_NOT_FULLY_OBSERVABLE 与 RUNTIME_DESCRIPTOR_NOT_RUNTIME_OBSERVED。 | accepted |
| Confidence policy | 94 | intent summary | data_service/HarnessOS status_counts 均为 accepted=8、inferred=1；未出现全部 accepted；无 LLM 字段；无绝对路径泄露。 | accepted |
| Diagram-to-Code Verification | 95 | diagram_code_alignment.jsonl | data_service accepted_count=9028；HarnessOS accepted_count=5337；accepted_gate_violation_count=0；token_only_accepted_count=0。 | accepted |
| Missing / Conflict / Stale detection | 95 | architecture_diff.json | data_service weak=359/missing=1774/conflict=142/stale=21；HarnessOS weak=470/missing=715/conflict=214/stale=30。 | accepted |
| Undocumented code fact | 95 | verification summary | data_service undocumented_code_fact_count=153；HarnessOS undocumented_code_fact_count=1322。 | accepted |
| HTML Architecture Intent Report | 96 | architecture_intent_report.html | data_service html_size=7912；HarnessOS html_size=7539；8 个要求区块全部存在；非 raw JSON。 | accepted |
| Mermaid / visual diff | 96 | architecture_intent_diff.mmd | data_service/HarnessOS mermaid_size=2926；节点来自 persisted report JSON；无绝对路径。 | accepted |
| Architecture Context Pack extension | 96 | context pack | data_service/HarnessOS context_recommendation_count=8；recommendations_without_evidence_or_review=0。 | accepted |
| Governance confirmation / revoke | 96 | confirmed_facts.jsonl / overlay | confirm_count_before_revoke=1；confirm_count_after_revoke=0；hash_gate_pass=true。 | accepted |
| Public HTTP/MCP/CLI contracts | 96B | HTTP/MCP/CLI public envelope | `test_v2_30_architecture_intent_public_contracts.py` 通过；data_service 与 HarnessOS 均通过 HTTP build、MCP report read、CLI report read；三端 snapshot/verification count 一致；无路径泄露。 | accepted |
| Final closure audit | 96B | closure audit report | `V2_25_30_ARCHITECTURE_INTENT_CLOSURE_AUDIT_REPORT.md` 已更新；26 个阶段/合同回归测试通过；全量后端测试 479 passed。 | accepted |

## 3. False-Green Matrix

| 假通过场景 | 期望处理 |
| --- | --- |
| token_overlap_only 被标 accepted | Reject |
| drawio 节点直接变 code fact | Reject |
| LLM-only intent candidate accepted | Reject |
| import/reference 被写成 runtime call | Reject |
| HarnessOS 未跑却显示 accepted | Reject |
| HTML/Mermaid 展示 artifact 中不存在的节点 | Reject |
| public payload 泄露绝对路径/secret/raw traceback | Reject |
| governance confirm 修改原始 artifacts | Reject |

## 4. Closure 要求

Phase 96 关闭前必须将本矩阵所有 in-scope row 从 `planned` 更新为：

```text
accepted
conditionally_accepted
not_implemented
out_of_scope
provider_or_runtime_unavailable
```

任何 `accepted` 行必须引用：

- 测试命令。
- artifact 路径。
- data_service 结果。
- HarnessOS 结果或明确 blocker。
- 审计报告路径。
