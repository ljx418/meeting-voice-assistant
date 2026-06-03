# V2 Full Remaining Development and Acceptance Plan

> Generated from repository analysis.
> Updated during V2 execution; business code changes are tracked in git.
> This document supersedes ad hoc remaining-plan summaries for V2 execution.

Date: 2026-06-01

Update: 2026-06-02 adds V2.4 Code-Derived Architecture Inference as the next architecture-intelligence planning line after V2.3 architecture source alignment.

## 1. Current Baseline

V2 is the active development track. V1.x plans are not the current execution basis unless explicitly requested for a separate maintenance line.

Current V2 status:

- Phase 1 Codebase Registry is treated as complete.
- Phase 2 Repo Snapshot + File Manifest is implemented and accepted after post-review closure.
- Phase 3 Public Surface Inventory is implemented and accepted.
- Phase 4 Python Symbol Index is implemented and accepted.
- Phase 5 Surface-to-Symbol Mapping + Code Evidence Trace is implemented and accepted.
- Phase 6 HTTP/MCP/CLI Read API Convergence is implemented and accepted.
- Phase 7 Project Overview + Agent Context Pack is implemented and accepted.
- V2.0 Agent-callable MVP is implementation-complete and ready for V2.0 closure review.
- The next V2 execution phase is V2.1 Phase 8 DevWiki Baseline, but it must not start until phase-specific development, acceptance, and audit documents are produced and cleared.

Evidence:

- `docs/V2.x/V2_0_TARGET_PRD.md:1-18` defines V2.0 as the Agent-callable Project Intelligence MVP.
- `docs/V2.x/V2_0_TARGET_PRD.md:21-42` defines V2.0 in-scope capabilities.
- `docs/V2.x/V2_0_TARGET_PRD.md:44-55` moves DevWiki, Code Graph, Code Quality Governance, and minimum frontend read-only pages to V2.1 Expansion.
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_AUDIT_REPORT.md` records Phase 4 implementation, verification, and acceptance.
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_AUDIT_REPORT.md` records Phase 5 implementation, verification, and acceptance.
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_AUDIT_REPORT.md` records Phase 6 implementation, verification, and acceptance.
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_7_AUDIT_REPORT.md` records Phase 7 implementation, verification, and acceptance.

## 2. V2 Scope Model

### V2.0 Agent-callable MVP

V2.0 consists of Phase 1-7:

1. Codebase Registry.
2. Repo Snapshot + File Manifest.
3. Public Surface Inventory.
4. Python Symbol Index.
5. Surface-to-Symbol Mapping + Code Evidence Trace.
6. HTTP/MCP/CLI Read API Convergence.
7. Project Overview + Agent Context Pack.

V2.0 completion means an external Agent can import the current repo, generate deterministic artifacts, inspect public surfaces, search symbols, trace evidence to files and line ranges, read a project overview, and generate evidence-backed context packs through HTTP/MCP/CLI.

### V2.1 Expansion

V2.1 begins only after V2.0 acceptance unless the PRD is explicitly revised. V2.1 contains:

8. DevWiki Baseline.
9. Code Graph Baseline.
10. Code Quality Governance Extension.
11. Minimum Frontend Read-only Project Intelligence Console.

### V2.x Closure and Hardening

V2.x closure freezes contracts, verifies scale/security boundaries, and prepares the service for broader agent use.

### V2.4 Code-Derived Architecture Inference

V2.4 begins after the V2.3 architecture abstraction baseline. It adds code-derived architecture inference:

1. Code role classification.
2. Code layer inference.
3. Architecture boundary inference.
4. Architecture pattern candidate detection.
5. Code-derived architecture model build/read.
6. Design-side model vs code-derived model drift findings.
7. HTTP/MCP/CLI access and HTML/Mermaid views.
8. Real-repo E2E on `data_service` and HarnessOS.

V2.4 does not reopen V2.0/V2.1/V2.3 acceptance. It reads accepted artifacts and writes new V2.4 architecture artifacts.

V2.4 authority documents:

