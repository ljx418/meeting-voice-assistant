# V2.7 Phase 52 Alignment Strategy Spec

Date: 2026-06-04

## Purpose

This specification makes Phase 52 implementation decision-complete. It defines deterministic match strategies, evidence requirements, confidence rules, and rejection rules for document-code alignment.

Phase 52 must compare document architecture claims with existing persisted code facts. It must not create new code facts or infer implementation from names alone.

## Inputs

Document inputs:

- `architecture_doc_claims.jsonl`
- `architecture_doc_relations.jsonl`
- `architecture_doc_quality_findings.jsonl`
- `architecture_doc_quality_summary.json`

Code/project inputs:

- V2.0 snapshot, public surfaces, symbols, evidence trace
- V2.1 graph and quality artifacts where present
- V2.4 roles, layers, boundaries, patterns, drift
- V2.6 scale profile, lightweight facts, taxonomy, review queue, large-project views

## Alignment Status Rules

Allowed statuses:

- `matched`
- `weak_match`
- `designed_not_found_in_code`
- `code_not_documented`
- `doc_claim_without_evidence`
- `stale_doc_claim`
- `needs_review`

`matched` requires all:

- document evidence exists
- code evidence exists
- confidence >= 0.80
- match strategy is stronger than token overlap
- target refs resolve
- row has no blocking `needs_review`

`token_overlap_only` is always `weak_match`.

## Match Strategy Rules

| strategy | Required input | Accepted evidence | Confidence ceiling |
| --- | --- | --- | --- |
| `exact_surface_id` | public surface/interface claim | public surface artifact ref | 0.95 |
| `exact_symbol_id` | symbol/component claim | symbol artifact ref | 0.95 |
| `artifact_ref_match` | document names explicit artifact | persisted artifact path/ref | 0.90 |
| `capability_id_match` | claim has normalized capability ID | matching capability/code asset ID | 0.90 |
| `path_and_line_evidence_match` | claim references repo-relative file/line | matching snapshot file and line evidence | 0.88 |
| `graph_node_id_match` | claim maps to V2.1 graph node | graph node artifact ref | 0.88 |
| `v24_role_boundary_match` | layer/boundary claim | V2.4 role/boundary artifact | 0.85 |
| `v26_taxonomy_match` | taxonomy/category claim | V2.6 taxonomy fact | 0.82 |
| `manual_reviewed` | explicit reviewed mapping artifact | reviewer/evidence ref | 0.90 |
| `token_overlap_only` | normalized label similarity | token evidence only | weak only, max 0.79 |

## Drift Rules

Emit drift rows for:

- designed claim not found in code
- code fact not documented
- accepted document claim without code evidence
- stale document claim
- weak match requiring review
- current code architecture missing from target docs

Each drift row must include document evidence, code evidence when applicable, recommendation, severity, and `needs_review`.

## Code-to-document Coverage

Phase 52 must emit code-to-document coverage. Code facts without matching documentation must remain visible as `code_not_documented` or drift rows.

## Negative Fixtures

Tests must include:

- token-only similarity becoming `weak_match`
- missing document evidence rejected
- missing code evidence rejected
- low confidence excluded from `matched`
- copied drawio label rejected as code evidence
- stale doc claim producing `stale_doc_claim`
- code-only public surface producing `code_not_documented`

## Acceptance

Phase 52 passes only if both real repositories produce non-empty alignment and drift artifacts, every accepted `matched` row has document and code evidence, and weak matches remain visible.
