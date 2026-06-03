# V2 Phase 4 Audit Report: Pre-Development Gate

> Phase: 4 / Python Symbol Index.
> Status: pre-development audit.

## 1. Audit Inputs

- `docs/V2.x/V2_0_TARGET_PRD.md`
- `docs/V2.x/V2_0_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_0_TARGET_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_DETAILED_PHASE_DESIGN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_4_ACCEPTANCE_PLAN.md`
- accepted Phase 3 audit: `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_AUDIT_REPORT.md`

## 2. PRD Spec Review

Phase 4 maps to the V2.0 Python Symbol Index requirement.

Covered:

- deterministic Python AST fact extraction
- module/class/function/method symbols
- import records
- line ranges
- signatures and docstrings
- syntax error isolation
- HTTP/MCP/CLI read/search access
- artifact persistence under codebase snapshot

Correctly out of scope:

- call graph
- data flow / control flow
- type inference
- runtime dispatch
- surface-to-symbol mapping
- DevWiki
- Code Graph
- Agent Context Pack

No major PRD deviation is identified.

## 3. Architecture Boundary Review

| Gate | Status |
|---|---|
| Use Phase 2 snapshot files as source of truth | planned compliant |
| Reuse Phase 3 inventory as prior artifact but do not mutate it | planned compliant |
| Keep core logic in `backend/data_service/code_assets/symbols.py` | planned compliant |
| Do not add Phase 4 routes to `backend/app/api/v1/data_service.py` | planned compliant |
| Do not add core logic to `backend/data_service/service.py` | planned compliant |
| CLI extension remains in `backend/data_service/cli_code.py` | planned compliant |
| No source registry mutation | planned compliant |
| No LLM dependency | planned compliant |

## 4. False Acceptance Risk Review

| Risk | Required Control |
|---|---|
| Symbol index extracts names only and cannot support evidence. | Require line range read-back samples. |
| Symbol IDs drift across builds. | Require repeated-build stability test. |
| Signature extraction silently fails. | Require sampled function signatures and non-empty signature ratio. |
| Syntax errors block whole repo. | Require bad Python fixture isolation. |
| Imports are superficial or empty. | Require real `mcp_code_tools -> code_assets.inventory` import assertion. |
| HTTP/MCP/CLI diverge. | Require same symbol IDs and counts across all three. |
| Output leaks absolute paths. | Require no repo/workspace root in public payloads. |
| Implementation overclaims call graph/type inference. | Require explicit negative assertions in tests/docs. |

## 5. Audit Findings

| Severity | Finding | Required Closure |
|---|---|---|
| note | Worktree has unrelated dirty files from prior tasks. | Use path-limited review/staging and do not attribute unrelated diffs to Phase 4. |
| note | Phase 4 will add one MCP tool, one CLI subcommand, and four target HTTP routes. | Update public surface guard, frontend contract, and CLI/MCP count tests only after implementation. |
| note | Symbol ID stability must be decided before code. | Development plan defines symbol ID as `py:{kind}:{qualified_name}` and excludes signature/body/line from ID. |

Open fatal findings: none.

Open major findings: none.

## 6. Gate Decision

Phase 4 is cleared to enter implementation.

Conditions:

- use current repository as real E2E codebase
- return to this audit after implementation with failures, rework, commands, artifacts inspected, PRD review, architecture review, and final decision
- stop for human confirmation if implementation requires claiming call graph/type inference or modifying legacy large files for core logic

## 7. Post-Implementation Evidence

Status: implementation completed and verified against the current repository as the real E2E codebase.

Phase-owned implementation files:

- `backend/data_service/code_assets/symbols.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/app/api/v1/code_assets.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`
- `backend/tests/test_v2_codebase_symbols.py`

Contract/test updates required by the new Phase 4 public surface:

- `backend/tests/test_data_service_mcp.py`
- `backend/tests/test_public_surface_guard.py`
- `backend/tests/test_session_graphrag_contract.py`
- `backend/tests/test_session_ingest_query_build_contract_plan.py`
- `backend/tests/test_target_http_session_query.py`
- `backend/tests/test_v16_closure_acceptance.py`
- `backend/tests/test_console_governance_evidence_plan.py`
- `backend/tests/test_data_service_api.py`
- `frontend/src/data/mcpContract.ts`
- `frontend/src/pages/KnowledgePage.vue`

Existing unrelated dirty files observed during this phase:

- `backend/app/api/v1/data_service.py`
- `backend/tests/test_target_http_studio_artifacts.py`

These files were not used for Phase 4 core implementation and should not be attributed to the Phase 4 symbol index work without a separate review.

