# V2 Phase 3 Audit Report: Pre-Development Gate

> Phase: 3 / Public Surface Inventory.
> Status: pre-development audit.

## 1. Audit Inputs

- `docs/V2.x/V2_0_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_0_TARGET_PRD.md`
- `docs/V2.x/V2_0_TARGET_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_0_PHASE_2_7_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_ACCEPTANCE_PLAN.md`
- Phase 2 accepted audit: `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_2_AUDIT_REPORT.md`

## 2. PRD Spec Review

Phase 3 maps to V2.0 Target PRD public surface inventory requirements.

Required PRD capabilities covered by the plan:

- deterministic project surface extraction
- HTTP route inventory
- MCP tool inventory
- CLI command inventory
- capability grouping
- HTTP/MCP/CLI alignment matrix
- source evidence path and line range where deterministically available
- unresolved/low-confidence reporting
- real repo acceptance

Out of scope remains correct:

- Python symbol index
- surface-to-symbol mapping
- evidence trace graph
- Project Overview
- Agent Context Pack
- DevWiki
- Code Graph
- Quality Governance Extension

No major PRD deviation is identified.

## 3. Architecture Boundary Review

Planned implementation uses V2 code asset modules and existing Phase 1/2 extension points.

Architecture gates:

| Gate | Status |
|---|---|
| No Phase 3 routes in `backend/app/api/v1/data_service.py` | planned compliant |
| No Phase 3 core logic in `backend/data_service/service.py` | planned compliant |
| No substantial CLI logic in `backend/data_service/__main__.py` | planned compliant |
| Inventory artifacts remain under `workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/` | planned compliant |
| No mutation of `lifecycle/sources.json` | planned compliant |
| No LLM dependency | planned compliant |
| Frontend inventory is best effort and does not block core HTTP/MCP/CLI inventory | planned compliant |

## 4. False Acceptance Risk Review

Key risks and required controls:

| Risk | Control |
|---|---|
| Inventory is non-empty but misses critical public services. | Golden HTTP/MCP/CLI surface assertions are required. |
| MCP inventory drifts from actual registry. | Required count equals `len(all_tool_specs())`. |
| Capability alignment is fragmented by naming variants. | Required normalized taxonomy and golden capability merge tests. |
| Empty artifacts are accepted. | Required artifact disk inspection and non-empty counts by surface type. |
| Line ranges are fabricated. | Required line range presence only when deterministically extracted; otherwise unresolved reason. |
| Frontend inventory becomes a blocker due to best-effort static analysis. | Explicitly mark frontend inventory as best effort for V2.0 Phase 3. |
| Public payload leaks absolute paths. | Required path leak tests across HTTP/MCP/CLI. |
| V2 inventory writes into V1 source registry. | Required source registry unchanged assertion. |

## 5. Audit Findings

| Severity | Finding | Required Closure |
|---|---|---|
| note | Existing worktree contains unrelated modified/untracked files from prior work and neighboring projects. | Use path-limited staging and changed-file review before commit. |
| note | Phase 3 will increase MCP and target HTTP counts. | Update contract baselines and frontend contract only after implementing the actual surfaces. |
| note | Frontend/API static inventory can be incomplete in V2.0. | Mark unresolved or best-effort; do not claim complete frontend surface coverage. |

No open `fatal` or `major` findings are identified in the Phase 3 plan.

## 6. Decision

Phase 3 may enter implementation after this pre-development gate.

Implementation must return to this report after development and append:

- changed files
- commands run
- artifact paths inspected
- golden surface evidence
- failures and rework
- PRD deviations
- architecture deviations
- false acceptance risk assessment
- final decision

## 7. Design Review Addendum

Reviewed additional design document:

- `docs/V2.x/V2_DETAILED_PHASE_DESIGN.md`

The detailed design adds concrete module boundaries, artifact schemas, extractor strategy, capability normalization rules, read behavior, and golden check output for Phase 3.

### PRD Alignment

| Requirement | Status |
|---|---|
| deterministic HTTP/MCP/CLI inventory | covered |
| capability grouping and alignment matrix | covered |
| target vs legacy route classification | covered |
| unresolved/low-confidence reporting | covered |
| frontend inventory best-effort boundary | covered |
| no symbol index or evidence trace overclaim | covered |

### Architecture Alignment

| Gate | Status |
|---|---|
| Use Phase 2 snapshot as input | compliant |
| Keep V2 core under `code_assets` | compliant |
| Do not add Phase 3 routes to `data_service.py` | compliant |
| Do not add Phase 3 core logic to `service.py` | compliant |
| Do not mutate source registry | compliant |
| No LLM dependency | compliant |

