# V2.7 Phase 50 Acceptance Plan: Architecture Claim Extractor

> Acceptance plan for Phase 50.
> Real repository data is mandatory.
> No mock-only result can pass.

Date: 2026-06-04

## 1. Required Tests

Focused tests must cover:

- Markdown heading extraction.
- Markdown bullet/list extraction.
- Markdown table row extraction.
- acceptance gate extraction.
- non-goal and forbidden claim extraction.
- Drawio node extraction.
- Drawio edge relation extraction.
- confidence ceiling enforcement.
- missing Phase 49 registry structured error.
- HTTP/MCP/CLI parity.

Required commands:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_claim_extractor.py
/usr/bin/python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_registry.py
git diff --check -- .
```

## 2. Real Repository E2E

Run against:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

Required `data_service` assertions:

- V2.7 target architecture components are extracted:
  - Document Asset Registry;
  - Architecture Claim Extractor;
  - Document Quality Evaluator;
  - Doc-Code Alignment v2;
  - Reconstructed Architecture Model;
  - Governance Overlay.
- Phase 49 accepted status can be represented as milestone or acceptance claim.
- non-goal statements about not recovering human design intent from code alone are extracted.

Required HarnessOS assertions:

- at least one V4 design/headless workflow claim is extracted when source docs exist;
- at least one V6 target architecture plane/layer claim is extracted when source docs exist;
- at least one Drawio document yields document-derived claims;
- missing or weak relation semantics remain `needs_review`.

## 3. Artifact Inspection

Inspect:

```text
architecture_doc_claims.jsonl
architecture_doc_relations.jsonl
```

Each artifact must be non-empty for both real repositories.

Every accepted claim row must have:

- `claim_id`;
- `doc_id`;
- `claim_type`;
- `repo_path`;
- `source_block_type`;
- evidence;
- confidence;
- `needs_review`.

Every relation row must have:

- `relation_id`;
- valid endpoint claim IDs;
- `doc_id`;
- relation evidence or `needs_review`.

## 4. Rejection Rules

Reject Phase 50 if:

- claim artifact is empty for either real repository;
- copied Drawio appears as code-derived architecture;
- LLM-only claim is accepted;
- any accepted claim lacks document evidence;
- token overlap is used as proof of implementation;
- non-goals or forbidden claims are dropped;
- Drawio-only claim exceeds confidence ceiling;
- public output leaks absolute paths;
- Phase 49 registry is silently rebuilt or mutated.

## 5. Acceptance Audit Output

On success, create:

```text
docs/V2.x/V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md
```

The report must include:

- implementation summary;
- test commands and results;
- real repository claim/relation counts;
- false-acceptance review;
- PRD/spec review;
- open findings;
- decision on whether Phase 51 can start planning.
