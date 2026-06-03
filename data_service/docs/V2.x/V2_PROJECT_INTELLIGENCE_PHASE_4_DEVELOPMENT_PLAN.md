# V2 Phase 4 Development Plan: Python Symbol Index

> Phase: 4 / Python Symbol Index.
> Status: pre-development plan.
> Governing PRD: `docs/V2.x/V2_0_TARGET_PRD.md`.

## 1. Objective

Build a deterministic Python AST symbol index from a Phase 2 repo snapshot and Phase 3 inventory baseline.

Phase 4 produces file/module/class/function/method/import facts that later Phase 5 can use for surface-to-symbol mapping and evidence trace.

## 2. Scope

In scope:

- read Python files from `files.jsonl`
- parse with Python `ast`
- extract module, class, function, method, import, decorator, docstring, and signature facts
- persist `symbols.jsonl`, `imports.jsonl`, and `symbol_summary.json`
- expose read/search via HTTP, MCP, and CLI
- isolate syntax errors per file and record warnings
- validate sampled line ranges against real source files

Out of scope:

- full call graph
- runtime dispatch analysis
- data flow / control flow
- type inference
- cross-language symbol extraction
- surface-to-symbol mapping
- code graph
- LLM synthesis

## 3. Modules

New module:

```text
backend/data_service/code_assets/symbols.py
```

Expected responsibilities:

- `CodebaseSymbolIndexService`
- `build_symbol_index(codebase_id, snapshot_id=None)`
- `read_symbols(codebase_id, snapshot_id=None, kind=None, query=None, limit=50)`
- `read_imports(codebase_id, snapshot_id=None)`
- `read_symbol(codebase_id, symbol_id, snapshot_id=None)`
- AST extraction helpers
- symbol id and qualified-name helpers

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
backend/tests/test_v2_codebase_symbols.py
backend/tests/test_data_service_mcp.py
backend/tests/test_public_surface_guard.py
backend/tests/test_session_ingest_query_build_contract_plan.py
backend/tests/test_session_graphrag_contract.py
backend/tests/test_v16_closure_acceptance.py
backend/tests/test_console_governance_evidence_plan.py
```

## 4. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbols.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/imports.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbol_summary.json
```

Each persisted row must include:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `path`
- `line_range`
- `extractor`
- `confidence`

## 5. Symbol Schema

```json
{
  "schema_version": "v2.0",
  "workspace_id": "phase4",
  "codebase_id": "codebase_data_service",
  "snapshot_id": "snap_xxx",
  "symbol_id": "py:function:backend.data_service.cli_code.run_code_command",
  "kind": "function",
  "name": "run_code_command",
  "qualified_name": "backend.data_service.cli_code.run_code_command",
  "module": "backend.data_service.cli_code",
  "path": "backend/data_service/cli_code.py",
  "line_range": [58, 128],
  "signature": "run_code_command(args)",
  "docstring": null,
  "decorators": [],
  "visibility": "internal",
  "parent_symbol_id": null,
  "extractor": "python_ast",
  "confidence": 1.0
}
```

Symbol kinds:

```text
module
class
function
method
```

## 6. Import Schema

```json
{
  "schema_version": "v2.0",
  "workspace_id": "phase4",
  "codebase_id": "codebase_data_service",
  "snapshot_id": "snap_xxx",
  "import_id": "pyimport:backend.data_service.mcp_code_tools:backend.data_service.code_assets.inventory",
  "from_module": "backend.data_service.mcp_code_tools",
  "to_module": "backend.data_service.code_assets.inventory",
  "import_type": "from_import",
  "name": "CodebaseInventoryService",
  "alias": null,
  "path": "backend/data_service/mcp_code_tools.py",
  "line_range": [8, 8],
  "extractor": "python_ast",
  "confidence": 1.0
}
```

Import types:

```text
import
from_import
relative_import
```

## 7. Symbol ID Rule

Symbol IDs must be deterministic and stable:

```text
py:{kind}:{qualified_name}
```

Rules:

- `qualified_name` is repo-root module path plus class/function nesting.
- module ID is `py:module:{module}`.
- method ID is `py:method:{module}.{class}.{method}`.
- nested functions use their lexical path, e.g. `module.outer.<locals>.inner`.
- function body edits must not change `symbol_id`.
- line movement must not change `symbol_id`.
- signature edits must not change `symbol_id`; signature remains a searchable field.
- if duplicate IDs occur in malformed or generated code, append a short deterministic path/line hash and record `collision_resolved=true`.

## 8. HTTP API

Build:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols
```

Read/search:

```text
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols/{symbol_id}
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/imports
```

Query params:

- `snapshot_id`
- `kind`
- `query`
- `limit`

## 9. MCP Tool

```text
knowledge_code_symbol_search
```

Input:

```json
{
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "optional string",
  "query": "optional string",
  "kind": "optional string",
  "limit": 20,
  "build": false
}
```

Behavior:

- `build=true` builds index then returns search results.
- `build=false` reads existing symbols.
- missing symbols artifact returns blocked with `next_actions=["knowledge_code_symbol_search --build", "knowledge_project_inventory"]`.

## 10. CLI

```text
knowledge code symbols
```

Options:

- `--workspace-root`
- `--workspace-id`
- `--codebase-id`
- `--snapshot-id`
- `--query`
- `--kind`
- `--limit`
- `--build`

Default behavior should be read/search only. `--build` explicitly creates or refreshes artifacts.

## 11. Extraction Design

Per file:

1. Read included Python records from `files.jsonl`.
2. Convert repo-relative path to module name.
3. Add one module symbol.
4. Parse AST.
5. Walk top-level classes and functions with lexical parent tracking.
6. For each class/function/method:
   - line range from `lineno` / `end_lineno`
   - signature from args
   - decorators from AST name/attribute/call names
   - docstring from `ast.get_docstring`
   - visibility from name prefix
7. Walk import/import-from nodes into `imports.jsonl`.
8. If a file has `SyntaxError`, record summary warning and continue.

## 12. Summary

`symbol_summary.json` includes:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `created_at`
- `symbol_count`
- `import_count`
- `symbols_by_kind`
- `python_file_count`
- `parsed_file_count`
- `syntax_error_count`
- `warnings`
- `golden_checks`

Golden checks:

- `backend.data_service.code_assets.inventory.CodebaseInventoryService`
- `backend.data_service.cli_code.run_code_command`
- `backend.app.api.v1.code_assets.build_codebase_inventory`
- `backend.data_service.mcp_code_tools.handle_code_tool`
- an import from `backend.data_service.mcp_code_tools` to `data_service.code_assets.inventory`

## 13. Architecture Gates

- Do not add core logic to `backend/data_service/service.py`.
- Do not add Phase 4 routes to `backend/app/api/v1/data_service.py`.
- Do not write into `lifecycle/sources.json`.
- Do not depend on LLM provider calls.
- Do not claim call graph, data flow, type inference, or runtime dispatch.
- Keep line ranges real and source-readable.

## 14. PRD Traceability

Phase 4 satisfies V2.0 Target PRD Python Symbol Index requirements and prepares Phase 5 mapping/evidence trace.

Phase 4 does not satisfy Project Overview or Agent Context Pack by itself; those remain Phase 7.
