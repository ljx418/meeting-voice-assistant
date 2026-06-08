# V2.11-V2.15 Target Architecture

## 1. Current Baseline

Accepted baseline:

- V2.0-V2.5: project import, snapshot, public surface, symbols, evidence, context packs, ResearchNotebook provider contracts.
- V2.6-V2.10: architecture abstraction, document-code governance, readable reports, evidence hardening, generic architecture pattern adapters.

Current limitation:

- The system can explain and audit a project, but it does not yet provide a complete coding-agent action layer for impact analysis, patch planning, runtime evidence, incremental updates, and interactive review.

## 2. Target Architecture Overview

```text
V2.0-V2.10 Artifacts
  -> Actionability Index
  -> Impact Analysis
  -> Task-to-Edit Planner
  -> Patch Plan Store
  -> Controlled Runtime Evidence
  -> Incremental Intelligence Store
  -> Review Workbench
  -> HTTP / MCP / CLI / Agent Context
```

## 3. New Logical Components

### 3.1 Actionability Index

Consumes:

- snapshots
- files
- symbols
- public surfaces
- architecture evidence
- document-code alignment
- pattern evidence

Produces:

- definition/reference graph v1
- file/symbol/capability/test links
- actionability facts

Rules:

- LSP/tree-sitter facts must be marked by provider.
- AST fallback is accepted only when line-level truth checks pass.
- Import/reference edges must not be labeled as runtime calls.

### 3.2 Impact Analysis Service

Inputs:

- task text
- changed files
- changed symbols
- diff metadata
- optional target capability

Outputs:

- impacted capabilities
- impacted public surfaces
- impacted modules
- impacted docs
- likely tests
- risks
- evidence
- needs_review

### 3.3 Task-to-Edit Planner

Inputs:

- task interpretation
- actionability facts
- impact analysis
- coding patterns
- test mapping

Outputs:

- recommended edit set
- candidate files and symbols
- reference patterns
- validation commands
- rollback scope
- confidence and blockers

### 3.4 Safe Patch Plan Store

Persists patch plans without applying them.

Consumes:

- V2.11 actionability index
- impact analysis reports
- task-to-edit plans
- test mapping
- file/symbol/surface evidence

Produces:

- candidate edit regions
- ranked patch options
- validation command plan
- rollback plan
- patch readiness status
- structured blockers

Rules:

- Plans are read-only advisory artifacts.
- No file mutation in V2.12.
- Every edit recommendation has evidence or `needs_review`.
- Validation commands are not executed in V2.12.
- A plan cannot be `ready_for_review` unless candidate edits, validation guidance, rollback coverage, and evidence checks are complete.

### 3.5 Controlled Runtime Evidence Layer

Inputs:

- allowlisted commands
- test commands
- runtime smoke descriptors

Outputs:

- runtime evidence artifacts
- redacted logs
- command status
- failure diagnosis hints

Rules:

- Default deny.
- No arbitrary shell execution.
- Secrets, absolute paths, and raw tracebacks are redacted from public payloads.

### 3.6 Incremental Intelligence Store

Stores:

- file fingerprints
- changed symbol facts
- changed surfaces
- changed document claims
- artifact diffs
- task memory
- drift timeline

Rules:

- Existing artifacts are immutable unless explicitly rebuilt by the owning phase.
- Snapshot identity must not depend on generated timestamps.

### 3.7 Interactive Review Workbench

Frontend/readable HTML consumer of backend artifacts.

Rules:

- It is not a source of truth.
- It must not hide blockers or needs_review.
- Every visible node links to persisted artifact IDs.

## 4. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/coding_agent/
  actionability/
    index.json
    references.jsonl
    definitions.jsonl
    test_mapping.jsonl
  impact/
    {impact_id}.json
  patch_plans/
    {plan_id}.json
  runtime/
    command_registry.json
    runs/{run_id}.json
    logs/{run_id}.redacted.txt
  incremental/
    snapshot_diffs/{from}_{to}.json
    task_memory.jsonl
    drift_timeline.jsonl
  workbench/
    review_workbench.html
    capability_graph.mmd
```

## 5. Public Contracts

Each stage must expose consistent HTTP/MCP/CLI read contracts.

V2.12 target endpoints:

```text
HTTP:
  POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans
  GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{patch_plan_id}

MCP:
  knowledge_code_patch_plan_create
  knowledge_code_patch_plan_read

CLI:
  knowledge code patch-plan create
  knowledge code patch-plan read
```

Minimum envelope:

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
  "error": {
    "code": "ACTIONABILITY_INDEX_NOT_BUILT",
    "message": "string",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

## 6. Architecture Boundaries

Do not add core logic to:

- `backend/app/api/v1/data_service.py`
- `backend/data_service/service.py`

Use focused modules under:

```text
backend/data_service/code_assets/coding_agent/
backend/data_service/code_assets/architecture/
```

## 7. Stop Conditions

Stop for human confirmation if a phase requires:

- automatic code mutation;
- arbitrary command execution;
- production credentials;
- non-redacted logs;
- claiming runtime behavior from static imports;
- accepting task recommendations without evidence or `needs_review`.

V2.12-specific stop conditions:

- patch planning requires editing a source file;
- validation can only be proven by executing a command before V2.13 allowlist governance exists;
- rollback scope cannot cover all proposed files;
- large-project output would require project-specific hardcoding;
- public payload would expose absolute paths, secrets, raw tracebacks, or generated patch text without evidence.
