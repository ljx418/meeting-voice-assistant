# V2.7 Phase 52 Acceptance Audit Report

Date: 2026-06-04

## 1. Status

Status: accepted.

Phase 52 Doc-Code Alignment v2 is accepted for the scoped V2.7 documentation-code architecture governance baseline.

This is not V2.7 closure. Phase 53-55 remain pending.

## 2. Scope

Phase 52 compares Phase 50 architecture document claims and Phase 51 quality findings against persisted code facts and architecture artifacts.

Inputs:

- `architecture_doc_claims.jsonl`
- `architecture_doc_relations.jsonl`
- `architecture_doc_quality_findings.jsonl`
- `architecture_doc_quality_summary.json`
- snapshot files, public surfaces, symbols
- V2.4 code roles/layers/boundaries/patterns when available
- V2.6 taxonomy when available

Outputs:

- `architecture_doc_code_alignment.jsonl`
- `architecture_doc_code_drift_v2.jsonl`

Phase 52 does not reconstruct target/current architecture views, mutate source documents, rewrite V2.0-V2.6 artifacts, or promote token-only similarity to accepted implementation evidence.

## 3. Implementation Summary

Implemented document-code alignment in:

- `backend/data_service/code_assets/architecture/doc_code_alignment.py`
- `backend/data_service/code_assets/architecture/service.py`
- `backend/data_service/code_assets/architecture/persistence.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/app/api/v1/code_assets_architecture.py`
- `backend/data_service/mcp_code_architecture_tools.py`
- `backend/data_service/cli_code_architecture.py`

Focused coverage was added in:

- `backend/tests/test_v2_7_doc_code_alignment.py`

The implementation emits deterministic alignment rows, drift rows, status counts, match strategy counts, confidence threshold metadata, and `token_overlap_only_accepted=false`.

## 4. Match Strategy Coverage

Focused tests cover:

- `exact_surface_id`
- `exact_symbol_id`
- `capability_id_match`
- `path_and_line_evidence_match`
- `artifact_ref_match`
- `v24_role_boundary_match`
- `v26_taxonomy_match`
- `token_overlap_only`
- `doc_claim_without_evidence`
- `stale_doc_claim`
- `designed_not_found_in_code`
- `code_not_documented`

Accepted `matched` rows require all:

- document evidence exists;
- code evidence exists;
- confidence is at least `0.80`;
- match strategy is stronger than `token_overlap_only`;
- no blocking major/fatal document quality state.

`token_overlap_only` rows are always `weak_match`.

## 5. Real Repository E2E Evidence

Real E2E used a temporary managed workspace under `/private/tmp`.

| Repository | Documents | Claims | Quality findings | Alignments | Drift rows | Matched | Weak matches | Token-only rows | Absolute repo path leaked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `data_service` | 345 | 20627 | 988 | 20827 | 13478 | 7349 | 725 | 719 | no |
| `harnessOS` | 644 | 18435 | 1629 | 18635 | 13989 | 4646 | 812 | 808 | no |

Status counts:

| Repository | Status counts |
| --- | --- |
| `data_service` | `code_not_documented=200`, `designed_not_found_in_code=10194`, `matched=7349`, `needs_review=2359`, `weak_match=725` |
| `harnessOS` | `code_not_documented=200`, `designed_not_found_in_code=10531`, `matched=4646`, `needs_review=2446`, `weak_match=812` |

Match strategy counts:

| Repository | Match strategy counts |
| --- | --- |
| `data_service` | `artifact_ref_match=558`, `capability_id_match=4811`, `code_coverage=200`, `exact_surface_id=3`, `no_code_evidence=10194`, `path_and_line_evidence_match=770`, `token_overlap_only=719`, `v24_role_boundary_match=3535`, `v26_taxonomy_match=37` |
| `harnessOS` | `artifact_ref_match=534`, `capability_id_match=1217`, `code_coverage=200`, `no_code_evidence=10531`, `path_and_line_evidence_match=799`, `token_overlap_only=808`, `v24_role_boundary_match=4521`, `v26_taxonomy_match=25` |

Both real repositories built V2.4 code architecture and V2.6 taxonomy artifacts before alignment.

## 6. Test Evidence

Passed:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_doc_code_alignment.py
/usr/bin/python3 -m pytest backend/tests/test_v2_7_doc_code_alignment.py backend/tests/test_v2_7_document_quality.py backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py
git diff --check -- backend/data_service/code_assets/artifacts.py backend/data_service/code_assets/architecture/persistence.py backend/data_service/code_assets/architecture/doc_code_alignment.py backend/data_service/code_assets/architecture/service.py backend/app/api/v1/code_assets_architecture.py backend/data_service/mcp_code_architecture_tools.py backend/data_service/cli_code_architecture.py backend/tests/test_v2_7_doc_code_alignment.py
```

Results:

- Phase 52 focused test: 3 passed.
- Phase 52 plus quality/public/MCP regression: 18 passed, 25 skipped.
- Diff check: passed.

The skipped MCP cases are pre-existing optional provider/runtime skips and are not Phase 52 hard failures.

## 7. Public Contract

Phase 52 is available through:

- HTTP `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment/build`
- HTTP `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment`
- MCP `knowledge_code_architecture_doc_code_alignment_build`
- MCP `knowledge_code_architecture_doc_code_alignment`
- CLI `knowledge code architecture docs-alignment-build`
- CLI `knowledge code architecture docs-alignment`

Missing Phase 51 quality artifacts return structured `ARCHITECTURE_DOC_QUALITY_NOT_BUILT`.

## 8. False-Acceptance Review

Pass.

The alignment implementation rejects token-only accepted matches. Real E2E produced token-only rows, but they remained `weak_match` and did not contribute to accepted `matched` rows.

The implementation does not infer complete human design intent from code. It keeps `designed_not_found_in_code`, `code_not_documented`, `weak_match`, and `needs_review` visible.

The implementation does not claim target/current/diff architecture reconstruction. That remains Phase 53.

## 9. PRD Spec Review

Pass.

Phase 52 satisfies V2.7 PRD story `US-027-004` for document-code comparison, drift reporting, and token-only false-green rejection.

V2.7 remains incomplete until Phase 55 closure passes.

## 10. Drift And False-Green Risk

Risk: Medium.

Reason: accepted matches are evidence-backed and token-only rows are blocked from accepted status, but Phase 53 reconstruction can still create false-green risk if rendered views hide weak/missing evidence.

No High risk remains for Phase 52.

## 11. Decision

Phase 52 accepted.

Phase 53 may enter implementation planning/execution after its development plan, acceptance plan, reconstructed view spec, and pre-implementation audit are rechecked against this Phase 52 evidence and have no open fatal or major findings.
