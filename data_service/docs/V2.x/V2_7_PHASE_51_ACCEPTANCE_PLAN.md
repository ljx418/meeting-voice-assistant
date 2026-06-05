# V2.7 Phase 51 Acceptance Plan: Document Quality Evaluation

> Acceptance plan for Phase 51.
> Real repository data is mandatory.
> Quality scoring cannot hide high-severity findings.

Date: 2026-06-04

## 1. Required Tests

Focused tests must cover:

- missing evidence finding;
- missing acceptance gate finding;
- stale document finding;
- status conflict finding;
- scope conflict finding;
- broken relation finding;
- major/fatal finding prevents `high_quality`;
- missing Phase 50 claim artifacts returns structured error;
- HTTP/MCP/CLI parity.

Required commands:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_quality.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_claim_extractor.py
/usr/bin/python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py
git diff --check -- .
```

## 2. Real Repository E2E

Run against:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

Required `data_service` assertions:

- V2.7 planning docs are not treated as implementation closure evidence.
- Phase 49 acceptance report is recognized as acceptance evidence for document registry only.
- any remaining Phase 50-55 planned claims are not marked implemented by quality evaluation.

Required HarnessOS assertions:

- stale or historical docs are not promoted to current target quality without review;
- target architecture docs without implementation evidence produce `needs_review` or quality findings;
- accepted/pending conflicts produce findings when present.

## 3. Artifact Inspection

Inspect:

```text
architecture_doc_quality_findings.jsonl
architecture_doc_quality_summary.json
```

Assertions:

- summary exists for both repos;
- severity counts match finding rows;
- every finding has target IDs and evidence or `needs_review`;
- `overall_status` follows severity rules.

## 4. Rejection Rules

Reject Phase 51 if:

- quality artifact is empty because checks were skipped;
- major/fatal finding coexists with `overall_status=high_quality`;
- findings have no target IDs;
- findings have no evidence or review reason;
- planning-ready is treated as implemented;
- quality evaluator mutates source docs or claim artifacts.

## 5. Acceptance Audit Output

On success, create:

```text
docs/V2.x/V2_7_PHASE_51_ACCEPTANCE_AUDIT_REPORT.md
```

The report must include real repository finding counts, severity counts, false-acceptance review, and a decision on whether Phase 52 can start planning.
