# V2 Remaining Development Plan: Project Intelligence Service

> Scope: remaining work after Phase 1 Codebase Registry foundation.
> Phase 1 is treated as implemented and validated: codebase import/list/describe/archive exist across HTTP/MCP/CLI.
> This document is a planning baseline only; it does not claim later phases are implemented.

## 1. Development Outline

V2 剩余开发按“确定性资产事实 -> 映射证据链 -> Agent 可消费上下文”的顺序推进。不得跳过 snapshot 直接做 LLM summary，也不得把代码仓库当普通 source chunk 塞入现有 RAG。

| Phase | Name | Goal | Primary Outputs | Blocks Next |
|---|---|---|---|---|
| 2 | Repo Snapshot + File Manifest | 对 codebase 生成稳定、可复读、可 diff 的文件级 snapshot | `snapshot.json`, `files.jsonl`, `stats.json`, `warnings.jsonl` | Phase 3/4 |
| 3 | Public Surface Inventory | 抽取 HTTP/MCP/CLI/frontend/storage/generated artifact surface | `surfaces.jsonl`, `capabilities.jsonl`, `alignment_matrix.json` | Phase 5/6 |
| 4 | Python Symbol Index | AST 抽取 Python module/class/function/method/import | `symbols.jsonl`, `imports.jsonl` | Phase 5 |
| 5 | Surface-Symbol Mapping + Evidence | 将 surface/capability 追踪到 symbol/file/line | `mappings.jsonl`, `evidence.jsonl`, trace API | Phase 7 |
| 6 | Three-Interface Convergence | 统一 HTTP/MCP/CLI 读取能力和 schema contract | MCP tools, HTTP APIs, CLI commands, contract tests | Phase 7 |
| 7 | Project Overview + Agent Context Pack MVP | 基于 snapshot/inventory/symbol/evidence 生成项目摘要和任务上下文包 | `overview.json`, `agent_context/{pack_id}.json`, Markdown/JSON pack | V2.0 MVP |
| 8 | DevWiki Baseline | 基于 V2 artifacts 生成最小项目 Wiki | `devwiki/pages/*.json`, `index.json` | V2.1 Expansion |
| 9 | Code Graph Baseline | 生成确定性 code graph artifact | `graph.json`, Mermaid exports | V2.1 Expansion |
| 10 | Code Quality Governance Extension | 将 quality feedback/rules 扩展到 code intelligence objects | new target/rule types, correction plan support | V2.1 Expansion |

## 2. Cross-Phase Architecture Rules

- V2 code artifacts must live under `workspace/assets/codebase/{codebase_id}/`.
- V2 must not write codebase files into existing source registry or distill root schema.
- New HTTP code routes should stay outside `backend/app/api/v1/data_service.py`.
- New core logic should stay outside `backend/data_service/service.py`.
- Each artifact must include `schema_version`, `workspace_id`, `codebase_id`, `created_at` or equivalent generation timestamp.
- Public responses must use repo-relative paths by default. Absolute paths are internal-only and must not leak through HTTP/MCP/CLI.
- V2.0 Agent-callable MVP is Phase 1-7. DevWiki, Code Graph, Code Quality Governance Extension, and minimum frontend read-only pages are V2.1 Expansion unless the PRD is explicitly revised again.
- LLM synthesis is allowed only after deterministic artifacts exist and every generated claim can reference evidence or be marked `needs_review`.
- Mock fixtures may test failure paths, but final phase acceptance must use the current real `data_service` repository.

## 3. Phase 2: Repo Snapshot + File Manifest

### Goal

Build a stable repo snapshot service for an imported codebase.

### Development Tasks

1. Add `backend/data_service/code_assets/snapshot.py`.
2. Add models for `RepoSnapshot`, `SnapshotFile`, `SnapshotStats`, `SnapshotWarning`.
3. Add artifact paths:
   - `snapshots/{snapshot_id}/snapshot.json`
   - `snapshots/{snapshot_id}/files.jsonl`
   - `snapshots/{snapshot_id}/stats.json`
   - `snapshots/{snapshot_id}/warnings.jsonl`
