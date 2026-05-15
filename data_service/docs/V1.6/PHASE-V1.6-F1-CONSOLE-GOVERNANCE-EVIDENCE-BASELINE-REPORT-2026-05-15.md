# Phase V1.6-F1 Console Governance Evidence Baseline Report

Date: 2026-05-15

## 1. Scope

F1 only syncs console governance evidence documentation, route-count evidence, drawio state, and focused documentation guard tests.

F1 opens no public surface: no target HTTP route, no MCP tool, no CLI command or subcommand, no compatibility HTTP route, and no frontend behavior change. `/knowledge` remains the service governance console.

## 2. Baseline

V1.6-E5 is accepted. V1.5 public surface baseline remains immutable.

Current accepted public surface:

- target HTTP route count: 35;
- MCP tool count: 40;
- CLI top-level diff: none;
- CLI nested diff: none;
- `/api/v1/knowledge/*` compatibility retained.

## 3. Evidence Matrix

F1 adds `console-governance-evidence-plan.md` with coverage for V1.5 immutable baseline, V1.6-A public surface guard, B lifecycle target HTTP, C graph advanced target HTTP and CLI nested additions, D session contract/lifecycle/ingest/query/build, E quality feedback/rules/review/plan/rules-build, and F2 planned console governance polish.

Route count evidence:

```text
V1.5 baseline 3
+ A guard 0
+ B1/B2/B3 overlays 11
+ C1/C2/C3/C4 overlays 4
+ D1 planning 0
+ D2 overlay 5
+ D3 planning 0
+ D4/D5/D6 overlays 5
+ E1/E2/E3/E4/E5 overlays 7
= 35
```

A, D1, and D3 are documented as zero-public-surface guard/planning phases, not route overlays.

## 4. Public Surface Scan

- target HTTP route count remains 35.
- MCP tool count remains 40.
- MCP diff: none.
- CLI top-level diff: none.
- CLI nested diff: none.
- no new backend route.
- no frontend behavior change.
- F2 remains planned, not implemented.

## 5. Tests and Regressions

Validation results:

- `python3 -m pytest backend/tests/test_public_surface_guard.py -q`: passed, 5 tests.
- `python3 -m pytest backend/tests/test_console_governance_evidence_plan.py -q`: passed, 4 tests.
- `python3 -m pytest backend/tests/test_target_http_quality_correction_rules_build.py -q`: passed, 3 tests.
- `python3 -m pytest backend/tests/test_data_service_api.py -q`: passed, 34 tests.
- `python3 -m pytest backend/tests/test_data_service_mcp.py -q`: passed, 32 tests.
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`: passed, 137 tests.
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse('docs/V1.6/current-vs-target-gap.drawio'); print('drawio xml ok')"`: passed.

Frontend build: not touched. F1 does not modify frontend files or `/knowledge` static assets.

## 6. Documentation Sync

Updated docs: README, development plan, acceptance plan, current-vs-target gap markdown and drawio, interface convergence plan, target architecture, target HTTP routes plan, public surface baseline, and console governance evidence plan.

## 7. Blocking Issues

None.

## 8. Final Decision

accepted.

## 9. Next Phase Recommendation

Next phase should be V1.6-F2 Console Governance Polish. F2 must remain separately scoped and must not add backend public surface unless explicitly replanned and accepted.