- `docs/V2.x/V2_4_TARGET_PRD.md`
- `docs/V2.x/V2_4_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_4_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_4_GAP_ANALYSIS.md`
- `docs/V2.x/V2_4_DOCUMENT_AUDIT_REPORT.md`
- `docs/V2.x/V2_4_TARGET_STATE.drawio`

## 3. Cross-Phase Governance Rules

Every remaining V2 phase must follow this loop:

1. Produce phase-specific development plan.
2. Produce phase-specific acceptance plan.
3. Produce phase-specific pre-development audit report.
4. Close all fatal and major audit findings.
5. Implement only after the audit gate passes.
6. Run focused tests and real repo E2E using `/Users/Zhuanz/Desktop/workspace/data_service`.
7. Inspect generated artifacts from disk.
8. Run V1 regression smoke and relevant V2 regression.
9. Perform PRD/spec review and false-acceptance review.
10. If acceptance fails, return to the phase plan and rework before continuing.

Stop for human confirmation if:

- A phase requires modifying source registry semantics.
- A phase requires adding V2 core routes into `backend/app/api/v1/data_service.py`.
- A phase requires adding V2 core logic into `backend/data_service/service.py`.
- A phase requires substantial CLI logic in `backend/data_service/__main__.py`.
- Evidence line ranges cannot be produced for public surfaces.
- Public output leaks absolute paths, sensitive files, or provider secrets.
- Tests pass only with mocks and not with the real repo.
- Implementation starts claiming full call graph, data flow, control flow, type inference, or true incremental semantics before those are designed and accepted.
- V2.4 architecture inference claims high-confidence roles, layers, boundaries, patterns, or drift without evidence.
- V2.4 validation on HarnessOS only repeats Drawio labels and does not build a code-derived model from code facts.
- V2.4 mutates V2.0/V2.1/V2.3 artifacts without an explicit audited rebuild plan.

## 4. Architecture Gates

V2 implementation must preserve these boundaries:

- V2 artifacts live under `workspace/assets/codebase/{codebase_id}/`.
- V2 codebase artifacts do not pollute `lifecycle/sources.json`.
- V2 HTTP routes use dedicated code asset routers and should not be added to `backend/app/api/v1/data_service.py`.
- V2 core services live under `backend/data_service/code_assets/` or subpackages.
- CLI V2 code should stay in `backend/data_service/cli_code.py` or dedicated helpers, not in `__main__.py`.
- Public responses use repo-relative paths.
- All persisted artifacts include `schema_version`, `workspace_id`, `codebase_id`, and a stable version/snapshot identity where applicable.
- LLM synthesis is allowed only after deterministic facts exist and every generated claim has evidence or `needs_review`.
- V2.4 code-derived architecture artifacts must remain separate from V2.3 design-side architecture artifacts. Drift analysis compares them but does not overwrite either side.

## 5. Phase 2: Repo Snapshot + File Manifest

Status: completed and accepted.

### Accepted Outputs

- `snapshot.json`
- `files.jsonl`
- `stats.json`
- `warnings.jsonl`
- HTTP snapshot routes.
- MCP `knowledge_codebase_snapshot`.
- CLI `knowledge code snapshot`.

### Carry-Forward Requirements

Phase 3+ must treat snapshot as the required input artifact and must not scan the repo independently without using snapshot identity and scan policy.

Carry-forward gates:

- Use snapshot file manifest as extractor input.
- Do not include self-generated V2 artifacts in downstream inventory/symbol processing.
- Preserve Phase 2 path and secret leak protections.

## 6. Phase 3: Public Surface Inventory

Status: completed and accepted.

### Goal

Extract deterministic public service surfaces and capability alignment from the current codebase snapshot.

### Development Plan

