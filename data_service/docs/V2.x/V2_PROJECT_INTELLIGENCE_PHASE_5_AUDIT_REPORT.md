# V2 Phase 5 Audit Report: Pre-Development Gate

> Phase: 5 / Surface-to-Symbol Mapping + Code Evidence Trace.
> Status: pre-development audit.

## 1. Audit Inputs

- `docs/V2.x/V2_0_TARGET_PRD.md`
- `docs/V2.x/V2_0_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_0_TARGET_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_DETAILED_PHASE_DESIGN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_5_ACCEPTANCE_PLAN.md`
- accepted Phase 4 audit: `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_AUDIT_REPORT.md`

## 2. PRD Spec Review

Phase 5 maps to V2.0 US-005: trace public capabilities to surfaces, symbols, files, and line ranges.

Covered:

- surface-to-symbol mapping
- code evidence spans
- capability trace
- V1 and V2 golden capability coverage
- line-range truth sampling
- HTTP/MCP/CLI trace access
- coverage metrics and unresolved reasons

Correctly out of scope:

- Project Overview
- Agent Context Pack
- DevWiki
- Code Graph
- Quality Governance Extension
- call graph
- data flow / control flow
- runtime dispatch
- type inference
- LLM-based semantic mapping

No major PRD deviation is identified.

## 3. Architecture Boundary Review

| Gate | Status |
|---|---|
| Uses Phase 3 inventory and Phase 4 symbol artifacts as source inputs | planned compliant |
| Keeps core logic in `backend/data_service/code_assets/trace.py` or split code-assets modules | planned compliant |
| Does not add Phase 5 routes to `backend/app/api/v1/data_service.py` | planned compliant |
| Does not add core logic to `backend/data_service/service.py` | planned compliant |
| CLI extension remains in `backend/data_service/cli_code.py` | planned compliant |
| No source registry mutation | planned compliant |
| Public responses remain repo-relative | planned compliant |
| No LLM dependency | planned compliant |

## 4. False Acceptance Risk Review

| Risk | Required Control |
|---|---|
| Mapping output is non-empty but misses V1 core capabilities. | Golden capability coverage for source import, query, build, quality, source trace, graph, and codebase import. |
| Evidence spans point to invalid or fabricated lines. | Automated truth sampling of at least 10 evidence spans. |
| Low-confidence mappings are treated as success. | `success_mapping_confidence_min = 0.80` and low-confidence rows must be unresolved. |
| MCP/CLI trace diverges from HTTP trace. | Compare stable IDs and counts across interfaces. |
| Tool/CLI mapping overclaims runtime dispatch. | Only deterministic mapping; ambiguous cases must use unresolved reasons. |
| Output leaks local absolute paths. | Public payload assertions for HTTP/MCP/CLI. |
| Phase 5 mutates source registry or V1 artifacts. | Source registry before/after check. |

## 5. Audit Findings

| Severity | Finding | Required Closure |
|---|---|---|
| note | Worktree already includes accepted Phase 3 and Phase 4 implementation changes plus unrelated dirty files. | Use path-limited review and do not attribute unrelated files to Phase 5. |
| note | Phase 5 will add public HTTP/MCP/CLI surfaces. | Update public surface guard, MCP contract tests, CLI command assertions, and frontend contract counts only after implementation. |
| note | MCP and CLI handler mapping may be deterministic for some tools but not all. | Unresolved reason must be used instead of guessing. |
| note | Golden source trace capability may depend on the exact Phase 3 capability normalization output. | If capability is absent from Phase 3 inventory, document `needs_review`; do not fabricate coverage. |

Open fatal findings: none.

Open major findings: none.

## 6. Gate Decision

Phase 5 is cleared to enter implementation.

Conditions:

- use the current repository as the real E2E codebase
- implement deterministic mappings only
- stop for human confirmation if golden coverage requires LLM inference or runtime analysis
- return to this audit after implementation with commands, artifacts inspected, failures/rework, PRD review, architecture review, false acceptance review, and final decision

## 7. Post-Implementation Evidence

Status: implementation completed and verified against the current repository as the real E2E codebase.

Phase-owned implementation files:

- `backend/data_service/code_assets/trace.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/app/api/v1/code_assets.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`
- `backend/tests/test_v2_codebase_trace.py`

Contract/test updates required by the new Phase 5 public surface:

- `backend/tests/test_data_service_mcp.py`
- `backend/tests/test_public_surface_guard.py`
- `backend/tests/test_session_ingest_query_build_contract_plan.py`
- `backend/tests/test_session_graphrag_contract.py`
- `backend/tests/test_target_http_session_query.py`
- `backend/tests/test_v16_closure_acceptance.py`
- `backend/tests/test_console_governance_evidence_plan.py`
- `backend/tests/test_data_service_api.py`
- `frontend/src/data/mcpContract.ts`
- `frontend/src/pages/KnowledgePage.vue`

Existing unrelated dirty files observed during this phase:

- `backend/app/api/v1/data_service.py`
- `backend/tests/test_target_http_studio_artifacts.py`

These files were not used for Phase 5 core implementation and should not be attributed to Phase 5 trace work without a separate review.

## 8. Implemented Capability

Phase 5 now provides deterministic surface-to-symbol mapping and evidence trace.

