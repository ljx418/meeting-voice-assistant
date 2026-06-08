# V2.15 Target Architecture: Interactive Review Workbench

## 1. Architecture Position

V2.15 is the readable presentation layer for Coding Agent actionability.

```text
V2.11 Actionability
V2.12 Patch Plans
V2.13 Runtime Evidence
V2.14 Incremental Intelligence
  -> Workbench Payload Builder
  -> HTML Renderer
  -> Mermaid Graph Renderer
  -> Context Export Builder
  -> HTTP / MCP / CLI
```

## 2. Components

### 2.1 Workbench Payload Builder

Builds a persisted JSON payload from existing artifacts. It performs no new fact extraction.

### 2.2 HTML Renderer

Renders readable sections:

- project actionability overview;
- patch plan readiness;
- runtime evidence;
- incremental drift;
- capability graph;
- risk lanes;
- blocker board;
- evidence table;
- context export summary.

### 2.3 Mermaid Graph Renderer

Generates graph from persisted payload node IDs and edge IDs only.

### 2.4 Context Export Builder

Creates role-aware export payloads for Coding Agents, reviewers, and maintainers.

## 3. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/coding_agent/workbench/
  review_workbench.json
  review_workbench.html
  capability_graph.mmd
  context_exports/{export_id}.json
```

## 4. Public Error Codes

```text
WORKBENCH_SOURCE_ARTIFACT_MISSING
WORKBENCH_PAYLOAD_NOT_FOUND
WORKBENCH_VIEW_NOT_FOUND
WORKBENCH_NODE_INTEGRITY_FAILED
WORKBENCH_CONTEXT_BUDGET_TOO_SMALL
WORKBENCH_SCHEMA_INVALID
```

## 5. Safety Boundaries

- HTML and Mermaid cannot introduce facts not present in backend payload.
- Labels must be escaped.
- Blockers and `needs_review` must remain visible.
- Context export must not drop evidence while keeping recommendations.
- Workbench is read-only and not a fact source.

## 6. Target User Experience

After V2.15, users can open one workbench page and understand:

- what the project exposes;
- what changes are planned;
- what evidence supports them;
- what runtime checks ran;
- what changed incrementally;
- what is risky, blocked, or ready for review.
