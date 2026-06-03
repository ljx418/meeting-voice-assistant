# V2 Phase 5 Development Plan: Surface-to-Symbol Mapping + Evidence Trace

> Phase: 5 / Surface-to-Symbol Mapping + Code Evidence Trace.
> Status: pre-development plan.
> Governing PRD: `docs/V2.x/V2_0_TARGET_PRD.md`.

## 1. Objective

Build deterministic links from Phase 3 public surfaces and capabilities to Phase 4 Python symbols and line-level evidence.

Phase 5 is the trust layer for V2.0. Its output must let an external Agent trace a capability such as `source_import`, `query`, `build`, `quality`, `graph`, or `codebase_import` to public surfaces, implementation symbols, files, and line ranges.

## 2. Scope

In scope:

- read accepted Phase 3 inventory artifacts
- read accepted Phase 4 symbol artifacts
- map HTTP route surfaces to handler symbols
- map MCP tool surfaces to tool spec / dispatcher / handler evidence where deterministic
- map CLI command surfaces to parser/helper evidence where deterministic
- map capabilities to related surfaces, symbols, and evidence
- persist `mappings.jsonl`, `evidence.jsonl`, `mapping_summary.json`, and `trace_index.json`
- expose trace read/build through HTTP, MCP, and CLI
- report coverage by surface type and by golden capability
- record unresolved mappings with stable reason codes
- verify sampled evidence spans against real repository source lines

Out of scope:

- full call graph
- runtime dispatch resolution
- data flow / control flow
- type inference
- semantic LLM mapping
- DevWiki
- Code Graph
- Project Overview or Agent Context Pack synthesis

## 3. Modules

New modules:

```text
backend/data_service/code_assets/trace.py
```

The module should keep clear internal boundaries:

- mapping models and ID helpers
- evidence span creation and validation helpers
- trace index creation
- public response helpers

If the implementation grows past a small service boundary, split before Phase 6 into:

```text
backend/data_service/code_assets/mapping.py
backend/data_service/code_assets/evidence.py
backend/data_service/code_assets/trace.py
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
backend/tests/test_v2_codebase_trace.py
backend/tests/test_data_service_mcp.py
backend/tests/test_public_surface_guard.py
backend/tests/test_session_ingest_query_build_contract_plan.py
backend/tests/test_session_graphrag_contract.py
backend/tests/test_v16_closure_acceptance.py
backend/tests/test_console_governance_evidence_plan.py
```

