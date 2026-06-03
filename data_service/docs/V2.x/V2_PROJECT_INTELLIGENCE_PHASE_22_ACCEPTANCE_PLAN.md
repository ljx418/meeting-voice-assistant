# V2.4 Phase 22 Acceptance Plan: Public Views and Interface Completion

Date: 2026-06-02

## 1. Required Verification

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_code_architecture_inference.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_architecture_abstraction.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py -q
git diff --check -- backend/data_service/code_assets backend/tests docs/V2.x
```

## 2. Hard Assertions

- `views/code_derived_architecture.mmd` exists and is non-empty.
- `views/code_derived_architecture.html` exists and is non-empty.
- Mermaid references persisted code-derived roles/layers/patterns.
- HTML renders summary, role counts, layer counts, pattern counts, and drift counts from persisted artifacts.
- HTTP/MCP/CLI can read the code-derived HTML view.
- Views do not contain absolute paths.

## 3. False Acceptance Rejection

Reject Phase 22 if:

- view contains facts not present in persisted artifacts;
- view is generated only in memory and not persisted;
- public output leaks absolute paths;
- quality overlay is claimed complete without target resolver support.
