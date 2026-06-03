# V2 Remaining Acceptance Plan: Project Intelligence Service

> This document defines acceptance gates for Phase 2 and later.
> Acceptance must use the current real repository unless explicitly marked as fixture-only.
> Passing unit tests alone is not sufficient for phase acceptance.

## 1. Shared Acceptance Rules

### Required Inputs

- Real codebase path: `/Users/Zhuanz/Desktop/workspace/data_service`
- Temporary workspace root: `/private/tmp/data_service_v2_acceptance`
- Existing Phase1 codebase import must be reused or recreated through public HTTP/MCP/CLI entrypoints.

### Required Checks Per Phase

- Unit tests for models and pure extractors.
- Contract tests for HTTP/MCP/CLI schema.
- Artifact tests that read generated files from disk.
- Real repo end-to-end test.
- Failure-path tests.
- V1 regression smoke test.
- PRD review after implementation.
- False acceptance risk review.

### Required Report Per Phase

Each phase must produce or update:

```text
docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_{N}_AUDIT_REPORT.md
```

The report must include:

- implemented scope
- explicitly not implemented scope
- commands run
- pass/fail result
- artifact paths inspected
- PRD deviations
- architecture deviations
- false acceptance risks
- decision: proceed / rework / stop for human review

## 2. Phase 2 Acceptance: Repo Snapshot

### Entry Criteria

- Phase1 import/list/describe/archive passes across HTTP/MCP/CLI.
- Codebase artifact exists under `workspace/assets/codebase/{codebase_id}/codebase.json`.

### E2E Flow

1. Create temporary workspace.
2. Import current repo as codebase.
3. Generate snapshot through HTTP.
4. Generate or read snapshot through MCP.
5. Generate or read snapshot through CLI.
6. Inspect artifact files on disk.
7. Repeat snapshot generation and compare stability.

### Expected Artifacts

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/snapshot.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/files.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/stats.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/warnings.jsonl
```

### Required Assertions

- `snapshot_id` exists and is stable for unchanged repo state and scan policy.
- `snapshot_id` changes after a controlled file content modification in a temporary test repo copy.
- `snapshot_id` is not affected by `generated_at` or other non-content timestamps.
- `stats.file_count > 0`.
- language stats include Python and Markdown.
- important paths include README, docs, backend, frontend, tests, config files.
- ignored directories do not appear in `files.jsonl`.
- `.env`, private key, credential, and secret-pattern files are skipped or reported as `SENSITIVE_SKIPPED`.
- changed files appear in snapshot diff output or changed fingerprint metadata.
- warnings are repo-relative and do not expose absolute paths.
- binary/oversized/unreadable test fixtures become warnings, not global failure.
- existing source registry is not modified.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_codebase_snapshot.py
python3 -m pytest backend/tests/test_v2_codebase_http.py backend/tests/test_v2_codebase_mcp.py backend/tests/test_v2_codebase_cli.py
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_target_http_source.py
```

## 3. Phase 3 Acceptance: Public Surface Inventory

### Entry Criteria

- Phase2 snapshot artifacts exist.

### E2E Flow

1. Import current repo.
2. Generate snapshot.
3. Build inventory from that snapshot.
4. Read inventory through HTTP, MCP, and CLI.
5. Inspect `surfaces.jsonl`, `capabilities.jsonl`, `alignment_matrix.json`.

### Expected Artifacts

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/surfaces.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/capabilities.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/alignment_matrix.json
```

### Required Assertions

- HTTP routes include target `/api/workspaces/...` and legacy `/api/v1/knowledge/...` surfaces.
- MCP inventory count matches `all_tool_specs()` for the current code, including V2 tools.
- CLI inventory includes `data-service` and `knowledge`, including `knowledge code`.
- Frontend inventory identifies the Knowledge Console entry and API-facing files if present.
- Each surface has deterministic `surface_id`, source file, line range or explicit unresolved reason, extractor, confidence.
- Capability alignment matrix identifies HTTP-only, MCP-only, CLI-only, and aligned capabilities.
- No surface is silently dropped because classification failed.
- Golden HTTP samples are present:
  - `POST /api/workspaces/{workspace_id}/codebases`
  - `POST /api/workspaces/{workspace_id}/query` or current target query route method/path if code confirms a different method
  - `/api/workspaces/{workspace_id}/graph/neighbors`
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
- HTTP route count is at least the current public surface guard baseline.
- CLI command count is at least the current CLI inventory baseline.
- Unresolved capability ratio is reported, even if it is zero.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_public_surface_inventory.py
python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py
npm run build --prefix frontend
```

