# V2.8 Context Pack and Public Contract Specification

> Decision specification for Phase 61 and V2.8 public contract parity.

## 1. Context Pack Modes

Allowed modes:

```text
project_brief
task_context
```

`project_brief` summarizes project architecture for reading and onboarding.

`task_context` accepts a task string and prioritizes relevant capabilities, chains, risks, tests, and evidence.

## 2. JSON Schema

`architecture_context_pack_v2/{pack_id}.json` must contain:

```text
schema_version
workspace_id
codebase_id
snapshot_id
pack_id
mode
task
sections
items
token_estimate
max_tokens
omitted_items
source_artifact_refs
evidence_refs
warnings
unresolved
confidence
created_at
```

Each `item` must contain:

```text
item_id
item_type
title
summary
priority
source_refs
evidence_refs
recommendation
needs_review
token_estimate
```

## 3. Markdown Template

Markdown output must use this structure:

```text
# Architecture Context Pack
## 1. Project Architecture Brief
## 2. Relevant Views and Diagrams
## 3. Ranked Architecture Signals
## 4. Relevant Code Fact Chains
## 5. Design Intent Evidence
## 6. Drift, Risks, and Review Queue
## 7. Suggested Tests
## 8. Implementation Guidance
## 9. Omitted Items
## 10. Evidence Appendix
```

## 4. Evidence Preservation

Rules:

- every recommendation must have evidence refs or `needs_review`;
- if token budget removes evidence, remove or downgrade the recommendation;
- `omitted_items` must explain why items were omitted;
- no unsupported recommendation may remain in small budget output.

## 5. Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/context-pack
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/context-pack/{pack_id}
```

MCP:

```text
knowledge_code_architecture_context_pack_v2
knowledge_code_architecture_context_pack_read
```

CLI:

```text
knowledge code architecture context-pack
knowledge code architecture context-pack-read
```

## 6. Public Envelope

All V2.8 public responses use:

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
```

Failure responses include:

```text
error.code
error.message
error.retryable
next_actions
```

## 7. Public Error Codes

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

## 8. Parity Acceptance

HTTP, MCP, and CLI must return equivalent:

- schema version;
- stable ids;
- artifact refs;
- counts;
- warnings;
- unresolved items;
- error codes;
- redaction state.