Create or update:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_AUDIT_REPORT.md`

Implement:

1. Add inventory package under `backend/data_service/code_assets/inventory/`.
2. Read file list from Phase 2 `files.jsonl`.
3. Extract FastAPI routes:
   - Prefer runtime/app route metadata where deterministic.
   - Fall back to AST only for source evidence.
   - Record method, path, handler, tags, summary, source file, line range, stability, capability, and unresolved reason.
4. Extract MCP tools:
   - Use current registry/tool spec source such as `all_tool_specs()`.
   - Preserve tool name, description, input schema, output envelope, handler module, and source evidence.
5. Extract CLI commands:
   - Use parser builders where possible.
   - Record `data-service`, `knowledge`, and nested `knowledge code` command groups.
6. Extract frontend/API-facing surfaces:
   - Treat as best-effort in V2.0.
   - Record frontend pages and API client calls where deterministic.
7. Add capability taxonomy:
   - deterministic `capability_id`
   - normalization rules
   - aliases for legacy/target/MCP/CLI names
   - explicit `unresolved` bucket
8. Persist:
   - `surfaces.jsonl`
   - `capabilities.jsonl`
   - `alignment_matrix.json`
   - `inventory_summary.json`
9. Add HTTP reads:
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/capabilities`
10. Add MCP:
   - `knowledge_project_inventory`
11. Add CLI:
   - `knowledge code inventory`

### Acceptance Plan

Entry criteria:

- Phase 2 snapshot accepted for the real repo.
- Phase 3 pre-development audit has no open fatal or major findings.

Required tests:

- `python3 -m pytest backend/tests/test_v2_public_surface_inventory.py`
- `python3 -m pytest backend/tests/test_v2_codebase_snapshot.py`
- `python3 -m pytest backend/tests/test_public_surface_guard.py`
- `python3 -m pytest backend/tests/test_data_service_mcp.py`

Real repo E2E:

1. Import `/Users/Zhuanz/Desktop/workspace/data_service`.
2. Generate or reuse Phase 2 snapshot.
3. Build inventory from snapshot artifacts.
4. Read inventory through HTTP, MCP, and CLI.
5. Inspect `surfaces.jsonl`, `capabilities.jsonl`, `alignment_matrix.json`, and `inventory_summary.json` from disk.

Hard assertions:

- MCP inventory count equals `len(all_tool_specs())`.
- Golden HTTP samples are present:
  - codebase import route
  - target query route
  - graph neighbors route
  - legacy `/api/v1/knowledge/query`
- Golden MCP samples are present:
  - `knowledge_codebase_import`
  - `knowledge_query_v2`
  - `knowledge_source_import`
  - `knowledge_build_start`
  - `knowledge_quality_summary`
- Golden CLI samples are present:
  - `knowledge code import`
  - `knowledge source import`
  - `knowledge build start`
  - `knowledge query`
- Golden capabilities are normalized:
  - `codebase_import`
  - `source_import`
  - `query`
  - `build`
  - `quality`
  - `graph`
- Every surface has deterministic ID, source file, line range or unresolved reason, extractor, and confidence.
- Target, legacy, internal, and experimental routes are classified.
- Unresolved capability ratio is reported.
- Empty inventory is a hard failure.
- No absolute path leakage.

Audit decision:

- Proceed to Phase 4 only if inventory artifacts are non-empty, golden assertions pass, and there are no open fatal or major findings.

## 7. Phase 4: Python Symbol Index

### Goal

Extract deterministic Python symbol facts and import dependencies from the Phase 2 snapshot.

### Development Plan

Create or update:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_AUDIT_REPORT.md`

Implement:

1. Add `backend/data_service/code_assets/symbols/`.
2. Add Python AST extractor.
3. Extract:
   - module
   - class
   - function
   - method
   - import
   - constant
   - decorator
   - docstring
4. Define `symbol_id` contract:
   - stable across repeated parse
   - stable across body-only edits
   - signature-change behavior documented
   - nested class/function/method IDs cannot collide
5. Capture repo-relative path and line range.
6. Capture function/method signature where available.
7. Capture syntax errors as warnings, not global failures.
8. Persist:
   - `symbols.jsonl`
   - `imports.jsonl`
   - updated `warnings.jsonl`
   - `symbol_summary.json`
9. Add HTTP:
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols/{symbol_id}`
10. Add MCP:
   - `knowledge_code_symbol_search`
