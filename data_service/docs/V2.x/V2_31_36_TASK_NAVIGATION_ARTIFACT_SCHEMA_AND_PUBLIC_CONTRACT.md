# V2.31-V2.36 Artifact Schema 与公共合同

## 1. 公共字段

所有 V2.31-V2.36 artifact 必须包含：

```json
{
  "schema_version": "v2.31-v2.36",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "created_at": "string",
  "source_artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "needs_review": [],
  "blockers": []
}
```

## 2. TaskNavigationQuery

```json
{
  "task_id": "string",
  "task": "string",
  "task_type": "api | mcp_tool | cli | workflow | provider | snapshot | governance | descriptor | entrypoint | bugfix | test | docs | architecture_review | unknown",
  "task_interpretation": {
    "summary": "string",
    "assumptions": [],
    "confidence": 0.8
  },
  "matched_capabilities": [],
  "matched_surfaces": [],
  "matched_symbols": [],
  "matched_tests": [],
  "matched_docs": [],
  "ranking_reason_codes": [],
  "evidence_refs": [],
  "needs_review": []
}
```

## 3. LightweightRelationship

```json
{
  "relationship_id": "string",
  "relationship_type": "direct_call_ast | method_call_candidate | handler_dispatch | surface_handled_by | registry_declared | config_declared | module_imports_module | symbol_references_symbol | test_references_symbol | capability_related_to_surface | heuristic_related | dynamic_unresolved",
  "source_ref": {
    "ref_type": "file | symbol | surface | capability | test | config | doc",
    "ref_id": "string",
    "path": "repo-relative"
  },
  "target_ref": {
    "ref_type": "file | symbol | surface | capability | test | config | doc",
    "ref_id": "string",
    "path": "repo-relative"
  },
  "confidence": 0.9,
  "semantic_limit": "direct_syntax | static_reference | registry_declared | config_declared | test_reference | heuristic_only | unresolved_dynamic",
  "truth_status": "accepted | needs_review | blocked",
  "evidence_refs": [],
  "line_range": [1, 10],
  "needs_review": [],
  "blockers": []
}
```

禁止出现在 artifact 中的 relationship type：

```text
full_call_graph
runtime_call_accepted
data_flow
control_flow
runtime_topology
type_inferred
production_runtime_topology
```

## 4. ImpactAnalysisV2

```json
{
  "impact_id": "string",
  "task_id": "string",
  "input_refs": [],
  "impacted_files": [],
  "impacted_symbols": [],
  "impacted_surfaces": [],
  "impacted_tests": [],
  "impacted_docs": [],
  "architecture_guardrails": [],
  "risk_items": [],
  "suggested_tests": [
    {
      "test_ref": "string",
      "reason": "string",
      "confidence": 0.8,
      "evidence_refs": [],
      "needs_review": []
    }
  ],
  "blockers": []
}
```

## 5. ModuleReadingPack

```json
{
  "pack_id": "string",
  "task_id": "string",
  "role": "coding_agent | review_agent | maintainer | documentation_agent",
  "required_reads": [],
  "optional_reads": [],
  "skip_reads": [],
  "reuse_patterns": [],
  "recommended_next_steps": [],
  "token_ledger": {
    "max_tokens": 16000,
    "estimated_tokens": 9000,
    "included_tokens": 8200,
    "omitted_tokens": 12000,
    "evidence_floor_tokens": 1600,
    "omitted_items": [
      {
        "item_ref": "string",
        "reason": "low_priority | duplicate | no_evidence | over_budget | superseded"
      }
    ]
  },
  "evidence_refs": [],
  "needs_review": []
}
```

## 6. Agent Handoff

```json
{
  "handoff_id": "string",
  "task_id": "string",
  "target_agent": "copilot | codex | claude_code | generic",
  "reading_pack_ref": "string",
  "impact_ref": "string",
  "recommended_commands": [],
  "guardrails": [],
  "acceptance_checks": [],
  "evidence_refs": [],
  "warnings": []
}
```

## 7. Public Envelope

所有 HTTP/MCP/CLI 输出必须包含：

```json
{
  "workspace_id": "string",
  "status": "ok | blocked | failed",
  "warnings": [],
  "artifact_refs": [],
  "next_actions": [],
  "data": {
    "v2": {
      "ok": true,
      "schema_version": "v2.31-v2.36",
      "workspace_id": "string",
      "codebase_id": "string",
      "snapshot_id": "string",
      "data": {},
      "artifact_refs": [],
      "warnings": [],
      "unresolved": [],
      "next_actions": []
    }
  }
}
```

错误响应：

```json
{
  "ok": false,
  "schema_version": "v2.31-v2.36",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "error": {
    "code": "TASK_NAVIGATION_NOT_BUILT",
    "message": "string",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

## 8. 错误码

```text
TASK_NAVIGATION_NOT_BUILT
TASK_QUERY_NOT_FOUND
RELATIONSHIP_GRAPH_NOT_BUILT
IMPACT_ANALYSIS_NOT_FOUND
READING_PACK_NOT_FOUND
TOKEN_BUDGET_TOO_SMALL
LARGE_PROJECT_RELATIONSHIP_BLOCKED
UNSUPPORTED_RELATIONSHIP_CLAIM
FORBIDDEN_RELATIONSHIP_TYPE
COPILOT_HANDOFF_NOT_FOUND
UPSTREAM_ARTIFACT_MISSING
PUBLIC_PAYLOAD_REDACTION_FAILED
```

## 9. HTTP/MCP/CLI Parity

验收必须比较：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- artifact refs 数量与排序
- warnings/unresolved/blockers 数量
- task/candidate/relationship/impact/pack stable ids
- error code 与 retryable 语义
