# V2 Phase 9 Audit Report: Code Graph Baseline

> Phase: 9 / Code Graph Baseline.
> Track: V2.1 Project Intelligence Expansion.
> Status: implemented and accepted.

## 1. Audit Inputs

- `docs/V2.x/V2_1_TARGET_PRD.md`
- `docs/V2.x/V2_1_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_1_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_8_AUDIT_REPORT.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_9_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_9_ACCEPTANCE_PLAN.md`

## 2. PRD Spec Review

Phase 9 maps to the V2.1 Expansion item "Code Graph Baseline".

Covered by the plan:

- deterministic graph artifacts
- supported node and edge types
- unsupported semantic edge rejection
- neighbor query
- Mermaid export
- HTTP/MCP/CLI access
- real repository E2E validation

Correctly out of scope:

- full call graph
- data flow
- control flow
- runtime trace
- type inference
- interactive graph editing

No fatal PRD deviation is identified.

## 3. Architecture Boundary Review

| Gate | Status |
|---|---|
| Consumes V2.0 and DevWiki artifacts | accepted |
| Keeps graph code under `backend/data_service/code_assets/graph/` | accepted |
| Does not add Phase 9 core logic to `backend/data_service/service.py` | accepted |
| Does not add Phase 9 routes to `backend/app/api/v1/data_service.py` | accepted |
| Does not mutate source registry | accepted |
| Public paths remain repo-relative | accepted |
| Unsupported edge count is zero | accepted |
| HTTP/MCP/CLI access added through split Phase 9 modules | accepted |

## 4. Pre-Development Gate Result

Gate command run:

```bash
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py backend/tests/test_v2_project_overview.py backend/tests/test_v2_codebase_trace.py -q
```

Result:

```text
5 passed
```

Phase 8 audit remains accepted. Phase 9 may enter implementation.

## 5. Implementation Summary

Phase 9 added a deterministic code graph layer on top of accepted V2.0 and Phase 8 artifacts.

New implementation modules:

- `backend/data_service/code_assets/graph/model.py`
- `backend/data_service/code_assets/graph/builder.py`
- `backend/data_service/code_assets/graph/neighbors.py`
- `backend/data_service/code_assets/graph/renderer_mermaid.py`
- `backend/data_service/code_assets/graph/persistence.py`
- `backend/data_service/code_assets/graph/service.py`
- `backend/app/api/v1/code_assets_graph.py`
- `backend/data_service/mcp_code_graph_tools.py`
- `backend/data_service/cli_code_graph.py`

New persisted artifacts:

- `workspace/assets/codebase/{codebase_id}/graph/{snapshot_id}/graph.json`
- `workspace/assets/codebase/{codebase_id}/graph/{snapshot_id}/nodes.jsonl`
- `workspace/assets/codebase/{codebase_id}/graph/{snapshot_id}/edges.jsonl`
- `workspace/assets/codebase/{codebase_id}/graph/{snapshot_id}/summary.json`
- `workspace/assets/codebase/{codebase_id}/graph/{snapshot_id}/mermaid/project.mmd`

New public interfaces:

- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/neighbors`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid`
- MCP:
  - `knowledge_code_graph_build`
  - `knowledge_code_graph_snapshot`
  - `knowledge_code_graph_neighbors`
  - `knowledge_code_graph_mermaid`
- CLI:
  - `knowledge code graph build`
  - `knowledge code graph snapshot`
  - `knowledge code graph neighbors`
  - `knowledge code graph mermaid`

## 6. Acceptance Evidence

Commands run:

```bash
python3 -m compileall backend/data_service/code_assets/graph backend/data_service/mcp_code_graph_tools.py backend/data_service/cli_code_graph.py backend/app/api/v1/code_assets_graph.py
python3 -m pytest backend/tests/test_v2_code_graph_baseline.py -q
python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py backend/tests/test_session_graphrag_contract.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py -q
python3 -m pytest backend/tests/test_v2_code_graph_baseline.py backend/tests/test_v2_devwiki_baseline.py backend/tests/test_v2_codebase_trace.py backend/tests/test_public_surface_guard.py -q
npm run build --prefix frontend
python3 -m pytest backend/tests -q
git diff --check -- .
```

Results:

```text
compileall: passed
Phase 9 graph baseline: 2 passed
contract/public surface focused suite: 58 passed
Phase 9 + Phase 8/V2.0 focused suite: 11 passed
frontend build: passed
full backend regression: 351 passed, 617 warnings
git diff --check: passed
```

Warnings are pre-existing deprecation warnings around `datetime.utcnow()` in LLMWiki-related modules and are not introduced by Phase 9.

## 7. PRD / Spec Review After Implementation

| Requirement | Result |
|---|---|
| Graph consumes V2.0/DevWiki facts rather than rescanning as a separate source of truth | pass |
| Graph contains file/module/symbol/surface/capability/evidence/DevWiki relationships | pass |
| Unsupported semantic relations are absent | pass |
| `unsupported_edge_count == 0` | pass |
| Edge coverage includes deterministic relation families | pass |
| Edges include evidence or `needs_review` | pass |
| Mermaid export references persisted graph nodes and hides absolute paths | pass |
| HTTP/MCP/CLI read surfaces converge on stable graph fields | pass |
| Missing DevWiki/V2.0 prerequisites return structured errors | pass |
| Existing V1 and V2.0 tests remain green | pass |

No fatal PRD deviation is identified.

No major PRD deviation is identified.

## 8. False Acceptance Review

| Risk | Phase 9 Mitigation |
|---|---|
| Mock-only graph validation | real repository E2E test builds V2.0, DevWiki, then graph artifacts |
| Empty graph treated as success | node types, edge coverage, artifact files, and Mermaid content are asserted |
| Unsupported claims such as full call graph | model rejects unsupported relation types and tests assert none are present |
| Evidence-less graph edges hidden as successful | each edge must carry evidence or explicit `needs_review` |
| Graph output leaks absolute paths | tests scan HTTP/MCP/CLI/Mermaid/public payloads for repository and workspace absolute paths |
| V2.1 mutates V2.0 artifacts | test hashes V2.0 source artifacts before and after graph build |
| HTTP-only implementation | HTTP, MCP, and CLI graph paths are all exercised |
| Public surface drift | public surface guard and static console contract updated and tested |

False acceptance risk after implementation: low.

## 9. Open Findings

| Severity | Finding | Required Closure |
|---|---|---|
| note | Graph remains a deterministic structural graph, not a semantic call graph. | Preserve this boundary in Phase 10 and Phase 11 docs/UI. |

Open fatal findings: none.

Open major findings: none.

## 10. Gate Decision

Phase 9 is accepted.

Phase 10 may start only after a new Phase 10 development plan, acceptance plan, and pre-development audit are produced and checked against the V2.1 PRD.

Required for Phase 10:

- keep Quality Governance as read-time overlay only
- do not mutate DevWiki, Graph, Context Pack, or V2.0 source artifacts when feedback/rules are recorded
- add artifact hash gates around quality feedback, rule approval, revoke, and plan generation
- validate targets resolve to real DevWiki/Graph/Surface/Symbol/Context objects