11. Add CLI:
   - `knowledge code symbols`

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_v2_python_symbol_index.py`
- `python3 -m pytest backend/tests/test_v2_codebase_snapshot.py`

Real repo E2E:

1. Use current repo snapshot.
2. Build Python symbol index from `files.jsonl`.
3. Search known symbols via HTTP/MCP/CLI.
4. Inspect `symbols.jsonl`, `imports.jsonl`, and `symbol_summary.json`.

Hard assertions:

- Symbols include route handlers, MCP handlers, CLI helpers, and code asset modules.
- Sampled line ranges read non-empty real source from disk.
- Function signatures are not globally empty.
- Same file parsed twice produces identical symbol IDs.
- Body-only changes do not change symbol IDs.
- Nested symbols do not collide.
- Syntax error fixture becomes a warning, not a global failure.
- Imports include real dependencies among V2 code asset modules after Phase 3/4 exists.
- Output does not claim full call graph, data flow, control flow, runtime dispatch, or type inference.
- No absolute path leakage.

Audit decision:

- Proceed to Phase 5 only if symbol ID stability and line-range truth checks pass.

## 8. Phase 5: Surface-to-Symbol Mapping + Code Evidence Trace

### Goal

Map public surfaces and capabilities to implementation symbols, files, and line ranges.

### Development Plan

Create or update:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_AUDIT_REPORT.md`

Implement:

1. Add `backend/data_service/code_assets/mapping.py`.
2. Add `backend/data_service/code_assets/evidence.py`.
3. Map:
   - FastAPI route to handler symbol.
   - MCP tool to tool spec, registry, dispatcher/helper.
   - CLI command to parser branch and service/helper.
   - Capability to surfaces, symbols, and evidence.
4. Define mapping confidence:
   - `>= 0.80` counts as successful.
   - below threshold is unresolved or low-confidence.
5. Define unresolved reason taxonomy.
6. Persist:
   - `mappings.jsonl`
   - `evidence.jsonl`
   - `mapping_summary.json`
   - `trace_index.json`
7. Add HTTP:
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id}`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/symbol/{symbol_id}`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability}`
8. Add MCP:
   - `knowledge_public_surface_trace`
9. Add CLI:
   - `knowledge code trace`

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_v2_surface_symbol_mapping.py`
- `python3 -m pytest backend/tests/test_v2_code_evidence_trace.py`
- `python3 -m pytest backend/tests/test_v2_public_surface_inventory.py`
- `python3 -m pytest backend/tests/test_v2_python_symbol_index.py`
- `python3 -m pytest backend/tests/test_public_surface_guard.py`

Real repo E2E:

1. Build snapshot, inventory, and symbols.
2. Build mapping and evidence.
3. Trace selected surfaces and capabilities through HTTP/MCP/CLI.
4. Inspect mapping and evidence artifacts from disk.

Hard assertions:

- V1 capabilities covered:
  - source import
  - query
  - build
  - quality
  - source trace
  - graph
- V2 capabilities covered:
  - codebase import
  - codebase snapshot
  - inventory
  - symbols
- Evidence truth sampling checks at least 10 evidence spans:
  - repo-relative path exists
  - `start_line` and `end_line` are within file bounds
  - snippet contains expected route, symbol, tool, or command hint
- Mapping coverage is reported by surface type:
  - HTTP
  - MCP
  - CLI
  - frontend/API-facing best-effort
- Evidence coverage is reported by capability.
- Low-confidence mappings are not counted as success.
- Unresolved mappings include reason.
- No absolute path leakage.

Audit decision:

- Proceed to Phase 6 only if evidence truth sampling passes and V1/V2 core capabilities have coverage or explicit unresolved reasons.

## 9. Phase 6: HTTP/MCP/CLI Read API Convergence

### Goal

Make V2 artifacts readable through HTTP, MCP, and CLI with consistent success and error envelopes.

### Development Plan