## 4. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mappings.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/evidence.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mapping_summary.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/trace_index.json
```

Each persisted row must include:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `extractor`
- `confidence`
- repo-relative source references

## 5. Mapping Schema

```json
{
  "schema_version": "v2.0",
  "workspace_id": "phase5",
  "codebase_id": "codebase_data_service",
  "snapshot_id": "snap_xxx",
  "mapping_id": "map:http:POST:/api/workspaces/{workspace_id}/codebases:py:function:backend.app.api.v1.code_assets.import_codebase",
  "from_type": "http_api",
  "from_id": "http:POST:/api/workspaces/{workspace_id}/codebases",
  "to_type": "symbol",
  "to_id": "py:function:backend.app.api.v1.code_assets.import_codebase",
  "relation": "HANDLED_BY",
  "capability_id": "codebase_import",
  "confidence": 1.0,
  "extractor": "deterministic_surface_symbol_mapper",
  "evidence_ids": ["ev_xxx"],
  "unresolved_reason": null
}
```

Required relation values:

```text
HANDLED_BY
DEFINED_IN
IMPLEMENTS_CAPABILITY
EVIDENCED_BY
UNRESOLVED
```

## 6. Evidence Schema

```json
{
  "schema_version": "v2.0",
  "workspace_id": "phase5",
  "codebase_id": "codebase_data_service",
  "snapshot_id": "snap_xxx",
  "evidence_id": "ev_abc123",
  "path": "backend/app/api/v1/code_assets.py",
  "start_line": 50,
  "end_line": 74,
  "symbol_id": "py:function:backend.app.api.v1.code_assets.import_codebase",
  "surface_id": "http:POST:/api/workspaces/{workspace_id}/codebases",
  "capability_id": "codebase_import",
  "extractor": "deterministic_surface_symbol_mapper",
  "confidence": 1.0,
  "snippet": "optional short excerpt"
}
```

Evidence IDs must be deterministic from:

```text
snapshot_id + path + start_line + end_line + symbol_id + surface_id + capability_id
```

## 7. Trace Index Schema

```json
{
  "schema_version": "v2.0",
  "workspace_id": "phase5",
  "codebase_id": "codebase_data_service",
  "snapshot_id": "snap_xxx",
  "by_surface": {
    "http:POST:/api/workspaces/{workspace_id}/codebases": {
      "mapping_ids": [],
      "evidence_ids": []
    }
  },
  "by_capability": {
    "codebase_import": {
      "surface_ids": [],
      "symbol_ids": [],
      "evidence_ids": []
    }
  },
  "by_symbol": {
    "py:function:...": {
      "surface_ids": [],
      "capability_ids": [],
      "evidence_ids": []
    }
  }
}
```

## 8. Mapping Rules

HTTP:

- Use Phase 3 `handler` field.
- Match handler against Phase 4 symbol `name` and `qualified_name`.
- Prefer exact source file + function name matches.
- If multiple symbols match, choose same `source_file` first; otherwise mark `AMBIGUOUS_HANDLER_SYMBOL`.

MCP:

- Use `tool_name` and Phase 3 `source_file`.
- Create evidence for tool spec/registration when source line exists.
- Map to `handle_code_tool`, `handle_source_tool`, `handle_build_tool`, `handle_quality_tool`, or equivalent deterministic handler if the tool module is known.
- If only registry evidence is known but no specific handler is deterministic, create evidence and mark the handler mapping unresolved with `NO_TOOL_HANDLER`.

CLI:

- Use `command` and `subcommand`.
- Map `knowledge code ...` to `run_code_command` plus command-branch evidence where source line exists.
- Map V1 commands to existing parser/helper symbols if deterministic.
- If branch detection is ambiguous, record `NO_CLI_HANDLER`.

Capability:

- Group by Phase 3 `capability_id`.
- Golden capabilities must have evidence coverage:
  - `source_import`
  - `query`
  - `build`
  - `quality`
  - `graph`
  - `source_trace`
  - `codebase_import`

## 9. Confidence Policy

```text
success_mapping_confidence_min = 0.80
```

Confidence values:

- `1.00`: exact surface handler and symbol source-file match
- `0.95`: exact tool/command handler module and symbol match
- `0.90`: source-line deterministic evidence without unique symbol mapping
- `0.80`: name-based helper match with one unambiguous candidate
- `<0.80`: unresolved and not counted as successful mapping

Stable unresolved reasons:

```text
NO_INVENTORY
NO_SYMBOL_INDEX
NO_HANDLER_SYMBOL
AMBIGUOUS_HANDLER_SYMBOL
NO_TOOL_HANDLER
NO_CLI_HANDLER
LOW_CONFIDENCE
OUT_OF_SCOPE_SURFACE_TYPE
SOURCE_LINE_NOT_FOUND
```

## 10. HTTP API

Build:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/build
```

Read:

```text
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id}
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability_id}
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/evidence
```

Query params:

- `snapshot_id`
- `limit`

## 11. MCP Tool

```text
knowledge_public_surface_trace
```

Input:

```json
{
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "optional string",
  "surface_id": "optional string",
  "capability": "optional string",
  "build": false,
  "limit": 50
}
```

Rules:

- At least one of `surface_id` or `capability` must be supplied for read mode.
- `build=true` may create artifacts from existing inventory and symbols.
- Missing inventory or symbol artifacts must return blocked/error with useful `next_actions`.

## 12. CLI Command

```text
knowledge code trace
```

Arguments:

- `--workspace-root`
- `--workspace-id`
- `--codebase-id`
- `--snapshot-id`
- `--surface-id`
- `--capability`
- `--build`
- `--limit`

Output:

- valid JSON
- no absolute repo/workspace path
- same stable IDs as HTTP/MCP

## 13. Architecture Constraints

Do not:

- add Phase 5 core routes to `backend/app/api/v1/data_service.py`
- add Phase 5 core logic to `backend/data_service/service.py`
- mutate `lifecycle/sources.json`
- claim call graph/type inference/runtime dispatch coverage
- treat low-confidence mappings as successful
- expose absolute filesystem paths in public payloads

## 14. Implementation Sequence

1. Add artifact path helpers.
2. Implement trace service and deterministic ID helpers.
3. Implement HTTP route mappings.
4. Implement MCP mappings.
5. Implement CLI mappings.
6. Implement evidence span generation and read-back validation helpers.
7. Implement trace index and coverage summary.
8. Add HTTP routes.
9. Add MCP tool.
10. Add CLI command.
11. Add targeted Phase 5 tests.
12. Update public surface guard and frontend contract counts if public surface changed.
13. Run real repository E2E and full regression.

## 15. Stop Conditions

Stop for human confirmation if:

- mapping needs non-deterministic LLM inference to satisfy a golden capability
- evidence line ranges cannot be verified from real source
- implementation requires adding V2 core logic to legacy large files
- golden capability coverage fails after deterministic mapping
- public payloads require absolute paths to be useful
