# V2.0 Phase 2-7 Development and Acceptance Plan

> This is the implementation-facing plan for the remaining V2.0 Agent-callable MVP phases.
> Phase 1 Codebase Registry is treated as complete.

## Phase 2: Repo Snapshot + File Manifest

### Development

- Add snapshot service under `backend/data_service/code_assets/`.
- Persist `snapshot.json`, `files.jsonl`, `stats.json`, and `warnings.jsonl`.
- Support ignore policy, sensitive file skip, binary/large/unreadable warnings, git metadata, language/LOC stats, important paths, and content-based snapshot ID.
- Document snapshot hash inputs, dirty fingerprint scope, and explicit self-exclusion rules for V2 artifact directories.
- Add HTTP snapshot routes, MCP `knowledge_codebase_snapshot`, and CLI `knowledge code snapshot`.

### Acceptance

- Current repo snapshot succeeds.
- Same content and policy produce same snapshot ID.
- Controlled content change produces different snapshot ID or changed fingerprint.
- `.env`, credentials, private keys, and secret-pattern files are skipped or `SENSITIVE_SKIPPED`.
- `.git`, `.venv`, `node_modules`, `dist`, `build`, `__pycache__` are excluded.
- `workspace/assets/codebase/**`, `assets/codebase/**`, and `.data_service/**` are excluded if present under the scanned repo.
- Warnings are repo-relative and no absolute paths leak.
- `lifecycle/sources.json` does not change.

## Phase 3: Public Surface Inventory

### Development

- Add deterministic inventory extractors for FastAPI HTTP routes, MCP tool registry, argparse CLI, and best-effort frontend/API-facing files.
- Add deterministic capability taxonomy and normalization rules.
- Persist `surfaces.jsonl`, `capabilities.jsonl`, and `alignment_matrix.json`.
- Add HTTP inventory/surfaces/capabilities reads, MCP `knowledge_project_inventory`, and CLI `knowledge code inventory`.

### Acceptance

- MCP count equals current `len(all_tool_specs())`.
- Golden surfaces exist for codebase import, source import, query, build, quality, and graph.
- Golden capabilities `source_import`, `query`, `build`, `quality`, `graph`, and `codebase_import` merge matching HTTP/MCP/CLI surfaces.
- Target and legacy HTTP routes are explicitly classified.
- CLI includes `knowledge code import`, `knowledge source import`, `knowledge build start`, and `knowledge query`.
- Each surface has deterministic ID, source file, line range or unresolved reason, extractor, and confidence.
- Unresolved capability ratio is reported.

## Phase 4: Python Symbol Index

### Development

- Add Python AST extractor for modules/classes/functions/methods/imports/constants.
- Document `symbol_id` stability rules, including body-only edits, signature changes, and nested symbol collisions.
- Persist `symbols.jsonl` and `imports.jsonl`.
- Add symbol search through HTTP, MCP `knowledge_code_symbol_search`, and CLI `knowledge code symbols`.

### Acceptance

- Backend Python files parse without global failure.
- Syntax error fixture is recorded as warning.
- Known HTTP/MCP/CLI handlers can be found by symbol search.
- Sampled line ranges read non-empty real source.
- Function signatures are not globally empty.
- Same file parsed twice produces identical symbol IDs.
- Function body-only changes do not change symbol IDs.
- Nested method/class IDs do not collide.
- Output does not claim full call graph, data flow, control flow, runtime dispatch, or type inference.

## Phase 5: Surface-to-Symbol Mapping + Evidence Trace

### Development

- Add mapping and evidence services.
- Report `mapping_coverage_by_surface_type` and `evidence_coverage_by_capability`.
- Persist `mappings.jsonl` and `evidence.jsonl`.
- Add trace reads for surface, symbol, and capability.
- Add MCP `knowledge_public_surface_trace` and CLI `knowledge code trace`.

### Acceptance

- V1 source import, query, build, quality, source trace, graph, and V2 codebase capabilities are covered.
- `knowledge_codebase_import`, `/codebases`, and `knowledge code import` trace to files and line ranges.
- At least 10 evidence spans pass automatic truth sampling.
- Low-confidence mappings are not counted as successful.
- Successful mappings require confidence >= 0.80.
- Unresolved mappings include reason.
- Evidence is repo-relative and public output has no absolute paths.

## Phase 6: HTTP/MCP/CLI Read API Convergence

### Development

- Define shared `V2ReadEnvelope`.
- Define success and error envelope shapes.
- Ensure snapshot, inventory, symbols, trace, and overview reads can be accessed through HTTP/MCP/CLI.
- Add convergence tests for stable IDs, counts, warnings, unresolved items, and artifact refs.
- Keep CLI JSON by default for automation.

### Acceptance

- HTTP/MCP/CLI agree on `workspace_id`, `codebase_id`, `snapshot_id`, `schema_version`.
- Counts, IDs, warning counts, unresolved counts, and artifact refs match across interfaces.
- CLI stdout contains JSON envelope and stderr is reserved for diagnostics.
- Failure responses have stable `error.code`, `error.message`, and `error.retryable`.
- No new V2 legacy wrappers are introduced.
- Existing V1 HTTP/MCP/CLI smoke tests pass.

## Phase 7: Project Overview + Agent Context Pack MVP

### Development

- Add Project Overview service consuming snapshot, inventory, symbols, mappings, and evidence.
- Add HTTP `/overview`, MCP `knowledge_project_overview`, and CLI `knowledge code overview`.
- Add context modules for model, selector, ranker, Markdown renderer, JSON renderer, token budget, and persistence.
- Support `project_brief` and `task_context`.
- Keep `overview` as a project fact summary and `project_brief` as a compressed Agent-context rendering.
- Persist `overview.json` and `agent_context/{pack_id}.json`.
- Add MCP `knowledge_agent_context_pack` and CLI `knowledge code context-pack`.

### Acceptance

- Overview includes project one-liner, how to run, entrypoints, public surfaces, core modules, storage summary, risks, evidence, and snapshot ID.
- `project_brief` answers generic project reading.
- `task_context` answers a coding task such as “新增 codebase import MCP tool，并同步 HTTP API”.
- Each guidance, risk, suggested test, and recommended next step has evidence or `needs_review`.
- Small token budget does not preserve unevidenced recommendations.
- If evidence is removed by token budget, the linked recommendation is omitted or downgraded to `needs_review`.
- Output includes `omitted_items` when budget or evidence constraints remove content.
- JSON and Markdown derive from the same pack model.
- Pack can be read back by `pack_id`.

## Final V2.0 Acceptance

V2.0 is complete when Phase 2-7 pass against the current real repo, all required artifacts are inspected, HTTP/MCP/CLI converge, V1 regression tests pass, and the final audit report has no open `fatal` or `major` findings.
