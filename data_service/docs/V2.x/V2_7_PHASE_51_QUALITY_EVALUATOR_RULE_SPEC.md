# V2.7 Phase 51 Quality Evaluator Rule Spec

Date: 2026-06-04

## Purpose

This specification makes Phase 51 implementation decision-complete. It defines deterministic document-quality rules for `architecture_doc_quality_findings.jsonl` and `architecture_doc_quality_summary.json`.

Phase 51 may only evaluate document quality. It must not perform doc-code alignment, architecture reconstruction, governance rule application, source document rewriting, or prior artifact mutation.

## Inputs

Required artifacts:

- `architecture_docs.jsonl`
- `architecture_doc_sources.jsonl`
- `architecture_doc_claims.jsonl`
- `architecture_doc_relations.jsonl`

Required source context:

- original documents referenced by `repo_path`
- Phase 49 and Phase 50 acceptance reports
- real `data_service` and HarnessOS repositories

Missing Phase 50 inputs must return a structured `missing_required_artifact` error and must not produce an accepted empty quality result.

## Finding Rules

| finding_type | Trigger | Default severity | Required evidence |
| --- | --- | --- | --- |
| `missing_acceptance_gate` | implementation/development claim lacks matching acceptance or exit gate claim in same phase/scope | major | source claim and searched phase/scope |
| `missing_evidence` | accepted/implemented claim lacks acceptance report, artifact ref, test ref, or source evidence | major | claim evidence and missing evidence type |
| `stale_document` | historical/supporting doc is used as target/current authority without supersession evidence | major | document metadata and authority fields |
| `scope_conflict` | document scope claims contradict phase, non-goal, or out-of-scope claim | major | both conflicting claims |
| `status_conflict` | same capability is both accepted/passed and planned/pending in same active scope | major | both status claims |
| `unsupported_claim` | claim is strong/current but confidence is low, evidence is weak, or source type is drawio-only/inferred | major for primary authority, minor otherwise | claim confidence and source block type |
| `ambiguous_ownership` | plan/action requires owner or phase but no phase/doc authority can be resolved | minor | claim or document evidence |
| `missing_current_target_split` | reconstructed/architecture doc mixes target and current without explicit labels | major | document section or claims |
| `doc_code_mismatch` | Phase 51 may only create placeholder quality risk when document itself asserts implementation evidence but evidence is absent | minor | document claim and missing reference |
| `overbroad_architecture_claim` | document claims complete/full/exact recovery beyond PRD scope | major | claim and PRD non-goal reference |
| `low_confidence_claim` | accepted-like claim has confidence below acceptance ceiling or `needs_review` | minor | claim confidence |
| `broken_document_relation` | relation endpoint claim IDs do not resolve | major | relation ID and endpoint IDs |

## Severity Summary Rules

`overall_status`:

- any fatal finding -> `blocked`
- any major finding -> `needs_review`
- only minor/info findings -> `review_recommended`
- no findings -> `high_quality`

No summary may report `high_quality` when any major or fatal finding exists.

## Output Row Requirements

Every finding must include:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `finding_id`
- `finding_type`
- `severity`
- `target_type`
- `target_id`
- `doc_id`
- `claim_id` when applicable
- `title`
- `recommendation`
- `evidence` or `needs_review`
- `confidence`
- `created_at`

## Negative Fixtures

Tests must include fixtures for:

- accepted wording without evidence
- planned phase marked implemented
- historical doc promoted to current authority
- target/current mixed in one section
- missing acceptance gate
- broken relation endpoint
- major finding hidden by `high_quality`

## Acceptance

Phase 51 passes only if both real repositories produce quality summary artifacts and findings preserve all major/fatal risks in public output without absolute path or secret leakage.
