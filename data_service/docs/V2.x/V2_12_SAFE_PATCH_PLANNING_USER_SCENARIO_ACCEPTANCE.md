# V2.12 User Scenario Acceptance: Safe Patch Planning

## 1. Purpose

This document defines the user-facing acceptance scenarios for V2.12.

The technical acceptance plan proves artifacts, contracts, and safety gates. This document proves that the completed stage gives humans and external Coding Agents the expected project experience:

```text
task -> reviewable patch plan -> evidence-backed edit candidates -> validation descriptors -> rollback scope -> readiness/blockers
```

V2.12 remains read-only. These scenarios must not imply automatic patch application, test execution, commit, or push.

## 2. Expected User Experience After V2.12

After V2.12 closes, a user or Coding Agent should be able to:

- submit a real development task;
- receive a stable `patch_plan_id`;
- inspect proposed files, symbols, line ranges, and edit intents;
- compare multiple patch options when enough evidence exists;
- see validation commands as descriptors only;
- see rollback coverage for every proposed file;
- understand whether the plan is `ready_for_review`, `needs_review`, or `blocked`;
- trace each recommendation to evidence or an explicit `needs_review`;
- trust that V2.12 did not mutate source files;
- receive exact structured blockers for large-project or low-confidence cases.

### Target Experience at V2.12 Closure

V2.12 should feel like a safe planning assistant that sits between project understanding and code editing.

The target experience is:

- A user gives the service a concrete development task.
- The service returns a reviewable patch plan instead of a prose-only answer.
- The plan tells the user what to inspect first, what could be changed, how risky each option is, how to validate it later, and how to roll it back.
- The plan is specific enough to hand to a Coding Agent, but conservative enough that a human can reject or revise it before any code is edited.
- The service is honest when it cannot safely plan: it returns structured blockers and next actions instead of false confidence.

### Capabilities the User Can Experience

At the end of V2.12, users can use this project to:

- turn a task description into an evidence-backed patch planning artifact;
- identify likely files, symbols, handlers, routes, registries, tests, and documentation targets;
- compare multiple implementation strategies before editing;
- generate a test and validation checklist without executing commands;
- generate a rollback checklist for every proposed file;
- review public-surface alignment risks before changing HTTP, MCP, or CLI capabilities;
- plan documentation-code mismatch fixes without directly rewriting docs or source;
- decide whether a task is ready for coding, needs review, or is blocked;
- hand a structured plan to another Agent as implementation context;
- use structured blockers as a safe stop signal for large or ambiguous tasks.

### Not Expected in V2.12

Users should not expect V2.12 to:

- apply patches;
- generate an approved diff;
- edit source files or documentation;
- run tests or validation commands;
- commit or push code;
- prove runtime behavior;
- replace human code review;
- guarantee that `ready_for_review` means the change is safe to apply automatically.

## 3. Scenario A: Coding Agent Plans an HTTP API Change

### User Goal

An external Coding Agent wants to plan an implementation for an HTTP API behavior change before editing files.

### User Path

1. The Agent submits a task such as:

   ```text
   Plan the change needed to add request validation to an existing workspace-scoped HTTP endpoint.
   ```

2. The Agent calls one of:

   ```text
   HTTP POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans
   MCP  knowledge_code_patch_plan_create
   CLI  knowledge code patch-plan create
   ```

3. The service reads V2.11 actionability, impact, task-to-edit, test mapping, and line-level evidence.
4. The service persists `coding_agent/patch_plans/{patch_plan_id}.json`.
5. The Agent reads the patch plan and reviews candidate files, candidate symbols, validation descriptors, rollback scope, readiness, evidence, and blockers.

### Expected Project Experience

- The user can identify the likely handler, request model, route registration, and tests.
- The user can see why each file or symbol is recommended.
- The user can see validation guidance but is not told that validation has already run.
- The user can see how to roll back all proposed files.
- The user can start implementation manually or in a later authorized phase with enough context.

### Acceptance Evidence

The scenario passes only if the output includes:

