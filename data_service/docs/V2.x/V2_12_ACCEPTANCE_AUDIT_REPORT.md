# V2.12 Acceptance Audit Report: Safe Patch Planning

## Conclusion

Accepted for V2.12 implementation scope.

V2.12 now produces persisted read-only patch plans from V2.11 actionability artifacts. The implementation exposes service, HTTP, MCP, and CLI contracts and preserves the safety boundary: it does not mutate source files and does not execute validation commands.

## Implemented Capability

- Patch plan artifact persistence under `coding_agent/patch_plans/{patch_plan_id}.json`.
- Patch plan create/read service methods.
- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{patch_plan_id}`
- MCP:
  - `knowledge_code_patch_plan_create`
  - `knowledge_code_patch_plan_read`
- CLI:
  - `knowledge code coding-agent patch-plan`
  - `knowledge code coding-agent patch-plan-read`
- Public payload sections for proposed files, patch options, evidence/review, validation, rollback, readiness, and blockers.

## Artifact Contract Review

| Requirement | Result |
| --- | --- |
| `schema_version` is `v2.12` | Pass |
| `patch_options` is used instead of `edit_options` | Pass |
| `readiness` includes `score`, `status`, and `reason_codes` | Pass |
| `mutates_code=false` | Pass |
| `executes_runtime=false` | Pass |
| Each edit candidate has evidence or `needs_review` | Pass |
| Validation commands are descriptor-only | Pass |
| Rollback covers all proposed candidates or blocks readiness | Pass |
| Low-readiness task does not return `ready_for_review` | Pass |
| Public payload avoids absolute repo path leakage | Pass |

## Test Evidence

```text
PYTHONPATH=backend pytest backend/tests/test_v2_12_safe_patch_planning.py -q
Result: 3 passed

PYTHONPATH=backend pytest backend/tests/test_v2_11_coding_agent_actionability.py -q
Result: 1 passed

PYTHONPATH=backend pytest backend/tests/test_public_surface_guard.py -q
Result: 5 passed

PYTHONPATH=backend python3 -m py_compile backend/data_service/code_assets/coding_agent/service.py backend/data_service/code_assets/coding_agent/persistence.py backend/app/api/v1/code_assets_coding_agent.py backend/data_service/mcp_code_coding_agent_tools.py backend/data_service/cli_code_coding_agent.py backend/tests/test_v2_12_safe_patch_planning.py
Result: pass
```

## Real Repository E2E

Real repository:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Smoke command imported the real repository into a temporary managed workspace, generated a snapshot, and created a V2.12 patch plan for:

```text
add HTTP API route behavior and update validation planning
```

Observed result:

```json
{
  "workspace_root": "/private/tmp/v212-real-7a7ghqi4",
  "codebase_id": "codebase_data_service_real",
  "snapshot_id": "snap_a18e3f2ecac227cd106d",
  "patch_plan_id": "patchplan_06e6475df9964a5e",
  "status": "ready_for_review",
  "candidate_count": 12,
  "option_count": 3,
  "validation_count": 12,
  "rollback_count": 10,
  "mutates_code": false,
  "executes_runtime": false
}
```

## User Scenario Review

The patch plan output exposes user-facing sections:

- proposed files and symbols;
- patch options;
- evidence and needs review;
- validation plan;
- rollback plan;
- readiness and blockers.

This satisfies the V2.12 user expectation: a human or Coding Agent can review where to edit, why those files were selected, how validation should later be selected, how rollback should be scoped, and whether the plan is ready, reviewable, or blocked.

## False-Green Review

| False-Green Risk | Result |
| --- | --- |
| Text-only plan without persisted artifact | Rejected by artifact path assertion |
| Source mutation by planner | Rejected by before/after source hash test |
| Validation descriptors treated as executed tests | Rejected by `execution_policy=plan_only` assertions |
| Low-confidence task marked ready | Rejected by blocker test |
| HTTP-only implementation | Rejected by HTTP/MCP/CLI parity test |
| Absolute path leakage | Rejected by public payload serialization checks |

## Open Findings

No open fatal or major findings for V2.12.

## Audit Opinion

V2.12 can be marked accepted for the safe patch planning scope. It remains intentionally read-only and does not provide patch application, runtime execution, or git automation.
