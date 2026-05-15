# Phase V1.6-B3 Build Target HTTP Report

更新时间：2026-05-13

## 1. Scope

V1.6-B3 只开放 build lifecycle 的最小 target HTTP surface。

本阶段实现：

- `POST /api/workspaces/{workspace_id}/build/start`
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`

本阶段不处理 graph advanced/session/quality target HTTP，不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不修改 `/api/v1/knowledge/*` compatibility routes，不修改 V1.5/B1/B2 已 accepted routes。

## 2. Baseline

V1.5 accepted baseline remains immutable：

- MCP tool count：`40`
- CLI top-level commands：`build / graph / quality / query / source / trace / workspace`
- target HTTP baseline：exactly 3 routes
  - `POST /api/workspaces/{workspace_id}/query`
  - `POST /api/workspaces/{workspace_id}/distill`
  - `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- compatibility HTTP：`/api/v1/knowledge/*` retained
- `/knowledge` remains service governance console

V1.6-A Public Surface Guard：accepted。

V1.6-B1 Workspace Target HTTP：accepted。

V1.6-B2 Source Target HTTP：accepted。

Pre-B3 current target HTTP route count：`11`。

## 3. Phase Overlay

B3 uses phase overlay instead of modifying the V1.5 baseline.

Overlay file：

- `docs/V1.6/public-surface-overlays/v1_6_b3.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/build/start`
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`

Allowed MCP tool additions：none。

Allowed CLI command additions：none。

Allowed compatibility HTTP additions：none。

## 4. Implemented Routes

### `POST /api/workspaces/{workspace_id}/build/start`

Starts a build operation using the existing operation lifecycle, operation registry and build worker queue.

Contract notes：

- request：`mode`, `paths`
- mode is limited to existing build modes
- paths reuse existing source path allowlist validation
- archived workspace returns blocked envelope
- returns a real `operation_id`
- does not create fake operation IDs
- does not create source records
- default response uses stable operation metadata only

### `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`

Reads one build operation status from the workspace operation registry.

Contract notes：

- unknown `workspace_id` returns HTTP 404
- unknown or cross-workspace `operation_id` returns blocked envelope
- queued operation behavior reuses the existing worker lifecycle
- default response does not expose filesystem path/layout

### `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`

Requests cancellation through the existing operation lifecycle.

Contract notes：

- queued operation is marked `cancelled`
- non-terminal running operation records `cancel_requested`
- terminal operation returns existing terminal status with warning
- unknown or cross-workspace `operation_id` returns blocked envelope
- default response does not expose filesystem path/layout

## 5. Build Contract Summary

Stable external fields：

- `workspace_id`
- `operation_id`
- `status`
- `mode`
- `stage`
- `progress`
- `created_at`
- `updated_at`
- `started_at`
- `completed_at`
- `artifact_refs`
- envelope `warnings`
- envelope `next_actions`
- normalized error detail for unknown operation and validation failures

Default target HTTP responses do not expose:

- `workspace_path`
- `root_path`
- `filesystem_path`
- `source_path`
- `original_path`
- `artifact_physical_path`
- `workspace_layout`
- `artifact_layout`
- `internal_path`
- `debug_paths`
- `cache_path`
- `physical_path`
- `local_path`
- raw traceback

Build may run existing internal pipeline stages such as LLMWiki, GraphRAG, summary and diagnostics. B3 does not open graph/session/quality target HTTP routes or public contracts.

Compatibility build routes remain retained and usable.

## 6. Public Surface Scan Result

### MCP

- baseline count：`40`
- current count：`40`
- diff：none
- new MCP tools：none

### CLI

- baseline top-level commands：`build / graph / quality / query / source / trace / workspace`
- current top-level commands：`build / graph / quality / query / source / trace / workspace`
- top-level diff：none
- nested command diff：none
- new CLI commands/subcommands：none

### HTTP

Target HTTP baseline：3 routes。

B1 accepted additions：4 routes。

B2 accepted additions：4 routes。

B3 allowed additions：3 routes。

Current target HTTP surface：14 routes。

Current route inventory：

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`
- `POST /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`
- `POST /api/workspaces/{workspace_id}/build/start`
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`
- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

Diff from V1.5 target baseline：exactly B1 + B2 + B3 overlays。

Diff from expected current surface：none。

New non-B3 HTTP routes：none。

Compatibility HTTP route diff：none。

## 7. Focused Tests

Focused test file：

- `backend/tests/test_target_http_build.py`

Coverage：

- build start/status/cancel
- real operation_id and operation registry
- unknown workspace/operation
- cross-workspace operation isolation
- archived workspace behavior
- invalid mode and path allowlist validation
- path traversal rejection
- build start does not create source records
- terminal cancel behavior
- no default internal path/layout leakage
- compatibility build routes retained
- source trace route unchanged
- auth/security smoke

## 8. Regression Results

- public surface guard：`5 passed`
- B3 focused tests：`4 passed`
- B2 focused tests：`5 passed`
- B1 focused tests：`5 passed`
- API regression：`34 passed`
- MCP regression：`32 passed`
- combined data_service/API/MCP regression：`137 passed`
- frontend `npm run build`：not touched
- drawio XML validation：passed (`drawio xml ok`)

## 9. Documentation Sync

Updated documents：

- `docs/V1.6/README.md`
- `docs/V1.6/development-plan.md`
- `docs/V1.6/acceptance-plan.md`
- `docs/V1.6/current-vs-target-gap.md`
- `docs/V1.6/current-vs-target-gap.drawio`
- `docs/V1.6/target-architecture.md`
- `docs/V1.6/target-http-routes-plan.md`
- `docs/V1.6/interface-convergence-plan.md`
- `docs/V1.6/public-surface-baseline.md`

Added：

- `docs/V1.6/public-surface-overlays/v1_6_b3.json`
- `docs/V1.6/PHASE-V1.6-B3-BUILD-TARGET-HTTP-REPORT-2026-05-13.md`

Documentation sync result：

- V1.5 public surface baseline remains immutable.
- B1/B2/B3 additions are recorded as phase overlays / allowed additions.
- graph advanced target HTTP remains planned.
- session target HTTP remains planned.
- quality write target HTTP remains planned.
- V1.6-C/D/E/F remain planned / candidate.
- MCP graph/session tools remain V1.5 baseline tools, not V1.6-B3 additions.
- `/knowledge` remains service governance console.

## 10. Blocking Issues

none

## 11. Final Decision

accepted

V1.6-B3 Build Target HTTP is accepted.

## 12. Next Phase Recommendation

Next phase：`V1.6-C1 Graph Neighbors Target HTTP / CLI Minimal Surface`

Do not enter full V1.6-C all at once. Do not open graph/session/quality together.
