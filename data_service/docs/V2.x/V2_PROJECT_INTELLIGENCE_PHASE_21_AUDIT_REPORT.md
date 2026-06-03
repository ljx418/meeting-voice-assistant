# V2.4 Phase 21 Audit Report: Code-Derived Model and Design-Code Drift

> Pre-development audit for Phase 21.

Date: 2026-06-02

## 1. Reviewed Documents

- `docs/V2.x/V2_4_TARGET_PRD.md`
- `docs/V2.x/V2_4_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_20_AUDIT_REPORT.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_21_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_21_ACCEPTANCE_PLAN.md`

## 2. Pre-Development Audit Conclusion

Conclusion: pass. Phase 21 may enter implementation.

Open fatal findings: none.

Open major findings: none.

## 3. Permission

Implementation may add aggregate model and drift artifacts. It must not add views, quality overlays, or unsupported static-analysis semantics in Phase 21.

## 4. Post-Implementation Audit Placeholder

## 4. Post-Implementation Audit

### Changed Files

Phase 21 implementation changed or added:

- `backend/data_service/code_assets/artifacts.py`
- `backend/data_service/code_assets/architecture/code_model_builder.py`
- `backend/data_service/code_assets/architecture/drift.py`
- `backend/data_service/code_assets/architecture/persistence.py`
- `backend/data_service/code_assets/architecture/service.py`
- `backend/tests/test_v2_code_architecture_inference.py`

### Implemented Scope

Implemented:

- `code_derived_model.json`.
- `design_code_drift.jsonl`.
- aggregate code-derived architecture model.
- deterministic token-overlap design-code drift analyzer.
- design-side model optionality: code-derived model builds even without design sources.
- focused tests for aggregate model and drift artifact generation.

Not implemented:

- code-derived HTML/Mermaid views.
- quality overlay.
- full call graph, data flow, control flow, runtime dispatch, or type inference.

### Commands Run

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_code_architecture_inference.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_architecture_abstraction.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py -q
PYTHONPATH=backend python3 - <<'PY'
# real data_service and HarnessOS E2E
PY
git diff --check -- backend/data_service/code_assets backend/app/api/v1/code_assets_architecture.py backend/data_service/mcp_code_architecture_tools.py backend/data_service/cli_code_architecture.py backend/tests/test_v2_code_architecture_inference.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py frontend/src/data/mcpContract.ts docs/V2.x
```

### Test Results

Focused tests:

```text
backend/tests/test_v2_code_architecture_inference.py
2 passed
```

Regression tests:

```text
backend/tests/test_v2_architecture_abstraction.py
backend/tests/test_data_service_mcp.py
backend/tests/test_public_surface_guard.py
39 passed, 103 warnings
```

The warnings are existing `datetime.utcnow()` deprecation warnings from LLMWiki modules.

Whitespace check:

```text
git diff --check: pass
```

### Real Repository E2E

`data_service`:

```json
{
  "workspace_id": "data_service_v24_phase21",
  "codebase_id": "codebase_data_service_v24_phase21",
  "snapshot_id": "snap_8a8a93345d142447119a",
  "design_built": true,
  "role_count": 952,
  "layer_count": 8,
  "boundary_count": 38,
  "pattern_count": 11,
  "drift_count": 859,
  "high_confidence_without_evidence": 0,
  "absolute_path_leak": false
}
```

HarnessOS:

```json
{
  "workspace_id": "harnessos_v24_phase21",
  "codebase_id": "codebase_harnessos_v24_phase21",
  "snapshot_id": "snap_5c94c3fac97ac66c5e8f",
  "design_built": true,
  "role_count": 2018,
  "layer_count": 9,
  "boundary_count": 296,
  "pattern_count": 10,
  "drift_count": 1572,
  "high_confidence_without_evidence": 0,
  "absolute_path_leak": false
}
```

Generated artifacts:

```text
/private/tmp/data_service_v24_phase21/assets/codebase/codebase_data_service_v24_phase21/architecture/code_derived_model.json
/private/tmp/data_service_v24_phase21/assets/codebase/codebase_data_service_v24_phase21/architecture/design_code_drift.jsonl
/private/tmp/harnessos_v24_phase21/assets/codebase/codebase_harnessos_v24_phase21/architecture/code_derived_model.json
/private/tmp/harnessos_v24_phase21/assets/codebase/codebase_harnessos_v24_phase21/architecture/design_code_drift.jsonl
```

### PRD and Specification Review

Phase 21 remains aligned with V2.4:

- It aggregates roles, layers, boundaries, and patterns into a code-derived architecture model.
- It compares design-side and code-derived models when design sources exist.
- It does not block code-derived model build when design sources are absent.
- It does not implement Phase 22 views or quality overlay.
- It does not claim unsupported static-analysis semantics.

### False-Acceptance Review

| Risk | Result |
| --- | --- |
| Code-derived model empty but accepted | pass: real E2E validates non-empty role/layer/boundary/pattern counts |
| Drift generated from LLM-only prose | pass: drift uses deterministic token overlap and existing evidence |
| Missing design blocks code model | pass: service reads design nodes only if available |
| High-confidence findings lack evidence | pass: E2E high-confidence-without-evidence remains 0 for architecture artifacts |
| HarnessOS not tested | pass: HarnessOS real E2E completed |
| Unsupported static-analysis claims | pass: not implemented |

### Final Phase 21 Decision

Decision: accepted.

Open fatal findings: none.

Open major findings: none.

Phase 22 may proceed to pre-development planning, but implementation must not start until Phase 22 development plan, acceptance plan, and audit report are created and cleared.
