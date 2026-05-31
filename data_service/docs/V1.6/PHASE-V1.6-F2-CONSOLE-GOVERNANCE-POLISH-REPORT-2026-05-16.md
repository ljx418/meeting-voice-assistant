# Phase V1.6-F2 Console Governance Polish Report

Date: 2026-05-16

## 1. Scope

F2 only updates `/knowledge` governance evidence display.

F2 does not add backend public surface, target HTTP routes, compatibility HTTP routes, MCP tools, CLI top-level commands, or CLI nested commands. F2 is not V1.6 closure acceptance.

## 2. Baseline

- V1.6-E5 accepted.
- V1.6-F1 accepted.
- V1.5 public surface baseline remains immutable.
- current target HTTP count = 35.
- MCP tool count = 40.
- CLI top-level diff = none relative to accepted current baseline.
- CLI nested diff = none relative to accepted current baseline.
- `/api/v1/knowledge/*` compatibility retained.

## 3. Implemented Console Evidence

`/knowledge` governance console now displays:

- V1.5 immutable baseline summary: target HTTP baseline 3, MCP tool count 40, CLI top-level 7.
- current target HTTP route count = 35.
- accepted overlay summary: A +0, B +11, C +4, D1 +0, D2 +5, D3 +0, D4/D5/D6 +5, E1-E5 +7.
- compatibility HTTP retained: `/api/v1/knowledge/*`.
- MCP tool count = 40.
- CLI diff = none.
- accepted graph CLI nested additions: graph neighbors, graph community, graph query, graph session.
- `/knowledge` role as service governance console, not end-user knowledge consumption app.
- F2 no backend public surface change.
- Closure Acceptance planned / not implemented.

The evidence is sourced from a frontend static evidence model. No backend API was added.

## 4. Public Surface Scan

- no new backend route.
- target HTTP remains 35.
- MCP remains 40.
- CLI diff none.
- no correction apply route.
- no backend public surface change.

## 5. Frontend Build Result

- `cd frontend && npm run build`: passed.

## 6. Tests and Regressions

Required validation passed:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`: 5 passed.
- `python3 -m pytest backend/tests/test_console_governance_evidence_plan.py -q`: 5 passed.
- `python3 -m pytest backend/tests/test_data_service_api.py -q`: 34 passed.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q`: 32 passed.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`: 137 passed.
- `cd frontend && npm run build`: passed.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"`: passed.

## 7. Documentation Sync

Updated:

- `README.md`
- `development-plan.md`
- `acceptance-plan.md`
- `current-vs-target-gap.md`
- `current-vs-target-gap.drawio`
- `interface-convergence-plan.md`
- `target-architecture.md`
- `target-http-routes-plan.md`
- `public-surface-baseline.md`
- `console-governance-evidence-plan.md`

## 8. Blocking Issues

None.

## 9. Final Decision

accepted.

## 10. Next Phase Recommendation

Next phase should be V1.6 Closure Acceptance / Final Release Audit. It should not add backend public surface.
