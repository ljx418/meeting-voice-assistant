# V1.6-E2 Quality Correction Rules Target HTTP Report

Date: 2026-05-15

## 1. Scope

V1.6-E2 only opens the minimal quality correction rules target HTTP surface:

- `GET /api/workspaces/{workspace_id}/quality/correction-rules`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`

E2 does not add MCP tools, CLI top-level commands, CLI nested commands, correction review target HTTP, correction plan target HTTP, quality build target HTTP, console polish, or any non-E2 route.

## 2. Baseline

- V1.5 immutable baseline remains unchanged.
- V1.6-A/B/C/D1-D6/E1 are accepted.
- Target HTTP pre-E2 route count: 29.
- MCP tool count: 40.
- CLI top-level and nested inventory unchanged.

## 3. Phase Overlay

E2 added `docs/V1.6/public-surface-overlays/v1_6_e2.json` with exactly two allowed target HTTP additions:

- `GET /api/workspaces/{workspace_id}/quality/correction-rules`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`

V1.5 baseline was not modified.

## 4. Implemented Routes

- `GET /api/workspaces/{workspace_id}/quality/correction-rules`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`

## 5. Contract Summary

The list route returns stable correction rule projection only. It does not return raw `correction_rules.json`, internal file paths, or raw storage rows. Missing rules return an empty stable list without triggering correction build.

The write route creates or updates draft correction rules only. `rule_id` is the primary stable identifier. If `artifact_ref` is returned, it uses a non-path `quality-correction-rules://...` reference. `status` is server-controlled and request bodies cannot set `approved`, `active`, `applied`, or other review/application states.

E2 does not review, approve, reject, activate, apply, generate correction plans, execute corrections, trigger read-time governance, trigger build/index/materialization, create operations, or mutate source/wiki/graph/session artifacts.

## 6. Public Surface Scan

- Target HTTP final route count: 31.
- MCP diff: none.
- CLI top-level diff: none.
- CLI nested diff: none.
- No correction review target HTTP.
- No correction plan target HTTP.
- No quality build target HTTP.
- No undeclared routes.
- Compatibility HTTP retained.

## 7. Tests And Regressions

Focused and regression coverage includes:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_quality_correction_rules.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_quality_feedback.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_session_build.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_session_query.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_session_ingest.py -q` - passed.
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q` - passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q` - passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q` - passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q` - passed on rerun.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"` - passed.
- `frontend npm run build` - not touched.

## 8. Documentation Sync

Updated V1.6 README, development plan, acceptance plan, current-vs-target gap, drawio, interface convergence plan, target architecture, target HTTP routes plan, public surface baseline, and minimal quality status references in session contract docs.

E3/E4/F remain planned, not implemented.

## 9. Blocking Issues

None.

## 10. Final Decision

Accepted.

## 11. Next Phase Recommendation

If accepted, next phase should be V1.6-E3 Quality Correction Review Target HTTP Minimal Surface.

Do not combine E3 with correction plan/build or F console polish.
