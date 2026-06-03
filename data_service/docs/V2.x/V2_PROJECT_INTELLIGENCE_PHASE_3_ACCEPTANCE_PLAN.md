# V2 Phase 3 Acceptance Plan: Public Surface Inventory

> Phase: 3 / Public Surface Inventory.
> Acceptance requires real data. Mock-only acceptance is not valid.

## 1. Real Data Scope

Real codebase:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

The E2E flow must use a Phase 1 imported codebase and a Phase 2 snapshot generated from the current repo.

## 2. Required E2E Flow

1. Create a temporary workspace.
2. Import the current repo as a codebase.
3. Generate a Phase 2 snapshot.
4. Generate Phase 3 inventory from that snapshot.
5. Read inventory through HTTP.
6. Read inventory through MCP.
7. Read inventory through CLI.
8. Inspect `surfaces.jsonl`, `capabilities.jsonl`, `alignment_matrix.json`, and `inventory_summary.json` on disk.
9. Verify V1 source registry is unchanged.

## 3. Required Golden Surface Assertions

HTTP golden samples:

- `POST /api/workspaces/{workspace_id}/codebases`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots`
- `POST /api/workspaces/{workspace_id}/sources`
- `POST /api/workspaces/{workspace_id}/build/start`
- `POST /api/workspaces/{workspace_id}/query`
- `GET /api/workspaces/{workspace_id}/graph/neighbors`
- legacy `/api/v1/knowledge/query`

MCP golden samples:

- `knowledge_codebase_import`
- `knowledge_codebase_snapshot`
- `knowledge_source_import`
- `knowledge_build_start`
- `knowledge_query_v2`
- `knowledge_quality_summary`
- `knowledge_graph_neighbors`

CLI golden samples:

- `knowledge code import`
- `knowledge code snapshot`
- `knowledge source import`
- `knowledge build start`
- `knowledge query`
- `knowledge quality summary`
- `knowledge graph neighbors`

## 4. Coverage Thresholds

- MCP inventory count must equal `len(all_tool_specs())`.
- HTTP target route count must be at least the current target route baseline after Phase 2.
- CLI command inventory must include all current `knowledge` top-level and nested commands.
- Golden capabilities must be merged correctly across HTTP / MCP / CLI:
  - `codebase_import`
  - `codebase_snapshot`
  - `source_import`
  - `query`
  - `build`
  - `quality`
  - `graph`
  - `source_trace`
- `unresolved_ratio` must be reported; unresolved entries must include `unresolved_reason`.

## 5. Public Contract Assertions

- No public response contains absolute repo or workspace paths.
- All surface `source_file` values are repo-relative.
- All deterministic source locations include `line_range`.
- Missing line ranges require `unresolved_reason`.
- Dynamic or ambiguous capability inference must use low confidence and not count as a successful merge.
- Frontend page/API usage inventory is best effort and may not block Phase 3 unless it breaks artifact schema or public response shape.

## 6. Failure Paths

Must test:

- missing snapshot ID
- unknown codebase ID
- corrupted or missing snapshot artifact
- inventory generation from an archived workspace is blocked
- invalid `surface_type` filter is rejected or returns a controlled blocked response
- no empty artifact is accepted as success

## 7. Suggested Commands

Focused Phase 3:

```bash
python3 -m pytest backend/tests/test_v2_codebase_inventory.py
```

Contract regression:

```bash
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py
```

Full backend before acceptance:

```bash
python3 -m pytest backend/tests
```

Frontend build is required if frontend contract files changed:

```bash
npm run build --prefix frontend
```

## 8. Acceptance Decision

Phase 3 passes only if:

- all focused tests pass
- current repo E2E passes
- artifacts are inspected from disk
- golden surface samples are present
- MCP count equals `all_tool_specs()`
- capability taxonomy merges golden capabilities correctly
- HTTP/MCP/CLI read results agree on stable IDs, counts, and artifact refs
- no absolute path leak is found
- source registry remains unchanged
- full backend regression passes
- Phase 3 audit report has no open fatal or major findings

## 9. Artifact Inspection Requirements

The acceptance report must include excerpts or summaries from disk-read artifacts:

- total rows in `surfaces.jsonl`
- total rows in `capabilities.jsonl`
- `alignment_matrix.json` capability keys
- `inventory_summary.json` surface counts and `golden_checks`
- at least one HTTP, MCP, and CLI surface record

Empty files, malformed JSONL, or in-memory-only results are hard failures.

## 10. PRD Spec Review Checklist

The Phase 3 audit report must explicitly answer:

- Does the inventory cover HTTP routes, MCP tools, and CLI commands?
- Does MCP count match the live registry?
- Are golden V1/V2 capabilities present?
- Are target and legacy HTTP routes separated?
- Is frontend inventory clearly marked best-effort?
- Are unresolved surfaces reported rather than silently dropped?
- Does the phase avoid Python symbol indexing and evidence trace claims?

Any negative answer must be classified as fatal, major, minor, or note before acceptance.

## 11. False Acceptance Rejection Rules

Reject acceptance if:

- inventory is non-empty but golden samples are missing
- MCP count is hardcoded instead of derived from live specs
- capability IDs are inconsistent across HTTP/MCP/CLI for golden capabilities
- line ranges are fabricated without source evidence
- frontend extraction incompleteness is hidden rather than marked best-effort
- public responses include absolute paths
- source registry changes during inventory generation
