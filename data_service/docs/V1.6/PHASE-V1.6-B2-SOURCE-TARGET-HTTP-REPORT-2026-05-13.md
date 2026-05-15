# Phase V1.6-B2 Source Target HTTP Report

更新时间：2026-05-13

## 1. Scope

V1.6-B2 只开放 source lifecycle 的最小 target HTTP surface。

本阶段实现：

- `POST /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`

本阶段不处理 build/graph/session/quality target HTTP，不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不修改 `/api/v1/knowledge/*` compatibility routes，不修改 V1.5 source trace target HTTP contract。

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

Pre-B2 current target HTTP route count：`7`。

## 3. Phase Overlay

B2 uses phase overlay instead of modifying the V1.5 baseline.

Overlay file：

- `docs/V1.6/public-surface-overlays/v1_6_b2.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`

Allowed MCP tool additions：none。

Allowed CLI command additions：none。

Allowed compatibility HTTP additions：none。

## 4. Implemented Routes

### `POST /api/workspaces/{workspace_id}/sources`

Imports file or text sources by reusing the existing source lifecycle handler.

Contract notes：

- request：`paths`, `texts`, `metadata`
- supports only request fields already supported by the existing source helper
- uses existing path allowlist validation
- does not trigger build, GraphRAG, session graph or quality write
- synchronous operation; no fake `operation_id`
- default response uses stable source metadata only

### `GET /api/workspaces/{workspace_id}/sources`

Lists source registry items for one workspace.

Contract notes：

- query：`status`, `limit`
- response contains stable source item list
- default response does not expose filesystem path/layout
- list does not trigger scan/build/index

### `GET /api/workspaces/{workspace_id}/sources/{source_id}`

Describes one source in the workspace registry.

Contract notes：

- unknown `workspace_id` returns HTTP 404 with normalized error detail
- unknown or cross-workspace `source_id` returns HTTP 404 with normalized error detail
- response contains stable source metadata only
- source trace route remains separate and unchanged

### `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`

Soft-removes one source by reusing the existing source lifecycle semantics.

Contract notes：

- request：optional `reason`
- non-destructive; does not delete original files
- repeated remove follows existing lifecycle semantics and returns removed state
- archived workspace remove remains blocked through existing lifecycle rules
- does not trigger build, GraphRAG, session graph or quality write

## 5. Contract Summary

Stable external fields：

- `workspace_id`
- `source_id`
- `status`
- `ingest_status`
- `title`
- `metadata`
- `created_at`
- `updated_at`
- `artifact_ref`
- envelope `status`
- normalized error detail for unknown workspace/source and validation failures

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

Compatibility routes remain retained and usable.

The V1.5 source trace target HTTP route remains unchanged and is not counted as a B2 addition.

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

B2 allowed additions：4 routes。

Current target HTTP surface：11 routes。

Current route inventory：

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`
- `POST /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`
- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

Diff from V1.5 target baseline：exactly B1 + B2 overlays。

Diff from expected current surface：none。

New non-B2 HTTP routes：none。

Compatibility HTTP route diff：none。

## 7. Focused Tests

Focused test file：

- `backend/tests/test_target_http_source.py`

Coverage：

- source file import and text import
- source list/describe/remove
- unknown workspace/source
- cross-workspace source isolation
- archived workspace import/remove behavior
- path allowlist and path traversal rejection
- duplicate import behavior
- default response no internal path/layout leakage
- compatibility source routes retained
- no build/graph/session/quality side effects
- source trace target HTTP unchanged
- auth/security smoke

## 8. Regression Results

- public surface guard：`5 passed`
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
- `docs/V1.6/target-http-routes-plan.md`
- `docs/V1.6/interface-convergence-plan.md`
- `docs/V1.6/public-surface-baseline.md`

Added：

- `docs/V1.6/public-surface-overlays/v1_6_b2.json`
- `docs/V1.6/PHASE-V1.6-B2-SOURCE-TARGET-HTTP-REPORT-2026-05-13.md`

Documentation sync result：

- V1.5 public surface baseline remains immutable.
- B1 and B2 additions are recorded as phase overlays / allowed additions.
- build target HTTP remains planned.
- graph/session/quality target HTTP remain planned.
- V1.6-B3/C/D/E/F remain planned / candidate.
- MCP graph/session tools remain V1.5 baseline tools, not V1.6-B2 additions.
- `/knowledge` remains service governance console.
- source import is documented as not triggering build/graph/session/quality.

## 10. Blocking Issues

none

## 11. Final Decision

accepted

V1.6-B2 Source Target HTTP is accepted.

## 12. Next Phase Recommendation

Next phase：`V1.6-B3 Build Target HTTP`

Do not enter graph/session/quality target HTTP next. Do not open all remaining target HTTP routes at once.
