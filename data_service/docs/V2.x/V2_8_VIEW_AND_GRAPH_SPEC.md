# V2.8 View and Graph Specification

> Decision specification for V2.8 dashboard views, graph aggregation, filtering, and rendered diagrams.

## 1. Purpose

This spec turns the V2.8 readability and graph usability goals into implementable rules. It is binding for Phase 56 and Phase 57.

## 2. Dashboard View Model

`architecture_reading_dashboard.json` must contain:

```text
schema_version
workspace_id
codebase_id
snapshot_id
dashboard_id
summary
charts
hotspots
navigation
source_artifact_refs
evidence_refs
warnings
unresolved
redaction
created_at
```

`summary` required fields:

```text
project_one_liner
primary_languages
document_count
claim_count
accepted_alignment_count
weak_alignment_count
drift_count
major_finding_count
public_surface_count
top_capabilities
top_risks
```

## 3. Required Charts

Phase 56 must render at least these chart sections:

| chart_id | Type | Data source | Required traceability |
| --- | --- | --- | --- |
| `architecture_overview` | SVG relation diagram | V2.7 reconstructed model + graph clusters | every node has `artifact_ref` and `node_id` |
| `capability_map` | Mermaid or SVG | public surfaces + V2.7 alignments + V2.8 chains | capability -> surface -> implementation chain |
| `doc_code_drift_map` | Mermaid or SVG | V2.7 drift + V2.8 ranking | drift id and evidence refs |
| `quality_severity` | bar/pill chart | V2.7/V2.8 quality findings | severity counts and finding refs |
| `evidence_coverage` | bar/pill chart | alignments + chains + intent evidence | accepted/weak/missing evidence counts |
| `hotspot_table` | table | ranking + review queue | reason codes and source refs |

No chart may introduce a fact that is absent from a persisted artifact.

## 4. HTML Rendering Rules

- The report must start with a first-screen dashboard before raw node cards.
- HTML text must be escaped.
- Links must be repo-relative or artifact refs; local absolute paths are redacted.
- Raw document HTML is never injected.
- SVG labels are escaped and truncated.
- Mermaid labels use generated node ids and escaped labels.
- Empty states must be explicit, not silently omitted.

## 5. Graph View Model

`architecture_graph_summary.json` required fields:

```text
graph_summary_id
node_count
edge_count
cluster_count
view_ids
filter_options
coverage
unsupported_edge_count
source_artifact_refs
```

`architecture_graph_clusters.json` rows required fields:

```text
cluster_id
cluster_type
label
primary_key
member_node_ids
member_count
edge_count
source_artifact_refs
expansion_refs
confidence
needs_review
```

`architecture_graph_views/{view_id}.json` required fields:

```text
view_id
view_type
filters
nodes
edges
clusters
summary
source_artifact_refs
warnings
unresolved
```

## 6. Cluster Rules

Cluster priority:

```text
layer > capability > public_surface > folder_module > document_authority > confidence_band > severity
```

Rules:

- each node may have multiple cluster memberships;
- each node must have exactly one `primary_cluster_id`;
- primary cluster is selected by priority order;
- cluster id is deterministic: `cluster:{cluster_type}:{stable_hash(primary_key)}`;
- cluster edge id is deterministic: `cluster_edge:{from_cluster_id}:{to_cluster_id}:{edge_type}`;
- cluster edges must preserve source edge ids and source evidence refs.

## 7. Filter Rules

Allowed filters:

```text
confidence_band = high | medium | low | review
severity = fatal | major | minor | info
accepted_only = true | false
unmatched_claims = true | false
public_surface_only = true | false
governance_state = governed | ungoverned | needs_review
source_kind = document_claim | code_fact | alignment | quality_finding | intent_evidence
```

Filter output must be deterministic. Unsupported filters return `ARCHITECTURE_GRAPH_VIEW_NOT_FOUND` or `ARCHITECTURE_VIEW_SCHEMA_INVALID`, not partial silent output.

## 8. False-Green Rejection

Reject acceptance if:

- a chart node cannot resolve to a persisted artifact;
- copied drawio is presented as code fact;
- token-only or weak matches appear as accepted graph edges;
- cluster membership loses source refs;
- major/fatal findings disappear after filtering unless filter explicitly excludes them;
- report contains local absolute paths.
