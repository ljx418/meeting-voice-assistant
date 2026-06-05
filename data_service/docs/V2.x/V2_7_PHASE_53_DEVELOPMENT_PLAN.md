# V2.7 Phase 53 Development Plan: Architecture Reconstruction Report

> Phase 53 implementation plan.
> Phase 52 alignment artifacts are required input.
> This document is planning authority for Phase 53 only.

Date: 2026-06-04

## 1. Goal

Phase 53 generates a target/current/diff architecture model and readable HTML/Mermaid views.

It must render only persisted document claims, code facts, alignments, quality findings, or explicitly marked inference. It must not copy source diagrams as reconstructed code architecture.

## 2. Inputs

Required inputs:

- `architecture_docs.jsonl`
- `architecture_doc_claims.jsonl`
- `architecture_doc_relations.jsonl`
- `architecture_doc_quality_findings.jsonl`
- `architecture_doc_code_alignment.jsonl`
- `architecture_doc_code_drift_v2.jsonl`
- V2.4 code architecture artifacts
- V2.6 large-project views and taxonomy

## 3. Outputs

Persist:

```text
workspace/assets/codebase/{codebase_id}/architecture/docs/
  architecture_reconstructed_model.json
  views/document_code_architecture_report.html
  views/document_code_architecture_diff.mmd
```

The reconstructed model must include:

```text
schema_version
workspace_id
codebase_id
snapshot_id
model_id
target_nodes
current_nodes
diff_nodes
edges
summary
source_artifact_refs
artifact_refs
created_at
```

Every model node must include:

```text
node_id
node_type
label
section
source_kind
source_refs
confidence
needs_review
```

Allowed `section`:

```text
target_from_documents
current_from_code
gap_and_drift
```

Allowed `source_kind`:

```text
document_claim
code_fact
alignment
quality_finding
explicit_inference
```

## 4. Rendering Rules

HTML must show three visible sections:

- Target Architecture from Documents;
- Current Architecture from Code;
- Gaps and Drift.

Mermaid must show key nodes and relations from the persisted model.

Safety rules:

- HTML document text must be escaped.
- Links must be sanitized.
- No raw script execution.
- Mermaid node IDs must be generated from artifact IDs, not raw labels.
- Mermaid labels must be escaped.
- No absolute path may appear in public output.

## 5. Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/views/{view_id}
```

MCP:

```text
knowledge_code_architecture_reconstructed_build
knowledge_code_architecture_reconstructed
knowledge_code_architecture_doc_view
```

CLI:

```text
knowledge code architecture docs-reconstructed-build
knowledge code architecture docs-reconstructed
knowledge code architecture docs-view
```

## 6. Development Steps

1. Add reconstructed model persistence and view artifact refs.
2. Build target nodes from document claims.
3. Build current nodes from code facts and V2.4/V2.6 artifacts.
4. Build diff nodes from alignments, drift rows, and quality findings.
5. Add cross-link integrity validator.
6. Add safe HTML renderer.
7. Add safe Mermaid renderer.
8. Add service build/read methods and public interfaces.
9. Add focused tests and real-repo E2E.
10. Update coverage matrix and Phase 53 acceptance audit.

## 7. Boundaries

- Do not add architecture facts during rendering.
- Do not treat Drawio labels as code facts.
- Do not hide unresolved or low-confidence nodes.
- Do not make Phase 53 govern or approve findings.
- Do not mutate source artifacts.

## 8. Exit Criteria

Phase 53 can be accepted only when both real repositories produce a non-empty reconstructed model, HTML report, and Mermaid diff, and every rendered node resolves to the persisted model.
