# V2.39-V2.45 Phase 116-122 Detailed Implementation Package

## 1. 模块边界

建议新增 focused package：

```text
backend/data_service/code_assets/architecture_scale_semantic/
  __init__.py
  paths.py
  models.py
  scale_profile.py
  language_providers.py
  workflow_runtime.py
  relationship_chains.py
  document_semantics.py
  token_budget.py
  profiles.py
  regression.py
  service.py
  renderers.py
```

接口层保持薄：

```text
backend/app/api/v1/code_assets_architecture_scale_semantic.py
backend/data_service/mcp_code_architecture_scale_semantic_tools.py
backend/data_service/cli_code_architecture_scale_semantic.py
```

不得把核心逻辑塞进 legacy 大文件。

## 2. Phase 116：大型项目性能

输入：repo snapshot、file manifest、ignore policy、scan policy。

输出：

- `scale_profile.json`
- `scan_budget_report.json`
- `scan_shards/*.jsonl`
- `paginated_readback_index.json`

关键测试：

- generated/vendor skip
- oversized file blocker
- partial status
- pagination readback

## 3. Phase 117：多语言 Provider

输出：

- `language_provider_status.jsonl`
- `symbol_facts.jsonl`
- `reference_facts.jsonl`

Provider 策略：

- Python AST：mandatory
- TS/JS：baseline fixture
- tree-sitter/LSP：optional

关键测试：

- Python symbol facts
- TS/JS fixture
- provider unavailable
- unsupported language

## 4. Phase 118：Workflow / Runtime Candidate

输出：

- `workflow_candidates.jsonl`
- `runtime_adapter_candidates.jsonl`
- `entrypoint_candidates.jsonl`

关键测试：

- workflow manifest pattern
- agent registry pattern
- CLI/TUI/console pattern
- candidate 不等于 topology

## 5. Phase 119：Relationship Chain v3

输出：

- `relationship_chains_v3.jsonl`
- `relationship_chain_summary.json`

关键测试：

- accepted chain evidence
- forbidden edge scan
- completeness score
- blocker visibility

## 6. Phase 120：Document Semantics

输出：

- `document_semantic_claims.jsonl`
- `document_semantic_relations.jsonl`
- `document_semantic_summary.json`

关键测试：

- Markdown acceptance/non-goal/stop condition
- drawio page/lane/group/edge
- escaping
- no code fact conversion

## 7. Phase 121：Token Budget

输出：

- `token_budget_ledger.json`
- `context_cache_index.json`
- `context_pack_optimized/{pack_id}.json`
- `context_pack_optimized/{pack_id}.md`

关键测试：

- low budget
- omitted_items reason
- evidence preserved
- cache hit

## 8. Phase 122：Profile / Regression

输出：

- `project_profiles/*.json`
- `taxonomy_registry.json`
- `real_repo_regression_matrix.json`
- `no_hardcode_audit.json`
- `closure_audit_report.md`

关键测试：

- profile read/write
- no HarnessOS-only hardcode in generic modules
- data_service/HarnessOS/codexPat matrix
- closure no fatal/major

## 9. 自动化测试建议

```text
test_v2_39_scale_profile.py
test_v2_40_language_provider_contract.py
test_v2_41_workflow_runtime_candidates.py
test_v2_42_relationship_chains.py
test_v2_43_document_semantics.py
test_v2_44_token_budget_optimizer.py
test_v2_45_profile_regression.py
test_v2_39_45_public_contract_parity.py
test_v2_39_45_no_hardcode_audit.py
```