## 4. Phase 4 Acceptance: Python Symbol Index

### Entry Criteria

- Phase2 snapshot artifacts exist.

### E2E Flow

1. Import current repo.
2. Generate snapshot.
3. Build Python symbol index.
4. Search for known symbols through HTTP/MCP/CLI.
5. Inspect `symbols.jsonl` and `imports.jsonl`.

### Expected Artifacts

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbols.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/imports.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/warnings.jsonl
```

### Required Assertions

- Symbols include classes/functions from `backend/data_service/code_assets/`.
- Symbols include FastAPI route handlers and MCP handlers.
- Symbols include CLI parser/helper functions.
- Each symbol has repo-relative path and line range.
- Sampled symbol line ranges can be read from real files and return non-empty source snippets.
- Function signatures are not globally empty for parsed function/method symbols.
- Module qualified names are stable across repeated runs.
- Nested class/method symbol IDs do not collide.
- Import records include module dependency edges.
- `imports.jsonl` includes real dependencies involving `code_assets` modules once Phase2/3/4 modules exist.
- Syntax error fixture produces warning, not global failure.
- Search by name and kind returns stable results.
- No output claims full call graph, type inference, runtime dispatch recognition, data flow, or control flow.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_python_symbol_index.py
python3 -m pytest backend/tests/test_v2_codebase_snapshot.py
```

## 5. Phase 5 Acceptance: Mapping + Evidence Trace

### Entry Criteria

- Phase3 inventory exists.
- Phase4 symbol index exists.

### E2E Flow

1. Build inventory and symbols for current repo.
2. Build mappings and evidence.
3. Trace selected surfaces and capabilities through HTTP/MCP/CLI.
4. Inspect `mappings.jsonl` and `evidence.jsonl`.

### Expected Artifacts

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mappings.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/evidence.jsonl
```

### Required Assertions

- `knowledge_codebase_import` traces to MCP spec/handler files and line ranges.
- `POST /api/workspaces/{workspace_id}/codebases` traces to HTTP handler and model files.
- `knowledge code import` traces to CLI parser/helper files.
- At least source import, query, build, quality, codebase capabilities trace to surfaces and evidence.
- Mapping coverage includes V1 source import, query, build, quality, source trace, graph, and V2 codebase capabilities.
- At least 10 evidence spans are sampled automatically:
  - repo-relative path exists
  - start_line/end_line are within file bounds
  - extracted snippet contains an expected route/tool/symbol/command hint
- Unresolved mapping entries include reason and confidence below success threshold.
- Low-confidence mappings are not counted as successful mappings.
- Evidence paths are repo-relative.
- Public output does not include absolute paths.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_surface_symbol_mapping.py
python3 -m pytest backend/tests/test_v2_code_evidence_trace.py
python3 -m pytest backend/tests/test_public_surface_guard.py
```

## 6. Phase 6 Acceptance: HTTP/MCP/CLI Convergence

### Entry Criteria

- Phase2-5 read artifacts exist.

### E2E Flow

1. Import current repo.
2. Build snapshot, inventory, symbols, mappings.
3. Read each major V2 artifact through HTTP, MCP, and CLI.
4. Compare stable fields.

### Required Assertions

