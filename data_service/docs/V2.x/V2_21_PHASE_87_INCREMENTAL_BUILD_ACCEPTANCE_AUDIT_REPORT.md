# V2.21 Phase 87 Incremental Build Acceptance Audit Report

## 1. Audit Conclusion

Status: **accepted for Phase 87 implementation closure**.

Phase 87 implemented the V2.21 platform incremental build planning layer. It produces a persisted incremental build plan, cache decisions, and scan profile from two real snapshots.

This phase is accepted as an **incremental planning and cache-decision capability**. It does not claim real selective rebuild execution.

No fatal or major PRD/spec deviation was found.

## 2. Implemented Scope

Implemented artifacts:

```text
platform/incremental/incremental_build_plan.json
platform/incremental/cache_decisions.jsonl
platform/incremental/scan_profile.json
```

Implemented module:

```text
backend/data_service/code_assets/platform/incremental.py
```

Implemented HTTP endpoints:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/incremental/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/incremental
```

Implemented MCP tools:

```text
knowledge_code_platform_incremental_build
knowledge_code_platform_incremental_read
```

Implemented CLI commands:

```text
knowledge code platform incremental-build
knowledge code platform incremental
```

## 3. Contract Checks

Verified contract properties:

- `schema_version = v2.21`
- `artifact_type = incremental_build_plan`
- from/to snapshot IDs are preserved
- changed files are derived from real snapshot manifests
- cache decisions include explicit `reason`
- changed files do not result in all artifacts being marked `reuse`
- scan budget reports file count, changed count, changed LOC estimate, changed ratio, duration, and budget status
- public payload has repo-safe `source_file` for changed files
- private path-like keys are still protected by existing public payload sanitization

## 4. Test Evidence

Focused test:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_21_incremental_build.py -q
```

Result:

```text
2 passed
```

Platform regression:

```bash
PYTHONPATH=backend python3 -m pytest \
  backend/tests/test_v2_18_platform_console.py \
  backend/tests/test_v2_19_artifact_contracts.py \
  backend/tests/test_v2_20_tool_catalog.py \
  backend/tests/test_v2_21_incremental_build.py -q
```

Result:

```text
8 passed
```

Public surface guard:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_public_surface_guard.py -q
```

Result:

```text
5 passed
```

Frontend build:

```bash
npm run build
```

Result:

```text
vue-tsc && vite build completed successfully
```

Full backend regression:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests -q
```

Result:

```text
464 passed, 617 warnings
```

Whitespace check:

```bash
git diff --check -- .
```

Result:

```text
passed
```

## 5. Real Repository E2E Evidence

Real source repository:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

E2E flow:

1. Copy real `data_service` repository into `/private/tmp/data_service_v221_e2e/repo`.
2. Import copied repository as a codebase asset.
3. Generate Snapshot A.
4. Modify `backend/app/main.py`.
5. Generate Snapshot B.
6. Build V2.21 incremental build plan from Snapshot A/B.
7. Verify changed files, cache decisions, scan profile, and artifact refs.
8. Run redaction scan over generated platform incremental artifacts.

Observed result:

```json
{
  "workspace_id": "data_service_v221_real_e2e",
  "codebase_id": "codebase_data_service_v221",
  "from_snapshot_id": "snap_3a555d680d36131375f5",
  "to_snapshot_id": "snap_800ef5b34e861dd312f2",
  "changed_file_count": 1,
  "cache_decision_count": 13,
  "reused_count": 2,
  "refreshed_count": 7,
  "invalidated_count": 4,
  "full_rebuild_required_count": 0,
  "changed_paths": ["backend/app/main.py"],
  "budget_status": "within_budget",
  "artifact_refs": 3
}
```

Redaction scan:

```bash
rg "/Users/Zhuanz/Desktop/workspace/data_service|/private/tmp/data_service_v221_e2e" \
  /private/tmp/data_service_v221_e2e/real_ws/assets/codebase/codebase_data_service_v221/platform/incremental
```

Result:

```text
no matches
```

## 6. PRD / Spec Review

Phase 87 aligns with V2.21 requirements:

- Snapshot diff reader: implemented by reusing existing V2.14 snapshot diff.
- Build impact planner: implemented as platform incremental build plan.
- Artifact cache invalidation: implemented as family-level cache decisions.
- Scan budget report: implemented as `scan_profile.json`.
- Large repo performance: supported through explicit scan budget reporting, not through unverified selective execution.

No unsupported claims were introduced:

- no full incremental rebuild execution claim;
- no runtime call graph claim;
- no data flow/control flow inference claim;
- no silent reuse when changed files exist.

## 7. False Acceptance Review

Rejected false-green risks checked:

- **Changed file ignored**: rejected by focused and real E2E tests.
- **All-reuse despite changed files**: rejected by focused tests.
- **Cache decision without reason**: rejected by focused tests.
- **Mock-only acceptance**: rejected by real repository E2E.
- **Path leakage**: rejected by redaction scan.
- **HTTP-only implementation**: rejected by MCP/CLI parity tests.
- **Regression risk**: rejected by full backend test suite and frontend build.

## 8. Open Findings

Fatal findings: none.

Major findings: none.

Minor residual risks:

- Artifact dependency decisions are conservative family-level policies, not complete semantic dependency analysis.
- The phase reports what should be reused/refreshed/invalidated; it does not execute partial rebuilds.

## 9. Exit Decision

Phase 87 can be marked complete.

Phase 88 may start after its phase-specific development plan, acceptance plan, and pre-implementation audit close without fatal or major findings.
