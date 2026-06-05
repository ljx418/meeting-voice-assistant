# V2.7 Phase 51 Development Plan: Document Quality Evaluation

> Phase 51 implementation plan.
> Phase 50 claim artifacts are required input.
> This document is planning authority for Phase 51 only.

Date: 2026-06-04

## 1. Goal

Phase 51 evaluates architecture documentation quality using Phase 49 document registry and Phase 50 claims/relations.

It must identify documentation quality risks without rewriting source documents or treating plans as implementation evidence.

## 2. Inputs

Required inputs:

- `architecture_docs.jsonl`
- `architecture_doc_sources.jsonl`
- `architecture_doc_claims.jsonl`
- `architecture_doc_relations.jsonl`
- original repository documents referenced by `repo_path`

Real repositories:

- `/Users/Zhuanz/Desktop/workspace/data_service`
- `/Users/Zhuanz/Desktop/workspace/harnessOS`

## 3. Outputs

Persist:

```text
workspace/assets/codebase/{codebase_id}/architecture/docs/
  architecture_doc_quality_findings.jsonl
  architecture_doc_quality_summary.json
```

Every finding must include:

```text
schema_version
workspace_id
codebase_id
snapshot_id
finding_id
finding_type
severity
target_type
target_id
doc_id
claim_id
title
recommendation
evidence
confidence
needs_review
created_at
```

The summary must include:

```text
schema_version
workspace_id
codebase_id
snapshot_id
document_count
claim_count
relation_count
finding_count
severity_counts
finding_type_counts
needs_review_count
overall_status
artifact_refs
created_at
```

## 4. Finding Taxonomy

Supported `finding_type`:

```text
missing_acceptance_gate
missing_evidence
stale_document
scope_conflict
status_conflict
unsupported_claim
ambiguous_ownership
missing_current_target_split
doc_code_mismatch
overbroad_architecture_claim
low_confidence_claim
broken_document_relation
```

Supported `severity`:

```text
info
minor
major
fatal
```

Severity defaults:

- missing evidence for primary target claim: `major`;
- stale historical document used as target authority: `major`;
- accepted/implemented wording without acceptance evidence: `major`;
- broken relation endpoint: `major`;
- low-confidence drawio-only claim: `minor`;
- ambiguous ownership or scope: `minor`;
- injection or path leak risk in document text: `fatal` only if it appears in generated public output.

`overall_status` rules:

- any `fatal` finding -> `blocked`;
- any `major` finding -> `needs_review`;
- only minor/info findings -> `review_recommended`;
- no findings -> `high_quality`.

## 5. Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality
```

MCP:

```text
knowledge_code_architecture_doc_quality_build
knowledge_code_architecture_doc_quality
```

CLI:

```text
knowledge code architecture docs-quality-build
knowledge code architecture docs-quality
```

## 6. Development Steps

1. Add quality finding persistence and artifact refs.
2. Implement target resolver for document, claim, and relation IDs.
3. Implement completeness checks for acceptance gates and evidence.
4. Implement consistency checks for status, scope, and current/target split.
5. Implement freshness checks using `stale_hint`, phase, and authority.
6. Implement summary aggregation and `overall_status` rule.
7. Add HTTP/MCP/CLI build/read interfaces.
8. Add focused tests and real-repo E2E.
9. Update coverage matrix and Phase 51 acceptance audit.

## 7. Boundaries

- Do not perform doc-code alignment; Phase 51 can flag missing code evidence only as a document quality risk.
- Do not mutate source documents or prior V2 artifacts.
- Do not auto-fix documentation.
- Do not hide major/fatal findings behind a high aggregate score.

## 8. Exit Criteria

Phase 51 can be accepted only when both real repositories produce quality summary artifacts and any fatal/major finding blocks `overall_status=high_quality`.
