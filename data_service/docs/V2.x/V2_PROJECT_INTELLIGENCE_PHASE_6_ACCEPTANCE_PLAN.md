# V2 Phase 6 Acceptance Plan: HTTP/MCP/CLI Read API Convergence

> Phase: 6 / HTTP, MCP, and CLI read convergence.
> Status: pre-development acceptance plan.

## 1. Required E2E Flow

Use real repository data:

1. Create managed workspace in a temp root.
2. Import `/Users/Zhuanz/Desktop/workspace/data_service` as codebase.
3. Create Phase 2 snapshot.
4. Build Phase 3 inventory.
5. Build Phase 4 symbol index.
6. Build Phase 5 trace artifacts.
7. Read each major artifact through HTTP.
8. Read the same artifact through MCP.
9. Read the same artifact through CLI.
10. Compare V2 read envelopes.
11. Compare missing-artifact error envelopes.
12. Inspect disk artifacts.
13. Run V1/V2 regression tests.

## 2. Required Convergence Targets

Convergence must cover:

```text
codebase describe
snapshot read
inventory read
surface list
capability list
symbol search
import list
surface trace
capability trace
evidence list
```

## 3. Success Envelope Assertions

For HTTP/MCP/CLI V2 read outputs:

- `ok` is `true`
- `schema_version` is `v2.0`
- `workspace_id` matches
- `codebase_id` matches
- `snapshot_id` matches for snapshot-scoped artifacts
- `artifact_refs` are sorted and equal where interfaces expose the same artifact
- item counts match
- stable IDs match
- warning counts match
- unresolved counts match
- public payloads do not contain absolute repo/workspace paths

Stable IDs to compare:

- `codebase_id`
- `snapshot_id`
- `surface_id`
- `capability_id`
- `symbol_id`
- `import_id`
- `mapping_id`
- `evidence_id`

## 4. Error Envelope Assertions

For HTTP/MCP/CLI missing-artifact or invalid-request outputs:

- `ok` is `false`
- `schema_version` is `v2.0`
- `error.code` is stable
- `error.message` is non-empty
- `error.retryable` is boolean
- `next_actions` is non-empty when the caller can repair the issue
- no absolute path leaks

Required error cases:

- inventory read before inventory exists
- symbol search before symbol index exists
- trace read before trace exists
- trace read without `surface_id` or `capability`
- unknown codebase
- invalid limit

## 5. HTTP Acceptance

HTTP may preserve the current outer envelope if required by existing target HTTP compatibility tests, but must expose a V2 read envelope in a stable location.

Required assertions:

- current target HTTP tests remain green
- V2 read envelope is present for code asset read APIs
- error code matches MCP/CLI for the same missing artifact
- no `debug_paths` in public response

## 6. MCP Acceptance

Required tools:

```text
knowledge_codebase_describe
knowledge_codebase_snapshot
knowledge_project_inventory
knowledge_code_symbol_search
knowledge_public_surface_trace
```

Assertions:

- MCP direct output exposes the V2 read envelope
- success/error fields match HTTP/CLI convergence fixture
- no legacy V2 wrapper tools are added for code asset reads

## 7. CLI Acceptance

Required commands:

```text
knowledge code describe
knowledge code snapshot
knowledge code inventory
knowledge code symbols
knowledge code trace
```

Assertions:

- stdout is valid JSON
- stderr has no JSON contract data
- exit code remains `0` for controlled blocked/error envelopes and non-zero only for parser/runtime failures
- success/error fields match HTTP/MCP convergence fixture

## 8. Regression Suite

Minimum:

```bash
python3 -m pytest backend/tests/test_v2_codebase_interface_convergence.py
python3 -m pytest backend/tests/test_v2_codebase_trace.py backend/tests/test_v2_codebase_symbols.py backend/tests/test_v2_codebase_inventory.py backend/tests/test_v2_codebase_snapshot.py
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py
python3 -m pytest backend/tests
```

If frontend contract files change:

```bash
npm run build --prefix frontend
```

## 9. PRD Review Checklist

- Does Phase 6 satisfy the V2.0 requirement for HTTP/MCP/CLI read convergence?
- Does it cover both success and error envelope shapes?
- Does it preserve V1 compatibility?
- Does it avoid adding new artifact semantics?
- Does it keep Project Overview and Agent Context Pack out of scope?
- Does it avoid frontend-only or mock-only acceptance?

## 10. False Acceptance Checks

Fatal if any are true:

- only HTTP is tested
- only success responses are compared
- comparison ignores stable IDs and item counts
- CLI stdout is not valid JSON
- HTTP/MCP/CLI use different error codes for the same missing artifact
- V2 envelope exists only in tests and not in public outputs
- output leaks absolute repo/workspace paths
- implementation mutates source registry
- implementation breaks existing V1 target HTTP or MCP contracts
