# V2 Phase 5 Acceptance Plan: Surface-to-Symbol Mapping + Evidence Trace

> Phase: 5 / Surface-to-Symbol Mapping + Code Evidence Trace.
> Status: pre-development acceptance plan.

## 1. Required E2E Flow

Use real repository data:

1. Create managed workspace in a temp root.
2. Import `/Users/Zhuanz/Desktop/workspace/data_service` as codebase.
3. Create Phase 2 snapshot.
4. Build Phase 3 inventory.
5. Build Phase 4 symbol index.
6. Build Phase 5 mapping/evidence trace.
7. Read trace by HTTP surface.
8. Read trace by HTTP capability.
9. Read trace by MCP.
10. Read trace by CLI.
11. Inspect disk artifacts.
12. Run V1/V2 regression tests.
13. Complete PRD/spec review and false acceptance review.

## 2. Required Artifacts

The following files must exist and be non-empty:

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mappings.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/evidence.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mapping_summary.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/trace_index.json
```

## 3. Contract Assertions

### Mappings

- `mapping_count > 0`
- every mapping has `mapping_id`, `from_type`, `from_id`, `relation`, `confidence`, and `extractor`
- successful mappings have `confidence >= 0.80`
- mappings below `0.80` are unresolved and not counted as successful
- unresolved mappings include one stable `unresolved_reason`
- mapping IDs are stable across repeated builds

### Evidence

- `evidence_count > 0`
- every evidence span has `path`, `start_line`, `end_line`, `confidence`, and at least one of `surface_id`, `symbol_id`, or `capability_id`
- evidence paths are repo-relative
- line ranges are 1-based inclusive
- at least 10 evidence spans are automatically sampled and validated:
  - path exists under real repo root
  - `start_line` and `end_line` are in range
  - source snippet is non-empty
  - snippet contains expected route/tool/command/symbol hint when expected metadata is present

### Coverage

`mapping_summary.json` must include:

```text
mapping_coverage_by_surface_type.http_api
mapping_coverage_by_surface_type.mcp_tool
mapping_coverage_by_surface_type.cli_command
evidence_coverage_by_capability.source_import
evidence_coverage_by_capability.query
evidence_coverage_by_capability.build
evidence_coverage_by_capability.quality
evidence_coverage_by_capability.graph
evidence_coverage_by_capability.source_trace
evidence_coverage_by_capability.codebase_import
success_mapping_confidence_min = 0.80
unresolved_reason_counts
```

Golden capability coverage is accepted if each golden capability has at least one surface and at least one verified evidence span, or has a documented `needs_review` only when the relevant public surface is absent from Phase 3 inventory.

## 4. Golden Assertions

Trace must cover:

HTTP:

- `POST /api/workspaces/{workspace_id}/codebases`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots`
- `POST /api/workspaces/{workspace_id}/sources`
- `POST /api/workspaces/{workspace_id}/build/start`
- `POST /api/workspaces/{workspace_id}/query`
- `GET /api/workspaces/{workspace_id}/graph/neighbors`

MCP:

- `knowledge_codebase_import`
- `knowledge_codebase_snapshot`
- `knowledge_source_import`
- `knowledge_build_start`
- `knowledge_query_v2`
- `knowledge_quality_summary`
- `knowledge_graph_neighbors`

CLI:

- `knowledge code import`
- `knowledge code snapshot`
- `knowledge source import`
- `knowledge build start`
- `knowledge query`
- `knowledge quality summary`
- `knowledge graph neighbors`

Capabilities:

- `codebase_import`
- `codebase_snapshot`
- `source_import`
- `build`
- `query`
- `quality`
- `graph`
- `source_trace`

## 5. HTTP Acceptance

Required routes:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/evidence
```

Assertions:

- build route returns summary, coverage metrics, and artifact refs
- surface trace returns mappings and evidence for a golden HTTP surface
- capability trace returns surfaces, symbols, mappings, and evidence for `codebase_import`
- evidence list supports `limit`
- unknown codebase returns controlled 404/block
- missing inventory or symbol artifacts returns controlled error with `next_actions`
- no absolute repo/workspace path leaks

## 6. MCP Acceptance

Required tool:

```text
knowledge_public_surface_trace
```

Assertions:

- tool exists in `all_tool_specs()` and stdio list
- `build=true` can create mapping/evidence artifacts from real inventory and symbols
- `surface_id="mcp:knowledge_codebase_import"` returns evidence
- `capability="codebase_import"` returns surfaces, mappings, and evidence
- missing artifacts return blocked with useful `next_actions`
- output does not leak absolute paths

## 7. CLI Acceptance

Required command:

```text
knowledge code trace
```

Assertions:

- `--build` creates artifacts
- read mode returns valid JSON
- `--surface-id mcp:knowledge_codebase_import` returns evidence
- `--capability codebase_import` returns capability trace
- no absolute path leaks
- stdout is JSON; stderr is diagnostics only

## 8. Regression Suite

Minimum:

```bash
python3 -m pytest backend/tests/test_v2_codebase_trace.py
python3 -m pytest backend/tests/test_v2_codebase_symbols.py backend/tests/test_v2_codebase_inventory.py backend/tests/test_v2_codebase_snapshot.py
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py
npm run build --prefix frontend
python3 -m pytest backend/tests
```

## 9. PRD Review Checklist

- Does Phase 5 satisfy US-005 capability-to-evidence trace?
- Does it cover V1 source import, query, build, quality, source trace, graph, and V2 codebase capabilities?
- Does it report mapping/evidence coverage metrics?
- Does it keep Project Overview and Agent Context Pack out of scope?
- Does it avoid claiming call graph, data flow, runtime dispatch, or type inference?
- Does it preserve V2.0/V2.1 boundary?

## 10. False Acceptance Checks

Fatal if any are true:

- trace artifacts are empty but build reports success
- evidence has file names but no real line ranges
- evidence line ranges cannot be read from real source
- fewer than 10 evidence spans are truth-sampled when at least 10 spans exist
- low-confidence mappings are counted as successful
- golden capabilities are omitted without explicit `needs_review`
- HTTP works but MCP/CLI cannot read the same trace
- output leaks absolute repo/workspace paths
- implementation writes to source registry
- implementation claims call graph/type inference/runtime dispatch
