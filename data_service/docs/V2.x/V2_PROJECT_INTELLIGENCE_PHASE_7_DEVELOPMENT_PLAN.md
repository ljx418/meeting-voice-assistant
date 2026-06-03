# V2 Phase 7 Development Plan: Project Overview + Agent Context Pack

> Phase: 7 / Project Overview + Agent Context Pack.
> Status: pre-development plan.
> Governing PRD: `docs/V2.x/V2_0_TARGET_PRD.md`.

## 1. Objective

Complete the V2.0 Agent-callable MVP by producing evidence-backed project reading and task context from accepted Phase 2-6 artifacts.

Phase 7 must not invent new extraction facts. It reads snapshot, inventory, symbols, trace, and convergence outputs, then renders project overview and context packs with evidence or `needs_review`.

## 2. Scope

In scope:

- generate `overview.json`
- generate persisted Agent Context Pack artifacts
- support `project_brief` and `task_context`
- support JSON and Markdown rendering
- include recommended next steps
- preserve evidence when applying token budget
- expose HTTP, MCP, and CLI access
- verify with real repository E2E

Out of scope:

- DevWiki
- Code Graph
- Quality Governance Extension
- LLM-only project summaries
- automatic code modification
- full impact analysis
- frontend read-only console

## 3. Modules

New modules:

```text
backend/data_service/code_assets/overview.py
backend/data_service/code_assets/context/model.py
backend/data_service/code_assets/context/selector.py
backend/data_service/code_assets/context/ranker.py
backend/data_service/code_assets/context/renderer_json.py
backend/data_service/code_assets/context/renderer_markdown.py
backend/data_service/code_assets/context/token_budget.py
backend/data_service/code_assets/context/persistence.py
```

Existing modules to extend:

```text
backend/data_service/code_assets/artifacts.py
backend/app/api/v1/code_assets.py
backend/data_service/mcp_code_tools.py
backend/data_service/cli_code.py
frontend/src/data/mcpContract.ts
frontend/src/pages/KnowledgePage.vue
```

Tests:

```text
backend/tests/test_v2_project_overview.py
backend/tests/test_v2_agent_context_pack.py
backend/tests/test_v2_codebase_interface_convergence.py
backend/tests/test_data_service_mcp.py
backend/tests/test_public_surface_guard.py
```

## 4. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/overview.json
workspace/assets/codebase/{codebase_id}/agent_context/{pack_id}.json
```

Every artifact must include:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `created_at`
- `evidence`
- `needs_review`

## 5. Project Overview Model

Required fields:

```text
project_one_liner
entrypoints
public_surface_summary
language_stats
important_paths
core_modules
storage_summary
known_risks
evidence
needs_review
snapshot_id
```

Rules:

- facts must derive from Phase 2-6 artifacts
- generated summaries must cite evidence or be marked `needs_review`
- no claim may depend on source files outside accepted snapshot

## 6. Agent Context Pack Model

Required fields:

```text
pack_id
mode
task
format
sections
items
recommended_next_steps
risks
suggested_tests
evidence
omitted_items
token_estimate
confidence
```

Modes:

- `project_brief`: generic project reading and compressed onboarding context
- `task_context`: task-specific development context

Formats:

- `json`
- `markdown`

## 7. Selection And Ranking

Rank context items by:

1. explicit focus inputs
2. task keyword match to capability, surface, symbol, and file names
3. evidence density
4. public interface risk
5. existing tests for related capability
6. core module centrality from imports and public surfaces

## 8. Token Budget Rule

If token budget is low:

- remove lower-priority sections first
- do not keep guidance while removing supporting evidence
- if evidence is removed, downgrade linked guidance to `needs_review` or move it to `omitted_items`
- always include `omitted_items` when budget changes the output

## 9. HTTP API

```text
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/overview
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}
```

## 10. MCP Tools

```text
knowledge_project_overview
knowledge_agent_context_pack
```

## 11. CLI Commands

```text
knowledge code overview
knowledge code context-pack
```

## 12. Implementation Sequence

1. Add overview and context artifact paths.
2. Implement overview synthesis from snapshot, inventory, symbols, and trace.
3. Implement context model and persistence.
4. Implement selector and ranker.
5. Implement JSON renderer.
6. Implement Markdown renderer.
7. Implement token budget enforcement.
8. Add HTTP routes.
9. Add MCP tools.
10. Add CLI commands.
11. Add real repo E2E tests.
12. Update public surface guard and frontend contract counts if public surface changed.
13. Run full V2.0 acceptance and final audit.

## 13. Stop Conditions

Stop for human confirmation if:

- overview requires unsupported LLM synthesis to pass
- context pack guidance cannot be linked to evidence or `needs_review`
- token budget cannot preserve evidence integrity
- implementation grows into a single giant context service
- accepted Phase 2-6 artifacts lack enough facts to satisfy PRD claims

## 14. Concrete Implementation Design

Phase 7 uses a deterministic, artifact-first pipeline:

```text
snapshot.json
  + inventory_summary/surfaces/capabilities/alignment
  + symbol_summary/symbols/imports
  + mapping_summary/evidence/trace_index
    -> overview.json
    -> agent_context/{pack_id}.json
