# V2 Phase 8 Audit Report: Pre-Development Gate

> Phase: 8 / DevWiki Baseline.
> Track: V2.1 Project Intelligence Expansion.
> Status: implemented and accepted.

## 1. Audit Inputs

- `docs/V2.x/V2_0_TARGET_PRD.md`
- `docs/V2.x/V2_0_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_1_TARGET_PRD.md`
- `docs/V2.x/V2_1_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_1_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_0_CLOSURE_AUDIT_REPORT.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_7_AUDIT_REPORT.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_8_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_8_ACCEPTANCE_PLAN.md`

## 2. PRD Spec Review

Phase 8 maps to the V2.1 Expansion item "DevWiki Baseline". It is not required for V2.0 Agent-callable MVP acceptance.

Covered by the plan:

- DevWiki index
- required baseline pages
- evidence-backed page sections
- JSON and Markdown page artifacts
- HTTP/MCP/CLI access
- real repository E2E validation

Correctly out of scope:

- Code Graph
- Code Quality Governance Extension
- frontend read-only console
- LLM-only wiki generation

No fatal PRD deviation is identified.

## 2.1 V2.0 Closure Gate

The Phase 8 entry gate was rerun on 2026-06-01 against the current repository.

Closure evidence:

- `docs/V2.x/V2_0_CLOSURE_AUDIT_REPORT.md` exists and states V2.0 closure PASS for the current worktree.
- Targeted V2.0 real-repo E2E gate passed:

```bash
python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py backend/tests/test_v2_codebase_interface_convergence.py -q
```

Result:

```text
5 passed
```

This closes the previous major gate finding. Phase 8 may enter implementation.

## 3. Architecture Boundary Review

| Gate | Status |
|---|---|
| Uses accepted Phase 2-7 artifacts as input | cleared |
| Keeps DevWiki code under `backend/data_service/code_assets/devwiki/` | planned compliant |
| Does not add Phase 8 core logic to `backend/data_service/service.py` | planned compliant |
| Does not add Phase 8 routes to `backend/app/api/v1/data_service.py` | planned compliant |
| Does not mutate source registry | planned compliant |
| Public paths remain repo-relative | planned compliant |
| Quality/read-time overlay not in Phase 8 scope | planned compliant |
| DevWiki missing V2.0 artifacts use structured errors | planned compliant |
| DevWiki JSON/Markdown consistency tested | planned compliant |

## 4. Implementation Summary

Implemented Phase 8 DevWiki Baseline as a deterministic V2.1 layer over V2.0 artifacts.

New core modules:

- `backend/data_service/code_assets/devwiki/model.py`
- `backend/data_service/code_assets/devwiki/planner.py`
- `backend/data_service/code_assets/devwiki/builder.py`
- `backend/data_service/code_assets/devwiki/renderer_markdown.py`
- `backend/data_service/code_assets/devwiki/persistence.py`
- `backend/data_service/code_assets/devwiki/service.py`

New interface modules:

- `backend/app/api/v1/code_assets_devwiki.py`
- `backend/data_service/mcp_code_devwiki_tools.py`
- `backend/data_service/cli_code_devwiki.py`

Updated thin registries:

- `backend/app/api/__init__.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`

New public surfaces:

- HTTP: `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/build`
- HTTP: `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages`
- HTTP: `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages/{page_slug}`
- MCP: `knowledge_devwiki_build`
- MCP: `knowledge_devwiki_read`
- CLI: `knowledge code devwiki build`
- CLI: `knowledge code devwiki pages`
- CLI: `knowledge code devwiki read`

## 5. Acceptance Evidence

Commands run:

```bash
python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py backend/tests/test_v2_codebase_interface_convergence.py -q
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py -q
python3 -m pytest backend/tests/test_public_surface_guard.py -q
python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py backend/tests/test_v2_codebase_interface_convergence.py backend/tests/test_data_service_mcp.py -q
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py backend/tests/test_v2_codebase_interface_convergence.py backend/tests/test_public_surface_guard.py -q
npm run build --prefix frontend
python3 -m pytest backend/tests -q
git diff --check -- .
```

Results:

- V2.0 entry gate: `5 passed`.
- Phase 8 DevWiki tests: `2 passed`.
- Public surface guard: `5 passed`.
- V2/MCP regression group: `37 passed`.
- Phase 8 target group: `12 passed`.
- Frontend build: passed.
- Full backend regression: `349 passed`.
- `git diff --check -- .`: passed.

Real data acceptance:

- The DevWiki E2E test imports `/Users/Zhuanz/Desktop/workspace/data_service` into a temporary managed workspace.
- It builds snapshot, inventory, symbols, trace, overview, then DevWiki.
- It verifies all required DevWiki pages are persisted as JSON and Markdown.
- It verifies HTTP/MCP/CLI read the same `page_id` and `snapshot_id`.
- It verifies V2.0 fact artifact hashes do not change during DevWiki build/read.
- It verifies missing V2.0 overview returns structured `V20_ARTIFACT_MISSING`.
- It verifies public payloads do not leak real repo or workspace absolute paths.

## 6. PRD / Spec Review

| Requirement | Status | Evidence |
|---|---|---|
| Required pages generated | pass | `test_v2_devwiki_baseline.py` checks all `REQUIRED_PAGE_SLUGS`. |
| JSON and Markdown artifacts persisted | pass | Test reads both from disk for every required page. |
| Section-level `generated_from` and evidence/needs_review | pass | Test validates every section has `generated_from` and evidence or `needs_review`. |
| Uses V2.0 artifacts | pass | DevWiki service reads snapshot, inventory, symbols, trace, and overview; missing artifacts fail with structured error. |
| Does not silently rebuild V2.0 facts | pass | Missing overview test returns `V20_ARTIFACT_MISSING`. |
| HTTP/MCP/CLI convergence | pass | Test compares DevWiki page read across all three. |
| Public paths safe | pass | Test rejects repo/workspace absolute path leakage. |
| V2.0 artifact hash gate | pass | Test hashes V2.0 fact artifacts before and after DevWiki build. |
| No source registry mutation | pass | Test asserts no `lifecycle/sources.json` is created. |

No PRD deviation found.

## 7. False-Acceptance Review

| Risk | Status | Notes |
|---|---|---|
| Mock-only acceptance | rejected | Tests use the real current repository. |
| In-memory-only artifacts | rejected | Tests inspect JSON and Markdown on disk. |
| LLM-only DevWiki prose | rejected | Builder uses deterministic V2.0 artifacts only. |
| JSON/Markdown divergence | guarded | Markdown is rendered from the same page model and section counts are checked. |
| HTTP-only completion | rejected | HTTP/MCP/CLI are compared. |
| V2.0 artifact mutation | rejected | Hash gate is tested. |
| Absolute path leakage | rejected | Public payloads are checked for repo/workspace absolute paths. |
| New giant service file | rejected | Logic is split across focused `code_assets/devwiki/*` modules. |

## 8. Open Findings

| Severity | Finding | Required Closure |
|---|---|---|
| note | DevWiki artifact naming may be confused with existing LLMWiki. | Keep Phase 8 under `code_assets/devwiki` and document that this is Project Intelligence DevWiki, not V1 LLMWiki. |

Open fatal findings: none.

Open major findings: none.

## 9. Gate Decision

Phase 8 is accepted.

Requirements before Phase 9:

- Create Phase 9 Code Graph development plan, acceptance plan, and pre-development audit report.
- Re-run Phase 9 entry gate against accepted V2.0 + Phase 8 DevWiki artifacts.
- Do not begin Code Graph implementation if Phase 9 audit has open fatal or major findings.
