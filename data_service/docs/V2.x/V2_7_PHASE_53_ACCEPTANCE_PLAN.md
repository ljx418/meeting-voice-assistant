# V2.7 Phase 53 Acceptance Plan: Architecture Reconstruction Report

> Acceptance plan for Phase 53.
> Generated views must be derived from persisted artifacts only.
> Rendering safety is mandatory.

Date: 2026-06-04

## 1. Required Tests

Focused tests must cover:

- target/current/diff section generation;
- model node source reference resolution;
- HTML escaping of document text;
- link sanitization;
- Mermaid node ID generation from artifact IDs;
- Mermaid label escaping;
- no unpersisted node rendered;
- missing Phase 52 alignment structured error;
- HTTP/MCP/CLI parity.

Required commands:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_architecture_reconstruction.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_doc_code_alignment.py
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

- HTML report exists and is non-empty for both repos.
- Mermaid diff exists and is non-empty for both repos.
- HTML contains visible sections:
  - Target Architecture from Documents;
  - Current Architecture from Code;
  - Gaps and Drift.
- unresolved and low-confidence findings are visible.
- no absolute paths are exposed.

HarnessOS-specific assertions:

- V4/V6 target claims appear in target section only when extracted from documents;
- current section uses code facts only;
- copied Drawio nodes are labeled document-derived, not code-inferred.

## 3. Artifact Inspection

Inspect:

```text
architecture_reconstructed_model.json
views/document_code_architecture_report.html
views/document_code_architecture_diff.mmd
```

Assertions:

- all rendered node IDs exist in `architecture_reconstructed_model.json`;
- all model source refs resolve;
- every diff node references alignment, drift, or quality finding evidence;
- HTML and Mermaid contain no raw local absolute paths.

## 4. Rejection Rules

Reject Phase 53 if:

- generated view includes a node absent from model artifact;
- copied Drawio is presented as code architecture;
- target/current/diff sections are not separated;
- HTML allows raw script injection;
- Mermaid labels can inject syntax;
- unresolved items are hidden;
- public output leaks absolute paths.

## 5. Acceptance Audit Output

On success, create:

```text
docs/V2.x/V2_7_PHASE_53_ACCEPTANCE_AUDIT_REPORT.md
```

The report must include model/view counts, safety test results, real repository screenshots or content summaries, false-acceptance review, and a decision on whether Phase 54 can start planning.