- `patch_plan_id`;
- `status` and `readiness.score`;
- non-empty `edit_candidates`;
- at least one `patch_options` entry or a clear blocker explaining why no option is safe;
- `validation_plan` entries with `execution_policy=plan_only`;
- `rollback_plan` entries covering every proposed file;
- evidence refs or `needs_review` for each candidate;
- no source mutation proof.

## 4. Scenario B: Maintainer Reviews MCP/CLI Capability Registration

### User Goal

A maintainer wants to plan a change that affects MCP tool registration and CLI command exposure.

### User Path

1. The maintainer submits a task such as:

   ```text
   Plan how to add a new MCP tool and keep the CLI command aligned.
   ```

2. The service creates a patch plan.
3. The maintainer reads the same plan through HTTP, MCP, and CLI.
4. The maintainer checks registration files, handler candidates, tests, alignment risks, and rollback scope.

### Expected Project Experience

- The user can see candidate registration and handler files.
- The user can see MCP/CLI alignment risks.
- The user can compare minimal implementation and documentation/test options if available.
- If alignment evidence is incomplete, the plan is `needs_review` or `blocked`, not `ready_for_review`.

### Acceptance Evidence

The scenario passes only if:

- HTTP/MCP/CLI read outputs align on stable fields;
- registration-related candidates have evidence or `needs_review`;
- readiness is not `ready_for_review` when alignment evidence or rollback coverage is incomplete;
- public payloads expose repo-relative paths only.

## 5. Scenario C: Reviewer Plans a Documentation-Code Mismatch Fix

### User Goal

A reviewer wants to plan how to address a mismatch between project documentation and code behavior.

### User Path

1. The reviewer submits a task such as:

   ```text
   Plan a safe fix for a documented capability that appears inconsistent with the implementation.
   ```

2. The service builds patch options from document-code evidence and V2.11 actionability.
3. The reviewer compares options before deciding whether to modify docs, code, tests, or some combination.

### Expected Project Experience

- The user sees at least one option when evidence is sufficient:
  - docs-only correction;
  - code behavior change;
  - test/documentation update;
  - combined implementation and documentation update.
- Each option explains tradeoffs, risk level, validation descriptors, rollback scope, and blockers.
- The service does not directly rewrite docs or source files.

### Acceptance Evidence

The scenario passes only if:

- `patch_options` include option summaries and risk levels;
- each option references candidate IDs;
- each recommendation has evidence or `needs_review`;
- the output distinguishes documentation edits from code edits;
- low-confidence mismatch evidence prevents `ready_for_review`.

## 6. Scenario D: Large Project or Low-Confidence Task

### User Goal

An Agent or maintainer wants to run V2.12 on HarnessOS or another large project without receiving false confidence.

### User Path

1. The user submits a broad or low-confidence task against a large project.
2. The service attempts to resolve actionability and patch candidates through generic V2.11/V2.12 logic.
3. If the service cannot safely produce a patch plan, it returns structured blockers instead of a false ready status.

### Expected Project Experience

- The user sees exact blocker reasons, not an empty or misleading success result.
- The user can understand whether the blocker is missing actionability, missing impact data, too many candidates, missing validation, missing rollback, timeout, or low confidence.
- The output gives next actions such as narrowing focus paths, rebuilding actionability artifacts, or moving to manual review.
- No project-specific HarnessOS logic is required for the scenario to pass.

### Acceptance Evidence

The scenario passes only if:

- the output is either an accepted patch plan or a structured blocker;
- timeouts or missing artifacts are not marked accepted;
- blockers appear in `unresolved` or `needs_review`;
- public payloads do not hide blockers;
- no source mutation occurs.

## 7. User Scenario Acceptance Matrix

