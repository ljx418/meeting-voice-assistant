# V2.21 Phase 87 Incremental Build Pre-Implementation Audit Report

## 1. Audit Conclusion

Status: **approved for implementation**.

No fatal or major PRD/spec deviation was found after reviewing the V2.18-V2.24 PRD, target architecture, artifact contract, and Phase 84-90 implementation package.

## 2. Scope Fit

Phase 87 correctly targets V2.21 Incremental Build & Large Repo Performance:

- snapshot diff reader;
- build impact planner;
- cache invalidation policy;
- scan budget report;
- large repo scan profile.

The implementation plan intentionally does not promise real selective rebuild execution. It produces an evidence-backed plan and cache decisions only.

## 3. Architecture Review

Approved module boundary:

```text
backend/data_service/code_assets/platform/incremental.py
backend/data_service/code_assets/platform/persistence.py
backend/app/api/v1/code_assets_platform.py
backend/data_service/mcp_code_platform_tools.py
backend/data_service/cli_code_platform.py
```

Forbidden changes:

- no V2.21 core logic in `backend/app/api/v1/data_service.py`;
- no V2.21 core logic in `backend/data_service/service.py`;
- no mutation of source registry;
- no runtime/data/control-flow claims.

## 4. Acceptance Readiness

Acceptance plan is sufficient because it requires:

- focused tests;
- real repo E2E;
- HTTP/MCP/CLI parity;
- artifact disk inspection;
- public redaction;
- full regression.

## 5. Risk Register

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Existing V2.14 diff is mistaken for full incremental rebuild | Major | Artifact wording uses `plan` and `decision`, not `executed rebuild`. |
| Unsafe reuse after changed file | Major | Test rejects all-reuse when changed files exist. |
| Cache decisions too broad | Minor | Allow `full_rebuild_required` with explicit reason. |
| Large repo performance not fully optimized | Minor | Phase 87 reports scan budget; optimization can continue later. |

## 6. Final Gate

Implementation may start.

If implementation cannot produce changed-file evidence from real snapshots, the phase must return to planning instead of claiming accepted.
