# V2 Phase 4 Acceptance Plan: Python Symbol Index

> Phase: 4 / Python Symbol Index.
> Status: pre-development acceptance plan.

## 1. Required E2E Flow

Use real repository data:

1. Create managed workspace in a temp root.
2. Import current repository as codebase.
3. Create Phase 2 snapshot.
4. Build Phase 3 inventory.
5. Build Phase 4 symbol index.
6. Read symbols via HTTP.
7. Search symbols via MCP.
8. Search symbols via CLI.
9. Inspect disk artifacts.
10. Run V1/V2 regression tests.

## 2. Required Artifacts

The following files must exist and be non-empty:

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbols.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/imports.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbol_summary.json
```

## 3. Contract Assertions

### Symbols

- `symbol_count > 0`
- `module`, `class`, `function`, and `method` kinds are represented when present in repo.
- Every symbol has `symbol_id`, `qualified_name`, `path`, `line_range`, `confidence`.
- Sampled line ranges can read non-empty source lines from real files.
- Function signatures are not all empty.
- Symbol IDs are stable across repeated builds.
- Function body-only edits do not change symbol IDs for unaffected declarations.
- Same-name methods in different classes do not collide.
- Nested functions/methods do not collide.

### Imports

- `import_count > 0`
- Every import has `from_module`, `to_module` or unresolved target, `import_type`, `path`, `line_range`.
- `imports.jsonl` includes a real dependency from MCP code tools to code asset inventory/snapshot modules.

### Syntax Errors

- A fixture Python file with syntax error must not fail the whole build.
- Syntax error must be recorded in `symbol_summary.json.warnings`.

## 4. Golden Assertions

The symbol index must include:

- `backend.data_service.code_assets.inventory.CodebaseInventoryService`
- `backend.data_service.cli_code.run_code_command`
- `backend.app.api.v1.code_assets.build_codebase_inventory`
- `backend.data_service.mcp_code_tools.handle_code_tool`

The import index must include an import from:

```text
backend.data_service.mcp_code_tools -> data_service.code_assets.inventory
```

## 5. HTTP Acceptance

Required routes:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols/{symbol_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/imports
```

Assertions:

- build route returns symbol summary and artifact refs.
- list route supports `query`, `kind`, and `limit`.
- describe route returns a single symbol by `symbol_id`.
- imports route returns import records.
- unknown codebase returns controlled 404/block.
- missing snapshot or missing symbol artifact returns controlled error.
- no absolute repo/workspace path leaks.

## 6. MCP Acceptance

Required tool:

```text
knowledge_code_symbol_search
```

Assertions:

- tool exists in `all_tool_specs()` and stdio list.
- `build=true` can create artifacts from a real snapshot.
- `build=false` can read/search existing artifacts.
- `query="CodebaseInventoryService"` returns the expected class symbol.
- `kind="function"` limits to function-like symbols.
- missing artifacts return blocked with useful `next_actions`.

## 7. CLI Acceptance

Required command:

```text
knowledge code symbols
```

Assertions:

- `--build` creates artifacts.
- read/search mode returns valid JSON.
- `--query CodebaseInventoryService` returns the class symbol.
- `--kind function` filters results.
- no absolute path leaks.

## 8. Regression Suite

Minimum:

```bash
python3 -m pytest backend/tests/test_v2_codebase_symbols.py
python3 -m pytest backend/tests/test_v2_codebase_inventory.py backend/tests/test_v2_codebase_snapshot.py
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py
npm run build --prefix frontend
python3 -m pytest backend/tests
```

## 9. PRD Review Checklist

- Does Phase 4 satisfy Python Symbol Index requirements?
- Does it avoid claiming call graph/type inference/data flow?
- Does it preserve V2.0 MVP boundary?
- Does it keep DevWiki/Code Graph/Quality Governance out of scope?
- Does it produce deterministic artifacts for Phase 5?

## 10. False Acceptance Checks

Fatal if any are true:

- symbol artifacts are empty but build reports success.
- symbols have fake or unreadable line ranges.
- function signatures are missing for nearly all functions.
- symbol IDs change across repeated builds without source declaration changes.
- syntax error in one file fails the entire build.
- HTTP works but MCP/CLI cannot read the same symbols.
- output leaks absolute repo/workspace paths.
- implementation writes to source registry.
- implementation claims call graph/type inference/runtime dispatch.
