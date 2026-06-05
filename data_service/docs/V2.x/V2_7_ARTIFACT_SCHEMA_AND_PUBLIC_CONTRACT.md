# V2.7 Artifact Schema and Public Contract

> Contract document for V2.7 documentation-code architecture governance.
> Phase 49-55 schemas and public contracts are accepted for the current V2.7 scope.

Date: 2026-06-04

## 1. Artifact Root

```text
workspace/assets/codebase/{codebase_id}/architecture/docs/
```

Artifacts:

```text
architecture_docs.jsonl
architecture_doc_sources.jsonl
architecture_doc_claims.jsonl
architecture_doc_relations.jsonl
architecture_doc_quality_findings.jsonl
architecture_doc_quality_summary.json
architecture_doc_code_alignment.jsonl
architecture_doc_code_drift_v2.jsonl
architecture_reconstructed_model.json
views/document_code_architecture_report.html
views/document_code_architecture_diff.mmd
```

## 2. Common Fields

All persisted JSON artifacts must include or reference:

```json
{
  "schema_version": "v2.7",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "created_at": "iso8601",
  "source_artifact_refs": [],
  "evidence": [],
  "confidence": 0.0,
  "needs_review": []
}
```

Public payloads must use repo-relative paths and safe artifact refs. Public payloads must not expose local absolute paths, secrets, raw tracebacks, or unredacted provider/runtime metadata.

Every phase must record and verify source artifact hashes for prior V2 artifacts, original documents, and the source registry. V2.7 artifacts are new outputs; prior artifacts must not be silently modified.

## 3. ArchitectureDocument

```json
{
  "schema_version": "v2.7",
  "doc_id": "archdoc_xxx",
  "doc_type": "target_architecture",
  "path": "docs/V2.x/V2_7_TARGET_ARCHITECTURE.md",
  "title": "V2.7 Target Architecture",
  "phase_hint": "V2.7",
  "version_hint": "2.7",
  "scope_hint": "documentation_code_architecture_governance",
  "authority_role": "target",
  "authority_level": "primary",
  "supersedes": [],
  "superseded_by": [],
  "stale_hint": false,
  "evidence": [
    {
      "type": "source_file",
      "path": "docs/V2.x/V2_7_TARGET_ARCHITECTURE.md",
      "repo_path": "docs/V2.x/V2_7_TARGET_ARCHITECTURE.md",
      "line_range": [1, 20],
      "extractor": "architecture_doc_registry"
    }
  ],
  "confidence": 0.9,
  "needs_review": []
}
```

Allowed `doc_type`:

```text
prd
target_architecture
gap_analysis
drawio
development_plan
acceptance_plan
audit_report
api_matrix
handoff_summary
readme
unknown_architecture_doc
```

Allowed `authority_role`:

```text
target
implementation_plan
acceptance_result
audit_status
historical_reference
unknown
```

Allowed `authority_level`:

```text
primary
supporting
historical
weak
```

## 4. ArchitectureDocumentClaim

```json
{
  "schema_version": "v2.7",
  "claim_id": "archclaim_xxx",
  "doc_id": "archdoc_xxx",
  "claim_type": "component",
  "label": "Document Quality Evaluator",
  "normalized_label": "document_quality_evaluator",
  "status_hint": "target",
  "scope_hint": "V2.7",
  "source_block_type": "heading",
  "drawio_cell_id": null,
  "drawio_diagram_id": null,
  "source_path": "docs/V2.x/V2_7_TARGET_ARCHITECTURE.md",
  "repo_path": "docs/V2.x/V2_7_TARGET_ARCHITECTURE.md",
  "line_range": [40, 55],
  "evidence": [],
  "confidence": 0.85,
  "needs_review": []
}
```

Allowed `claim_type`:

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

Allowed `source_block_type`:

```text
heading
bullet
numbered_item
table_row
diagram_node
diagram_edge
acceptance_gate
non_goal
stop_condition
interface_list
```

Claim confidence policy:

```text
explicit heading/table/API matrix claim: <= 0.90
explicit acceptance gate/non-goal/forbidden claim: <= 0.90
Markdown bullet/list claim: <= 0.80
drawio node only: <= 0.70
drawio edge without explicit relation label: <= 0.65
inferred claim: <= 0.60 and needs_review
```

## 5. ArchitectureDocumentRelation

```json
{
  "schema_version": "v2.7",
  "relation_id": "archrel_xxx",
  "from_claim_id": "archclaim_source",
  "to_claim_id": "archclaim_target",
  "relation_type": "depends_on",
  "source_doc_id": "archdoc_xxx",
  "evidence": [],
  "confidence": 0.8,
  "needs_review": []
}
```

