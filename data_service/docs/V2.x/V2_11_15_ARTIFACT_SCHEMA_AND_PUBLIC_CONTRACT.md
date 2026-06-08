# V2.11-V2.15 Artifact Schema and Public Contract

## 1. Common Rules

All V2.11-V2.15 artifacts must include:

```json
{
  "schema_version": "v2.11+",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "created_at": "iso8601",
  "artifact_refs": [],
  "warnings": [],
  "unresolved": []
}
```

Public responses must use repo-relative paths and must not expose secrets, raw tracebacks, or absolute local paths.

## 2. ActionabilityIndex

```json
{
  "schema_version": "v2.11",
  "index_id": "actionability_{snapshot_id}",
  "provider_results": [],
  "definition_count": 0,
  "reference_count": 0,
  "test_mapping_count": 0,
  "confidence_policy": {
    "accepted_min": 0.85,
    "weak_min": 0.4
  }
}
```

Provider results must identify `provider=ast|tree_sitter|lsp|fallback` and `provider_status=available|partial|unavailable`.

## 3. DefinitionReferenceGraph

```json
{
  "graph_id": "refgraph_{snapshot_id}",
  "nodes": [],
  "edges": []
}
```

Allowed edge types:

```text
defines
references
imports
exposes_surface
mapped_to_test
implements_capability
```

Forbidden edge types:

```text
runtime_call
data_flow
control_flow
type_inferred
```

## 4. ImpactAnalysisReport

```json
{
  "impact_id": "impact_xxx",
  "input": {
    "task": "string",
    "changed_files": [],
    "changed_symbols": [],
    "target_capability": "optional"
  },
  "impacted_files": [],
  "impacted_symbols": [],
  "impacted_surfaces": [],
  "impacted_tests": [],
  "risks": [],
  "evidence": [],
  "needs_review": []
}
```

Every high-confidence impact item must cite evidence.

## 5. TaskToEditPlan

```json
{
  "plan_id": "editplan_xxx",
  "task_interpretation": {},
  "recommended_edits": [],
  "reference_patterns": [],
  "validation_commands": [],
  "rollback_scope": [],
  "confidence": 0.0,
  "needs_review": []
}
```

Recommended edits are advisory only in V2.11 and V2.12.

## 6. TestMapping

```json
{
  "mapping_id": "testmap_{snapshot_id}",
  "links": [
    {
      "source_type": "file|symbol|capability|surface",
      "source_id": "string",
      "test_path": "string",
      "match_strategy": "name|path|import|fixture|historical|manual",
      "confidence": 0.0,
      "evidence": [],
      "needs_review": []
    }
  ]
}
```

`name` and `path` matches alone must not exceed weak confidence unless supported by additional evidence.

## 7. PatchPlan

```json
{
  "schema_version": "v2.12",
  "patch_plan_id": "patchplan_xxx",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "task": "string",
  "status": "draft|ready_for_review|needs_review|blocked",
  "readiness": {
    "score": 0.0,
    "status": "ready_for_review|needs_review|blocked",
    "reason_codes": []
  },
  "edit_candidates": [
    {
      "candidate_id": "candidate_xxx",
      "path": "repo/relative/path.py",
      "symbol_id": "optional",
      "line_range": [1, 10],
      "change_intent": "add|modify|remove|rename|unknown",
      "evidence_refs": [],
      "needs_review": [],
      "confidence": 0.0
    }
  ],
  "patch_options": [
    {
      "option_id": "option_xxx",
      "summary": "string",
      "candidate_ids": [],
      "risk_level": "low|medium|high|unknown",
      "validation_command_ids": [],
      "rollback_step_ids": [],
      "evidence_refs": [],
      "needs_review": []
    }
  ],
  "validation_plan": [
    {
      "command_id": "validate_xxx",
      "command": "pytest ...",
      "execution_policy": "plan_only",
      "source": "test_mapping|existing_pattern|needs_review",
      "evidence_refs": [],
      "needs_review": []
    }
  ],
  "rollback_plan": [
    {
      "rollback_step_id": "rollback_xxx",
      "path": "repo/relative/path.py",
      "strategy": "restore_original|revert_generated_file|manual_review",
      "covers_candidate_ids": [],
      "needs_review": []
    }
  ],
  "evidence": [],
  "needs_review": [],
  "warnings": [],
  "unresolved": []
}
```

V2.12 must not apply this plan, execute validation commands, mutate source files, commit changes, or push code. Every public response must keep paths repo-relative and must not expose absolute local paths, secrets, or raw tracebacks.

Patch plan error codes:

```text
ACTIONABILITY_INDEX_NOT_FOUND
IMPACT_ANALYSIS_NOT_FOUND
TASK_PLAN_NOT_FOUND
PATCH_PLAN_NOT_FOUND
NO_EDIT_CANDIDATES
VALIDATION_TEST_NOT_FOUND
ROLLBACK_SCOPE_INCOMPLETE
PATCH_READINESS_TOO_LOW
PATCH_PLAN_SCHEMA_INVALID
```

## 8. RuntimeCommandRegistry

```json
{
  "registry_id": "runtime_commands_{codebase_id}",
  "default_policy": "deny",
  "allowlisted_commands": [],
  "blocked_commands": []
}
```

Each allowlisted command must include purpose, working directory policy, timeout, redaction policy, and expected artifact type.

## 9. RuntimeEvidence

```json
{
  "runtime_evidence_id": "runtime_xxx",
  "command_id": "string",
  "status": "queued|running|passed|failed|blocked|timeout",
  "exit_code": 0,
  "redacted_stdout_ref": "artifact://...",
  "redacted_stderr_ref": "artifact://...",
  "linked_static_evidence": [],
  "diagnosis_hints": []
}
```

Runtime evidence supports or challenges static evidence. It does not replace source evidence.

## 10. IncrementalSnapshotDiff

```json
{
  "diff_id": "diff_{from}_{to}",
  "from_snapshot_id": "string",
  "to_snapshot_id": "string",
  "changed_files": [],
  "changed_symbols": [],
  "changed_surfaces": [],
  "changed_doc_claims": [],
  "artifact_diffs": [],
  "identity_inputs": []
}
```

Generated timestamps must not affect identity.

## 11. ReviewWorkbenchPayload

```json
{
  "workbench_id": "workbench_{snapshot_id}",
  "sections": [],
  "visible_nodes": [],
  "visible_edges": [],
  "risk_lanes": [],
  "blocker_board": [],
  "context_exports": [],
  "source_artifact_refs": []
}
```

HTML and Mermaid views must be rendered from this payload only.

## 12. Public HTTP/MCP/CLI Contract

Success envelope:

```json
{
  "ok": true,
  "schema_version": "v2.11+",
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

Error envelope:

```json
{
  "ok": false,
  "schema_version": "v2.11+",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
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

Required error codes:

```text
ACTIONABILITY_INDEX_NOT_BUILT
IMPACT_ANALYSIS_NOT_FOUND
PATCH_PLAN_NOT_FOUND
NO_EDIT_CANDIDATES
ROLLBACK_SCOPE_INCOMPLETE
RUNTIME_COMMAND_NOT_ALLOWLISTED
RUNTIME_EVIDENCE_NOT_FOUND
INCREMENTAL_DIFF_NOT_FOUND
WORKBENCH_NOT_BUILT
PUBLIC_PAYLOAD_REDACTION_FAILED
```
