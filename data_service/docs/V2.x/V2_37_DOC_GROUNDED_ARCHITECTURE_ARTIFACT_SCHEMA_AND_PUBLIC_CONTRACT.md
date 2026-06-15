# V2.37 Artifact Schema and Public Contract

## 1. Common Envelope

```json
{
  "ok": true,
  "schema_version": "v2.37",
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

Error envelope：

```json
{
  "ok": false,
  "schema_version": "v2.37",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "error": {
    "code": "DOC_GROUNDED_ARCHITECTURE_NOT_BUILT",
    "message": "string",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

## 2. ArchitectureDocumentAuthority

```json
{
  "doc_id": "string",
  "path": "repo-relative path",
  "doc_type": "prd | target_architecture | gap_analysis | drawio | audit | acceptance | readme | unknown",
  "authority_role": "target | implementation_plan | acceptance_result | audit_status | historical_reference | evidence | unknown",
  "authority_level": "primary | supporting | historical | weak",
  "phase_hint": "V2.37",
  "version_hint": "string",
  "stale": false,
  "supersedes": [],
  "superseded_by": [],
  "evidence": [
    {"path": "docs/...", "line_range": [1, 1]}
  ],
  "confidence": 0.9,
  "needs_review": []
}
```

## 3. ArchitectureClaimNode

```json
{
  "claim_id": "string",
  "doc_id": "string",
  "claim_type": "plane | layer | component | workflow | agent | runtime | adapter | artifact | storage | governance | public_interface | quality_gate | non_goal",
  "label": "string",
  "normalized_label": "string",
  "source_block_type": "heading | bullet | table_row | diagram_node | diagram_edge | acceptance_gate | non_goal",
  "source_path": "repo-relative path",
  "line_range": [1, 2],
  "drawio_cell_id": "optional",
  "authority_role": "target",
  "evidence": [],
  "confidence": 0.8,
  "needs_review": []
}
```

## 4. CurrentArchitectureNode

```json
{
  "node_id": "string",
  "node_type": "module | package | surface | symbol | workflow_candidate | runtime_candidate | test | config | artifact",
  "label": "string",
  "source_artifact_ref": "string",
  "path": "repo-relative path",
  "line_range": [1, 2],
  "evidence": [],
  "confidence": 0.9,
  "needs_review": []
}
```

## 5. VerificationRow

```json
{
  "verification_id": "string",
  "claim_id": "string",
  "status": "supported | weakly_supported | unsupported | contradicted | code_not_documented | needs_review",
  "match_strategy": "exact_id | path_line_match | taxonomy_alias | graph_relation | token_overlap_only | manual_reviewed",
  "confidence": 0.8,
  "document_evidence": [],
  "code_evidence": [],
  "contradiction_evidence": [],
  "needs_review": [],
  "recommendation": "string"
}
```

Rules：

- `supported` requires non-empty `document_evidence` and non-empty `code_evidence`.
- `token_overlap_only` cannot produce `supported`.
- `contradicted` requires both document and code evidence; otherwise use `needs_review`.

## 6. ReconstructionReport

```json
{
  "report_id": "string",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "target_model_ref": "artifact://...",
  "current_model_ref": "artifact://...",
  "verification_ref": "artifact://...",
  "sections": [
    {
      "section_id": "target_architecture",
      "title": "Target Architecture from Docs",
      "node_refs": [],
      "evidence_refs": [],
      "needs_review": []
    }
  ],
  "html_ref": "artifact://...",
  "mermaid_ref": "artifact://..."
}
```

## 7. Public Error Codes

```text
DOC_AUTHORITY_REGISTRY_NOT_BUILT
ARCHITECTURE_CLAIMS_NOT_BUILT
CURRENT_IMPLEMENTATION_MODEL_NOT_BUILT
CLAIM_CODE_VERIFICATION_NOT_BUILT
RECONSTRUCTION_REPORT_NOT_BUILT
ARCHITECTURE_BRIEF_NOT_FOUND
DOC_GROUNDED_SCHEMA_INVALID
DOC_GROUNDED_SOURCE_ARTIFACT_MISSING
```

## 8. HTTP/MCP/CLI Parity

Success 和 error path 都必须比较：

- schema_version
- workspace_id / codebase_id / snapshot_id
- artifact_refs count
- claim/current/verification/report counts
- warnings count
- unresolved count
- error code
