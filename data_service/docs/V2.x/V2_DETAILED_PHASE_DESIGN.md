# V2 Detailed Phase Design

> Generated from repository analysis.
> Updated during V2 execution; business code changes are tracked in git.
> This document gives concrete design details for remaining V2 phases.

Date: 2026-06-01

## 1. Design Baseline

V2.0 is the active development target. Phase 1 Codebase Registry, Phase 2 Repo Snapshot, Phase 3 Public Surface Inventory, Phase 4 Python Symbol Index, Phase 5 Surface-to-Symbol Mapping + Evidence Trace, Phase 6 HTTP/MCP/CLI Read API Convergence, and Phase 7 Project Overview + Agent Context Pack are treated as accepted. V2.0 is implementation-complete pending closure review; V2.1 Phase 8 DevWiki Baseline requires its own phase-specific development, acceptance, and audit documents before implementation.

Design sources:

- `docs/V2.x/V2_0_TARGET_PRD.md`
- `docs/V2.x/V2_FULL_REMAINING_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_2_AUDIT_REPORT.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_AUDIT_REPORT.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_AUDIT_REPORT.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_AUDIT_REPORT.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_AUDIT_REPORT.md`

## 2. Shared V2 Artifact Model

All remaining V2 artifacts are scoped to:

```text
workspace/assets/codebase/{codebase_id}/
```

Snapshot-scoped facts live under:

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/
```

Required common fields:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id` where snapshot-scoped
- `created_at` or generation timestamp
- `extractor`
- `confidence` where inference or mapping is involved
- repo-relative `path` or `source_file`

Public responses must not expose absolute paths. Absolute root paths may exist internally in the codebase registry, but V2 read APIs must return repo-relative references.

## 3. Phase 3 Design: Public Surface Inventory

### Purpose

Create deterministic inventory of public services exposed by the repository.

### Modules

```text
backend/data_service/code_assets/inventory.py
backend/data_service/code_assets/artifacts.py
backend/app/api/v1/code_assets.py
backend/data_service/mcp_code_tools.py
backend/data_service/cli_code.py
```

If inventory grows, split into:

```text
backend/data_service/code_assets/inventory/
  model.py
  service.py
  http_extractor.py
  mcp_extractor.py
  cli_extractor.py
  frontend_extractor.py
  capability.py
  alignment.py
```

### Data Model

`PublicSurface`:

- `surface_id`
- `surface_type`: `http_api | mcp_tool | cli_command | frontend_page | api_client_call | storage_artifact | generated_artifact`
- `name`
- `capability_id`
- `stability`: `target | legacy | internal | experimental | best_effort`
- `source_file`
- `line_range`
- `handler`
- HTTP fields: `method`, `route_path`, `tags`, `summary`
- MCP fields: `tool_name`, `description`, `input_schema`
- CLI fields: `command`, `subcommand`, `arguments`
- `extractor`
- `confidence`
- `unresolved_reason`

`CapabilityRecord`:

- `capability_id`
- `name`
- `description`
- `surface_ids`
- `surface_counts`
- `alignment`: `http | mcp | cli | frontend`
- `unresolved_surface_ids`
- `confidence`

`AlignmentMatrix`:

- capability rows
- interface columns
- stable surface IDs per cell
- missing interface list
- unresolved ratio

### Algorithms

HTTP extraction:

1. Load route definitions from runtime app metadata where possible.
2. For source evidence, parse route decorators or find handler definitions in source.
3. Classify legacy paths under `/api/v1/knowledge/*`.
4. Classify target paths under `/api/workspaces/...`.
5. Generate deterministic IDs: `http:{METHOD}:{path}`.

MCP extraction:

1. Use registry specs rather than README text.
2. Generate ID: `mcp:{tool_name}`.
3. Capture schema from tool spec.
4. Link source file using spec owner module or handler module if deterministically known.

CLI extraction:

1. Use parser construction helpers where available.
2. Include `knowledge` and `data-service` entrypoints.
3. Generate ID: `cli:{command path}`.

Capability normalization:

1. Strip `knowledge_` prefix for MCP names.
2. Collapse `_v2` suffix where it is compatibility naming for the same stable capability.
3. Normalize plural route fragments such as `sources` to `source`.
4. Use golden aliases for V1/V2 core capabilities.
5. Do not merge ambiguous surfaces; mark unresolved.

### APIs

HTTP:

```text
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/capabilities
```

MCP:

```text
knowledge_project_inventory
```

CLI:

```text
knowledge code inventory
```

### Artifacts

