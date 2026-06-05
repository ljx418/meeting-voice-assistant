# V2.7 Phase 53 Reconstructed View Spec

Date: 2026-06-04

## Purpose

This specification makes Phase 53 implementation decision-complete. It defines the reconstructed model and rendered HTML/Mermaid view rules for target/current/diff architecture output.

Phase 53 must render only persisted artifacts. It must not introduce architecture facts during rendering.

## Inputs

Required:

- `architecture_docs.jsonl`
- `architecture_doc_claims.jsonl`
- `architecture_doc_relations.jsonl`
- `architecture_doc_quality_findings.jsonl`
- `architecture_doc_code_alignment.jsonl`
- `architecture_doc_code_drift_v2.jsonl`
- V2.4 architecture artifacts
- V2.6 large-project views and taxonomy

Missing Phase 52 artifacts must produce a structured error.

## Reconstructed Model

`architecture_reconstructed_model.json` must include:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `model_id`
- `target_nodes`
- `current_nodes`
- `diff_nodes`
- `edges`
- `summary`
- `source_artifact_refs`
- `artifact_refs`
- `created_at`

Every node must include:

- `node_id`
- `node_type`
- `label`
- `section`
- `source_kind`
- `source_refs`
- `confidence`
- `needs_review`

Allowed sections:

- `target_from_documents`
- `current_from_code`
- `gap_and_drift`

Allowed source kinds:

- `document_claim`
- `code_fact`
- `alignment`
- `quality_finding`
- `explicit_inference`

## HTML Report Rules

HTML must include visible sections:

- Target Architecture from Documents
- Current Architecture from Code
- Gaps and Drift
- Evidence and Unresolved Items

Rules:

- all text escaped
- links sanitized
- no raw script execution
- no absolute path output
- unresolved and low-confidence nodes visible
- copied drawio nodes labeled document-derived

## Mermaid Diff Rules

Rules:

- node IDs generated from model artifact IDs
- labels escaped
- no raw document text injection
- every rendered node resolves to model node
- every rendered edge resolves to model edge or relation source

## Ordering

Render order:

1. primary target authority claims
2. supporting target claims
3. current code facts
4. matched alignments
5. designed-not-found/code-not-documented drifts
6. unresolved/needs_review items

## Negative Fixtures

Tests must include:

- HTML injection in source document
- Mermaid syntax injection in label
- node absent from model
- copied drawio node mislabeled as code fact
- target/current mixed output
- absolute path leak

## Acceptance

Phase 53 passes only if both real repositories produce non-empty reconstructed model, HTML report, and Mermaid diff, and every rendered node resolves to a persisted model node.
