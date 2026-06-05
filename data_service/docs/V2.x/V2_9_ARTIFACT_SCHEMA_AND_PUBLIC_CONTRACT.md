# V2.9 Artifact Schema and Public Contract

> Schema and public contract baseline for V2.9 documentation development.

Date: 2026-06-05

## 1. Common Requirements

All V2.9 artifacts must include:

```text
schema_version = v2.9
workspace_id
codebase_id
snapshot_id
created_at
source_artifact_refs
warnings
unresolved
```

Public paths must be repo-relative. Local absolute paths must not be exposed.

## 2. ArchitecturePublicSurfaceEvidenceV2

```text
evidence_id
surface_type = http_api | mcp_tool | cli_command | workflow_entrypoint | console_entrypoint | tui_entrypoint | storage_artifact | generated_artifact
surface_id
label
path
line_range
extractor
confidence
status = accepted | needs_review | blocked
blocker_reason
evidence_refs
needs_review
truth_check = passed | failed | not_applicable
```

Accepted evidence requires `confidence >= 0.85`, a repo-relative path, a valid line range, and `truth_check = passed`.

Allowed blocker reasons:

```text
NO_DECORATOR_PATTERN
DYNAMIC_REGISTRY_UNRESOLVED
ENTRYPOINT_NOT_LINE_RESOLVED
HANDLER_NOT_RESOLVED
WORKFLOW_MANIFEST_UNSUPPORTED
CONSOLE_PATTERN_UNSUPPORTED
TUI_PATTERN_UNSUPPORTED
SOURCE_FILE_MISSING
LINE_RANGE_INVALID
```

## 3. ArchitectureCodeRelationshipV2

```text
relationship_id
relationship_type = capability_implemented_by | surface_handled_by | handler_uses_module | module_referenced_by_test | workflow_uses_step | module_imports_module
from_ref
to_ref
path
line_range
status = deterministic | heuristic | needs_review
confidence
semantic_claim = dependency_evidence | implementation_hint | deterministic_surface_binding | runtime_claim_forbidden
source_phase_refs
evidence_refs
needs_review
```

Forbidden relationship claims:

```text
runtime_calls
data_flow
control_flow
type_inferred_dependency
production_runtime_topology
```

## 4. ArchitectureModuleClusterV2

```text
cluster_id
cluster_type = package | capability | layer | workflow | test_area | unknown
label
member_refs
relationship_refs
evidence_refs
confidence
needs_review
```

## 5. ArchitectureSignalRankingV2

```text
ranking_id
items
groups
score_components
reason_codes
calibration_metrics
blocked_by_major_findings
input_top_n_major_count
output_top_n_major_count
hidden_major_count
hidden_fatal_count
duplicate_reduction_ratio
```

Required score components:

```text
severity
evidence_strength
relationship_depth
doc_code_drift
duplicate_group_size
staleness
human_priority
blocked_by_major_findings
```

## 6. ArchitectureHumanReviewReportV2

```text
report_id
summary
sections
charts
artifact_refs
view_refs
unresolved
needs_review_count
redaction
node_integrity
renderer_consistency
```

Required sections:

```text
executive_summary
capability_to_entrypoint_map
module_cluster_map
evidence_coverage_heatmap
target_current_drift_board
ranking_priority_lanes
unresolved_needs_review_table
```

## 7. ArchitectureContextPackV3

```text
pack_id
mode = project_brief | task_context | architecture_review
role = maintainer | coding_agent | documentation_agent | architecture_reviewer
task
sections
items
token_estimate
max_tokens
omitted_items
source_artifact_refs
source_phase_refs
evidence_refs
warnings
unresolved
confidence
content
recommendation_evidence_policy
```

Every recommendation must have evidence refs or `needs_review`.

When token budget is small, unsupported recommendations must be omitted before their evidence is removed. Removed material must be listed in `omitted_items`.

## 8. Public Envelope

HTTP, MCP, and CLI payloads must expose:

```text
ok
schema_version
workspace_id
codebase_id
snapshot_id
data
artifact_refs
warnings
unresolved
redaction
next_actions
```

Failure responses include:

```text
error.code
error.message
error.retryable
next_actions
```

## 9. Public Error Codes

```text
ARCHITECTURE_V29_SOURCE_ARTIFACT_MISSING
ARCHITECTURE_PUBLIC_SURFACE_EVIDENCE_NOT_BUILT
ARCHITECTURE_RELATIONSHIPS_NOT_BUILT
ARCHITECTURE_RANKING_V2_NOT_BUILT
ARCHITECTURE_HUMAN_REPORT_NOT_BUILT
ARCHITECTURE_CONTEXT_PACK_V3_NOT_FOUND
ARCHITECTURE_CONTEXT_BUDGET_TOO_SMALL
ARCHITECTURE_VIEW_SCHEMA_INVALID
ARCHITECTURE_EVIDENCE_TRUTH_CHECK_FAILED
ARCHITECTURE_UNSUPPORTED_RELATIONSHIP_TYPE
ARCHITECTURE_REPORT_NODE_UNRESOLVED
ARCHITECTURE_V28_BASELINE_MISSING
ARCHITECTURE_HARNESSOS_BASELINE_MISSING
ARCHITECTURE_RELATIONSHIP_SEMANTIC_CLAIM_INVALID
ARCHITECTURE_RANKING_HIDDEN_MAJOR_FINDING
ARCHITECTURE_REPORT_RENDERER_INTEGRITY_FAILED
ARCHITECTURE_CONTEXT_SOURCE_PHASE_REF_MISSING
```

## 10. Parity Acceptance

HTTP, MCP, and CLI must agree on:

- schema version;
- stable ids;
- artifact refs;
- counts;
- warnings;
- unresolved items;
- error codes;
- redaction state.