4. Implement scan policy merge: codebase default policy + request override.
5. Respect ignore defaults: `.git`, `.venv`, `node_modules`, `dist`, `build`, `__pycache__`, caches, binary files, private env/secret patterns.
6. Capture git metadata when available: branch, commit SHA, dirty state.
7. Compute language/file/LOC stats.
8. Detect important paths: README, docs, backend, frontend, tests, configs, entrypoints.
9. Add HTTP:
   - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots/{snapshot_id}`
10. Add MCP `knowledge_codebase_snapshot`.
11. Add CLI `knowledge code snapshot`.

### Risks

- Snapshot ID instability if dirty-state hashing includes generated files.
- Large repo traversal cost if ignore rules are incomplete.
- Absolute path leakage in warnings.

## 4. Phase 3: Public Surface Inventory

### Goal

Extract the project’s public service surface from deterministic sources.

### Development Tasks

1. Add `backend/data_service/code_assets/inventory/`.
2. Implement FastAPI route extractor using app/router metadata where possible; fall back to AST only when needed.
3. Implement MCP extractor from `all_tool_specs()` and handler registry.
4. Implement CLI extractor from argparse parser builders.
5. Implement frontend static extractor for Vue routes/pages and API calls at file/string level.
6. Add capability classifier with explicit `unresolved` bucket.
7. Generate:
   - `surfaces.jsonl`
   - `capabilities.jsonl`
   - `alignment_matrix.json`
8. Add HTTP:
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/capabilities`
9. Add MCP `knowledge_project_inventory`.
10. Add CLI `knowledge code inventory`.

### Risks

- Over-classifying capabilities without evidence.
- Treating compatibility/legacy routes as target APIs.
- Drift between generated inventory and existing public surface guard tests.

## 5. Phase 4: Python Symbol Index

### Goal

Extract deterministic Python symbol facts and import dependencies.

### Development Tasks

1. Add `backend/data_service/code_assets/symbols/python_ast.py`.
2. Parse modules listed in snapshot `files.jsonl`.
3. Extract module/class/function/method/import/constant records.
4. Capture line ranges using AST lineno/end_lineno.
5. Capture function signatures, decorators, docstrings, visibility.
6. Isolate syntax errors into warnings.
7. Generate:
   - `symbols.jsonl`
   - `imports.jsonl`
8. Add HTTP:
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols/{symbol_id}`
9. Add MCP `knowledge_code_symbol_search`.
10. Add CLI `knowledge code symbols`.

### Risks

- Symbol ID conflicts for duplicate qualified names.
- AST parsing drift across Python versions.
- Missing dynamically registered handlers.

## 6. Phase 5: Surface-Symbol Mapping + Evidence Trace

### Goal

Map public surfaces and capabilities to implementation symbols and code evidence.

### Development Tasks

1. Add `backend/data_service/code_assets/evidence.py`.
2. Add `backend/data_service/code_assets/mapping.py`.
3. Implement mapping rules:
   - FastAPI route -> handler function.
   - MCP tool -> tool spec -> dispatcher/helper.
   - CLI command -> parser branch -> handler/service.
   - Capability -> surfaces -> symbols.
4. Generate:
   - `mappings.jsonl`
   - `evidence.jsonl`
5. Add trace APIs:
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id}`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/symbol/{symbol_id}`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability}`
6. Add MCP `knowledge_public_surface_trace`.
7. Add CLI `knowledge code trace`.

### Risks

- False-positive mapping if string matching is overused.
- Missing evidence for generated or indirect registrations.
- Returning absolute paths in evidence.

## 7. Phase 6: HTTP/MCP/CLI Read API Convergence

### Goal

Make Phase2-5 artifacts consistently accessible across HTTP, MCP, and CLI.

### Development Tasks

1. Define shared response envelope for V2 project intelligence read APIs.
2. Ensure all V2 MCP tools use stable schemas.
3. Ensure CLI outputs JSON by default for automation.
4. Add contract inventory tests comparing HTTP/MCP/CLI fields.
5. Update frontend contract data only after backend contract is stable.
6. Add public surface guard expectations for V2 additions.

### Risks

- Adding legacy wrappers too early.
- Frontend static contract drifting from MCP registry.
- CLI becoming human-only instead of agent-consumable JSON.

## 8. Phase 7: Project Overview + Agent Context Pack MVP

### Goal

Generate a project overview for generic project reading and a task-aware context package for external coding agents.

### Development Tasks

