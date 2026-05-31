# V2.0 Target PRD: Agent-callable Project Intelligence MVP

> Product target: Local Knowledge Governance Service V2.0.
> MVP boundary: Agent-callable project intelligence from Phase 1-7.
> Out of V2.0: DevWiki, Code Graph, Code Quality Governance Extension, and minimum frontend read-only pages.
> V2.0 acceptance is governed by this document, not the older broad V2 PRD unless explicitly referenced.

## 1. Product Goal

V2.0 lets an external Agent call the local service to import a software project, inspect its deterministic project facts, trace conclusions to code evidence, and produce a compact context pack for development tasks.

V2.0 is not a code RAG. It is a local code asset governance layer that produces structured, evidence-backed project intelligence.

## 2. Target Users

- External Coding Agent: needs task-specific files, surfaces, symbols, risks, tests, and evidence.
- Project Understanding Agent: needs project summary, entrypoints, public capabilities, and implementation evidence.
- Developer/Maintainer: needs a reliable public surface and architecture baseline without manually searching the repo.

## 3. V2.0 In Scope

V2.0 must include:

1. Codebase Registry, already completed in Phase 1.
2. Repo Snapshot + File Manifest.
3. Public Surface Inventory.
4. Python Symbol Index.
5. Surface-to-Symbol Mapping + Code Evidence Trace.
6. HTTP/MCP/CLI Read API Convergence.
7. Project Overview.
8. Agent Context Pack.
9. Tests, contract fixtures, artifact inspections, and real repo E2E acceptance.

## 4. V2.0 Out of Scope

The following are V2.1 Expansion items and do not block V2.0:

- DevWiki Baseline.
- Code Graph Baseline.
- Code Quality Governance Extension.
- Minimum frontend read-only page.
- Full call graph, data flow, control flow, runtime tracing, and type inference.
- Full incremental build semantics.
- Multi-language semantic indexing beyond deterministic file/surface inventory and Python AST symbols.

## 5. User Stories

### US-001: Import Codebase

As an external Agent, I can import a local repo as a codebase asset and receive a stable `codebase_id`.

Acceptance:

- HTTP/MCP/CLI import is available.
- Import does not mutate source registry.
- Public response does not leak absolute paths.

### US-002: Generate Repo Snapshot

As an Agent, I can generate a snapshot of the current codebase and read file, language, important-path, git, and warning facts.

Acceptance:

- Snapshot artifacts are persisted.
- Snapshot ID is stable for unchanged content and changes when content changes.
- Sensitive files are skipped or reported as `SENSITIVE_SKIPPED`.
- Snapshot scanning excludes V2 artifact outputs if the workspace or artifact directory is inside the repo.

### US-003: Inspect Public Surface

As an Agent, I can list HTTP APIs, MCP tools, CLI commands, frontend/API-facing entrypoints, and capability alignment.

Acceptance:

- Golden HTTP/MCP/CLI samples are present.
- Golden capabilities include `source_import`, `query`, `build`, `quality`, `graph`, and `codebase_import`.
- Capability IDs are deterministic and normalized.
- MCP count matches `all_tool_specs()`.
- Unresolved capability ratio is reported.

### US-004: Search Symbols

As an Agent, I can search Python modules, classes, functions, methods, imports, and constants.

Acceptance:

- Symbols have stable IDs, repo-relative paths, line ranges, and signatures where available.
- Symbol IDs are stable across repeated parsing and do not change when only a function body changes.
- Symbol ID behavior for signature changes is explicit in the implementation contract.
- Syntax errors are isolated as warnings.

### US-005: Trace Capability to Evidence

As an Agent, I can trace a public capability to surfaces, symbols, files, and line ranges.

Acceptance:

- V1 source import, query, build, quality, source trace, graph, and V2 codebase capabilities are covered.
- At least 10 evidence spans are automatically sampled for path and line-range truth.
- Mapping coverage is reported by surface type and evidence coverage is reported by capability.
- Successful mappings require confidence >= 0.80.

### US-006: Get Project Overview

As an Agent, I can request a project overview for general project reading.

Acceptance:

- Overview includes one-liner, entrypoints, public surface summary, language stats, important paths, core modules, known risks, evidence, and snapshot ID.
- Every important claim has evidence or is marked `needs_review`.

### US-007: Generate Agent Context Pack

As a Coding Agent, I can request a task-specific or generic context pack.

Acceptance:

- Supports `project_brief` and `task_context`.
- Supports JSON and Markdown.
- Honors token budget.
- Includes recommended next steps.
- Implementation guidance, risks, and suggested tests have evidence or `needs_review`.
- Token budget truncation must not retain guidance while dropping its evidence; if evidence is omitted, the guidance is omitted or downgraded to `needs_review`.
- Context pack output includes `omitted_items` when budget or evidence constraints remove content.

## 6. Required Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/...
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/overview
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack
```

MCP:

```text
knowledge_codebase_snapshot
knowledge_project_inventory
knowledge_code_symbol_search
knowledge_public_surface_trace
knowledge_project_overview
knowledge_agent_context_pack
```

CLI:

```text
knowledge code snapshot
knowledge code inventory
knowledge code symbols
knowledge code trace
knowledge code overview
knowledge code context-pack
```

## 7. Non-functional Requirements

- Real repo acceptance must use `/Users/Zhuanz/Desktop/workspace/data_service`.
- Public responses must use repo-relative paths.
- `.env`, credentials, private keys, and secret-pattern files must be skipped or reported as sensitive skipped.
- V2 artifacts must include `schema_version`.
- Phase outputs must be readable from disk, not only returned in memory.
- HTTP/MCP/CLI must converge on stable identifiers and counts.
- HTTP/MCP/CLI must converge on both success and error envelope shapes.
- V1 tests must remain green.
- Frontend build is required only if frontend contract files change.

## 8. V2.0 Completion Definition

V2.0 is complete when an external Agent can:

1. Import the current repo as codebase.
2. Generate and read a repo snapshot.
3. Read public HTTP/MCP/CLI capabilities.
4. Search Python symbols.
5. Trace capabilities to files and line ranges.
6. Read a project overview.
7. Generate `project_brief` and `task_context` context packs.
8. Use HTTP/MCP/CLI with consistent output.
9. Verify all important claims through evidence or `needs_review`.
