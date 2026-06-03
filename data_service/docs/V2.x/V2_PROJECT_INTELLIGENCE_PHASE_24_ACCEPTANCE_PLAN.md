# V2.4 Phase 24 Acceptance Plan: Architecture Quality Overlay

Date: 2026-06-02

## Required Verification

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_code_quality_governance.py backend/tests/test_v2_code_architecture_inference.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_architecture_abstraction.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py -q
git diff --check -- backend/data_service/code_assets backend/tests docs/V2.x
```

## Hard Assertions

- Feedback can be recorded for architecture role, layer, boundary, pattern, and drift finding.
- Approved rules generate quality plan overlays for architecture targets.
- Architecture read payloads show `applied_rules` and `governed_by` only at read time.
- Original architecture artifact hashes do not change after feedback/rule/review/plan generation.
- Public payloads do not leak absolute paths.

## False Acceptance Rejection

Reject if:

- rules mutate `code_roles.jsonl`, `pattern_candidates.jsonl`, or `design_code_drift.jsonl`;
- unsupported target types are silently accepted;
- overlay is claimed complete without approved rule application;
- architecture read output hides `needs_review`.
