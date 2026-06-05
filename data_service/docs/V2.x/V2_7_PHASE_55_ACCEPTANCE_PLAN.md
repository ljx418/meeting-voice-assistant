# V2.7 Phase 55 Acceptance Plan: Closure Acceptance

> Acceptance plan for V2.7 closure.
> Phase 55 does not add product features.
> Closure is rejected if accepted rows lack evidence.

Date: 2026-06-04

## 1. Required Tests

Run full V2.7 focused suites:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_registry.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_claim_extractor.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_quality.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_doc_code_alignment.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_architecture_reconstruction.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_governance_integration.py
/usr/bin/python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py
git diff --check -- .
```

If test filenames change during implementation, the closure audit must list exact replacement commands.

## 2. Real Repository Closure E2E

Run full pipeline against:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

Required artifact classes for both repos:

- document registry;
- document claims;
- document relations;
- quality findings;
- quality summary;
- doc-code alignment;
- doc-code drift;
- reconstructed model;
- HTML report;
- Mermaid diff;
- governance evidence where feedback/rules are exercised.

## 3. Closure Matrix Requirements

Each accepted row in `V2_7_FULL_PRD_COVERAGE_MATRIX.md` must cite:

- test command;
- test result;
- artifact path or artifact ref;
- artifact count;
- real repo result;
- acceptance audit report.

Each conditionally accepted row must cite:

- condition;
- residual risk;
- owner;
- follow-up phase or decision.

Each rejected/not implemented row must cite:

- reason;
- owner or explicit out-of-scope decision.

## 4. Rejection Rules

Reject closure if:

- any Phase 49-54 acceptance report is missing;
- any in-scope row remains pending;
- any accepted row lacks concrete evidence;
- skipped test is counted as pass;
- mock-only E2E is used;
- HTML/Mermaid view includes unpersisted facts;
- token-only alignment is accepted;
- copied Drawio is presented as code-derived architecture;
- original documents or prior V2 artifacts are silently mutated;
- closure report claims full human design intent recovery from code.

## 5. Closure Audit Output

Create:

```text
docs/V2.x/V2_7_CLOSURE_AUDIT_REPORT.md
```

The report must include:

- final PRD coverage summary;
- real repository artifact counts;
- test command table;
- public contract table;
- false-acceptance review;
- open findings;
- final decision.
