# V2.7 Phase 54 Acceptance Plan: Governance Integration

> Acceptance plan for Phase 54.
> Governance must be read-time overlay only.
> Original artifacts must remain unchanged.

Date: 2026-06-04

## 1. Required Tests

Focused tests must cover:

- feedback for `architecture_doc_claim`;
- feedback for `architecture_doc_code_alignment`;
- feedback rejection for missing target ID;
- rule generation from document quality finding;
- rule approval;
- rule rejection;
- rule revoke;
- correction plan generation;
- read-time `applied_rules`;
- artifact hash unchanged before/after rule approval.

Required commands:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_governance_integration.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_architecture_reconstruction.py
/usr/bin/python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py
git diff --check -- .
```

## 2. Real Repository E2E

Run against:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

Required assertions:

- record feedback for one document claim;
- record feedback for one doc-code alignment mismatch;
- build correction rule;
- approve rule;
- governed read output includes `applied_rules`;
- revoke rule;
- governed read output no longer applies revoked rule;
- original V2.7 artifacts have unchanged hashes.

## 3. Artifact Inspection

Inspect:

- existing quality feedback artifacts;
- correction rules;
- correction plan;
- V2.7 source artifact hashes.

Assertions:

- V2.7 target IDs resolve;
- applied rules reference valid rule IDs;
- correction plan references valid V2.7 target IDs;
- no original document, claim, alignment, or reconstructed model artifact is rewritten by governance.

## 4. Rejection Rules

Reject Phase 54 if:

- approved rule mutates source artifact;
- revoked rule still applies;
- missing target ID is accepted;
- governed read hides `applied_rules`;
- correction plan references unresolved targets;
- feedback/rule output leaks absolute paths;
- quality summary excludes V2.7 target counts.

## 5. Acceptance Audit Output

On success, create:

```text
docs/V2.x/V2_7_PHASE_54_ACCEPTANCE_AUDIT_REPORT.md
```

The report must include governance target counts, approve/revoke evidence, artifact hash evidence, false-acceptance review, and a decision on whether Phase 55 can start planning.