Allowed `relation_type`:

```text
contains
depends_on
governs
produces
consumes
implements
documents
validates
blocks
supersedes
conflicts_with
```

## 6. ArchitectureDocumentQualityFinding

```json
{
  "schema_version": "v2.7",
  "finding_id": "archdocq_xxx",
  "target_type": "architecture_doc_claim",
  "target_id": "archclaim_xxx",
  "finding_type": "missing_evidence",
  "severity": "major",
  "title": "Architecture claim has no implementation evidence.",
  "evidence": [],
  "recommendation": "Map the claim to code evidence or mark it as planned.",
  "confidence": 0.85,
  "needs_review": []
}
```

Allowed `finding_type`:

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
```

## 7. ArchitectureDocCodeAlignment

```json
{
  "schema_version": "v2.7",
  "alignment_id": "archalignv2_xxx",
  "claim_id": "archclaim_xxx",
  "code_ref": {
    "type": "public_surface",
    "id": "http:GET:/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs"
  },
  "status": "matched",
  "match_strategy": "surface_name_and_capability",
  "document_evidence": [],
  "code_evidence": [],
  "confidence": 0.86,
  "needs_review": []
}
```

Allowed `status`:

```text
matched
weak_match
designed_not_found_in_code
code_not_documented
doc_claim_without_evidence
stale_doc_claim
needs_review
```

Accepted match requirements:

- document evidence exists;
- code evidence exists;
- confidence is >= 0.80;
- match strategy is stronger than token overlap alone;
- no blocking `needs_review`.

Match strategy policy:

```text
accepted_match_confidence_min = 0.80
weak_match_confidence_range = 0.40 - 0.79
token_overlap_only -> weak_match only
```

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

## 8. ReconstructedArchitectureModel

```json
{
  "schema_version": "v2.7",
  "model_id": "archrecon_xxx",
  "target_nodes": [],
  "current_nodes": [],
  "diff_nodes": [],
  "edges": [],
  "coverage_summary": {
    "document_claim_count": 0,
    "accepted_alignment_count": 0,
    "weak_match_count": 0,
    "designed_not_found_in_code_count": 0,
    "code_not_documented_count": 0
  },
  "quality_summary": {
    "finding_count": 0,
    "fatal_count": 0,
    "major_count": 0,
    "needs_review_count": 0
  },
  "source_artifact_refs": [],
  "confidence_distribution": {},
  "needs_review_count": 0
}
```

## 9. Public Interface Contract

HTTP reads must return a V2 envelope:

```json
{
  "ok": true,
  "schema_version": "v2.7",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

HTTP errors must return:

```json
{
  "ok": false,
  "schema_version": "v2.7",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": null,
  "error": {
    "code": "ARCHITECTURE_DOCS_NOT_BUILT",
    "message": "Architecture document artifacts were not found.",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

Target error codes:

```text
ARCHITECTURE_DOCS_NOT_BUILT
ARCHITECTURE_DOC_NOT_FOUND
ARCHITECTURE_DOC_PARSE_FAILED
ARCHITECTURE_DOC_CLAIMS_NOT_BUILT
ARCHITECTURE_DOC_QUALITY_NOT_BUILT
ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT
ARCHITECTURE_RECONSTRUCTION_NOT_FOUND
ARCHITECTURE_DOC_VIEW_NOT_FOUND
ARCHITECTURE_DOC_SCHEMA_INVALID
```

MCP and CLI outputs must preserve the same stable IDs, counts, warnings, unresolved items, artifact refs, and schema version as HTTP reads.

## 10. Cross-Link Integrity Contract

Validators must reject or mark `needs_review` when:

- a claim references a missing `doc_id`;
- a relation endpoint references a missing claim;
- an alignment references a missing claim;
- an accepted alignment `code_ref` cannot be resolved;
- a reconstructed node references a missing claim, missing code fact, or unmarked inference;
- a rendered view node is absent from `architecture_reconstructed_model.json`.

## 11. Rendering Safety Contract

HTML and Mermaid renderers must:

- escape document-provided labels and text;
- sanitize links;
- reject or neutralize raw script injection;
- generate Mermaid node IDs from artifact IDs;
- escape Mermaid labels;
- omit absolute paths from public outputs.

## 12. Governance Target Types

V2.7 quality governance should support:

```text
architecture_doc
architecture_doc_claim
architecture_doc_relation
architecture_doc_quality_finding
architecture_doc_code_alignment
architecture_reconstructed_node
architecture_reconstructed_edge
```

Approved rules are read-time overlays only. They must not rewrite source documents, code facts, or existing V2 artifacts.