```text
surfaces.jsonl
capabilities.jsonl
alignment_matrix.json
inventory_summary.json
```

## 4. Phase 4 Design: Python Symbol Index

### Purpose

Create deterministic Python symbol facts from snapshot files.

### Modules

```text
backend/data_service/code_assets/symbols.py
```

If the symbol index grows materially in V2.1, split the flat module into `model.py`, `python_ast.py`, `service.py`, and `search.py`. V2.0 keeps the implementation flat to avoid introducing abstraction before Phase 5 needs it.

### Data Model

`CodeSymbol`:

- `symbol_id`
- `kind`: `module | class | function | method | import | constant`
- `name`
- `qualified_name`
- `module`
- `path`
- `line_range`
- `signature`
- `decorators`
- `docstring`
- `visibility`
- `parent_symbol_id`
- `extractor`
- `confidence`

`ImportEdge`:

- `from_module`
- `to_module`
- `import_type`
- `path`
- `line_range`

### Symbol ID Rule

Initial rule:

```text
py:{kind}:{module}:{qualified_name}
```

For nested functions/classes:

```text
py:{kind}:{module}:{parent_qualified_name}.{name}
```

Body-only edits must not change IDs. Signature changes should not change IDs in V2.0 unless two symbols would otherwise collide; signature hash may be stored as metadata, not ID input.

### Artifacts

```text
symbols.jsonl
imports.jsonl
symbol_summary.json
```

## 5. Phase 5 Design: Surface-to-Symbol Mapping + Evidence Trace

### Purpose

Connect public surfaces to code implementation evidence.

### Modules

```text
backend/data_service/code_assets/mapping.py
backend/data_service/code_assets/evidence.py
backend/data_service/code_assets/trace.py
backend/app/api/v1/code_assets.py
backend/data_service/mcp_code_tools.py
backend/data_service/cli_code.py
```

V2.0 may combine mapping/evidence/trace implementation into a single `backend/data_service/code_assets/trace.py` only if tests keep the public model boundaries clear. If the file starts carrying unrelated responsibilities, split it before Phase 6.

### Data Model

`SurfaceSymbolMapping`:

- `mapping_id`
- `from_type`
- `from_id`
- `to_type`
- `to_id`
- `relation`
- `confidence`
- `extractor`
- `evidence_ids`
- `unresolved_reason`

`MappingSummary`:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `surface_count`
- `mapped_surface_count`
- `unresolved_surface_count`
- `mapping_coverage_by_surface_type`
- `evidence_coverage_by_capability`
- `success_mapping_confidence_min`
- `unresolved_reason_counts`
- `warnings`

`CodeEvidenceSpan`:

- `evidence_id`
- `path`
- `start_line`
- `end_line`
- `symbol_id`
- `surface_id`
- `capability_id`
- `extractor`
- `confidence`
- optional short `snippet`

### Mapping Rules

- HTTP route handler name -> function symbol.
- MCP tool name -> MCP tool spec source, dispatcher, and deterministic handler helper when known.
- CLI command path -> parser function and invoked helper.
- Capability -> all high-confidence surfaces and symbols.

Evidence span creation:

- Every high-confidence mapping must have at least one evidence span.
- Evidence spans use repo-relative paths and 1-based inclusive line ranges.
- Evidence line ranges must be read back from the real repo during tests.
- Snippets are optional and must remain short; evidence identity must not depend on snippet text.

Confidence:

- exact handler/symbol match: `1.0`
- deterministic source line match: `0.9`
- name-based helper match: `0.8`
- ambiguous or missing symbol: unresolved below `0.8`

Successful mapping threshold:

```text
success_mapping_confidence_min = 0.80
```

Stable unresolved reasons:

- `NO_SYMBOL_INDEX`
- `NO_INVENTORY`
- `NO_HANDLER_SYMBOL`
- `AMBIGUOUS_HANDLER_SYMBOL`
- `NO_TOOL_HANDLER`
- `NO_CLI_HANDLER`
- `LOW_CONFIDENCE`
- `OUT_OF_SCOPE_SURFACE_TYPE`

### Artifacts

```text
mappings.jsonl
evidence.jsonl
mapping_summary.json
trace_index.json
```

### Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/evidence
```

MCP:

```text
knowledge_public_surface_trace
```

CLI:

```text
knowledge code trace
```

## 6. Phase 6 Design: HTTP/MCP/CLI Read API Convergence

### Purpose

Make V2 artifacts equally consumable by HTTP, MCP, and CLI.

### Shared Envelope

Success:

```json
{
  "ok": true,
  "schema_version": "v2.0",
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

Error:

```json
{
  "ok": false,
  "schema_version": "v2.0",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": null,
  "error": {
    "code": "SNAPSHOT_NOT_FOUND",
    "message": "string",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

### Design Rules

- CLI stdout is valid JSON.
- CLI stderr is diagnostic only.
- MCP and HTTP use the same stable IDs and counts.
- Artifact refs are sorted deterministically.

## 7. Phase 7 Design: Project Overview + Agent Context Pack

### Purpose

Produce evidence-backed project reading and task context for external coding agents.

### Modules

```text
backend/data_service/code_assets/overview.py
backend/data_service/code_assets/context/
  model.py
  selector.py
  ranker.py
  renderer_markdown.py
  renderer_json.py
  token_budget.py
  persistence.py
```

### Overview Model

- `project_one_liner`
- `entrypoints`
- `public_surface_summary`
- `language_stats`
- `important_paths`
- `core_modules`
- `storage_summary`
- `known_risks`
- `evidence`
- `needs_review`
- `snapshot_id`

### Context Pack Model

- `pack_id`
- `mode`: `project_brief | task_context`
- `task`
- `sections`
- `items`
- `recommended_next_steps`
- `risks`
- `suggested_tests`
- `evidence`
- `omitted_items`
- `token_estimate`

### Ranking

Rank by:

1. Direct task keyword match to capabilities.
2. Surface/symbol evidence density.
3. Existing tests for related capability.
4. High-risk public interfaces.
5. Core module centrality from inventory/symbol imports.

### Token Budget

If budget is low:

- Drop low-priority sections first.
- Do not keep guidance without evidence.
- If evidence is dropped, downgrade or omit linked guidance.
- Record omitted items and reasons.

## 8. Phase 8 Design: DevWiki Baseline

### Purpose

Generate readable project pages from accepted V2 artifacts.

### Artifacts

```text
devwiki/index.json
devwiki/pages/{slug}.json
```

### Pages

- project overview
- architecture
- public surface
- HTTP API
- MCP tools
- CLI
- storage
- build pipeline
- developer onboarding

### Stale Rule

A page is stale if its `snapshot_id` is not the latest accepted snapshot for the codebase.

## 9. Phase 9 Design: Code Graph Baseline

### Purpose

Create deterministic graph of repo structure, symbols, public surfaces, capabilities, and evidence.

### Nodes

- Codebase
- Snapshot
- Folder
- File
- Module
- Class
- Function
- Method
- HTTPRoute
- MCPTool
- CLICommand
- Capability
- EvidenceSpan
- DevWikiPage

### Edges

- CONTAINS
- DEFINES
- IMPORTS
- HANDLED_BY
- IMPLEMENTS_CAPABILITY
- EVIDENCED_BY
- DOCUMENTED_BY
- GENERATED_FROM

V2.1 must not claim CALLS, DATA_FLOW, CONTROL_FLOW, runtime trace, or type inference.

## 10. Phase 10 Design: Code Quality Governance Extension

### Purpose

Govern V2 code intelligence artifacts using existing quality feedback/rules/plan concepts.

### Target Types

- `codebase`
- `repo_snapshot`
- `code_file`
- `code_symbol`
- `public_surface`
- `capability`
- `devwiki_page`
- `agent_context_pack`
- `code_graph_edge`

### Rule Types

- `missing_evidence`
- `stale_snapshot`
- `wrong_surface_mapping`
- `missing_public_surface`
- `doc_code_mismatch`
- `low_confidence_inference`
- `overbroad_agent_context`

## 11. Phase 11 Design: Minimum Frontend Read-only Console

### Purpose

Expose V2 artifacts for human inspection without creating a frontend-first product.

### Views

- latest snapshot summary
- inventory counts
- alignment matrix
- symbol summary
- trace sample
- overview
- context pack reader/request form

### UI Constraints

- read-only by default
- evidence and unresolved status visible
- no absolute paths
- no hidden backend behavior

## 12. V2.x Closure Design

### Closure Artifacts

```text
docs/V2_X_FINAL_ACCEPTANCE_REPORT.md
docs/V2_X_PUBLIC_SURFACE_MANIFEST.md
docs/V2_X_ARTIFACT_SCHEMA_INDEX.md
docs/V2_X_AGENT_USAGE_GUIDE.md
```

### Closure Checks

- full backend regression
- frontend build if touched
- real repo E2E
- artifact schema audit
- public surface audit
- path/secret leakage audit
- documentation consistency audit
