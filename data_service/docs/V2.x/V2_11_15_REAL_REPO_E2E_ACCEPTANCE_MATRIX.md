# V2.11-V2.15 Real Repository E2E Acceptance Matrix

## 1. Repositories

Primary:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Large-project generality:

```text
/Users/Zhuanz/Desktop/workspace/harnessOS
```

If HarnessOS is unavailable, the phase must use another large local repository and record the replacement.

## 2. V2.11 E2E Tasks

| Task | Required Output | Acceptance |
| --- | --- | --- |
| Add or modify a HTTP API behavior in data_service | impacted files, surfaces, symbols, tests, risks | every high-confidence item has evidence |
| Add or modify a MCP/CLI capability in data_service | impacted MCP tools, CLI commands, registration files, tests | HTTP/MCP/CLI alignment risk is visible |
| Investigate a failing or missing test mapping | likely tests and test gaps | weak mappings remain `needs_review` |
| Large-project architecture actionability | actionable evidence or structured blockers | no project-specific code path |

## 3. V2.12 E2E Tasks

| Task | Required Output | Acceptance | User Experience Result |
| --- | --- | --- | --- |
| Generate patch plan for API change | edit candidates, validation plan, rollback plan | no source mutation | user can identify proposed handler/model/test files and why they were recommended |
| Generate patch plan for MCP/CLI registration change | registration candidates, alignment risk, validation plan, rollback plan | HTTP/MCP/CLI output parity | maintainer can review public surface alignment before editing |
| Generate patch plan for docs-code mismatch | proposed docs/code/test edit options | recommendations have evidence or `needs_review` | reviewer can compare docs-only, code-change, and combined options when evidence supports them |
| Generate low-confidence or large-project patch plan | needs_review/blockers | no false ready status | user receives exact blockers and next actions instead of misleading success |

## 4. V2.13 E2E Tasks

| Task | Required Output | Acceptance |
| --- | --- | --- |
| Try non-allowlisted command | structured blocked result | command not executed |
| Run allowlisted focused pytest | runtime evidence artifact | logs redacted, static evidence linked |
| Runtime smoke descriptor for public surface | pass/fail/blocked artifact | runtime evidence not merged into source evidence |

## 5. V2.14 E2E Tasks

| Task | Required Output | Acceptance |
| --- | --- | --- |
| Modify one fixture file | changed file and changed symbol report | generated_at does not affect diff identity |
| Add one public-surface-like fixture | changed surface candidate | evidence or `needs_review` |
| Compare two snapshots | artifact diff report | prior artifacts unchanged |

## 6. V2.15 E2E Tasks

| Task | Required Output | Acceptance |
| --- | --- | --- |
| Generate data_service workbench | HTML + Mermaid + backend payload | all visible nodes resolve to artifact IDs |
| Generate HarnessOS workbench | readable report or structured blockers | blockers visible |
| Export task context | context export artifact | evidence preserved under token budget |

## 7. Global E2E Rejection Rules

Reject phase acceptance if:

- mock-only data is used for real E2E;
- absolute local path appears in public output;
- accepted action item has no evidence and no `needs_review`;
- frontend introduces facts absent from backend artifact;
- runtime command executes without allowlist;
- patch plan mutates source files in V2.12.

## 8. Actual Closure Evidence

### data_service

Real repository smoke:

```text
repo=/Users/Zhuanz/Desktop/workspace/data_service
codebase_id=codebase_data_service
snapshot_id=snap_787592231f2e97e1f417
definitions=3863
references=32413
patch_plan=patchplan_4db2d42406c2251b
runtime_commands=12
selected_runtime_command=python_ast_check
runtime_status=passed
runtime_exit_code=0
run_id=run_4fcfc807a3a558d8
workbench_id=workbench_f79225a4effba9ad
workbench_nodes=3
```

Acceptance result: accepted. The smoke wrote only managed workspace artifacts and did not mutate the source repository.

### HarnessOS

Large-project generality smoke:

```text
repo=/Users/Zhuanz/Desktop/workspace/harnessOS
codebase_id=codebase_harnessOS
snapshot_id=snap_54c394227a37e37bf763
definitions=7538
references=51550
test_mapping_count=7719
patch_plan=patchplan_156e2209cf0d8b2b
patch_status=needs_review
runtime_commands=12
selected_runtime_command=python_ast_check
runtime_status=passed
runtime_exit_code=0
run_id=run_3b2847120b8db8f1
workbench_id=workbench_9d5f3c4ccb3c8f67
workbench_nodes=3
blocker_count=0
```

Acceptance result: accepted for large-project smoke. `patch_status=needs_review` is expected and acceptable because V2.12/V2.15 must not promote large-project recommendations to ready without human review.