Implemented artifact outputs:

- `mappings.jsonl`
- `evidence.jsonl`
- `mapping_summary.json`
- `trace_index.json`

Implemented public access:

- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id:path}`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability_id}`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/evidence`
- MCP:
  - `knowledge_public_surface_trace`
- CLI:
  - `knowledge code trace`

Implemented trace facts:

- mappings from surfaces to evidence spans
- mappings from deterministic HTTP/MCP/CLI surfaces to handler symbols when available
- capability trace index
- symbol trace index
- surface trace index
- coverage by surface type
- evidence coverage by capability
- stable unresolved reason codes
- deterministic mapping and evidence IDs
- repo-relative evidence references for public responses

Confirmed non-goals:

- no call graph
- no data flow
- no control flow
- no type inference
- no runtime trace
- no LLM-based mapping

## 9. Rework During Implementation

One contract issue was found by the Phase 5 targeted regression suite:

| Issue | Impact | Resolution |
|---|---|---|
| Frontend governance evidence test still asserted old target HTTP count `46`. | The new Phase 5 trace routes correctly raised the accepted target HTTP display count to `50`, but one test still used the Phase 4 value. | Updated the frontend contract and test expectation to `target HTTP 50` and `MCP 48`. |

This was corrected before acceptance.

## 10. Validation Commands

Commands run:

```bash
python3 -m pytest backend/tests/test_v2_codebase_trace.py
python3 -m pytest backend/tests/test_v2_codebase_trace.py backend/tests/test_v2_codebase_symbols.py backend/tests/test_v2_codebase_inventory.py backend/tests/test_v2_codebase_snapshot.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py backend/tests/test_data_service_api.py::test_phaseg27_knowledge_entrypoint_exposes_build_write_aliases_only
npm run build --prefix frontend
python3 -m pytest backend/tests
```

Results:

- Phase 5 trace tests: `2 passed`
- targeted V2/V1 regression suite after rework: `72 passed, 103 warnings`
- frontend build: passed
- full backend suite: `342 passed, 617 warnings`

The warnings are existing test/runtime warnings and did not represent Phase 5 acceptance failures.

## 11. Artifact Inspection

Phase 5 tests generate and read back real V2 artifacts under the Phase 2 codebase artifact layout:

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mappings.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/evidence.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mapping_summary.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/trace_index.json
```

Acceptance checks include:

- artifact existence and non-empty mapping/evidence output
- mapping ID and evidence ID stability across repeated builds
- `success_mapping_confidence_min = 0.80`
- successful mappings have confidence at least `0.80`
- low-confidence mappings have unresolved reasons
- coverage metrics for HTTP, MCP, and CLI surfaces
- evidence coverage for `source_import`, `query`, `build`, `quality`, `graph`, `source_trace`, and `codebase_import`
- at least 10 evidence spans truth-sampled against real repository source lines
- HTTP/MCP/CLI read paths for `mcp:knowledge_codebase_import` and `codebase_import`
- public payloads avoid absolute repository and workspace paths
- source registry remains unchanged

## 12. PRD Spec Review

Phase 5 remains aligned with `docs/V2.x/V2_0_TARGET_PRD.md`:

- It implements US-005 capability-to-evidence trace.
- It covers V1 source import, query, build, quality, source trace, graph, and V2 codebase capabilities.
- It produces deterministic artifacts required by Phase 6 and Phase 7.
- It keeps Project Overview, Agent Context Pack, DevWiki, Code Graph, and Quality Governance Extension out of scope.
- It does not claim call graph, type inference, runtime dispatch, or LLM semantic mapping.

No fatal or major PRD deviation was found.

## 13. Architecture Review

| Gate | Result |
|---|---|
| No Phase 5 core logic in `backend/app/api/v1/data_service.py` | passed |
| No Phase 5 core logic in `backend/data_service/service.py` | passed |
| CLI implementation kept in `backend/data_service/cli_code.py` | passed |
| Trace implementation isolated in `backend/data_service/code_assets/trace.py` | passed |
| Source registry not used as a codebase artifact store | passed by test coverage |
| Public output uses repo-relative references | passed by test coverage |

The Phase 5 implementation did require updating contract tests and frontend static contract data because it adds one MCP tool, one CLI subcommand, and four target HTTP routes.

## 14. False Acceptance Review

| Risk | Result |
|---|---|
| Non-empty trace output misses V1 core capabilities. | mitigated by golden evidence coverage assertions |
| Evidence spans point to fake or unreadable lines. | mitigated by 10-span real source truth sampling |
| Low-confidence mappings counted as success. | mitigated by confidence threshold and unresolved reason assertions |
| HTTP/MCP/CLI diverge. | mitigated by shared trace read tests |
| Implementation overclaims call graph/runtime analysis. | mitigated by scope checks and docs |
| Public payload leaks absolute paths. | mitigated by public response assertions |

No false-acceptance risk remains at fatal or major severity for Phase 5.

## 15. Final Decision

Phase 5 is accepted.

Next required gate before implementation:

- create Phase 6 development plan
- create Phase 6 acceptance plan
- create Phase 6 audit report
- close all fatal and major Phase 6 audit findings before any Phase 6 code changes
