# V2.7 Phase 52 Acceptance Plan: Doc-Code Alignment v2

> Acceptance plan for Phase 52.
> Alignment is the highest false-green risk in V2.7.
> Accepted matches require document evidence and code evidence.

Date: 2026-06-04

## 1. Required Tests

Focused tests must cover:

- exact surface ID match;
- exact symbol ID match;
- capability ID match;
- V2.4 role/boundary match;
- V2.6 taxonomy match;
- token-overlap-only weak match;
- designed-not-found-in-code status;
- code-not-documented coverage;
- missing code evidence rejection;
- missing document evidence rejection;
- HTTP/MCP/CLI parity.

Required commands:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_doc_code_alignment.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_quality.py
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

- Phase 49 implemented document registry claims map to public surfaces or code artifacts where available.
- Phase 50-55 target claims remain planned or designed-not-found until code exists.
- code-only surfaces appear in code-to-document coverage when no document claim exists.

Required HarnessOS assertions:

- target architecture planes map only when code evidence exists;
- V4/V6 documentation claims without implementation evidence remain `needs_review` or `designed_not_found_in_code`;
- copied drawio labels do not become accepted code evidence.

## 3. Artifact Inspection

Inspect:

```text
architecture_doc_code_alignment.jsonl
architecture_doc_code_drift_v2.jsonl
```

Assertions:

- artifacts are non-empty for both repos;
- every `matched` row has document and code evidence;
- every `weak_match` row remains visible;
- status counts are present;
- code-to-document coverage is present.

## 4. Rejection Rules

Reject Phase 52 if:

- token-only match is accepted;
- low-confidence match is counted as implemented;
- accepted row lacks code evidence;
- accepted row lacks document evidence;
- weak matches are hidden;
- code-not-documented coverage is omitted;
- prior drift artifacts are overwritten;
- public output leaks absolute paths.

## 5. Acceptance Audit Output

On success, create:

```text
docs/V2.x/V2_7_PHASE_52_ACCEPTANCE_AUDIT_REPORT.md
```

The report must include strategy counts, status counts, accepted/weak/missing examples, real repository results, and a decision on whether Phase 53 can start planning.
