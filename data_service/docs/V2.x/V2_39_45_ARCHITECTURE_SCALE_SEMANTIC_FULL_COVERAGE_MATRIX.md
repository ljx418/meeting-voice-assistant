# V2.39-V2.45 Full Coverage Matrix

本矩阵记录 V2.39-V2.45 当前 closure 状态。每个 accepted row 必须绑定 test command、artifact path、真实项目结果和 audit report；没有这些证据的行不得标记为 accepted。

| PRD Item | Phase | Expected Artifact | Acceptance Status | Required Evidence |
| --- | --- | --- | --- | --- |
| 大型项目性能优化 | V2.39 | scale_profile.json | accepted | `test_v2_6_architecture_scale_profile.py`; data_service/HarnessOS/codexPat real repo E2E; `V2_39_PHASE_116_SCALE_PROFILE_ACCEPTANCE_AUDIT_REPORT.md` |
| Scan Budget | V2.39 | scan_budget_report.json | accepted | low-budget real repo E2E produced `partial` + `SCAN_BUDGET_EXCEEDED`; `V2_39_PHASE_116_SCALE_PROFILE_ACCEPTANCE_AUDIT_REPORT.md` |
| Sharded Readback | V2.39 | scan_shards + readback index | accepted | shard artifacts and paginated readback verified across HTTP/MCP/CLI; `V2_39_PHASE_116_SCALE_PROFILE_ACCEPTANCE_AUDIT_REPORT.md` |
| Python AST Provider | V2.40 | symbol_facts.jsonl | accepted | `test_v2_40_language_provider_contract.py`; Python AST provider accepted on data_service/HarnessOS/codexPat; `V2_40_PHASE_117_LANGUAGE_PROVIDER_ACCEPTANCE_AUDIT_REPORT.md` |
| TS/JS Baseline | V2.40 | symbol/reference facts | accepted | TS/JS lexical baseline facts generated with `needs_review=true`; `V2_40_PHASE_117_LANGUAGE_PROVIDER_ACCEPTANCE_AUDIT_REPORT.md` |
| LSP Optional Boundary | V2.40 | language_provider_status.jsonl | accepted | tree-sitter/LSP unavailable contract verified as `provider_unavailable`, not accepted execution; `V2_40_PHASE_117_LANGUAGE_PROVIDER_ACCEPTANCE_AUDIT_REPORT.md` |
| Workflow Candidates | V2.41 | workflow_candidates.jsonl | accepted | `test_v2_41_workflow_runtime_candidates.py`; workflow fixture + real repo candidate extraction; `V2_41_PHASE_118_WORKFLOW_RUNTIME_ACCEPTANCE_AUDIT_REPORT.md` |
| Runtime Adapter Candidates | V2.41 | runtime_adapter_candidates.jsonl | accepted | runtime/agent candidates persisted with evidence or review flags; `V2_41_PHASE_118_WORKFLOW_RUNTIME_ACCEPTANCE_AUDIT_REPORT.md` |
| Entrypoint Candidates | V2.41 | entrypoint_candidates.jsonl | accepted | CLI/TUI/console entrypoint candidates verified; no production topology claim; `V2_41_PHASE_118_WORKFLOW_RUNTIME_ACCEPTANCE_AUDIT_REPORT.md` |
| Relationship Chain v3 | V2.42 | relationship_chains_v3.jsonl | accepted | `test_v2_42_relationship_chain_v3.py`; data_service/HarnessOS/codexPat E2E; `V2_42_PHASE_119_RELATIONSHIP_CHAIN_ACCEPTANCE_AUDIT_REPORT.md` |
| Forbidden Edge Guard | V2.42 | relationship_chain_summary.json | accepted | forbidden edge scan: 0 forbidden/unsupported edges; `V2_42_PHASE_119_RELATIONSHIP_CHAIN_ACCEPTANCE_AUDIT_REPORT.md` |
| drawio Semantic Claims | V2.43 | document_semantic_claims.jsonl | accepted | `test_v2_43_document_semantics.py`; drawio claims marked document-only/needs_review; `V2_43_PHASE_120_DOCUMENT_SEMANTICS_ACCEPTANCE_AUDIT_REPORT.md` |
| Markdown Semantic Claims | V2.43 | document_semantic_claims.jsonl | accepted | data_service/HarnessOS/codexPat Markdown extraction E2E; no code facts; `V2_43_PHASE_120_DOCUMENT_SEMANTICS_ACCEPTANCE_AUDIT_REPORT.md` |
| Token Budget Ledger | V2.44 | token_budget_ledger.json | accepted | `test_v2_44_token_budget_context_cache.py`; low budget E2E with `token_estimate <= max_tokens`; `V2_44_PHASE_121_TOKEN_CACHE_ACCEPTANCE_AUDIT_REPORT.md` |
| Context Cache | V2.44 | context_cache_index.json | accepted | repeated task cache hit bound to source artifact hash; `V2_44_PHASE_121_TOKEN_CACHE_ACCEPTANCE_AUDIT_REPORT.md` |
| Project Profile | V2.45 | project_profiles/*.json | accepted | `test_v2_45_profile_taxonomy_regression.py`; profile read/write; `V2_45_PHASE_122_PROFILE_TAXONOMY_REGRESSION_ACCEPTANCE_AUDIT_REPORT.md` |
| Taxonomy Registry | V2.45 | taxonomy_registry.json | accepted | taxonomy registry persisted/read; `V2_45_PHASE_122_PROFILE_TAXONOMY_REGRESSION_ACCEPTANCE_AUDIT_REPORT.md` |
| Regression Matrix | V2.45 | real_repo_regression_matrix.json | accepted | data_service/HarnessOS/codexPat E2E matrix; `V2_45_PHASE_122_PROFILE_TAXONOMY_REGRESSION_ACCEPTANCE_AUDIT_REPORT.md` |
| No Hardcode Audit | V2.45 | no_hardcode_audit.json | accepted | no-hardcode scan passed with 0 findings; `V2_45_PHASE_122_PROFILE_TAXONOMY_REGRESSION_ACCEPTANCE_AUDIT_REPORT.md` |
| Public Contract | V2.39-V2.45 | HTTP/MCP/CLI envelope | accepted | public surface guard, MCP registry, CLI focused tests, frontend MCP parity |

## Phase-Specific Planning Status

| Phase | Development Plan | Acceptance Plan | Pre-Implementation Audit | Acceptance Audit |
| --- | --- | --- | --- | --- |
| V2.39 / Phase 116 | ready | ready | ready | accepted |
| V2.40 / Phase 117 | ready | ready | ready | accepted |
| V2.41 / Phase 118 | ready | ready | ready | accepted |
| V2.42 / Phase 119 | ready | ready | ready | accepted |
| V2.43 / Phase 120 | ready | ready | ready | accepted |
| V2.44 / Phase 121 | ready | ready | ready | accepted |
| V2.45 / Phase 122 | ready | ready | ready | accepted |

## Closure Rule

任何行从 `planned` 改成 `accepted` 时必须包含：

```text
test_command
test_result
artifact_path
data_service_result
HarnessOS_result
codexPat_result
audit_report_path
open_findings
```
