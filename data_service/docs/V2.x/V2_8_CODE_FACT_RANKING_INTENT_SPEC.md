# V2.8 Code Fact, Ranking, and Intent Evidence Specification

> Decision specification for Phase 58, Phase 59, and Phase 60.

## 1. Code Fact Chains

`architecture_code_fact_chains.jsonl` rows must contain:

```text
chain_id
chain_type
status
entry_ref
steps
source_files
line_ranges
evidence_refs
confidence
needs_review
warnings
created_at
```

Allowed `chain_type`:

```text
http_route_chain
mcp_tool_chain
cli_command_chain
config_runtime_boundary
import_dependency_cluster
test_reference_chain
```

Allowed `status`:

```text
accepted
inferred
needs_review
unresolved
```

## 2. Deterministic Chain Rules

Accepted chains require source file and line evidence.

Accepted examples:

- FastAPI route decorator or router registration -> handler function;
- MCP tool spec registration -> dispatcher -> handler function;
- CLI subcommand parser branch -> command handler or service call;
- explicit config file entry -> named runtime/provider/storage boundary;
- test file name/import/reference -> implementation path.

Not accepted as deterministic:

- import edge alone as runtime call;
- name similarity alone;
- folder proximity alone;
- doc claim without code evidence;
- token overlap alone.

These must be `inferred` or `needs_review`.

## 3. Runtime Boundary Hints

`architecture_runtime_boundaries.jsonl` rows must contain:

```text
boundary_id
boundary_type
label
status
source_refs
evidence_refs
confidence
needs_review
```

Allowed `boundary_type`:

```text
http_server
mcp_stdio
cli
frontend_static
local_file_storage
external_provider
database
test_runtime
unknown
```

`status=deterministic` requires explicit code/config evidence. Otherwise use `inferred` or `needs_review`.

## 4. Ranking Formula

`architecture_signal_ranking.json` must expose score components and reason codes.

Default weights:

```text
document_authority = 20
public_surface_importance = 20
evidence_density = 15
drift_severity = 20
code_centrality = 10
recency_staleness = 10
confidence = 5
```

Total score is capped at 100.

Tie-breaker:

```text
severity desc
authority desc
public_surface_importance desc
artifact_id lexical asc
```

Major or fatal findings must be pinned to the high-priority review queue even if their score is low.

## 5. Ranking Reason Codes

Allowed `reason_codes`:

```text
primary_authority_doc
public_surface_impacted
high_evidence_density
major_drift
fatal_or_major_quality_finding
central_module
stale_document
low_confidence_match
undocumented_code_fact
accepted_audit_evidence
```

## 6. Review Queue v2

`architecture_review_queue_v2.json` required queues:

```text
top_unsupported_target_claims
top_undocumented_code_facts
top_stale_docs
top_high_impact_drift
low_confidence_architecture_matches
major_quality_findings
agent_action_candidates
```

Every queue item must include evidence refs, ranking score, reason codes, and `recommended_action`.

## 7. Intent Evidence

`architecture_intent_evidence.jsonl` rows must contain:

```text
intent_id
intent_type
status
label
claim_refs
code_refs
audit_refs
conflict_refs
evidence_refs
confidence
needs_review
```

Allowed `intent_type`:

```text
documented_intent
code_observed
audit_accepted
mismatch
needs_review
```

Rules:

- primary PRD/target architecture evidence produces `documented_intent`;
- source code evidence produces `code_observed`;
- audit/acceptance evidence produces `audit_accepted`;
- conflict between target and observed code produces `mismatch`;
- drawio-only intent has confidence <= 0.70 and stays reviewable unless supported by text or code evidence.

## 8. False-Green Rejection

Reject acceptance if:

- runtime hint is labeled as deterministic without explicit evidence;
- import edge is labeled runtime call;
- ranking hides major/fatal findings;
- score converts weak evidence into accepted evidence;
- intent row claims pure code recovery of human design intent;
- drawio-only intent is accepted without supporting evidence.
