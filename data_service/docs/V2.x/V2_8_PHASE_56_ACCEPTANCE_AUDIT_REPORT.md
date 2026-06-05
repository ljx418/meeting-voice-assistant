# V2.8 Phase 56 Acceptance Audit Report

> Generated from repository implementation and validation.
> Business code was modified only for V2.8 Phase 56 public views and tests.
> Accepted claims below are backed by focused tests and real-repository E2E runs.

## 1. Scope

Phase 56 implements the V2.8 human-readable architecture dashboard layer.

Implemented scope:

- Persisted V2.8 dashboard artifact under `architecture/v2_8/`.
- Human-readable HTML dashboard with six required chart sections.
- Mermaid relationship summary view.
- HTTP read/build endpoints under an explicit V2.8 namespace.
- MCP build/read/view tools.
- CLI build/read/view commands.
- Focused tests for HTML escaping, artifact persistence, HTTP/MCP/CLI parity, and missing prerequisite errors.

Compatibility note:

- Existing `/architecture/views/build` remains the V2.6 large-project view route.
- V2.8 uses `/architecture/v2_8/views/build`, `/architecture/v2_8/views`, and `/architecture/v2_8/views/{view_id}` to avoid changing V2.6 semantics.

## 2. Implemented Files

- `backend/data_service/code_assets/architecture/reading_dashboard.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/data_service/code_assets/architecture/persistence.py`
- `backend/data_service/code_assets/architecture/service.py`
- `backend/app/api/v1/code_assets_architecture.py`
- `backend/data_service/mcp_code_architecture_tools.py`
- `backend/data_service/cli_code_architecture.py`
- `backend/tests/test_v2_8_reading_dashboard.py`
- `backend/tests/test_data_service_mcp.py`
- `backend/tests/test_public_surface_guard.py`
- `backend/tests/test_session_ingest_query_build_contract_plan.py`

## 3. Acceptance Evidence

Focused tests:

```text
pytest backend/tests/test_v2_8_reading_dashboard.py -q
3 passed
```

Regression tests:

```text
pytest backend/tests/test_v2_7_architecture_reconstruction.py backend/tests/test_v2_8_reading_dashboard.py -q
6 passed
```

Public surface guards:

```text
pytest backend/tests/test_public_surface_guard.py::test_v16_current_http_route_inventory_matches_v15_baseline_plus_accepted_overlays -q
1 passed

pytest backend/tests/test_public_surface_guard.py::test_v16a_mcp_registry_matches_v15_public_surface_baseline -q
1 passed

pytest backend/tests/test_public_surface_guard.py::test_v16a_knowledge_cli_parser_matches_v15_public_surface_baseline -q
1 passed

pytest backend/tests/test_session_ingest_query_build_contract_plan.py::test_v16d3_d4_d5_d6_surface_accepts_e_quality_minimal_routes_only -q
1 passed
```

Compile and formatting checks:

```text
python3 -m py_compile backend/data_service/code_assets/architecture/reading_dashboard.py backend/data_service/code_assets/architecture/service.py backend/data_service/mcp_code_architecture_tools.py backend/data_service/cli_code_architecture.py backend/app/api/v1/code_assets_architecture.py
passed

git diff --check -- <changed files>
passed
```

MCP registry contract:

```text
pytest backend/tests/test_data_service_mcp.py::test_data_service_mcp_tool_registry_contract -q
skipped because optional mcp package is not installed in this environment
```

The public-surface guard still validates the tool registry without requiring the optional `mcp` package.

## 4. Real Repository E2E

### data_service

```json
{
  "codebase_id": "data_service_v28_real",
  "snapshot_id": "snap_16d6d37d11810492ffbe",
  "files": 710,
  "docs": 367,
  "claims": 21665,
  "findings": 1063,
  "alignments": 21865,
  "drift": 17079,
  "target_nodes": 180,
  "current_nodes": 180,
  "dashboard_charts": 6,
  "dashboard_hotspots": 80,
  "dashboard_exists": true,
  "html_exists": true,
  "mmd_exists": true,
  "html_has_charts": true,
  "html_no_script": true,
  "html_no_repo_path": true,
  "mmd_no_repo_path": true
}
```

### HarnessOS

```json
{
  "codebase_id": "harnessos_v28_real",
  "snapshot_id": "snap_44f4b5bde991e2f0dd81",
  "files": 2086,
  "docs": 678,
  "claims": 18798,
  "findings": 1716,
  "alignments": 18998,
  "drift": 17212,
  "target_nodes": 180,
  "current_nodes": 180,
  "dashboard_charts": 6,
  "dashboard_hotspots": 80,
  "dashboard_exists": true,
  "html_exists": true,
  "mmd_exists": true,
  "html_has_charts": true,
  "html_no_script": true,
  "html_no_repo_path": true,
  "mmd_no_repo_path": true
}
```

## 5. PRD / Spec Review

Phase 56 satisfies the V2.8 PRD requirement for a more readable human-facing architecture dashboard.

Confirmed:

- The dashboard consumes persisted V2.7 artifacts and does not rescan or invent architecture facts.
- HTML contains the required chart sections:
  - `architecture_overview`
  - `capability_map`
  - `doc_code_drift_map`
  - `quality_severity`
  - `evidence_coverage`
  - `hotspot_table`
- HTML and Mermaid output escape untrusted text and do not expose absolute repository paths.
- HTTP/MCP/CLI all read the same persisted V2.8 artifact.

Known compatible deviation:

- The PRD used `/architecture/views/build` as the generic V2.8 example route, but that route is already the V2.6 large-project view build endpoint in the current codebase.
- Phase 56 intentionally uses `/architecture/v2_8/views/build` to avoid changing existing V2.6 behavior.

Assessment: compatible deviation, not a major PRD drift.

## 6. False-Acceptance Review

Rejected false-green risks:

- HTML generated from mock-only data: rejected by data_service and HarnessOS real-repo E2E.
- Empty dashboard accepted: rejected by chart count and node count assertions.
- Hidden script/path leakage: rejected by focused tests and real E2E checks.
- HTTP-only completion: rejected by HTTP/MCP/CLI tests.
- V2.6 route behavior silently changed: avoided by dedicated V2.8 route namespace.

## 7. Audit Conclusion

Phase 56 is accepted.

No fatal or major PRD/spec deviation remains for Phase 56.

Phase 57 may proceed after its phase-specific pre-implementation audit confirms graph aggregation consumes persisted V2.8/V2.7 artifacts and does not generate unsupported architecture relationships.
