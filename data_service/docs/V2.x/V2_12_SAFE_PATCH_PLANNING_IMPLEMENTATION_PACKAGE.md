# V2.12 Implementation Package: Safe Patch Planning

## 1. Goal

Generate read-only patch plans that help humans and Coding Agents review a proposed implementation before any file is edited.

## 2. Development Plan

Implement:

- patch plan builder;
- edit candidate selector;
- validation command planner;
- rollback planner;
- readiness scoring;
- patch plan read contracts.

V2.12 must not apply patches.

## 3. Artifact Outputs

```text
coding_agent/patch_plans/{patch_plan_id}.json
```

## 4. Public Interface Targets

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

## 5. Acceptance Plan

- Patch plan persists and can be read by HTTP/MCP/CLI.
- `git diff --name-only` before and after V2.12 patch planning shows no source mutation from the planner.
- Every edit candidate cites evidence or `needs_review`.
- Rollback plan covers all proposed files.
- Validation plan includes candidate tests or structured blockers.
- Low readiness score cannot be reported as ready.

## 6. Stop Conditions

Stop if:

- implementation attempts to write source files;
- patch plan omits rollback scope;
- recommendation lacks evidence and lacks `needs_review`;
- plan claims edits are safe without validation rationale.
