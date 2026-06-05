# V2.7 Phase 52 Development Plan: Doc-Code Alignment v2

> Phase 52 implementation plan.
> Phase 50 claim artifacts and Phase 51 quality artifacts are required input.
> This document is planning authority for Phase 52 only.

Date: 2026-06-04

## 1. Goal

Phase 52 compares document architecture claims against deterministic code facts and prior architecture artifacts.

It must produce evidence-backed alignment statuses. Token overlap alone can only produce `weak_match`.

## 2. Inputs

Required document inputs:

- `architecture_doc_claims.jsonl`
- `architecture_doc_relations.jsonl`
- `architecture_doc_quality_findings.jsonl`
- `architecture_doc_quality_summary.json`

Required code/project inputs:

- V2.0 snapshot files, public surfaces, symbols, and evidence trace;
- V2.1 graph and quality artifacts when present;
- V2.4 roles, layers, boundaries, patterns, and design-code drift;
- V2.6 scale profile, lightweight facts, taxonomy, review queue, and large-project views.

## 3. Outputs

Persist:

```text
workspace/assets/codebase/{codebase_id}/architecture/docs/
  architecture_doc_code_alignment.jsonl
  architecture_doc_code_drift_v2.jsonl
```

Every alignment row must include:

```text
schema_version
workspace_id
codebase_id
snapshot_id
alignment_id
claim_id
doc_id
claim_type
status
match_strategy
confidence
document_evidence
code_evidence
code_refs
quality_refs
needs_review
created_at
```

Every drift row must include:

```text
schema_version
workspace_id
codebase_id
snapshot_id
drift_id
drift_type
target_id
target_type
status
document_evidence
code_evidence
recommendation
severity
needs_review
created_at
```

## 4. Status and Strategy Policy

Allowed alignment `status`:

```text
matched
weak_match
designed_not_found_in_code
code_not_documented
doc_claim_without_evidence
stale_doc_claim
needs_review
```

Accepted `matched` requires:

- document evidence;
- code evidence;
- confidence >= 0.80;
- match strategy stronger than token overlap;
- no blocking `needs_review`;
- no unresolved target references.

Allowed `match_strategy`:

```text
exact_surface_id
exact_symbol_id
artifact_ref_match
capability_id_match
path_and_line_evidence_match
graph_node_id_match
v24_role_boundary_match
v26_taxonomy_match
manual_reviewed
token_overlap_only
```

Thresholds:

```text
accepted_match_confidence_min = 0.80
weak_match_confidence_range = 0.40 - 0.79
token_overlap_only -> weak_match only
```

## 5. Coverage Requirements

Phase 52 must emit both:

- claim-to-code coverage;
- code-to-document coverage.

Code facts without matching documentation must appear as `code_not_documented` coverage or drift rows, even when there are no major findings.

## 6. Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment
```

MCP:

```text
knowledge_code_architecture_doc_code_alignment_build
knowledge_code_architecture_doc_code_alignment
```

CLI:

```text
knowledge code architecture docs-alignment-build
knowledge code architecture docs-alignment
```

## 7. Development Steps

1. Add alignment and drift persistence helpers.
2. Add resolver for document claim IDs.
3. Add resolver for code references across V2.0/V2.1/V2.4/V2.6 artifacts.
4. Implement deterministic match strategies.
5. Implement token-overlap weak matching.
6. Implement code-to-document coverage generation.
7. Add service build/read methods and public interfaces.
8. Add focused tests and real-repo E2E.
9. Update coverage matrix and Phase 52 acceptance audit.

## 8. Boundaries

- Do not infer implementation from name similarity alone.
- Do not generate new code facts.
- Do not mutate V2.0-V2.6 artifacts.
- Do not hide weak matches.
- Do not mark planned documentation as implemented without code evidence.

## 9. Exit Criteria

Phase 52 can be accepted only when both real repositories produce alignment and drift artifacts, accepted rows have both document and code evidence, and token-only matches never produce accepted `matched` status.