Create or update:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_AUDIT_REPORT.md`

Implement:

1. Define shared `V2ReadEnvelope`.
2. Define success shape:
   - `ok`
   - `schema_version`
   - `workspace_id`
   - `codebase_id`
   - `snapshot_id`
   - `data`
   - `artifact_refs`
   - `warnings`
   - `unresolved`
   - `next_actions`
3. Define error shape:
   - `ok=false`
   - stable `error.code`
   - stable `error.message`
   - `error.retryable`
   - scoped IDs where available
4. Normalize read outputs for:
   - snapshot
   - inventory
   - surfaces
   - capabilities
   - symbols
   - trace
   - overview placeholder or later Phase 7 output
5. Keep CLI JSON-first for automation.
6. Add convergence comparison tests.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_v2_codebase_interface_convergence.py`
- `python3 -m pytest backend/tests/test_v2_codebase_snapshot.py`
- `python3 -m pytest backend/tests/test_v2_codebase_inventory.py`
- `python3 -m pytest backend/tests/test_v2_codebase_symbols.py`
- `python3 -m pytest backend/tests/test_v2_codebase_trace.py`
- `python3 -m pytest backend/tests`

Real repo E2E:

1. Build Phase 2-5 artifacts.
2. Read major artifacts through HTTP.
3. Read same artifacts through MCP.
4. Read same artifacts through CLI.
5. Compare stable semantic fields.

Hard assertions:

- HTTP/MCP/CLI agree on IDs and `schema_version`.
- Counts match for inventory, capabilities, symbols, mappings, evidence.
- Warning counts and unresolved counts match.
- Artifact refs match and are sorted deterministically.
- CLI stdout is valid JSON.
- CLI stderr contains diagnostics only.
- Error responses use the shared error envelope.
- Existing V1 HTTP/MCP/CLI smoke tests pass.
- No new legacy wrappers are introduced for V2.

Audit decision:

- Proceed to Phase 7 only if the same facts are consumable through all three interfaces.

## 10. Phase 7: Project Overview + Agent Context Pack MVP

### Goal

Generate evidence-backed project summaries and task-aware context packs for external agents.

### Development Plan

Create or update:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_7_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_7_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_7_AUDIT_REPORT.md`

Implement:

1. Add project overview service.
2. Overview consumes:
   - snapshot
   - inventory
   - symbols
   - mapping
   - evidence
3. Persist:
   - `overview.json`
4. Add HTTP:
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/overview`
5. Add MCP:
   - `knowledge_project_overview`
6. Add CLI:
   - `knowledge code overview`
7. Add context package modules under `backend/data_service/code_assets/context/`:
   - `model.py`
   - `selector.py`
   - `ranker.py`
   - `renderer_markdown.py`
   - `renderer_json.py`
   - `token_budget.py`
   - `persistence.py`
8. Support context modes:
   - `project_brief`
   - `task_context`
9. Persist:
   - `agent_context/{pack_id}.json`
10. Add HTTP:
   - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}`
11. Add MCP:
   - `knowledge_agent_context_pack`
12. Add CLI:
   - `knowledge code context-pack`

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_v2_project_overview.py`
- `python3 -m pytest backend/tests/test_v2_agent_context_pack.py`
- `python3 -m pytest backend/tests/test_v2_codebase_interface_convergence.py`
- `python3 -m pytest backend/tests`

Real repo E2E:

1. Build Phase 2-6 artifacts.
2. Read overview through HTTP/MCP/CLI.
3. Generate `project_brief` for:
   - `请阅读并汇总当前项目的定位、入口、公开能力、核心模块、存储结构和证据。`
4. Generate `task_context` for:
   - `新增 codebase import MCP tool，并同步 HTTP API`
5. Generate both JSON and Markdown.
6. Repeat with small token budget.
7. Read pack back by `pack_id`.

Hard assertions:

- Overview includes:
   - project one-liner
   - how to run
   - entrypoints
   - HTTP/MCP/CLI surfaces
   - core modules
   - storage summary
   - risks
   - evidence
   - snapshot ID
- Every important overview claim has evidence or `needs_review`.
- Context pack includes:
   - task interpretation
   - relevant capabilities
   - public surfaces
   - files
   - symbols
   - similar patterns
   - implementation guidance
   - risks
   - suggested tests
   - recommended next steps
   - evidence
   - omitted items
- Guidance, risks, suggested tests, and next steps have evidence or `needs_review`.
- Token truncation never keeps guidance while dropping its evidence.
- Markdown and JSON derive from the same pack model.
- Pack can be read back by `pack_id`.

