# V2 Phase 6 Development Plan: HTTP/MCP/CLI Read API Convergence

> Phase: 6 / HTTP, MCP, and CLI read convergence.
> Status: pre-development plan.
> Governing PRD: `docs/V2.x/V2_0_TARGET_PRD.md`.

## 1. Objective

Make V2 project-intelligence artifacts consistently readable through HTTP, MCP, and CLI.

Phase 6 does not create new project facts. It standardizes how accepted Phase 1-5 artifacts are read, how success and error envelopes are shaped, and how counts, IDs, warnings, unresolved items, and artifact refs match across interfaces.

## 2. Scope

In scope:

- define and implement a V2 read envelope for code asset read APIs
- normalize success and error response shape across HTTP/MCP/CLI
- add shared payload builders for snapshot, inventory, symbols, imports, trace, and evidence
- ensure CLI stdout is JSON and stderr is diagnostic only
- sort `artifact_refs`, IDs, warnings, and unresolved lists deterministically
- compare HTTP/MCP/CLI outputs on real repository artifacts
- preserve V1 compatibility and existing MCP/HTTP/CLI behavior outside V2 code asset commands

Out of scope:

- new artifact extraction
- Project Overview
- Agent Context Pack
- DevWiki
- Code Graph
- Quality Governance Extension
- migration of all V1 APIs to a new envelope

## 3. Modules

New module:

```text
backend/data_service/code_assets/envelope.py
```

Expected responsibilities:

- `v2_success_envelope(...)`
- `v2_error_envelope(...)`
- `normalize_artifact_refs(...)`
- `normalize_warnings(...)`
- `normalize_unresolved(...)`
- public response helpers for stable `ok/schema_version/...` contracts

Existing modules to extend:

```text
backend/app/api/v1/code_assets.py
backend/data_service/mcp_code_tools.py
backend/data_service/cli_code.py
backend/data_service/code_assets/snapshot.py
backend/data_service/code_assets/inventory.py
backend/data_service/code_assets/symbols.py
backend/data_service/code_assets/trace.py
```

Tests:

```text
backend/tests/test_v2_codebase_interface_convergence.py
backend/tests/test_v2_codebase_snapshot.py
backend/tests/test_v2_codebase_inventory.py
backend/tests/test_v2_codebase_symbols.py
backend/tests/test_v2_codebase_trace.py
backend/tests/test_data_service_mcp.py
backend/tests/test_public_surface_guard.py
```

## 4. V2 Read Envelope

Success shape:

```json
{
  "ok": true,
  "schema_version": "v2.0",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string or null",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

Error shape:

```json
{
  "ok": false,
  "schema_version": "v2.0",
  "workspace_id": "string",
  "codebase_id": "string or null",
  "snapshot_id": "string or null",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": [],
  "error": {
    "code": "TRACE_NOT_FOUND",
    "message": "Trace artifact not found",
    "retryable": false
  }
}
```

Compatibility rule:

- Existing outer HTTP/MCP envelopes may remain for V1 compatibility if needed.
- V2 code asset read payloads must expose the V2 read envelope either as the top-level response for CLI/MCP direct tool output or as `data.v2` for HTTP routes if the existing API envelope cannot be changed without breaking tests.
- Phase 6 acceptance compares the V2 read envelope portion, not incidental outer wrapper fields.

## 5. Stable Read Targets

Phase 6 must converge these artifact families:

```text
codebase
snapshot
inventory
surfaces
capabilities
symbols
imports
trace
evidence
```

For each family, HTTP/MCP/CLI must agree on:

- `workspace_id`
- `codebase_id`
- `snapshot_id` where applicable
- item counts
- stable IDs
- artifact refs
- warning count
- unresolved count
- error code for missing artifacts

## 6. Interface Mapping

HTTP:

- existing codebase target HTTP routes under `/api/workspaces/{workspace_id}/codebases/...`

MCP:

- `knowledge_codebase_describe`
- `knowledge_codebase_list`
- `knowledge_codebase_snapshot`
- `knowledge_project_inventory`
- `knowledge_code_symbol_search`
- `knowledge_public_surface_trace`

CLI:

- `knowledge code describe`
- `knowledge code list`
- `knowledge code snapshot`
- `knowledge code inventory`
- `knowledge code symbols`
- `knowledge code trace`

## 7. Error Codes

Stable error codes:

```text
CODEBASE_NOT_FOUND
CODEBASE_NOT_ACTIVE
SNAPSHOT_NOT_FOUND
INVENTORY_NOT_FOUND
SYMBOL_INDEX_NOT_FOUND
TRACE_NOT_FOUND
TRACE_SURFACE_NOT_FOUND
TRACE_CAPABILITY_NOT_FOUND
INVALID_LIMIT
INVALID_SURFACE_TYPE
INVALID_TRACE_REQUEST
```

HTTP status codes may remain idiomatic, but the V2 read envelope error code must match MCP and CLI.

## 8. Implementation Sequence

1. Add `code_assets/envelope.py`.
2. Add unit tests for success/error envelope normalization.
3. Add convergence test fixture that imports the real repo and builds Phase 2-5 artifacts.
4. Normalize artifact refs and counts for snapshot read.
5. Normalize inventory/surface/capability reads.
6. Normalize symbol/import reads.
7. Normalize trace/evidence reads.
8. Normalize MCP tool output for V2 code tools.
9. Normalize CLI output for V2 code commands.
10. Run targeted convergence tests and full backend regression.

## 9. Architecture Constraints

Do not:

- migrate unrelated V1 APIs into the V2 read envelope
- break existing V1 response contract tests
- add V2 convergence logic to `backend/data_service/service.py`
- add Phase 6 core logic to `backend/app/api/v1/data_service.py`
- change artifact schemas produced by Phase 2-5 unless required for response normalization
- expose absolute paths in public responses

## 10. Stop Conditions

Stop for human confirmation if:

- enforcing V2 envelope top-level would require breaking existing V1/target HTTP contract tests
- MCP and CLI cannot expose the same stable fields without incompatible behavior changes
- convergence requires changing persisted artifact schemas from accepted Phases 2-5
- error normalization hides actionable diagnostics needed by agents
