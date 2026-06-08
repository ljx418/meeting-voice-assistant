# V2.11-V2.15 Full Coverage Matrix

> This is a planning and closure scaffold. It is not implementation evidence until each stage fills concrete test results and artifact paths.

| PRD Item | Target Architecture Item | Stage | Planned Status | Closure Evidence Required | Acceptance Status |
| --- | --- | ---: | --- | --- | --- |
| Actionability index | Actionability Index | V2.11 | implemented | `pytest backend/tests/test_v2_11_coding_agent_actionability.py -q`; real data_service E2E definitions=3736, references=31363 | accepted |
| Definition/reference graph v1 | Actionability Index | V2.11 | implemented | definitions/references artifacts generated; forbidden relation count=0 | accepted |
| Impact analysis | Impact Analysis Service | V2.11 | implemented | three data_service task reports returned candidate counts `[3313, 2757, 2720]` | accepted |
| Test mapping | Actionability Index | V2.11 | implemented | test mapping artifact generated, rows=4328 with accepted/needs_review statuses | accepted |
| Task-to-edit plan | Task-to-Edit Planner | V2.11 | implemented | three task plans generated 12 recommendations each; evidence or needs_review enforced; HarnessOS smoke generated actionability with definitions=7538 and references=51550 | accepted |
| Patch plan | Patch Plan Store | V2.12 | implemented | `PYTHONPATH=backend pytest backend/tests/test_v2_12_safe_patch_planning.py -q`; persisted `coding_agent/patch_plans/{patch_plan_id}.json`; HTTP/MCP/CLI create/read parity; real data_service smoke `patchplan_06e6475df9964a5e`; HarnessOS smoke `patchplan_156e2209cf0d8b2b` with `needs_review` | accepted |
| Candidate edit regions | Candidate Edit Selector | V2.12 | implemented | every candidate has repo-relative `path` in artifact or public `source_file`, line range, evidence refs or `needs_review`; low-confidence tasks become structured blocker | accepted |
| Validation plan | Validation Plan Builder | V2.12 | implemented | validation commands cite V2.11 test mapping or `needs_review`; every command has `execution_policy=plan_only`; V2.12 executes no command | accepted |
| Rollback plan | Rollback Plan Builder | V2.12 | implemented | rollback steps cover every proposed candidate path; incomplete scope blocks readiness through `ROLLBACK_SCOPE_INCOMPLETE` | accepted |
| No source mutation | Patch Safety Gate | V2.12 | implemented | focused before/after repo source hash test passes; real smoke writes only managed workspace artifacts; `mutates_code=false`, `executes_runtime=false` | accepted |
| Runtime command registry | Controlled Runtime Evidence | V2.13 | implemented | `PYTHONPATH=backend pytest backend/tests/test_v2_13_15_coding_agent_remaining.py -q`; default-deny registry persisted at `coding_agent/runtime/command_registry.json`; HTTP/MCP/CLI parity; real non-allowlisted block test | accepted |
| Allowlisted test run | Controlled Runtime Evidence | V2.13 | implemented | allowlisted pytest or read-only AST syntax command run on real fixture repo; real `data_service` smoke `python_ast_check` passed with `run_4fcfc807a3a558d8`; HarnessOS smoke `python_ast_check` passed with `run_3b2847120b8db8f1`; persisted runtime evidence at `coding_agent/runtime/runs/{run_id}.json`; linked static evidence and optional patch plan refs | accepted |
| Log redaction | Controlled Runtime Evidence | V2.13 | implemented | redacted stdout/stderr artifacts persisted under `coding_agent/runtime/logs/`; public payload scan rejects absolute repo path leak | accepted |
| Incremental diff | Incremental Intelligence Store | V2.14 | implemented | two-snapshot real fixture mutation E2E; deterministic diff artifact at `coding_agent/incremental/snapshot_diffs/{diff_id}.json` | accepted |
| Changed fact detection | Incremental Intelligence Store | V2.14 | implemented | changed file/symbol/surface/doc hints emitted with evidence or `needs_review`; `identity_inputs` excludes `created_at` | accepted |
| Task memory | Incremental Intelligence Store | V2.14 | implemented | task memory and drift timeline JSONL written/read; timeline event count asserted after real file mutation | accepted |
| Workbench payload | Review Workbench | V2.15 | implemented | workbench JSON generated from persisted V2.11-V2.14 artifacts only at `coding_agent/workbench/review_workbench.json`; real `data_service` smoke `workbench_f79225a4effba9ad`; HarnessOS smoke `workbench_9d5f3c4ccb3c8f67` | accepted |
| Workbench HTML | Review Workbench | V2.15 | implemented | HTML rendered from payload; blockers and `needs_review` visible; labels escaped; no `<script>` in generated page | accepted |
| Capability graph | Review Workbench | V2.15 | implemented | Mermaid graph generated at `coding_agent/workbench/capability_graph.mmd`; every edge endpoint resolves to a persisted JSON node | accepted |
| Context export | Review Workbench | V2.15 | implemented | context export persists under `coding_agent/workbench/context_exports/{export_id}.json`; recommendations preserve evidence or `needs_review`; source phase refs include V2.13-V2.15 | accepted |

## Closure Row Fields

Each row must be updated with:

```text
implementation_status
acceptance_status
test_command
test_result
artifact_paths
real_repo_result
audit_report_path
open_findings
```

## Allowed Acceptance Status Values

```text
accepted
conditionally_accepted
structured_blocker
not_implemented
out_of_scope
blocked_major
blocked_fatal
```

No in-scope row may remain `pending` at final roadmap closure.