## 8. Implemented Capability

Phase 4 now provides deterministic Python symbol extraction from snapshot files.

Implemented artifact outputs:

- `symbols.jsonl`
- `imports.jsonl`
- `symbol_summary.json`

Implemented public access:

- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/imports`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols/{symbol_id}`
- MCP:
  - `knowledge_code_symbol_search`
- CLI:
  - `knowledge code symbols`

Implemented symbol facts:

- module symbols
- class symbols
- function symbols
- method symbols
- import records
- line ranges
- signatures
- decorators
- docstrings
- visibility
- parent symbol IDs
- syntax error warnings without whole-run failure

Confirmed non-goals:

- no call graph
- no data flow
- no control flow
- no type inference
- no runtime dispatch claim

## 9. Rework During Implementation

One implementation issue was found by the Phase 4 tests:

| Issue | Impact | Resolution |
|---|---|---|
| Nested functions inside methods were initially classified as `method`. | Symbol kind was not precise enough for nested local functions and could confuse Phase 5 evidence mapping. | Updated classification so only functions whose immediate parent is a class are `method`; nested local functions remain `function`. |

This was corrected before acceptance.

## 10. Validation Commands

Commands run:

```bash
python3 -m pytest backend/tests/test_v2_codebase_symbols.py
python3 -m pytest backend/tests/test_v2_codebase_symbols.py backend/tests/test_v2_codebase_inventory.py backend/tests/test_v2_codebase_snapshot.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py backend/tests/test_data_service_api.py::test_phaseg27_knowledge_entrypoint_exposes_build_write_aliases_only
npm run build --prefix frontend
git diff --check -- .
python3 -m pytest backend/tests
```

Results:

- Phase 4 symbol tests: `3 passed`
- targeted V2/V1 regression suite: `70 passed, 103 warnings`
- frontend build: passed
- whitespace check: passed
- full backend suite: `340 passed, 617 warnings`

The warnings are existing test/runtime warnings and did not represent Phase 4 acceptance failures.

## 11. Artifact Inspection

Phase 4 tests generate and read back real V2 artifacts under the Phase 2 codebase artifact layout:

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbols.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/imports.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbol_summary.json
```

Acceptance checks include:

- repeated build symbol ID stability
- body-only edits do not change existing symbol IDs
- function signature extraction
- line range read-back against real source files
- import extraction including code asset module dependencies
- syntax error isolation using a real bad Python fixture
- HTTP/MCP/CLI read/search consistency for stable symbol IDs
- no absolute repository root in public HTTP/MCP/CLI payloads

## 12. PRD Spec Review

Phase 4 remains aligned with `docs/V2.x/V2_0_TARGET_PRD.md`:

- It implements Python Symbol Index as deterministic asset facts.
- It depends on accepted snapshots instead of scanning arbitrary live files directly.
- It exposes read/search access through HTTP, MCP, and CLI.
- It keeps DevWiki, Code Graph, Agent Context Pack, and surface-to-symbol evidence out of scope until later phases.

No fatal or major PRD deviation was found.

## 13. Architecture Review

| Gate | Result |
|---|---|
| No Phase 4 core logic in `backend/app/api/v1/data_service.py` | passed |
| No Phase 4 core logic in `backend/data_service/service.py` | passed |
| CLI implementation kept in `backend/data_service/cli_code.py` | passed |
| Symbol implementation isolated in `backend/data_service/code_assets/symbols.py` | passed |
| Source registry not used as a codebase artifact store | passed by test coverage |
| Public output uses repo-relative references | passed by test coverage |

The Phase 4 implementation did require updating contract tests and frontend static contract data because it adds one MCP tool, one CLI subcommand, and four target HTTP routes.

## 14. False Acceptance Review

| Risk | Result |
|---|---|
| Empty or superficial symbol extraction passes. | mitigated by real repo symbol counts, signature checks, and line read-back tests |
| Symbol IDs drift and break later evidence mapping. | mitigated by repeated-build and body-edit stability checks |
| Syntax errors fail the whole index. | mitigated by bad Python fixture test |
| HTTP/MCP/CLI return different facts. | mitigated by shared symbol ID/count checks |
| Public payload leaks absolute paths. | mitigated by public response assertions |
| Implementation overclaims call graph/type inference. | mitigated by scope checks and docs |

No false-acceptance risk remains at fatal or major severity for Phase 4.

## 15. Final Decision

Phase 4 is accepted.

Next required gate before implementation:

- create Phase 5 development plan
- create Phase 5 acceptance plan
- create Phase 5 audit report
- close all fatal and major Phase 5 audit findings before any Phase 5 code changes