| Scenario | Primary User | Required Experience | Required Status |
| --- | --- | --- | --- |
| HTTP API patch planning | Coding Agent | Finds likely files, edit candidates, validation, rollback, evidence | `ready_for_review`, `needs_review`, or explicit blocker |
| MCP/CLI registration planning | Maintainer | Shows alignment risk and registration candidates across public surfaces | Not ready if alignment evidence is incomplete |
| Docs-code mismatch planning | Reviewer | Presents docs/code/test options with risk and evidence | Not ready if mismatch evidence is weak |
| Large-project planning | Coding Agent / Maintainer | Returns useful plan or exact structured blocker | No false accepted status |

## 8. Additional User Scenarios

### Scenario E: Test Coverage Planning

User task:

```text
This capability appears under-tested. Plan which tests should be added or updated before implementation.
```

User experience:

- The user sees likely capability, surface, handler, existing test patterns, and candidate test files.
- The user receives validation descriptors that can later be executed by a controlled runtime phase.
- Missing test evidence lowers readiness and creates `needs_review` or `VALIDATION_TEST_NOT_FOUND`.

Acceptance:

- The output identifies candidate test files or exact blockers.
- Validation entries are descriptors only.
- The plan does not claim that tests have run.

### Scenario F: Low-Confidence Broad Architecture Task

User task:

```text
Improve the architecture of this project and make it clearer.
```

User experience:

- The system refuses to fabricate a precise patch plan for an overly broad task.
- The user sees blockers such as task too broad, too many candidates, missing focus paths, missing evidence, or no validation plan.
- The user receives next actions such as narrowing by capability, specifying focus paths, or requesting impact analysis first.

Acceptance:

- The result is `needs_review` or `blocked`, not `ready_for_review`.
- Blockers appear in `unresolved[]` or `needs_review[]`.
- Next actions are visible.

### Scenario G: Code Review Preparation

User task:

```text
Before I let another Agent edit this feature, generate a patch plan I can review for risk.
```

User experience:

- The user receives a review checklist derived from patch options, impacted files, validation descriptors, rollback steps, and risks.
- High-risk files or public-surface changes are visible.
- The plan can be used as a go/no-go checkpoint before allowing code edits in a future phase.

Acceptance:

- The plan includes reviewable options and risks.
- High-risk recommendations include evidence or `needs_review`.
- The output does not imply that V2.12 authorizes automatic editing.

## 9. Scenario Closure Requirements

V2.12 cannot close unless the acceptance audit report includes a user scenario section with:

- user input task;
- interface used;
- `patch_plan_id` or structured blocker id;
- observed user-facing sections;
- expected project experience result;
- pass/fail conclusion;
- evidence artifact refs;
- no-source-mutation result.

The closure report must also state whether the user could understand:

- what to change;
- why those files or symbols were proposed;
- which option is safest;
- how validation should be performed later;
- how rollback would work;
- whether the plan is ready, reviewable, or blocked.

## 10. Generated Plan Quality Gate

V2.12 generated output must be usable as a human-readable planning document, even when represented as JSON.

The generated patch plan must expose these user-facing sections:

- task interpretation;
- proposed files and candidate symbols or line ranges;
- patch options and tradeoffs;
- evidence and `needs_review`;
- validation descriptors;
- rollback plan;
- readiness status and reason codes;
- unresolved blockers and next actions;
- no-source-mutation statement.

Quality requirements:

- The plan must not be a raw dump that forces the user to infer meaning from internal fields.
- Section names and summaries must be understandable to a maintainer or external Coding Agent.
- Each recommendation must be traceable to evidence or marked `needs_review`.
- Structured blockers must include exact reason and next action.
- The plan must not imply that validation ran or that code was modified.

## 11. False Experience Rejections

Reject user-scenario acceptance if:

- the user receives a patch plan but cannot tell which files or symbols are proposed;
- the generated plan is only a raw JSON dump with no inspectable planning sections;
- a validation command is presented as already executed;
- rollback scope is missing for any proposed file;
- low-confidence output is marked `ready_for_review`;
- a recommendation has neither evidence nor `needs_review`;
- a large-project timeout is marked accepted;
- HTTP/MCP/CLI results differ in user-visible status, unresolved counts, or needs_review counts;
- the report implies V2.12 can edit, test, commit, or push code.