### Open Findings After Design Review

| Severity | Finding | Closure |
|---|---|---|
| note | The first implementation may start as `inventory.py`; if it becomes too large it should split into an `inventory/` package. | Track during implementation review. |
| note | Frontend/API-facing extraction is explicitly best-effort in V2.0. | Acceptance must not claim complete frontend inventory. |

Open fatal findings: none.

Open major findings: none.

## 8. Updated Gate Decision

Phase 3 is cleared to enter implementation.

Conditions for implementation:

- Use real repo data in acceptance.
- Do not stage unrelated worktree changes.
- Return to this report after implementation with commands run, artifacts inspected, failures, rework, PRD/spec review, false acceptance review, and final pass/fail decision.

## 9. Implementation Review

Phase 3 implementation added deterministic public surface inventory over Phase 2 codebase snapshots.

### Phase 3-Owned Files

- `backend/data_service/code_assets/inventory.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/app/api/v1/code_assets.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`
- `backend/tests/test_v2_codebase_inventory.py`
- public surface / CLI / MCP contract tests updated for Phase 3 inventory surfaces
- `frontend/src/data/mcpContract.ts`
- `frontend/src/pages/KnowledgePage.vue`
- rebuilt `backend/app/static/knowledge_console/*`
- `docs/V2.x/V2_DETAILED_PHASE_DESIGN.md`
- Phase 3 development / acceptance / audit docs

### Existing Non-Phase-3 Dirty Files Observed

The worktree also contains unrelated modified files that were not part of Phase 3 public surface inventory work:

- `backend/app/api/v1/data_service.py`
- `backend/tests/test_target_http_studio_artifacts.py`
- unrelated backup or planning docs such as `docs/V1.x/V1_X_*` and drawio backup files

These were not used to satisfy Phase 3 and must be handled with path-limited staging.

## 10. Implemented Capability

### Artifacts

Phase 3 writes inventory artifacts under the Phase 2 snapshot directory:

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/surfaces.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/capabilities.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/alignment_matrix.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/inventory_summary.json
```

### Public Interfaces

HTTP:

- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/capabilities`

MCP:

- `knowledge_project_inventory`

CLI:

- `knowledge code inventory`

## 11. Real-Data E2E Acceptance Evidence

Acceptance used the current repository as the codebase input.

Automated E2E coverage in `backend/tests/test_v2_codebase_inventory.py` verifies:

- codebase import from the real repository
- Phase 2 snapshot generation
- Phase 3 inventory artifact creation and read-back
- non-empty HTTP / MCP / CLI inventory counts
- `mcp_tool` inventory count equals `len(all_tool_specs())`
- golden HTTP, MCP, CLI samples are present
- golden capabilities merge into the alignment matrix
- source registry is not created or modified
- public HTTP / MCP / CLI payloads do not leak absolute repo or workspace paths
- failure paths for missing snapshot, missing inventory, and invalid surface type

Golden samples include:

- HTTP: `/api/workspaces/{workspace_id}/codebases`, `/query`, `/graph/neighbors`, legacy `/api/v1/knowledge/query`
- MCP: `knowledge_project_inventory`, `knowledge_source_import`, `knowledge_build_start`, `knowledge_query_v2`, `knowledge_quality_summary`
- CLI: `knowledge code inventory`, `knowledge source import`, `knowledge build start`, `knowledge query`

## 12. Commands Run

```bash
git diff --check -- backend/data_service/code_assets/inventory.py backend/data_service/code_assets/artifacts.py backend/app/api/v1/code_assets.py backend/data_service/mcp_code_tools.py backend/data_service/cli_code.py backend/tests/test_v2_codebase_inventory.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_graphrag_contract.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py frontend/src/data/mcpContract.ts frontend/src/pages/KnowledgePage.vue docs/V2.x/V2_DETAILED_PHASE_DESIGN.md docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_DEVELOPMENT_PLAN.md docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_ACCEPTANCE_PLAN.md docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_AUDIT_REPORT.md
npm run build --prefix frontend
python3 -m pytest backend/tests/test_v2_codebase_inventory.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py
python3 -m pytest backend/tests/test_data_service_api.py::test_phaseg27_knowledge_entrypoint_exposes_build_write_aliases_only
python3 -m pytest backend/tests
```

Results:

- `git diff --check`: passed
- frontend build: passed
- targeted Phase 3 and contract suite: `60 passed, 103 warnings`
- full backend regression: `337 passed, 617 warnings`

## 13. Failures and Rework