```

### 14.1 Overview Service

`backend/data_service/code_assets/overview.py` owns overview generation and reading.

Responsibilities:

- resolve `snapshot_id` to the latest snapshot when omitted
- read accepted Phase 2-6 artifacts only
- summarize project facts without LLM synthesis
- persist `overview.json`
- expose public payloads with repo-relative evidence paths

Overview evidence rules:

- `entrypoints` cite snapshot path evidence
- `public_surface_summary` cites inventory summary evidence
- `language_stats` cites snapshot stats evidence
- `core_modules` cite symbol/import evidence
- `known_risks` cite trace/inventory/symbol summaries or are marked `needs_review`

### 14.2 Context Package

`backend/data_service/code_assets/context/` is split by responsibility:

- `model.py`: schema constants and stable ID helpers
- `selector.py`: select capabilities, surfaces, files, symbols, evidence, risks, tests, next steps
- `ranker.py`: deterministic ranking by focus, task keywords, evidence density, public surface risk, tests, and import centrality
- `renderer_json.py`: JSON payload assembly
- `renderer_markdown.py`: Markdown rendering from the same JSON model
- `token_budget.py`: evidence-preserving truncation
- `persistence.py`: artifact path and read/write helpers

### 14.3 HTTP/MCP/CLI Contract

HTTP routes:

```text
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/overview
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}
```

MCP tools:

```text
knowledge_project_overview
knowledge_agent_context_pack
```

CLI commands:

```text
knowledge code overview
knowledge code context-pack
```

All three interfaces return or embed the Phase 6 `data.v2` envelope. Existing outer envelopes remain compatible.

### 14.4 Controlled Errors

Missing prerequisites fail with V2 error envelopes and `next_actions`:

- missing snapshot -> `SNAPSHOT_NOT_FOUND`, next `knowledge_codebase_snapshot`
- missing inventory -> `INVENTORY_NOT_FOUND`, next `knowledge_project_inventory`
- missing symbols -> `SYMBOL_INDEX_NOT_FOUND`, next `knowledge_code_symbol_search`
- missing trace -> `TRACE_NOT_FOUND`, next `knowledge_public_surface_trace`
- missing context pack -> `CONTEXT_PACK_NOT_FOUND`, next `knowledge_agent_context_pack`

### 14.5 Phase 7 Acceptance Samples

Real repo E2E must verify:

- `project_one_liner` is non-empty and evidence-backed
- overview has entrypoints, language stats, surface summary, core modules, risks, evidence, and `needs_review`
- `project_brief` differs from `task_context`
- every guidance/risk/test item has evidence or `needs_review`
- small `max_tokens` returns `omitted_items` and does not keep evidence-free guidance
- `pack_id` readback returns the persisted artifact
