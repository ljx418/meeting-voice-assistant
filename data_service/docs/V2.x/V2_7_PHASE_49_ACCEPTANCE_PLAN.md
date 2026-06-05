# V2.7 Phase 49 Acceptance Plan: Document Asset Registry

> Phase-specific acceptance plan.
> Uses real `data_service` and HarnessOS inputs.

Date: 2026-06-04

## Required Checks

Focused tests:

```text
python -m pytest backend/tests/test_v2_7_document_registry.py
python -m pytest backend/tests/test_public_surface_guard.py
python -m pytest backend/tests/test_data_service_mcp.py
python -m pytest backend/tests/test_v2_6_architecture_scale_profile.py
git diff --check -- .
```

Real E2E:

- build a codebase asset for `/Users/Zhuanz/Desktop/workspace/data_service`;
- build a codebase asset for `/Users/Zhuanz/Desktop/workspace/harnessOS` if present;
- create snapshots;
- build document registry;
- inspect artifacts on disk;
- confirm no absolute path leak.

## Golden Assertions

For `data_service`:

- `V2_7_TARGET_PRD.md` is `doc_type=prd`, `authority_role=target`, `authority_level=primary`.
- `V2_7_TARGET_ARCHITECTURE.md` is `doc_type=target_architecture`, `authority_role=target`, `authority_level=primary`.
- `V2_7_DOCUMENT_AUDIT_REPORT.md` is `doc_type=audit_report`, `authority_role=audit_status`.
- `V2_6_*` docs are not current V2.7 target authority.

For HarnessOS:

- V4 or V6 design docs are discovered if repository path exists.
- drawio docs are discovered if present.
- path case is recorded.

## Rejection Conditions

Reject Phase 49 if:

- registry is empty;
- filename-only historical docs are promoted to current target authority;
- absolute paths appear in public JSON;
- source registry changes during registry build;
- repeated run changes stable IDs for unchanged snapshot;
- HarnessOS E2E is claimed accepted when path is missing.
