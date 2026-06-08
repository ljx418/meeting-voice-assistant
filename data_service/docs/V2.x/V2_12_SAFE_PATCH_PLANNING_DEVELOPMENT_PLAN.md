# V2.12 Development Plan: Safe Patch Planning

## 1. Objective

Implement the planning layer that creates read-only patch plans from V2.11 actionability artifacts.

This phase must preserve the safety boundary:

```text
plan only; no source mutation; no command execution
```

## 2. Development Steps

### Step 1: Pre-Implementation Audit

Create:

```text
docs/V2.x/V2_12_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

The audit must confirm:

- V2.11 acceptance report exists.
- V2.11 actionability artifacts can be built or read.
- V2.12 will not mutate source files.
- V2.12 will not run validation commands.
- No fatal or major spec finding is open.

### Step 2: Patch Plan Artifact and Persistence

Add persistence for:

```text
coding_agent/patch_plans/{patch_plan_id}.json
```

The artifact must include schema version, source refs, `edit_candidates`, `patch_options`, validation plan, rollback plan, `readiness`, evidence, `needs_review`, warnings, unresolved items, and artifact refs.

Canonical schema source:

```text
docs/V2.x/V2_11_15_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md
```

### Step 3: Candidate Edit Selector

Consume V2.11:

- actionability index
- impact analysis
- task-to-edit plan
- test mapping

Select candidate edit regions by:

- direct task-plan recommendation;
- impact target;
- focus path;
- linked symbol evidence;
- linked tests.

Weak matches must become `needs_review`.

### Step 4: Patch Option Builder

Produce up to `max_options` patch options:

- minimal option;
- broader implementation option when enough evidence exists;
- test/documentation option when implementation evidence is weak.

Each option must include tradeoffs and blocker reason codes through `unresolved` or `needs_review` references.

### Step 5: Validation and Rollback Plan

Validation plan:

- recommends commands as descriptors only;
- never executes commands;
- marks missing or broad commands as blockers.

Rollback plan:

- includes every proposed file;
- describes manual rollback action;
- includes evidence or `needs_review`.

### Step 6: HTTP/MCP/CLI

Expose:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{patch_plan_id}
knowledge_code_patch_plan_create
knowledge_code_patch_plan_read
knowledge code patch-plan create
knowledge code patch-plan read
```

### Step 7: Acceptance Audit

Create:

```text
docs/V2.x/V2_12_ACCEPTANCE_AUDIT_REPORT.md
```

The audit must include focused tests, real data_service E2E, large-project result, artifact inspection, no-mutation proof, PRD review, and false-green review.

## 3. Implementation Boundaries

Do not implement:

- patch application;
- source file editing;
- runtime validation execution;
- direct git mutation;
- automatic commit/push;
- full semantic refactoring.

## 4. Expected Code Organization

Preferred module boundary:

```text
backend/data_service/code_assets/coding_agent/
  patch_plans.py
  patch_persistence.py
```

HTTP/MCP/CLI adapters should stay thin and call focused service modules.

## 5. Stop Conditions

Stop and report if:

- planner attempts to write source files;
- rollback scope omits a proposed file;
- validation plan implies execution;
- readiness status says ready while unresolved blockers exist;
- accepted edit lacks evidence and lacks `needs_review`;
- implementation requires modifying legacy large service files.
