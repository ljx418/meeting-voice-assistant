# V2.8 Artifact Schema and Public Contract

> Contract draft for V2.8 documentation development.

## 1. Common Artifact Fields

Every V2.8 artifact must include:

```text
schema_version = v2.8
workspace_id
codebase_id
snapshot_id
artifact_id
source_artifact_refs
evidence_refs
confidence
needs_review
warnings
redaction
created_at
```

## 2. Core Artifacts

### ArchitectureReadingDashboard

```text
dashboard_id
summary
key_architecture_layers
key_capabilities
top_risks
quality_summary
drift_summary
hotspots
chart_refs
evidence_refs
```

### ArchitectureGraphSummary

```text
graph_summary_id
node_count
edge_count
cluster_count
view_ids
filter_options
coverage
unsupported_edge_count
```

### ArchitectureGraphCluster

```text
cluster_id
cluster_type
label
member_node_ids
member_count
source_artifact_refs
expansion_refs
confidence
needs_review
```

### ArchitectureCodeFactChain

```text
chain_id
chain_type = http_route | mcp_tool | cli_command | config_runtime | import_cluster | test_reference
entry_ref
steps
source_files
line_ranges
evidence_refs
confidence
needs_review
```

### ArchitectureRuntimeBoundary

```text
boundary_id
boundary_type
label
evidence
confidence
status = deterministic | inferred | needs_review
```

### ArchitectureSignalRanking

```text
ranking_id
items
score_components
reason_codes
blocked_by_major_findings
```

### ArchitectureIntentEvidence

```text
intent_id
intent_type = documented_intent | code_observed | audit_accepted | mismatch | needs_review
claim_refs
code_refs
audit_refs
confidence
needs_review
```

### ArchitectureContextPackV2

```text
pack_id
mode = project_brief | task_context
task
sections
items
token_estimate
omitted_items
evidence_refs
warnings
```

## 3. Public Response Envelope

```json
{
  "ok": true,
  "schema_version": "v2.8",
  "workspace_id": "...",
  "codebase_id": "...",
  "snapshot_id": "...",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "redaction": {
    "local_paths_redacted": true
  }
}
```

Failure shape:

```json
{
  "ok": false,
  "schema_version": "v2.8",
  "workspace_id": "...",
  "codebase_id": "...",
  "snapshot_id": null,
  "error": {
    "code": "ARCHITECTURE_VIEW_NOT_BUILT",
    "message": "V2.8 architecture view has not been built.",
    "retryable": false
  },
  "warnings": [],
  "unresolved": []
}
```

## 4. Error Codes

```text
ARCHITECTURE_V28_SOURCE_ARTIFACT_MISSING
ARCHITECTURE_VIEW_NOT_BUILT
ARCHITECTURE_GRAPH_VIEW_NOT_FOUND
ARCHITECTURE_RANKING_NOT_BUILT
ARCHITECTURE_CONTEXT_PACK_NOT_FOUND
ARCHITECTURE_CONTEXT_BUDGET_TOO_SMALL
ARCHITECTURE_FACT_CHAIN_NOT_BUILT
ARCHITECTURE_INTENT_EVIDENCE_NOT_BUILT
ARCHITECTURE_VIEW_SCHEMA_INVALID
```

## 5. Contract Parity

HTTP, MCP, and CLI must expose stable:

- schema version;
- artifact refs;
- counts;
- warnings;
- unresolved items;
- redaction state;
- error codes.
