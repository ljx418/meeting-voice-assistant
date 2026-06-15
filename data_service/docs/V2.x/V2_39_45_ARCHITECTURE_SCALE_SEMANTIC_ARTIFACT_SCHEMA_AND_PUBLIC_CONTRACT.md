# V2.39-V2.45 Artifact Schema and Public Contract

## 1. 目标

本文定义 V2.39-V2.45 的核心 artifact schema、public read/build envelope、错误码和 HTTP/MCP/CLI 对齐规则。实现阶段不得只生成临时报告，必须落盘可读、可追踪、可审计的结构化 artifacts。

## 2. 通用字段

所有 V2.39-V2.45 artifact 必须包含：

```json
{
  "schema_version": "v2.39_45",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "artifact_id": "string",
  "created_at": "iso8601",
  "source_phase": "V2.39 | V2.40 | V2.41 | V2.42 | V2.43 | V2.44 | V2.45",
  "artifact_refs": [],
  "warnings": [],
  "unresolved": []
}
```

所有路径默认 repo-relative。public payload 不允许包含绝对路径、secret、token、raw traceback。

## 3. ScaleProfile

```json
{
  "artifact_type": "scale_profile",
  "stats": {
    "file_count": 0,
    "loc_estimate": 0,
    "language_counts": {},
    "large_file_count": 0,
    "generated_or_vendor_count": 0
  },
  "budget": {
    "max_files": 0,
    "max_loc": 0,
    "max_file_size_mb": 0,
    "timeout_seconds": 0
  },
  "status": "ready | partial | blocked",
  "blockers": [],
  "shards": []
}
```

验收要求：

- `partial` 不得被标记为 `ready`。
- 超预算必须有 blocker。
- shard ref 必须可读回。

## 4. LanguageProviderStatus

```json
{
  "artifact_type": "language_provider_status",
  "language": "python | typescript | javascript | go | rust | java | unknown",
  "provider": "ast | tree_sitter | lsp | profile_only",
  "status": "accepted | configured | provider_unavailable | unsupported_language | provider_failed | timeout",
  "error": {
    "code": "string",
    "message": "string",
    "retryable": false
  }
}
```

验收要求：

- Python AST 是 mandatory baseline。
- tree-sitter/LSP 未配置时只能 `provider_unavailable`。
- provider failed 不能写成 accepted。

## 5. SymbolFact / ReferenceFact

```json
{
  "fact_id": "string",
  "kind": "module | class | function | method | import | reference",
  "language": "string",
  "qualified_name": "string",
  "path": "repo/relative/path",
  "line_range": [1, 10],
  "provider": "ast | tree_sitter | lsp",
  "confidence": 1.0,
  "evidence_refs": []
}
```

accepted fact 必须有 repo-relative path 和有效 line range 或 artifact ref。token overlap 不得产生 accepted code fact。

## 6. WorkflowRuntimeCandidate

```json
{
  "candidate_id": "string",
  "candidate_type": "workflow_manifest | runtime_adapter | agent_registry | cli_entrypoint | tui_entrypoint | console_entrypoint | pipeline_config",
  "label": "string",
  "path": "repo/relative/path",
  "line_range": [1, 10],
  "determinism": "deterministic | heuristic",
  "confidence": 0.0,
  "evidence_refs": [],
  "needs_review": []
}
```

candidate 不等于 production runtime topology。heuristic candidate 必须在报告中显式标记。

## 7. RelationshipChainV3

```json
{
  "chain_id": "string",
  "capability_id": "string",
  "nodes": [],
  "edges": [
    {
      "edge_id": "string",
      "edge_type": "deterministic_handler_mapping | symbol_reference | import_dependency | config_reference | test_reference | doc_constraint_reference | heuristic_candidate",
      "source": "string",
      "target": "string",
      "provenance": "surface_inventory | ast_provider | lsp_provider | config_parser | test_discovery | doc_claim",
      "confidence": 0.0,
      "evidence_refs": []
    }
  ],
  "completeness_score": 0.0,
  "status": "accepted | weak | blocked | needs_review",
  "blockers": []
}
```

禁止 accepted edge type：

```text
runtime_call
data_flow
control_flow
production_topology
type_inferred_dependency
```

## 8. DocumentSemanticClaim

```json
{
  "claim_id": "string",
  "source_type": "markdown | drawio",
  "source_block_type": "heading | bullet | table_row | acceptance_gate | non_goal | stop_condition | drawio_page | drawio_lane | drawio_group | drawio_edge | drawio_legend",
  "label": "string",
  "normalized_label": "string",
  "path": "repo/relative/path",
  "line_range": [1, 10],
  "drawio_cell_id": "optional",
  "confidence": 0.0,
  "evidence_refs": [],
  "claim_role": "target_design | constraint | non_goal | acceptance_gate | historical | unknown"
}
```

drawio claim 只能作为 document claim，不得直接变成 code fact。

## 9. TokenBudgetLedger

```json
{
  "ledger_id": "string",
  "task": "string",
  "role": "coding_agent | architecture_reviewer | documentation_agent | maintainer",
  "max_tokens": 0,
  "token_estimate": 0,
  "cache_hit_ratio": 0.0,
  "reused_artifacts": [],
  "omitted_items": [],
  "recommendations": []
}
```

recommendation 必须有 evidence_refs 或 needs_review。如果 evidence 被裁剪，对应 recommendation 必须 omitted 或 needs_review。

## 10. ProjectProfile

```json
{
  "profile_id": "string",
  "project_family": "string",
  "terms": {},
  "entrypoint_patterns": [],
  "workflow_patterns": [],
  "doc_authority_rules": [],
  "regression_targets": [],
  "scope": "global | workspace | codebase"
}
```

HarnessOS 特殊术语只能出现在 profile/taxonomy artifact。通用 extractor 不得包含 HarnessOS-only hardcode。

## 11. Public Envelope

成功响应：

```json
{
  "ok": true,
  "schema_version": "v2.39_45",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

失败响应：

```json
{
  "ok": false,
  "schema_version": "v2.39_45",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": null,
  "error": {
    "code": "string",
    "message": "string",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

## 12. Public Error Codes

```text
SCALE_PROFILE_NOT_BUILT
SCAN_BUDGET_EXCEEDED
SHARD_NOT_FOUND
LANGUAGE_PROVIDER_UNAVAILABLE
LANGUAGE_PROVIDER_FAILED
LANGUAGE_UNSUPPORTED
WORKFLOW_CANDIDATES_NOT_BUILT
RELATIONSHIP_CHAINS_NOT_BUILT
DOCUMENT_SEMANTICS_NOT_BUILT
TOKEN_BUDGET_TOO_SMALL
PROFILE_NOT_FOUND
REGRESSION_TARGET_UNAVAILABLE
PUBLIC_PAYLOAD_REDACTION_FAILED
```

## 13. HTTP / MCP / CLI Parity

HTTP、MCP、CLI read/build 输出必须在以下字段上保持一致：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- artifact refs count
- warning count
- unresolved count
- accepted / blocker / provider_unavailable counts
- public error code