| Failure | Root Cause | Closure |
|---|---|---|
| Import collection failed with circular import between `inventory.py`, `mcp_tool_registry.py`, and `mcp_code_tools.py`. | Inventory imported `all_tool_specs()` at module import time. | Changed MCP registry access to lazy import inside MCP extraction. |
| HTTP/MCP public payload inserted `debug_paths` into schema payloads. | Generic envelope sanitizer treated JSON Schema `properties.path` as runtime path data. | Public inventory payload converts input schemas into a schema field-list representation and removes internal schema fields. |
| Contract tests failed on old MCP/tool counts and CLI command sets. | Phase 3 intentionally adds one MCP tool, one CLI subcommand, and four target HTTP routes. | Updated public surface guards, session contract tests, data service MCP tests, and frontend contract evidence. |
| Full backend regression failed on one older CLI assertion. | The assertion did not include `knowledge code inventory`. | Updated the assertion and reran full backend regression successfully. |

## 14. PRD Spec Review After Implementation

| V2.0 Phase 3 Requirement | Status | Evidence |
|---|---|---|
| deterministic public surface inventory | pass | `CodebaseInventoryService` extracts from snapshot files only |
| HTTP route inventory | pass | FastAPI AST extractor and golden HTTP tests |
| MCP tool inventory | pass | live `all_tool_specs()` count and `knowledge_project_inventory` |
| CLI command inventory | pass | argparse-source extraction and `knowledge code inventory` |
| capability grouping | pass | `capabilities.jsonl` and golden capability tests |
| alignment matrix | pass | `alignment_matrix.json` and `query` HTTP/MCP/CLI merge tests |
| target/legacy classification | pass | legacy `/api/v1/knowledge/query` and target `/api/workspaces/...` golden checks |
| unresolved reporting | pass | summary includes unresolved counts and ratio |
| real-data acceptance | pass | current repository used as imported codebase |

Out-of-scope boundaries remain intact:

- no Python symbol index
- no surface-to-symbol mapping
- no evidence trace graph
- no Project Overview
- no Agent Context Pack
- no DevWiki
- no Code Graph
- no LLM dependency

## 15. Architecture Review After Implementation

| Gate | Status | Notes |
|---|---|---|
| No Phase 3 routes added to `backend/app/api/v1/data_service.py` | pass | Phase 3 HTTP routes are in `backend/app/api/v1/code_assets.py`. Existing unrelated dirty diff in `data_service.py` remains separate. |
| No Phase 3 core logic added to `backend/data_service/service.py` | pass | Core inventory logic is in `backend/data_service/code_assets/inventory.py`. |
| No substantial CLI logic in `backend/data_service/__main__.py` | pass | CLI extension is in `backend/data_service/cli_code.py`. |
| Artifacts under codebase snapshot directory | pass | `surfaces.jsonl`, `capabilities.jsonl`, `alignment_matrix.json`, `inventory_summary.json`. |
| No source registry mutation | pass | E2E test asserts `lifecycle/sources.json` unchanged/not created. |
| No absolute path leakage | pass | HTTP/MCP/CLI E2E tests assert repo/workspace roots absent. |
| Frontend inventory best effort | pass | Not used as a blocking Phase 3 completeness claim. |

## 16. False Acceptance Review

| Risk | Result |
|---|---|
| Non-empty inventory but missing critical surfaces | controlled by golden HTTP/MCP/CLI assertions |
| MCP count drift | controlled by `len(all_tool_specs())` assertion |
| Fragmented capability taxonomy | controlled by golden capability merge checks |
| Empty artifacts accepted | controlled by disk artifact inspection and non-empty counts |
| Fake line ranges | controlled by sampled line range checks for representative surfaces |
| Public path leakage | controlled by HTTP/MCP/CLI no-absolute-path tests |
| Source registry pollution | controlled by source registry unchanged assertion |
| Frontend extraction overclaim | controlled by best-effort labeling and no blocker claim |

No fatal or major false-acceptance risk remains open for Phase 3.

## 17. Final Phase 3 Decision

Phase 3 is accepted.

Acceptance basis:

- planning and audit gate completed before implementation
- implementation used real repository data
- targeted E2E and contract suite passed
- frontend build passed
- full backend regression passed
- PRD/spec review found no major deviation
- architecture review found no Phase 3 core logic in legacy large files
- false-acceptance review found no open fatal or major risk

Next required step before implementation of Phase 4:

- create or update Phase 4 detailed development, acceptance, and audit docs against the V2.0 target PRD
- close Phase 4 audit findings before writing code
