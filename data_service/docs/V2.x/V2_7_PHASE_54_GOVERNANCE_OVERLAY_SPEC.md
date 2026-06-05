# V2.7 Phase 54 Governance Overlay Spec

Date: 2026-06-04

## Purpose

This specification makes Phase 54 implementation decision-complete. It defines how V2.7 document-code architecture findings integrate with the existing quality governance workflow.

Approved rules must apply as read-time overlays only. Source artifacts must not be rewritten.

## Target Types

Supported V2.7 governance targets:

- `architecture_doc`
- `architecture_doc_claim`
- `architecture_doc_relation`
- `architecture_doc_quality_finding`
- `architecture_doc_code_alignment`
- `architecture_reconstructed_node`
- `architecture_reconstructed_edge`

Missing target IDs must be rejected.

## Rule Types

Supported rule types:

- `missing_evidence`
- `stale_document`
- `wrong_surface_mapping`
- `wrong_capability_mapping`
- `doc_code_mismatch`
- `low_confidence_inference`
- `overbroad_architecture_claim`
- `missing_acceptance_gate`
- `wrong_target_current_split`
- `unsafe_rendered_output`
- `broken_cross_link`

## Feedback Payload

Feedback must include:

- `target_type`
- `target_id`
- `finding_type`
- `comment`
- `evidence_ref`
- `reviewer`
- `created_at`

Public feedback output must use repo-relative artifact refs only.

## Rule Overlay Behavior

Approved rules may:

- annotate a target as corrected
- lower confidence
- add warning/recommendation
- mark `needs_review`
- suppress accepted status in read output only

Approved rules must not:

- rewrite source documents
- rewrite claims
- rewrite alignments
- rewrite reconstructed model
- mutate V2.0-V2.6 artifacts
- delete persisted findings

Revoked rules must stop applying to governed read output.

## Governed Read Payload

Governed reads must include:

- `applied_rules`
- `governance_status`
- `needs_review`
- original artifact reference
- overlay decision

## Hash Gate

Phase 54 must record artifact hashes before and after governance operations for:

- original documents
- document claims
- quality findings
- alignments
- reconstructed model
- prior V2 artifacts

Hashes must remain unchanged unless an owning rebuild phase explicitly runs.

## Negative Fixtures

Tests must include:

- feedback against missing target rejected
- approved rule mutates artifact rejected
- revoked rule still applied rejected
- correction plan references unresolved target rejected
- applied_rules hidden rejected
- absolute path leak rejected

## Acceptance

Phase 54 passes only if feedback/rule/plan works for V2.7 targets, approved rules appear as read-time overlays, revoked rules stop applying, and original artifact hashes remain unchanged.
