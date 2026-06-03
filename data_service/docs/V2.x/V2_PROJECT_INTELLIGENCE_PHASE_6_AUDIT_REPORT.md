# V2 Phase 6 Audit Report: Implementation Review

> Phase: 6 / HTTP, MCP, and CLI read convergence.
> Status: implemented and accepted.

## 1. Audit Inputs

- `docs/V2.x/V2_0_TARGET_PRD.md`
- `docs/V2.x/V2_0_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_0_TARGET_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_DETAILED_PHASE_DESIGN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_6_ACCEPTANCE_PLAN.md`
- accepted Phase 5 audit: `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_AUDIT_REPORT.md`

## 2. PRD Spec Review

Phase 6 maps to the V2.0 requirement that HTTP, MCP, and CLI reads converge on stable V2 project-intelligence facts.

Covered:

- shared V2 read envelope
- success and error shape convergence
- artifact read convergence across HTTP/MCP/CLI
- stable IDs and counts
- public path privacy
- real repository E2E validation

Correctly out of scope:

- new extraction artifacts
- Project Overview
- Agent Context Pack
- DevWiki
- Code Graph
- Quality Governance Extension
- migrating all V1 APIs to the V2 envelope

No major PRD deviation is identified.

## 3. Architecture Boundary Review

| Gate | Status |
|---|---|
| Adds shared V2 envelope helper under `backend/data_service/code_assets/` | planned compliant |
| Does not add Phase 6 core logic to `backend/app/api/v1/data_service.py` | planned compliant |
| Does not add Phase 6 core logic to `backend/data_service/service.py` | planned compliant |
| Preserves existing V1 target HTTP and MCP contracts | planned compliant |
| Does not mutate Phase 2-5 artifact schemas unless explicitly justified | planned compliant |
| No source registry mutation | planned compliant |
| No LLM dependency | planned compliant |

## 4. False Acceptance Risk Review

| Risk | Required Control |
|---|---|
| Tests compare only HTTP and ignore MCP/CLI. | Convergence fixture must call all three interfaces. |
| Only success responses converge. | Missing-artifact and invalid-request errors must be compared. |
| Envelope is wrapped inconsistently. | Tests must locate and compare the V2 read envelope portion explicitly. |
| CLI emits non-JSON diagnostics to stdout. | CLI stdout JSON assertion and stderr diagnostics rule. |
| Existing V1 contracts break. | Full backend regression and public surface guard. |
| Public response leaks paths while normalizing envelopes. | Absolute path leakage assertions across HTTP/MCP/CLI. |

## 5. Audit Findings

| Severity | Finding | Required Closure |
|---|---|---|
| note | Existing V2 code asset APIs currently use the project-wide `status` envelope rather than the final V2 `ok` read envelope. | Phase 6 must add an explicit V2 read envelope without breaking V1 target tests. |
| note | HTTP compatibility may require retaining an outer existing envelope. | Acceptance compares the explicit V2 read envelope portion. |
| note | Error code naming differs today between HTTP exceptions and MCP blocked envelopes. | Phase 6 must normalize V2 read error codes. |

Open fatal findings: none.

Open major findings: none.

## 6. Gate Decision

Phase 6 was cleared to enter implementation and has now passed implementation review.

Pre-implementation conditions were:

- use the current repository as the real E2E codebase
- preserve existing V1 and target HTTP compatibility tests
- stop for human confirmation if top-level V2 envelope enforcement requires breaking accepted V1 contracts
- return to this audit after implementation with commands, artifacts inspected, failures/rework, PRD review, architecture review, false acceptance review, and final decision

## 7. Implementation Summary

Implemented:

- added shared V2 read envelope helpers in `backend/data_service/code_assets/envelope.py`
- added explicit `data.v2` success/error envelopes to V2 code asset HTTP reads in `backend/app/api/v1/code_assets.py`
- added explicit `data.v2` success/error envelopes to V2 code asset MCP reads in `backend/data_service/mcp_code_tools.py`
- preserved V2 error code casing through MCP payload sanitization in `backend/data_service/mcp_common.py`
- added real-repository HTTP/MCP/CLI convergence tests in `backend/tests/test_v2_codebase_interface_convergence.py`

