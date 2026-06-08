# V2.12 Target Architecture: Safe Patch Planning

## 1. Position in the Roadmap

V2.12 consumes V2.11 actionability artifacts and produces read-only patch plan artifacts.

```text
V2.11 Actionability
  -> Impact Analysis
  -> Task-to-Edit Plan
  -> V2.12 Patch Plan Builder
  -> Patch Plan Store
  -> HTTP / MCP / CLI
```

V2.12 does not call the V2.13 runtime layer and does not apply patches.

## 2. Components

### 2.1 Patch Plan Builder

Responsibilities:

- resolve V2.11 actionability, impact, and task-plan inputs;
- select candidate edit regions;
- group regions into patch options;
- assign readiness score;
- produce blockers and `needs_review`.

### 2.2 Candidate Edit Selector

Inputs:

- V2.11 definitions
- V2.11 references
- V2.11 test mapping
- impact analysis
- task-to-edit recommendations

Outputs:

- candidate files
- candidate symbols
- candidate line ranges
- confidence and reason codes

### 2.3 Validation Plan Builder

Produces validation command descriptors only.

Rules:

- Does not execute commands.
- May recommend tests from V2.11 test mapping.
- If no suitable test exists, emits `VALIDATION_TEST_NOT_FOUND`.
- Unsafe or broad commands are `needs_review`.

### 2.4 Rollback Plan Builder

Produces rollback scope covering all proposed files.

Rules:

- No `git checkout`, `git reset`, or patch application.
- Rollback is advisory and manual-review oriented.
- Every proposed file must appear in rollback scope.

### 2.5 Patch Plan Store

Artifact location:

```text
workspace/assets/codebase/{codebase_id}/coding_agent/patch_plans/{patch_plan_id}.json
```

Artifacts must be immutable unless explicitly regenerated.

## 3. Artifact Schema Summary

```json
{
  "schema_version": "v2.12",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "patch_plan_id": "patchplan_xxx",
  "task": "string",
  "status": "ready_for_review | needs_review | blocked",
  "readiness": {
    "score": 0.0,
    "status": "ready_for_review | needs_review | blocked",
    "reason_codes": []
  },
  "mutates_code": false,
  "executes_runtime": false,
  "source_refs": [],
  "edit_candidates": [],
  "patch_options": [],
  "validation_plan": [],
  "rollback_plan": [],
  "evidence": [],
  "needs_review": [],
  "warnings": [],
  "unresolved": [],
  "artifact_refs": []
}
```

Canonical field names are inherited from `V2_11_15_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md`. User-facing blocker language maps to `unresolved[]` and `needs_review[]`; public implementations must not create a second incompatible blocker schema.

## 4. Public API Contract

### Create

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans
```

Request:

```json
{
  "task": "string",
  "snapshot_id": "optional",
  "impact_id": "optional",
  "task_plan_id": "optional",
  "focus_paths": [],
  "max_options": 3
}
```

### Read

```text
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{patch_plan_id}
```

MCP and CLI must expose the same stable ids, counts, warnings, unresolved items, `needs_review`, and artifact refs.

## 5. Architecture Boundaries

V2.12 must not:

- modify source files;
- apply generated patches;
- run validation commands;
- use runtime command execution;
- add core logic to `backend/app/api/v1/data_service.py`;
- add core logic to `backend/data_service/service.py`;
- treat a low-readiness plan as ready.

V2.12 should use focused `coding_agent` modules and thin HTTP/MCP/CLI adapters.

## 6. Failure Modes

Structured blockers:

```text
ACTIONABILITY_INDEX_NOT_FOUND
IMPACT_ANALYSIS_NOT_FOUND
TASK_PLAN_NOT_FOUND
NO_EDIT_CANDIDATES
VALIDATION_TEST_NOT_FOUND
ROLLBACK_SCOPE_INCOMPLETE
PATCH_READINESS_TOO_LOW
PATCH_PLAN_SCHEMA_INVALID
```

Blockers may be accepted output if they are explicit and evidence-backed.