- HTTP/MCP/CLI output agree on `workspace_id`, `codebase_id`, `snapshot_id`, `schema_version`.
- HTTP/MCP/CLI use the shared `V2ReadEnvelope` fields: `ok`, `schema_version`, `workspace_id`, `codebase_id`, `snapshot_id`, `data`, `artifact_refs`, `warnings`, `unresolved`, `next_actions`.
- Inventory counts match across interfaces.
- Symbol search result IDs match across interfaces.
- Trace result evidence IDs match across interfaces.
- Artifact refs match across interfaces for the same operation.
- Warning counts and unresolved counts match across interfaces for the same operation.
- CLI output is valid JSON.
- No new legacy wrappers are introduced for V2.
- Existing V1 routes/tools/commands remain available.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_interface_convergence.py
python3 -m pytest backend/tests
npm run build --prefix frontend
```

## 7. Phase 7 Acceptance: Project Overview + Agent Context Pack MVP

### Entry Criteria

- Phase5 evidence trace is stable.
- Phase6 interface convergence passes.

### E2E Flow

1. Import current repo.
2. Build all MVP artifacts.
3. Request project overview through HTTP, MCP, and CLI.
4. Request context pack with `mode=project_brief` for:

```text
请阅读并汇总当前项目的定位、入口、公开能力、核心模块、存储结构和证据。
```

5. Request context pack with `mode=task_context` for:

```text
新增 codebase import MCP tool，并同步 HTTP API
```

6. Request context pack in Markdown and JSON.
7. Repeat with small `max_tokens`.
8. Inspect persisted overview and pack artifacts.

### Expected Artifacts

```text
workspace/assets/codebase/{codebase_id}/agent_context/{pack_id}.json
workspace/assets/codebase/{codebase_id}/overview.json
```

### Required Assertions

- Project overview includes project one-liner, how to run, HTTP/MCP/CLI surfaces, core files/modules, risks, evidence, and snapshot_id.
- Pack includes task interpretation, relevant capabilities, public surface, files, symbols, similar patterns, risks, tests, evidence.
- Pack references MCP registry/tool modules, HTTP router, CLI parser/helper, tests.
- Each implementation guidance, risk, suggested test, and recommended next step has evidence or `needs_review`.
- Pack includes `recommended_next_steps`.
- JSON and Markdown derive from the same pack model.
- `max_tokens` is respected by deterministic truncation.
- Small token budget does not keep a recommendation while removing its evidence; if evidence is omitted, the recommendation is omitted or marked `needs_review`.
- Omitted items include reason.
- Pack can be read back by `pack_id`.
- `project_brief` and `task_context` modes are both covered by real repo E2E.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py
python3 -m pytest backend/tests/test_v2_interface_convergence.py
python3 -m pytest backend/tests
npm run build --prefix frontend
```

## 8. Phase 8 Acceptance: DevWiki Baseline (V2.1 Expansion)

### Entry Criteria

- Phase7 Project Overview + Agent Context Pack MVP passes, unless product explicitly moves DevWiki earlier and updates the PRD.

### Required Assertions

- Pages are generated from V2 artifacts.
- Pages include `snapshot_id`, `schema_version`, evidence, confidence, stale flag.
- Pages cover project overview, architecture, public surface, HTTP API, MCP tools, CLI, onboarding.
- Stale state changes when snapshot changes.
- Query/context-pack can consume DevWiki pages.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py
```

## 9. Phase 9 Acceptance: Code Graph Baseline (V2.1 Expansion)

### Entry Criteria

- Phase5 mapping/evidence is stable.

### Required Assertions

- Graph includes file/module/symbol/surface/capability/evidence nodes.
- Graph includes deterministic CONTAINS/DEFINES/IMPORTS/HANDLED_BY/IMPLEMENTS_CAPABILITY/EVIDENCED_BY edges.
- Graph does not claim CALLS/DATA_FLOW/CONTROL_FLOW.
- Neighbors API returns bounded results.
- Mermaid export is valid text and traceable to graph nodes.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_code_graph_baseline.py
```

## 10. Phase 10 Acceptance: Code Quality Governance Extension (V2.1 Expansion)

### Entry Criteria

- Code artifacts have stable IDs.
- Context pack or DevWiki object IDs exist.

### Required Assertions

- Feedback can target codebase, snapshot, symbol, surface, capability, DevWiki page, context pack.
- Correction rules can be generated and reviewed.
- Correction plan includes V2 targets.
- Approved rule is visible to at least one V2 reader.
- Existing quality governance tests remain passing.

### Suggested Commands

```bash
python3 -m pytest backend/tests/test_v2_code_quality_governance.py
python3 -m pytest backend/tests/test_target_http_quality_feedback.py backend/tests/test_target_http_quality_correction_rules.py
```

## 11. Final V2.0 Agent-callable MVP Acceptance

V2.0 Agent-callable MVP is accepted only when Phase2-7 pass and the following command set passes:

```bash
python3 -m pytest backend/tests
npm run build --prefix frontend
```

Manual audit must confirm:

- current repo can be imported
- snapshot can be generated
- inventory can explain HTTP/MCP/CLI surfaces
- symbols can be searched
- evidence trace can reach file/line
- context pack can guide a coding agent without raw whole-repo stuffing
- important claims are evidence-backed or marked `needs_review`

DevWiki, Code Graph, Code Quality Governance Extension, and minimum frontend read-only pages are V2.1 Expansion acceptance items and do not block V2.0 unless the PRD is revised.