Audit decision:

- V2.0 may enter final acceptance only if Phase 7 passes real repo E2E and has no open fatal or major findings.

## 11. V2.0 Final Acceptance

### Required Flow

1. Import current repo as codebase.
2. Generate snapshot.
3. Build public surface inventory.
4. Build Python symbol index.
5. Build mapping and evidence trace.
6. Read artifacts via HTTP/MCP/CLI.
7. Generate project overview.
8. Generate project brief context pack.
9. Generate task context pack.
10. Inspect all artifacts from disk.
11. Run full backend regression.
12. Run frontend build only if frontend contracts changed.
13. Produce final V2.0 acceptance report.

### Required Commands

```bash
python3 -m pytest backend/tests
```

If frontend files changed:

```bash
npm run build --prefix frontend
```

### Acceptance Gates

- Current repo can be imported.
- Snapshot can be generated and read.
- Public surface inventory explains HTTP/MCP/CLI surfaces.
- Symbol search finds core handlers.
- Evidence trace reaches repo-relative file and line ranges.
- Project overview is evidence-backed.
- Context pack is actionable and evidence-backed.
- HTTP/MCP/CLI outputs converge.
- V1 regression remains green.
- No public path or secret leakage.
- No unsupported claims about full call graph, data flow, control flow, runtime dispatch, or type inference.

## 12. Phase 8: DevWiki Baseline (V2.1)

### Goal

Generate minimal DevWiki pages from V2 deterministic artifacts.

### Development Plan

Create:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_8_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_8_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_8_AUDIT_REPORT.md`

Implement:

1. Add DevWiki artifact module under code assets.
2. Generate pages:
   - project overview
   - architecture
   - public surface
   - HTTP API
   - MCP tools
   - CLI
   - storage
   - build pipeline
   - developer onboarding
3. Persist:
   - `devwiki/index.json`
   - `devwiki/pages/{slug}.json`
4. Add stale detection using snapshot ID.
5. Add HTTP page list/read.
6. Add MCP `knowledge_devwiki_read`.
7. Add CLI `knowledge code devwiki`.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_v2_devwiki_baseline.py`

Hard assertions:

- Pages derive from snapshot, inventory, symbols, mapping, and evidence.
- Pages include `schema_version`, `snapshot_id`, evidence, confidence, stale flag.
- No page contains major unevidenced claims.
- Stale flag changes when snapshot changes.
- Pages are readable from disk and through public interfaces.

## 13. Phase 9: Code Graph Baseline (V2.1)

### Goal

Generate deterministic code graph artifacts for file, module, symbol, surface, capability, and evidence relationships.

### Development Plan

