# V2.10 Artifact Schema and Public Contract

## 1. PatternAdapter

```json
{
  "adapter_id": "python_registry_assignment",
  "adapter_type": "registry_assignment",
  "language": "python",
  "file_globs": ["**/*.py"],
  "match_strategy": "ast_assignment",
  "confidence_policy": {
    "accepted_min": 0.85,
    "candidate_min": 0.4
  },
  "unsupported_claims": ["runtime_call", "data_flow", "control_flow"]
}
```

## 2. AdapterAttempt

```json
{
  "attempt_id": "attempt_xxx",
  "adapter_id": "python_registry_assignment",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "path": "repo-relative",
  "status": "matched | no_match | unavailable | blocked",
  "reason": "string",
  "created_at": "string"
}
```

## 3. ArchitectureBinding

```json
{
  "binding_id": "binding_xxx",
  "surface_id": "workflow:folder_summary",
  "surface_type": "workflow_entrypoint",
  "binding_type": "registry_key_to_class_definition",
  "source_path": "core/workflows/registry.py",
  "line_range": [10, 18],
  "definition_path": "core/workflows/folder_summary.py",
  "definition_line_range": [20, 96],
  "symbol_id": "py:class:core.workflows.folder_summary.FolderSummaryWorkflow",
  "adapter_id": "python_registry_assignment",
  "confidence": 0.9,
  "status": "accepted | needs_review | blocked",
  "truth_check": "passed | failed | not_run",
  "evidence_refs": [],
  "needs_review": []
}
```

## 4. ManifestCandidate

```json
{
  "candidate_id": "manifest_xxx",
  "manifest_path": "architecture.manifest.json",
  "surface_id": "agent:worker",
  "declared_symbol": "package.module.Worker",
  "declared_path": "package/module.py",
  "status": "candidate | schema_invalid | bound | blocked",
  "binding_id": "optional",
  "needs_review": []
}
```

## 5. RuntimeIntrospectionCandidate

```json
{
  "candidate_id": "runtime_xxx",
  "command_id": "list_workflows",
  "enabled": false,
  "status": "disabled | unavailable | candidate | blocked",
  "raw_output_stored": false,
  "surface_candidates": [],
  "needs_review": []
}
```

## 6. Public Envelope

All V2.10 public responses use:

```json
{
  "ok": true,
  "schema_version": "v2.10",
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

Error codes:

- `ARCHITECTURE_PATTERN_ADAPTERS_NOT_BUILT`
- `ARCHITECTURE_PATTERN_ADAPTER_UNAVAILABLE`
- `ARCHITECTURE_BINDING_NOT_FOUND`
- `ARCHITECTURE_MANIFEST_SCHEMA_INVALID`
- `ARCHITECTURE_RUNTIME_INTROSPECTION_DISABLED`
- `ARCHITECTURE_RUNTIME_INTROSPECTION_UNSAFE`
- `DEFINITION_LOOKUP_UNAVAILABLE`
- `LINE_RANGE_INVALID`
- `LINE_RANGE_TRUTH_CHECK_FAILED`

## 7. Acceptance Invariants

- `status=accepted` requires valid line range and truth check passed.
- `manifest` and `runtime` data are candidate-only until bound to code.
- `token_overlap_only` cannot produce accepted binding.
- Absolute paths are not returned in public payloads.

## 8. DefinitionLookupResult

```json
{
  "lookup_id": "lookup_xxx",
  "provider": "ast_import_resolver | jedi | tree_sitter",
  "provider_status": "available | unavailable | disabled",
  "request": {
    "source_path": "repo-relative",
    "symbol_name": "Worker",
    "import_statement": "from package.module import Worker"
  },
  "result": {
    "status": "resolved | unresolved | ambiguous | unavailable",
    "definition_path": "package/module.py",
    "definition_line_range": [12, 80],
    "confidence": 0.9
  },
  "error": {
    "code": "optional",
    "message": "redacted public message",
    "retryable": false
  }
}
```

Acceptance rules:

- `resolved` requires a readable repo-relative definition path and valid line range.
- `ambiguous` and `unresolved` can only produce `needs_review`.
- provider unavailable must be public and structured, never silently converted to no-match.

## 9. DocCodeEvidenceV3

```json
{
  "match_id": "doc_code_xxx",
  "doc_claim_id": "claim_xxx",
  "binding_id": "binding_xxx",
  "status": "matched | weak_match | missing_code_evidence | code_not_documented | blocked",
  "match_strategy": "exact_symbol | exact_path_line | adapter_binding | manifest_bound | token_overlap_only",
  "confidence": 0.86,
  "document_evidence_refs": [],
  "code_evidence_refs": [],
  "needs_review": [],
  "blockers": []
}
```

Acceptance rules:

- `matched` requires both document evidence and code line evidence.
- `token_overlap_only` can never become `matched`.
- document/drawio labels remain document claims, not code-derived evidence.

## 10. PatternEvidenceReport

```json
{
  "report_id": "pattern_report_xxx",
  "schema_version": "v2.10",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "summary": {
    "adapter_count": 12,
    "attempt_count": 100,
    "accepted_evidence_count": 20,
    "needs_review_count": 5,
    "blocked_count": 3
  },
  "sections": [
    {
      "section_id": "adapter_coverage",
      "title": "Adapter Coverage",
      "artifact_refs": [],
      "needs_review": []
    }
  ],
  "views": {
    "html": "architecture/v2_10/views/architecture_pattern_evidence_report.html",
    "mermaid": "architecture/v2_10/views/architecture_pattern_adapter_map.mmd"
  }
}
```

Renderer rules:

- HTML is generated only from persisted report JSON.
- Mermaid node ids come from artifact ids, not raw labels.
- Renderers must escape labels, text, and links.
- HTML/Mermaid cannot introduce unpersisted facts.

## 11. HTTP / MCP / CLI Public Contract

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/blockers
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/views/{view_id}
```

MCP:

```text
knowledge_code_architecture_patterns_v2_build
knowledge_code_architecture_patterns_v2
knowledge_code_architecture_pattern_blockers
knowledge_code_architecture_pattern_view
```

CLI:

```text
knowledge code architecture patterns-v2-build
knowledge code architecture patterns-v2
knowledge code architecture pattern-blockers
knowledge code architecture pattern-view
```

Parity assertions:

- same `schema_version`;
- same stable artifact refs;
- same adapter/evidence/blocker/report counts;
- same warnings and unresolved counts;
- same redaction state;
- same structured error code for equivalent failures.

## 12. Error Envelope

```json
{
  "ok": false,
  "schema_version": "v2.10",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "optional",
  "error": {
    "code": "ARCHITECTURE_PATTERN_ADAPTERS_NOT_BUILT",
    "message": "Pattern adapters have not been built for this snapshot.",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

Additional public error codes:

- `V29_BASELINE_UNAVAILABLE`
- `PATTERN_ADAPTER_CONFIG_INVALID`
- `PATTERN_ADAPTER_HARDCODED_PROJECT_RULE`
- `DEFINITION_LOOKUP_AMBIGUOUS`
- `MANIFEST_BINDING_MISSING`
- `RUNTIME_COMMAND_NOT_ALLOWLISTED`
- `RUNTIME_OUTPUT_NOT_STATICALLY_BOUND`
- `REPORT_VIEW_NOT_BUILT`
