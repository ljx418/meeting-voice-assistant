# V2.12 PRD: Safe Patch Planning

## 1. Product Goal

V2.12 turns V2.11 Coding Agent actionability into a safe, reviewable patch planning layer.

The service should help a human or external Coding Agent answer:

```text
Given this task, what files and symbols should be edited, what change options exist, what should be validated, and how can the change be rolled back?
```

V2.12 must not edit source files. It creates only persisted advisory artifacts.

## 2. Users

- External Coding Agent
- Maintainer
- Code Reviewer
- Test Agent

## 3. In Scope

- Patch plan creation from a task and optional focus hints.
- Candidate edit region selection from V2.11 actionability and impact artifacts.
- Multi-option edit plan generation.
- Validation command planning as descriptors only.
- Rollback scope planning.
- Patch readiness scoring.
- Evidence and `needs_review` for every proposed edit.
- HTTP, MCP, and CLI read/create contracts.
- Real data_service E2E.
- Large-project accepted result or structured blocker.
- User scenario acceptance for the expected project experience after V2.12.

## 4. Out of Scope

- Applying patches.
- Rewriting source files.
- Running validation commands.
- Committing or pushing code.
- Generating exact diff hunks as accepted implementation without review.
- Claiming patch safety without evidence, validation rationale, and rollback scope.

## 5. Core User Stories

### US-001: Create Patch Plan

As a Coding Agent, I want to submit a development task and receive a read-only patch plan so I can decide where to edit safely.

Acceptance:

- Returns `patch_plan_id`.
- Persists `coding_agent/patch_plans/{patch_plan_id}.json`.
- Includes proposed files, edit regions, validation plan, rollback plan, readiness score, blockers, and evidence.
- Does not mutate source files.

### US-002: Review Patch Plan

As a maintainer, I want to read an existing patch plan over HTTP/MCP/CLI so I can audit the proposed implementation before editing.

Acceptance:

- HTTP/MCP/CLI return stable ids, counts, warnings, blockers, and artifact refs.
- Every proposed edit has evidence or `needs_review`.
- Low readiness plans are not marked ready.

### US-003: Rollback and Validation Planning

As a reviewer, I want the plan to show validation commands and rollback scope so I can judge risk before approving code edits.

Acceptance:

- Validation commands are descriptors, not executed commands.
- Rollback scope covers every proposed file.
- Missing tests or low-confidence validation produce structured blockers.

### US-004: User Scenario Review

As a product owner or maintainer, I want V2.12 closure to prove the expected user journey, not just internal artifact generation.

Acceptance:

- Scenario acceptance covers HTTP API patch planning, MCP/CLI registration planning, docs-code mismatch planning, and large-project/low-confidence blockers.
- Each scenario records the user input task, interface used, observed plan sections, expected project experience, evidence refs, and pass/fail result.
- The user-facing result must make clear that V2.12 plans edits but does not apply patches, run validation commands, commit, or push.

### US-005: Experience Clear Enough to Hand Off

As a maintainer, I want a V2.12 patch plan to be clear enough to hand to another Coding Agent or reviewer without needing to re-explain the project context.

Acceptance:

- The plan exposes proposed files, candidate symbols or line ranges, options, validation descriptors, rollback scope, readiness, and blockers as inspectable sections.
- The plan distinguishes concrete evidence from `needs_review`.
- The plan includes enough next actions for blocked or broad tasks to be narrowed safely.

## 6. Functional Requirements

### FR-001 Patch Plan Builder

Inputs:

```json
{
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "optional",
  "task": "string",
  "focus_paths": [],
  "impact_id": "optional",
  "task_plan_id": "optional",
  "max_options": 3
}
```

Output:

```json
{
  "patch_plan_id": "patchplan_xxx",
  "status": "ready_for_review | needs_review | blocked",
  "readiness": {
    "score": 0.0,
    "status": "ready_for_review | needs_review | blocked",
    "reason_codes": []
  },
  "mutates_code": false,
  "executes_runtime": false
}
```

### FR-002 Candidate Edit Regions

Each candidate edit region must include:

- repo-relative source file
- line range or symbol range
- edit intent
- linked evidence refs
- confidence
- `needs_review` if confidence is weak

### FR-003 Multi-Option Plan

The patch plan may include `patch_options`:

- minimal change option
- broader refactor option
- documentation/test-only option when appropriate

Each option must explain tradeoffs and blockers.

### FR-003A Canonical PatchPlan Fields

V2.12 implementation must use the canonical schema from `V2_11_15_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md`:

```text
edit_candidates[]
patch_options[]
validation_plan[]
rollback_plan[]
readiness.score
readiness.status
readiness.reason_codes[]
evidence[]
needs_review[]
warnings[]
unresolved[]
```

Structured blockers must be represented in `unresolved[]` and, when user attention is needed, `needs_review[]`. Do not introduce a separate incompatible `blockers[]` field in public contracts.

### FR-004 Validation Command Plan

Validation command planning is descriptor-only in V2.12.

Each command descriptor must include:

- command label
- command text
- reason
- expected coverage
- safety classification
- source of recommendation
- status: `planned | needs_review | blocked`

### FR-005 Rollback Plan

Rollback plan must include:

- all proposed files
- expected manual rollback action
- test re-run suggestions
- evidence refs or `needs_review`

### FR-006 Public Contracts

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{patch_plan_id}
```

MCP:

```text
knowledge_code_patch_plan_create
knowledge_code_patch_plan_read
```

CLI:

```text
knowledge code patch-plan create
knowledge code patch-plan read
```

## 7. Non-Functional Requirements

- Public payloads must not expose absolute paths, secrets, or raw tracebacks.
- Patch plan creation must not change source files.
- Existing V2.0-V2.11 artifacts must be read-only inputs unless explicitly rebuilt by their owning stage.
- All accepted recommendations must have evidence or `needs_review`.
- Low readiness score must not be labeled as ready.

## 8. Completion Definition

V2.12 is complete when:

1. Patch plan create/read exists over HTTP/MCP/CLI.
2. Patch plan artifact persists and reads back.
3. No source mutation occurs during planning.
4. Validation and rollback plans are present.
5. Every proposed edit has evidence or `needs_review`.
6. data_service real E2E passes.
7. HarnessOS or another large project produces accepted evidence or structured blocker.
8. User scenario acceptance proves the expected project experience for Coding Agent, maintainer, reviewer, and large-project blocker paths.
9. No fatal or major PRD/spec findings remain.