The implementation intentionally keeps the existing outer HTTP/MCP/CLI response shapes for compatibility and compares the explicit `data.v2` envelope for V2.0 read convergence.

## 8. Acceptance Evidence

Commands executed:

```bash
python3 -m pytest backend/tests/test_v2_codebase_interface_convergence.py
python3 -m pytest backend/tests/test_v2_codebase_interface_convergence.py backend/tests/test_v2_codebase_trace.py backend/tests/test_v2_codebase_symbols.py backend/tests/test_v2_codebase_inventory.py backend/tests/test_v2_codebase_snapshot.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py
python3 -m pytest backend/tests
git diff --check -- .
npm run build --prefix frontend
```

Observed results:

- `backend/tests/test_v2_codebase_interface_convergence.py`: `2 passed`
- targeted V2/V1 regression suite: `73 passed`
- full backend regression: `344 passed`
- whitespace/conflict-marker check: passed
- frontend production build: passed

The convergence tests import the current repository as the real codebase, generate/read Phase 2-5 artifacts, and compare HTTP, MCP, and CLI `data.v2` envelopes for stable identifiers, counts, artifact refs, warnings, unresolved items, and error shape. Missing inventory error responses are checked across all three interfaces.

Frontend build is not required by Phase 6 behavior, but was run as an additional guard because the working tree already contains frontend/static console changes from prior V2 work.

## 9. Failures and Rework

Initial convergence validation found that MCP/CLI error codes inside `data.v2.error.code` were being lowercased by the generic MCP external payload sanitizer, while HTTP returned uppercase V2 error codes such as `INVENTORY_NOT_FOUND`.

Closure:

- added V2-specific sanitizer handling in `backend/data_service/mcp_common.py`
- preserved outer legacy/target MCP error normalization while keeping `data.v2.error.code` stable
- reran convergence tests successfully

## 10. Post-Implementation PRD Review

| Requirement | Result |
|---|---|
| HTTP/MCP/CLI read convergence | satisfied for inventory, symbol search, and trace representative reads |
| Success and error envelope shape | satisfied through `data.v2` success and error envelopes |
| Real repository E2E | satisfied by using the current repository as the codebase fixture |
| No new extraction behavior in Phase 6 | satisfied |
| Project Overview / Agent Context Pack out of scope | preserved for Phase 7 |
| DevWiki / Code Graph / Quality out of scope | preserved for V2.1 |

No major PRD deviation is identified.

## 11. Post-Implementation Architecture Review

| Gate | Result |
|---|---|
| Phase 6 envelope helper under `backend/data_service/code_assets/` | pass |
| No Phase 6 core logic added to `backend/app/api/v1/data_service.py` | pass |
| No Phase 6 core logic added to `backend/data_service/service.py` | pass |
| Existing outer HTTP/MCP contracts preserved | pass |
| Phase 2-5 artifact schemas unchanged | pass |
| Source registry not used as a V2 artifact store | pass |
| No LLM dependency | pass |

## 12. False Acceptance Review

| Risk | Closure |
|---|---|
| Tests compare only HTTP and ignore MCP/CLI | convergence tests call HTTP, MCP, and CLI |
| Only success responses converge | missing inventory error envelope is compared across all three interfaces |
| Empty artifacts falsely pass | tests build/read real inventory, symbols, and trace artifacts before comparison |
| CLI emits non-JSON stdout | CLI output is parsed as JSON in convergence tests |
| Public response leaks absolute paths | convergence tests assert path-shaped public values do not contain the repo absolute path |
| V1 contracts break | targeted V1 regression suite passed |

## 13. Final Decision

Phase 6 is accepted.

No fatal or major open audit findings remain for Phase 6.
