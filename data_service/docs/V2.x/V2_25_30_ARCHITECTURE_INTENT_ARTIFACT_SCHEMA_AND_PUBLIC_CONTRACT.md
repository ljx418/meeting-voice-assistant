# V2.25-V2.30 Artifact Schema 与公共合同

## 1. 通用 Envelope

```json
{
  "schema_version": "v2.25",
  "artifact_type": "architecture_intent_artifact",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "created_at": "string",
  "source_artifact_refs": [],
  "warnings": [],
  "needs_review": []
}
```

## 2. ArchitectureSource

```json
{
  "source_id": "doc:target_architecture:abc",
  "source_type": "markdown | drawio | mermaid | plantuml | code | config | test | runtime_descriptor",
  "path": "repo-relative/path",
  "authority_role": "target | plan | acceptance | audit | implementation | historical | unknown",
  "authority_level": "primary | supporting | weak | historical",
  "version_hint": "V2.25",
  "evidence": [{"path": "docs/...", "line_range": [1, 10]}],
  "confidence": 1.0,
  "needs_review": []
}
```

## 3. DiagramClaim

```json
{
  "claim_id": "claim_xxx",
  "source_id": "doc_xxx",
  "claim_type": "component | layer | boundary | adapter | provider | runtime | workflow | storage | public_interface | quality_gate",
  "label": "Workflow Engine",
  "normalized_label": "workflow_engine",
  "source_locator": {
    "path": "docs/design/target.drawio",
    "diagram_page": "目标架构",
    "cell_id": "abc123",
    "line_range": null
  },
  "confidence": 0.7,
  "status_hint": "target | current | planned | historical | unknown",
  "evidence": [],
  "needs_review": []
}
```

## 4. ProofNode / ProofEdge

```json
{
  "node_id": "proof:surface:mcp:knowledge_query",
  "node_type": "document_claim | code_symbol | public_surface | config_fact | test_fact | runtime_observed | human_confirmed",
  "label": "knowledge_query_v2",
  "source_refs": [],
  "evidence_refs": [],
  "confidence": 1.0
}
```

```json
{
  "edge_id": "proof_edge_xxx",
  "edge_type": "documented_by | defined_by | exposed_by | configured_by | tested_by | observed_by | confirmed_by | contradicts",
  "source_node_id": "string",
  "target_node_id": "string",
  "evidence_refs": [],
  "confidence": 0.9,
  "semantic_limit": "not_runtime_call | runtime_observed | inferred_only"
}
```

## 5. IntentCandidate

```json
{
  "intent_id": "intent_xxx",
  "intent_type": "capability | module_boundary | workflow | governance | runtime | storage",
  "summary": "The project uses MCP tools as the primary external agent surface.",
  "evidence_bundle_refs": [],
  "counter_evidence_refs": [],
  "confidence": 0.82,
  "status": "accepted | inferred | weak | needs_review | rejected",
  "human_confirmation": null,
  "recommendations": []
}
```

## 6. DiagramCodeVerification

```json
{
  "verification_id": "verify_xxx",
  "claim_id": "claim_xxx",
  "match_status": "accepted | weak_match | missing_code_evidence | undocumented_code_fact | conflict | stale | needs_review",
  "match_strategy": "exact_symbol_id | surface_id | path_line | config_manifest | test_reference | runtime_descriptor | taxonomy_synonym | token_overlap_only | manual_confirmed",
  "document_evidence_refs": [],
  "code_evidence_refs": [],
  "counter_evidence_refs": [],
  "confidence": 0.86,
  "blocking_reason": null
}
```

accepted 必须满足：

- `match_strategy != token_overlap_only`
- `confidence >= 0.80`
- `document_evidence_refs` 非空
- `code_evidence_refs` 非空
- 无 blocking counter evidence

## 7. Public Envelope

```json
{
  "ok": true,
  "schema_version": "v2.25",
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

错误形态：

```json
{
  "ok": false,
  "schema_version": "v2.25",
  "error": {
    "code": "ARCHITECTURE_INTENT_SOURCE_MISSING",
    "message": "Architecture source artifacts are missing.",
    "retryable": false
  },
  "warnings": [],
  "next_actions": []
}
```

## 8. 错误码

```text
ARCHITECTURE_INTENT_SOURCE_MISSING
ARCHITECTURE_DIAGRAM_PARSE_UNSUPPORTED
ARCHITECTURE_PROOF_GRAPH_NOT_BUILT
ARCHITECTURE_INTENT_NOT_BUILT
ARCHITECTURE_DIAGRAM_VERIFICATION_NOT_BUILT
ARCHITECTURE_MATCH_BELOW_THRESHOLD
ARCHITECTURE_RUNTIME_EVIDENCE_UNAVAILABLE
ARCHITECTURE_CONFIRMATION_TARGET_NOT_FOUND
ARCHITECTURE_PUBLIC_PAYLOAD_REDACTION_FAILED
```
