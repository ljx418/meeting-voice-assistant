# V2.7 Phase 50 Development Plan: Architecture Claim Extractor

> Phase 50 implementation plan.
> Phase 49 Document Asset Registry is accepted and must be used as input.
> This document is planning authority for Phase 50 only.

Date: 2026-06-04

## 1. Goal

Phase 50 extracts architecture claims and document relations from registered project documents.

It must convert Markdown, Mermaid, and Drawio document assets into traceable document claims. It must not present document claims as code-derived facts.

## 2. Inputs

Required inputs:

- `architecture/docs/architecture_docs.jsonl`
- `architecture/docs/architecture_doc_sources.jsonl`
- original repository documents referenced by `repo_path`
- Phase 49 public path and authority metadata

Real repositories:

- `/Users/Zhuanz/Desktop/workspace/data_service`
- `/Users/Zhuanz/Desktop/workspace/harnessOS`

## 3. Outputs

Persist:

```text
workspace/assets/codebase/{codebase_id}/architecture/docs/
  architecture_doc_claims.jsonl
  architecture_doc_relations.jsonl
```

Every claim must include:

```text
schema_version
workspace_id
codebase_id
snapshot_id
claim_id
doc_id
claim_type
label
normalized_label
status_hint
scope_hint
source_path
repo_path
line_range
source_block_type
drawio_cell_id
drawio_diagram_id
evidence
confidence
needs_review
created_at
```

Every relation must include:

```text
schema_version
workspace_id
codebase_id
snapshot_id
relation_id
from_claim_id
to_claim_id
relation_type
doc_id
source_block_type
evidence
confidence
needs_review
created_at
```

## 4. Extraction Rules

Markdown extraction must handle:

- headings;
- bullets and numbered lists;
- simple tables;
- acceptance criteria;
- non-goals;
- stop conditions;
- interface lists;
- public API / MCP / CLI mentions.

Drawio extraction must handle:

- diagram pages;
- nodes as document claims;
- edges as document relations;
- cell IDs and diagram IDs;
- labels as document-derived text only.

Claim type candidates:

```text
system
plane
layer
bounded_context
component
adapter
provider
runtime
storage
artifact
public_interface
governance_boundary
policy
milestone
acceptance_gate
forbidden_claim
non_goal
quality_gate
```

Confidence ceilings:

```text
explicit heading/table/API matrix claim: <= 0.90
explicit acceptance gate/non-goal/forbidden claim: <= 0.90
Markdown bullet/list claim: <= 0.80
drawio node only: <= 0.70
drawio edge without explicit relation label: <= 0.65
inferred claim: <= 0.60 and needs_review
```

## 5. Public Interfaces

Add read/build support only for Phase 50 artifacts:

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims
```

MCP:

```text
knowledge_code_architecture_doc_claims_build
knowledge_code_architecture_doc_claims
```

CLI:

```text
knowledge code architecture docs-claims-build
knowledge code architecture docs-claims
```

Interface modules must remain thin. Extraction logic belongs under `backend/data_service/code_assets/architecture/`.

## 6. Required Implementation Boundaries

- Do not rebuild or mutate Phase 49 registry artifacts.
- Do not mutate V2.0-V2.6 artifacts.
- Do not mutate original repository documents.
- Do not use LLM-only claims.
- Do not mark copied Drawio nodes as code facts.
- Do not accept claims without document evidence.

## 7. Development Steps

1. Add claim and relation persistence helpers.
2. Implement Markdown claim block extraction with line ranges.
3. Implement Drawio claim and relation extraction with cell IDs.
4. Add claim type classification and confidence policy.
5. Add service build/read methods.
6. Add HTTP/MCP/CLI build/read interfaces.
7. Add focused tests for fixture repositories.
8. Run real `data_service` and HarnessOS E2E.
9. Update coverage matrix and Phase 50 acceptance audit.

## 8. Exit Criteria

Phase 50 can be accepted only when:

- both real repositories produce non-empty claim artifacts;
- every claim has `doc_id`, `repo_path`, evidence, confidence, and source block type;
- Drawio-only claims stay below accepted confidence ceiling;
- non-goals and forbidden claims are extracted as first-class claims;
- public output does not leak absolute paths;
- HTTP/MCP/CLI outputs are contract-compatible.
