# V2.43 Phase 120 Document Semantics v3 Acceptance Audit Report

## Verdict

Accepted.

Phase 120 is accepted for the current worktree scope after one failed real-repo E2E run was rejected and fixed. The initial run produced valid document semantic claims, but public payloads leaked absolute paths from source document text. That was treated as a false-acceptance blocker. The extractor now redacts absolute filesystem paths in claim labels while preserving repo-relative evidence paths.

## Implemented Scope

- Document Semantics v3 builder and reader.
- Markdown semantic extraction from headings, bullets, numbered lists, tables, acceptance gates, non-goals, stop conditions, and milestone-like statements.
- Drawio semantic extraction from pages, nodes, lanes, groups, legends, and edges.
- Document-only semantics boundary: generated claims and relations are not code facts.
- Drawio review boundary: drawio claims carry needs_review and cannot become code-derived facts.
- Public payload truncation for large claim/relation sets.
- Public redaction for absolute filesystem paths and raw HTML/script-like labels.
- HTTP, MCP, and CLI read/build access.

## Public Surfaces

- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_43/document-semantics`
- MCP:
  - `knowledge_code_architecture_document_semantics_v3_build`
  - `knowledge_code_architecture_document_semantics_v3`
- CLI:
  - `knowledge code architecture document-semantics-v3-build`
  - `knowledge code architecture document-semantics-v3`

## Artifacts

Artifacts are written under:

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_43/
```

Files:

- `document_semantic_claims.jsonl`
- `document_semantic_relations.jsonl`
- `document_semantic_summary.json`

## Test Evidence

Focused tests:

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_43_document_semantics.py
2 passed
```

Regression tests:

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_43_document_semantics.py \
  backend/tests/test_v2_42_relationship_chain_v3.py \
  backend/tests/test_v2_41_workflow_runtime_candidates.py \
  backend/tests/test_v2_40_language_provider_contract.py \
  backend/tests/test_public_surface_guard.py \
  backend/tests/test_session_ingest_query_build_contract_plan.py \
  backend/tests/test_data_service_mcp.py
23 passed, 25 skipped
```

Compile check:

```text
python3 -m py_compile backend/data_service/code_assets/architecture/document_semantics_v3.py
passed
```

MCP frontend contract parity:

```text
same: true
missing: []
extra: []
```

## Real Repo E2E

Real repositories:

- `data_service`
- `harnessOS`
- `codexPat`

Final E2E results:

| Repo | Status | Claims | Relations | Markdown Claims | Drawio Claims | Code Facts | Needs Review | Path Leak | Raw Script Leak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| data_service | accepted | 35503 | 28687 | 34625 | 878 | 0 | 878 | false | false |
| harnessOS | accepted | 25163 | 18201 | 23980 | 1183 | 0 | 1183 | false | false |
| codexPat | accepted | 27687 | 21803 | 27612 | 75 | 0 | 75 | false | false |

## PRD / Spec Review

Phase 120 requirements were met:

- Document semantics are extracted from real Markdown and drawio sources.
- Drawio semantics remain document claims and are not promoted to code facts.
- No generated claim is marked as a code fact.
- Large repositories produce persisted artifacts and public readback payloads.
- Public payloads avoid local absolute paths and raw script leakage.
- HTTP/MCP/CLI surfaces are available and included in parity checks.

## False-Acceptance Review

Rejected false-green cases:

- Markdown/drawio extraction from mock-only fixtures.
- Drawio labels treated as code facts.
- Diagram edges represented as runtime topology.
- Public payload leaking local absolute paths.
- Raw `<script>` text reaching public payload labels.
- Empty claim set marked as accepted.

The first real E2E run was blocked because document text contained local absolute paths. Acceptance was granted only after redaction was implemented and the same real-repo E2E passed.

## Open Findings

No fatal or major findings remain for Phase 120.

Minor follow-up:

- Later rendering phases should keep using persisted claim IDs and sanitized labels, rather than re-parsing raw document text in view renderers.
