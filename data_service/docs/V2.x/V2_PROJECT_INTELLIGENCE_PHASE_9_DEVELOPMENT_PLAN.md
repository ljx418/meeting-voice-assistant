# V2 Phase 9 Development Plan: Code Graph Baseline

> Phase: 9 / Code Graph Baseline.
> Track: V2.1 Project Intelligence Expansion.
> Status: pre-development plan.
> Governing references: `docs/V2.x/V2_1_TARGET_PRD.md`, `docs/V2.x/V2_1_TARGET_ARCHITECTURE.md`, `docs/V2.x/V2_1_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`, accepted Phase 8 audit.

## 1. Objective

Build a deterministic Code Graph from accepted V2.0 artifacts plus Phase 8 DevWiki artifacts, so agents can inspect relationships between files, modules, symbols, public surfaces, capabilities, DevWiki pages, and evidence spans.

Phase 9 must not claim full call graph, data flow, control flow, runtime trace, or type inference.

## 2. Entry Inputs

Required inputs:

- V2.0 snapshot artifacts.
- V2.0 inventory surfaces and capabilities.
- V2.0 symbol and import artifacts.
- V2.0 trace evidence and mappings.
- V2.0 project overview.
- Phase 8 DevWiki index and pages.

Phase 9 must fail with structured errors if required inputs are missing. It must not silently rebuild V2.0 or DevWiki facts.

## 3. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/graph/graph.json
workspace/assets/codebase/{codebase_id}/graph/nodes.jsonl
workspace/assets/codebase/{codebase_id}/graph/edges.jsonl
workspace/assets/codebase/{codebase_id}/graph/summary.json
workspace/assets/codebase/{codebase_id}/graph/mermaid/project.mmd
```

## 4. Proposed Modules

```text
backend/data_service/code_assets/graph/model.py
backend/data_service/code_assets/graph/builder.py
backend/data_service/code_assets/graph/neighbors.py
backend/data_service/code_assets/graph/renderer_mermaid.py
backend/data_service/code_assets/graph/persistence.py
backend/data_service/code_assets/graph/service.py
```

Thin interface modules:

```text
backend/app/api/v1/code_assets_graph.py
backend/data_service/mcp_code_graph_tools.py
backend/data_service/cli_code_graph.py
```

Existing registries to extend:

```text
backend/app/api/__init__.py
backend/data_service/mcp_code_tools.py
backend/data_service/cli_code.py
frontend/src/data/mcpContract.ts
```

## 5. Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/neighbors
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid
```

MCP:

```text
knowledge_code_graph_build
knowledge_code_graph_snapshot
knowledge_code_graph_neighbors
knowledge_code_graph_mermaid
```

CLI:

```text
knowledge code graph build
knowledge code graph snapshot
knowledge code graph neighbors
knowledge code graph mermaid
```

## 6. Implementation Sequence

1. Add graph artifact path helpers.
2. Add graph node and edge model helpers.
3. Build deterministic nodes from codebase, snapshot, files, modules/classes/functions/methods, imports, public surfaces, capabilities, DevWiki pages, and evidence spans.
4. Build deterministic edges only from supported relationships: `CONTAINS`, `DEFINES`, `IMPORTS`, `EXPOSES_ROUTE`, `REGISTERS_MCP_TOOL`, `EXPOSES_CLI_COMMAND`, `HANDLED_BY`, `IMPLEMENTS_CAPABILITY`, `DOCUMENTED_BY`, `EVIDENCED_BY`, `GENERATED_FROM`.
5. Persist graph JSON, node JSONL, edge JSONL, summary JSON, and Mermaid export.
6. Add neighbor read service over persisted graph.
7. Add thin HTTP/MCP/CLI surfaces.
8. Add real-repo E2E tests for graph build, read, neighbors, Mermaid, unsupported edge count, node integrity, and no absolute path leakage.
9. Update public surface guard and frontend MCP contract.
10. Run full backend regression and frontend build.
11. Update Phase 9 audit report with PRD/spec/false-acceptance results.

## 7. Stop Conditions

Stop for human confirmation if:

- Graph requires unsupported semantic edges.
- Graph cannot connect core public surfaces to evidence.
- Mermaid export would expose absolute paths.
- Phase 9 would require modifying `backend/app/api/v1/data_service.py` or `backend/data_service/service.py`.
- Phase 9 must mutate V2.0 or DevWiki artifacts to pass.
