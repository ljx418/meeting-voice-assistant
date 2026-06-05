# V2.8 Phase 57 Graph Aggregation Specification

> Development, acceptance, and pre-implementation audit specification for Phase 57.

## 1. Goal

Make large architecture graphs readable through clustering, deterministic filters, and view-specific graph artifacts.

## 2. Required Implementation

- Build `architecture_graph_summary.json`.
- Build `architecture_graph_clusters.json`.
- Build `architecture_graph_views/{view_id}.json`.
- Support required view ids:
  - `system_overview`
  - `layer_view`
  - `capability_view`
  - `public_surface_view`
  - `doc_code_drift_view`
  - `evidence_view`

## 3. Aggregation Rules

Use cluster priority:

```text
layer > capability > public_surface > folder_module > document_authority > confidence_band > severity
```

Every graph node must have:

- `node_id`;
- `primary_cluster_id`;
- `cluster_memberships`;
- `source_artifact_refs`;
- `evidence_refs`;
- `confidence`;
- `needs_review`.

## 4. Acceptance Gates

- HarnessOS graph is clustered by default.
- cluster edges preserve source edge ids and evidence refs.
- filter output is deterministic.
- weak/token-only matches do not become accepted edges.
- rendered graph view nodes resolve to persisted graph view artifact nodes.

## 5. Pre-Implementation Audit

Before implementation:

- confirm V2.7 reconstructed model and V2.6 taxonomy artifacts are available;
- confirm filter enum and cluster priority are frozen;
- confirm unsupported filter behavior returns structured error.

## 6. False-Green Rejection

Reject Phase 57 if:

- clusters lose source refs;
- large graph is only capped, not clustered;
- weak matches are shown as accepted relationships;
- filter output differs across repeated runs with same input.
