# V2.8 Phase 58 Acceptance Audit Report: Code Fact Chains

> Generated from repository analysis and real-data validation.
> Business code was modified for V2.8 Phase 58 implementation.
> This report is an acceptance/audit record, not a PRD replacement.

## 1. Phase Scope

Phase 58 adds deterministic code fact chains for V2.8 architecture readability:

- HTTP route chains
- MCP tool chains
- CLI command chains
- configuration/runtime boundaries
- import dependency clusters as non-runtime dependency context
- test reference chains

The phase does not claim full call graph, data flow, control flow, runtime tracing, type inference, or design-intent recovery.

## 2. Implemented Public Surface

### HTTP

- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/code-fact-chains`

### MCP

- `knowledge_code_architecture_code_fact_chains_build`
- `knowledge_code_architecture_code_fact_chains`

### CLI

- `knowledge code architecture chains-build`
- `knowledge code architecture chains`

## 3. Artifact Contract

Phase 58 writes:

- `workspace/assets/codebase/{codebase_id}/architecture/docs/architecture_code_fact_chains.jsonl`
- `workspace/assets/codebase/{codebase_id}/architecture/docs/architecture_runtime_boundaries.jsonl`

Every accepted chain requires source evidence with repo-relative file paths and line ranges. Chains without sufficient line evidence are not promoted to accepted status and must carry `needs_review`.

## 4. Automated Test Evidence

| Command | Result |
| --- | --- |
| `pytest backend/tests/test_v2_8_reading_dashboard.py -q` | Passed: 7 tests |
| `pytest backend/tests/test_public_surface_guard.py -q` | Passed: 5 tests |
| `python3 -m py_compile backend/data_service/code_assets/architecture/code_fact_chains.py backend/data_service/code_assets/architecture/service.py backend/data_service/code_assets/architecture/persistence.py backend/app/api/v1/code_assets_architecture.py backend/data_service/mcp_code_architecture_tools.py backend/data_service/cli_code_architecture.py` | Passed |
| `git diff --check -- ...` | Passed |

The public surface guard was updated to account for the two new HTTP routes and two new MCP tools. It also preserves existing V1/V2 route compatibility checks.

## 5. Real Repo E2E Evidence

### data_service

Input workspace:

- Workspace root: `/private/tmp/data_service_v28_real_e2e/ws`
- Workspace id: `v28_real`
- Codebase id: `data_service_v28_real`

Observed result:

```json
{
  "chain_count": 405,
  "boundary_count": 5,
  "chain_types": [
    "cli_command_chain",
    "http_route_chain",
    "mcp_tool_chain",
    "test_reference_chain"
  ],
  "boundary_types": [
    "cli",
    "http_server",
    "local_file_storage",
    "mcp_stdio",
    "test_runtime"
  ],
  "accepted": 325,
  "needs_review": 80
}
```

Acceptance notes:

- HTTP, MCP, and CLI chain types were generated.
- Runtime boundary types include HTTP server, MCP stdio, CLI, local file storage, and test runtime.
- Accepted chains are backed by source evidence.
- Public payload did not expose `/Users/Zhuanz` or `/private/tmp` paths.

### HarnessOS

Input workspace:

- Workspace root: `/private/tmp/harnessos_v28_real_e2e/ws`
- Workspace id: `harnessos_v28_real`
- Codebase id: `harnessos_v28_real`

Observed result:

```json
{
  "chain_count": 178,
  "boundary_count": 3,
  "chain_types": [
    "mcp_tool_chain",
    "test_reference_chain"
  ],
  "boundary_types": [
    "local_file_storage",
    "mcp_stdio",
    "test_runtime"
  ],
  "accepted": 0,
  "needs_review": 178
}
```

Acceptance notes:

- HarnessOS generated real chain artifacts from the existing snapshot/inventory/symbol/evidence baseline.
- The generated chains were not promoted to accepted status because surface source line evidence was missing.
- The dominant needs-review reason is `MISSING_SURFACE_LINE_EVIDENCE`.
- This is treated as a valid unresolved real-project result, not as accepted architecture evidence.
- Public payload did not expose `/Users/Zhuanz` or `/private/tmp` paths.

## 6. PRD / Spec Review

Phase 58 matches the V2.8 PRD requirement to improve code fact readability without overclaiming code-derived architecture intent.

Confirmed:

- Deterministic code fact chains are generated from existing code artifacts.
- Accepted chains require line-level evidence.
- Unresolved chains remain visible instead of being hidden.
- Import dependency context is not claimed as runtime calls.
- Public surfaces are exposed through HTTP, MCP, and CLI.

Not claimed:

- Full call graph
- Data flow
- Control flow
- Runtime topology
- Type inference
- Complete architectural design reconstruction

## 7. False-Green Review

Rejected false-green patterns:

- Empty chains marked as success.
- HarnessOS unresolved chains promoted to accepted evidence.
- Token/name overlap treated as runtime relationship.
- Imported modules treated as runtime calls.
- Missing source line ranges hidden from public output.
- Absolute local paths exposed in public payload.

No fatal or major false-acceptance risk remains for Phase 58.

## 8. Open Findings

| Severity | Finding | Status |
| --- | --- | --- |
| Minor | HarnessOS currently lacks accepted code fact chains because public surface line evidence is missing. | Tracked as needs-review output; not a Phase 58 blocker because it is not falsely accepted. |

## 9. Phase 58 Decision

Phase 58 is accepted.

The accepted capability is strongest for repositories with deterministic HTTP/MCP/CLI source evidence, demonstrated by `data_service`. Repositories without line-level surface evidence, demonstrated by HarnessOS, produce explicit `needs_review` chains rather than unsupported accepted claims.
