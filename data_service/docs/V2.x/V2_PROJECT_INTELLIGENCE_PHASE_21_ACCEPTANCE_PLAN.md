# V2.4 Phase 21 Acceptance Plan: Code-Derived Model and Design-Code Drift

Date: 2026-06-02

## 1. Required Verification

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_code_architecture_inference.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_architecture_abstraction.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py -q
git diff --check -- backend/data_service/code_assets backend/tests docs/V2.x
```

## 2. Hard Assertions

- `code_derived_model.json` exists and contains roles, layers, boundaries, patterns, and summary.
- `design_code_drift.jsonl` exists after build.
- Build succeeds without design-side sources.
- If design-side model exists, drift findings compare design labels to code-derived roles/patterns.
- Every high-confidence drift finding has design evidence, code evidence, or both.
- Low-confidence findings are marked `needs_review`.
- HarnessOS real repo E2E builds a code-derived model.
- HarnessOS comparison runs when V2.3 design model exists.

## 3. False Acceptance Rejection

Reject Phase 21 if:

- drift is generated from LLM-only prose;
- code-derived model is empty but accepted;
- missing design model blocks code-derived model build;
- low-confidence drift is treated as a hard mismatch;
- unsupported static-analysis claims appear.
