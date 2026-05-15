# Phase V1.6-E3 Quality Correction Review Target HTTP Report

Date: 2026-05-15

## 1. Scope

V1.6-E3 only opens the minimal quality correction review target HTTP surface:

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`

E3 adds no MCP tools, no CLI top-level commands, no CLI nested commands, no correction plan target HTTP, and no quality build target HTTP.

E3 review is review-status-only. `approved` means review approval only; it does not mean `active`, `applied`, read-time governance activation, plan generation, or correction execution.

## 2. Baseline

- V1.5 public surface baseline remains immutable.
- V1.6-A/B/C/D1-D6/E1/E2 are accepted.
- Pre-E3 target HTTP route count: 31.
- MCP tool count: 40.
- CLI top-level commands: `build / graph / quality / query / source / trace / workspace`.
- CLI nested inventory unchanged from E2.
- `/api/v1/knowledge/*` compatibility routes retained.

## 3. Phase Overlay

E3 overlay file:

- `docs/V1.6/public-surface-overlays/v1_6_e3.json`

Allowed target HTTP addition:

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`

Allowed MCP additions: none.
Allowed CLI additions: none.
Allowed compatibility HTTP additions: none.

V1.5 baseline was not modified.

## 4. Implemented Route

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`

The route reuses the quality correction rules storage/projection boundary but uses a review-only helper so that review does not rebuild or update correction plans.

## 5. Contract Summary

- `rule_id` is path-only. Request body `rule_id` is rejected.
- Request body supports review status plus optional non-authoritative reviewer metadata and note.
- `reviewer` from the body is not treated as authenticated identity.
- Supported review status is limited to existing review/lifecycle states: `draft`, `approved`, `rejected`, `archived`, `revoked`.
- `active` and `applied` request status is rejected.
- Rules already in `active` or `applied` state reject review transitions.
- Terminal transition behavior is fixed by focused tests: approved-to-approved, approved-to-rejected, rejected-to-approved, archived-to-approved, revoked-to-approved, and active/applied transitions.
- `correction_plan_summary` is not returned by default.
- No correction plan is generated, rebuilt, or updated.
- No read-time governance state is activated.
- No correction execution occurs.
- Source, wiki, graph, and session artifacts are unchanged by review.
- No build/session operation is created.
- Responses use stable correction rule projection and do not expose internal path/layout.

## 6. Public Surface Scan

- Target HTTP count after E3: 32.
- New target HTTP route: exactly the E3 review route.
- MCP diff: none.
- CLI top-level diff: none.
- CLI nested diff: none.
- Correction plan target HTTP: not opened.
- Quality build target HTTP: not opened.
- Undeclared routes: none.
- Compatibility HTTP retained.

## 7. Tests and Regressions

Focused E3 tests cover:

- route existence and successful review;
- body `rule_id` rejection;
- unsupported request fields rejection;
- status validation and terminal transitions;
- cross-workspace rule isolation;
- archived workspace blocked envelope;
- no correction plan creation/update;
- no read-time governance activation;
- source/wiki/graph/session artifact fingerprints unchanged;
- no build/session operation creation;
- no correction execution;
- no correction plan/build target HTTP;
- API key boundary behavior;
- path/layout leakage guard.

Regression commands run:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_review.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_correction_rules.py -q`
- `python3 -m pytest backend/tests/test_target_http_quality_feedback.py -q`
- `python3 -m pytest backend/tests/test_target_http_session_build.py -q`
- `python3 -m pytest backend/tests/test_target_http_session_query.py -q`
- `python3 -m pytest backend/tests/test_target_http_session_ingest.py -q`
- `python3 -m pytest backend/tests/test_target_http_session_lifecycle.py -q`
- `python3 -m pytest backend/tests/test_data_service_api.py -q`
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q`
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"`

Frontend build: not touched.

## 8. Documentation Sync

Updated V1.6 documents distinguish:

- immutable V1.5 baseline;
- accepted B/C/D/E1/E2/E3 overlays;
- current target HTTP route count = 32;
- E3 review-only semantics;
- correction plan/build routes remain planned / not opened;
- V1.6-F remains planned.

`current-vs-target-gap.md` and `current-vs-target-gap.drawio` were synchronized.

## 9. Blocking Issues

None.

## 10. Final Decision

accepted

## 11. Next Phase Recommendation

Next phase should be V1.6-E4 Quality Correction Plan Target HTTP Minimal Surface.

Do not combine correction plan with quality build or console polish.