Create:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_9_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_9_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_9_AUDIT_REPORT.md`

Implement:

1. Add code graph module.
2. Generate nodes:
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
   - DevWikiPage where available
3. Generate edges:
   - CONTAINS
   - DEFINES
   - IMPORTS
   - HANDLED_BY
   - IMPLEMENTS_CAPABILITY
   - EVIDENCED_BY
   - DOCUMENTED_BY
   - GENERATED_FROM
4. Persist:
   - `graph/graph.json`
   - `graph/summary.json`
   - `graph/mermaid/*.mmd`
5. Add graph snapshot read.
6. Add bounded neighbors read.
7. Add Mermaid export.
8. Add MCP `knowledge_code_graph_snapshot`.
9. Add CLI `knowledge code graph`.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_v2_code_graph_baseline.py`

Hard assertions:

- Graph includes file/module/symbol/surface/capability/evidence nodes.
- Graph includes deterministic edges only.
- Graph does not claim CALLS, DATA_FLOW, CONTROL_FLOW, runtime trace, or type inference.
- Neighbors are bounded.
- Mermaid export is valid text and references real graph nodes.
- Graph IDs are stable for unchanged snapshot.

## 14. Phase 10: Code Quality Governance Extension (V2.1)

### Goal

Extend quality governance to code intelligence objects.

### Development Plan

Create:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_10_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_10_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_10_AUDIT_REPORT.md`

Implement:

1. Add target types:
   - `codebase`
   - `repo_snapshot`
   - `code_file`
   - `code_symbol`
   - `public_surface`
   - `capability`
   - `devwiki_page`
   - `agent_context_pack`
   - `code_graph_edge`
2. Add rule types:
   - `missing_evidence`
   - `stale_snapshot`
   - `wrong_surface_mapping`
   - `missing_public_surface`
   - `doc_code_mismatch`
   - `low_confidence_inference`
   - `overbroad_agent_context`
3. Extend feedback capture.
4. Extend correction rule generation and review.
5. Extend correction plan generation.
6. Make approved rules visible to at least one V2 reader.

### Acceptance Plan

Required tests:

- `python3 -m pytest backend/tests/test_v2_code_quality_governance.py`
- existing quality governance regression tests.

Hard assertions:

- Feedback can target V2 code intelligence objects.
- Correction rule can be generated and reviewed.
- Correction plan references stable V2 object IDs.
- Approved rule is visible in overview, DevWiki, context pack, or trace reader.
- Existing V1 quality governance remains compatible.

## 15. Phase 11: Minimum Frontend Read-only Project Intelligence Console (V2.1)

### Goal

Expose a minimal read-only V2 console for humans without turning V2 into a frontend-first product.

### Development Plan

Create:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_11_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_11_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_11_AUDIT_REPORT.md`

Implement:

1. Add read-only Project Intelligence view under existing `/knowledge` console or a clearly scoped tab.
2. Show latest codebase snapshot.
3. Show inventory counts and surface alignment matrix.
4. Show symbol count and searchable examples.
5. Show trace sample with file/line evidence.
6. Show overview.
7. Allow context pack request in read-only mode if backend Phase 7 is accepted.
8. Keep frontend as a consumer of existing HTTP APIs.

### Acceptance Plan

Required checks:

- `npm run build --prefix frontend`
- screenshot/manual or Playwright smoke for desktop and mobile if UI changes are substantial.
- backend tests for APIs used by the frontend.

Hard assertions:

- No new backend behavior is hidden inside frontend work.
- UI displays evidence and unresolved status clearly.
- Text does not overflow or overlap.
- No absolute paths or sensitive content displayed.

## 16. V2.x Closure and Release Audit

### Goal

Freeze V2 Agent-callable and V2.1 Expansion contracts with auditable evidence.

### Development Plan

Create:

- `docs/V2_X_FINAL_ACCEPTANCE_REPORT.md`
- `docs/V2_X_PUBLIC_SURFACE_MANIFEST.md`
- `docs/V2_X_ARTIFACT_SCHEMA_INDEX.md`
- `docs/V2_X_AGENT_USAGE_GUIDE.md`

Perform:

1. Public surface inventory of V2 HTTP/MCP/CLI.
2. Artifact schema inventory.
3. Real repo E2E acceptance.
4. Path/secret leakage audit.
5. V1 regression.
6. V2 regression.
7. Documentation consistency audit.

### Acceptance Plan

Required commands:

```bash
python3 -m pytest backend/tests
```

If frontend was changed:

```bash
npm run build --prefix frontend
```

Hard assertions:

- All accepted phase docs exist.
- All generated artifacts have schema versions.
- HTTP/MCP/CLI public surfaces are indexed.
- Agent usage guide can drive a fresh external agent flow.
- All known major/fatal findings are closed or explicitly deferred with owner and rationale.

## 17. Recommended Execution Order

Immediate V2.0 sequence:

1. Phase 3: Public Surface Inventory.
2. Phase 4: Python Symbol Index.
3. Phase 5: Surface-to-Symbol Mapping + Code Evidence Trace.
4. Phase 6: HTTP/MCP/CLI Read API Convergence.
5. Phase 7: Project Overview + Agent Context Pack.
6. V2.0 Final Acceptance.

V2.1 sequence:

7. Phase 8: DevWiki Baseline.
8. Phase 9: Code Graph Baseline.
9. Phase 10: Code Quality Governance Extension.
10. Phase 11: Minimum Frontend Read-only Console.
11. V2.x Closure and Release Audit.