1. Add project overview service that consumes snapshot, inventory, symbols, mappings, and evidence.
2. Add overview HTTP/MCP/CLI:
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/overview`
   - `knowledge_project_overview`
   - `knowledge code overview`
3. Overview output must include `project_one_liner`, `entrypoints`, `public_surface_summary`, `language_stats`, `important_paths`, `core_modules`, `known_risks`, `evidence`, and `snapshot_id`.
4. Add context package modules under `backend/data_service/code_assets/context/` instead of one giant service:
   - `model.py`
   - `selector.py`
   - `ranker.py`
   - `renderer_markdown.py`
   - `renderer_json.py`
   - `token_budget.py`
   - `persistence.py`
5. Support context pack modes:
   - `project_brief`: generic project reading, summary, entrypoints, public surface, core modules, risks, evidence.
   - `task_context`: task-specific implementation guidance, relevant files/symbols, risks, tests, next steps, evidence.
6. Implement relevance ranking over capabilities, surfaces, symbols, tests, docs.
7. Implement token budget estimation and deterministic truncation.
8. Implement Markdown and JSON renderers from one internal model.
9. Persist `overview.json` and `agent_context/{pack_id}.json`.
10. Add HTTP:
   - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack`
   - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}`
11. Add MCP `knowledge_agent_context_pack`.
12. Add CLI `knowledge code context-pack`.

### Risks

- LLM-like claims without evidence.
- Over-broad packs that exceed token budget.
- Context pack not actionable for real coding tasks.
- Project overview becoming a prose-only summary without evidence.
- Context pack implementation becoming a new high-coupling center.

## 9. Phase 8: DevWiki Baseline (V2.1 Expansion)

### Goal

Generate minimal DevWiki pages from V2 artifacts, not from raw LLM guessing.

### Development Tasks

1. Add DevWiki artifact writer under codebase assets.
2. Generate baseline pages:
   - project-overview
   - architecture
   - public-surface
   - http-api
   - mcp-tools
   - cli
   - developer-onboarding
3. Add stale detection based on snapshot ID.
4. Add read API and MCP `knowledge_devwiki_read`.

### Risks

- Duplicating existing LLMWiki without code evidence.
- Wiki pages becoming stale without clear status.

## 10. Phase 9: Code Graph Baseline (V2.1 Expansion)

### Goal

Generate deterministic code graph artifacts for file/module/symbol/surface/capability relations.

### Development Tasks

1. Add `backend/data_service/code_assets/graph.py`.
2. Generate nodes: Codebase, Snapshot, Folder, File, Module, Class, Function, Method, HTTPRoute, MCPTool, CLICommand, Capability, EvidenceSpan.
3. Generate edges: CONTAINS, DEFINES, IMPORTS, HANDLED_BY, IMPLEMENTS_CAPABILITY, EVIDENCED_BY, DOCUMENTED_BY.
4. Add graph read, neighbors, Mermaid export.
5. Add MCP `knowledge_code_graph_snapshot`.
6. Add CLI `knowledge code graph`.

### Risks

- Accidentally claiming full call graph/data flow.
- Graph size explosion for large repos.

## 11. Phase 10: Code Quality Governance Extension (V2.1 Expansion)

### Goal

Allow feedback/rules/correction plans for code intelligence artifacts.

### Development Tasks

1. Add code-specific target types:
   - `codebase`, `repo_snapshot`, `code_file`, `code_symbol`, `public_surface`, `capability`, `devwiki_page`, `agent_context_pack`, `code_graph_edge`.
2. Add rule types:
   - `missing_evidence`, `stale_snapshot`, `wrong_surface_mapping`, `missing_public_surface`, `doc_code_mismatch`, `low_confidence_inference`, `overbroad_agent_context`.
3. Extend correction plan generation to read V2 artifacts.
4. Ensure approved rules are visible to query/context-pack/devwiki readers.

### Risks

- Governance objects not stable enough to govern.
- Rules not applied consistently across readers.

## 12. Stop Conditions

Stop development and ask for human confirmation if any condition appears:

- A phase requires modifying V1 source registry semantics.
- A phase requires adding V2 core logic into `backend/data_service/service.py`.
- A phase requires expanding `backend/app/api/v1/data_service.py` for new V2 code routes.
- Real repo E2E fails twice after implementation.
- Evidence line ranges cannot be produced reliably for a public surface.
- A response leaks absolute path or sensitive file contents.
- Snapshot scan needs to include ignored/secret directories to pass tests.
- Implementation makes unsupported claims such as full call graph, data flow, or full incremental semantics.
