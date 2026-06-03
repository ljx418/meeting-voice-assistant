# V2.1 Development and Acceptance Plan

> Scope: V2.1 Project Intelligence Expansion.
> Baseline: V2.0 closure accepted by `docs/V2.x/V2_0_CLOSURE_AUDIT_REPORT.md`.
> Rule: each phase requires phase-specific development plan, acceptance plan, audit report, real repository E2E, PRD/spec review, and false-acceptance review before the next phase starts.

## 1. Phase Sequence

```text
Phase 8  DevWiki Baseline                         implemented and accepted
Phase 9  Code Graph Baseline                      implemented and accepted
Phase 10 Code Knowledge Quality Governance        implemented and accepted
Phase 11 Minimum Read-only Frontend               implemented and accepted
Phase 12 V2.1 Closure Acceptance                  accepted
```

No phase may start implementation until its pre-development audit has no open fatal or major findings.

## 2. Phase 8 Entry Gate

Before Phase 8 implementation starts, the team must run and document a V2.0 closure gate:

- Confirm `docs/V2.x/V2_0_CLOSURE_AUDIT_REPORT.md` exists.
- Confirm V2.0 closure has no open fatal or major finding.
- Confirm the current real repo can regenerate or read V2.0 artifacts.
- Confirm snapshot, files, inventory, capabilities, symbols, imports, evidence, overview, and context pack artifacts exist.
- Record hashes for required V2.0 artifacts.
- Confirm V2.1 services will fail with structured errors instead of silently re-scanning or rebuilding missing V2.0 facts.

If any gate check fails, Phase 8 implementation is blocked and the team must return to V2.0 closure remediation.

## 3. Shared Acceptance Rules

Every phase must:

- Use `/Users/Zhuanz/Desktop/workspace/data_service` as real repository input.
- Build or reuse accepted V2.0 artifacts before using V2.1 artifacts.
- Inspect generated files on disk.
- Validate artifact schemas, not just file existence.
- Check cross-link integrity for references to V2.0 evidence, DevWiki pages, Graph nodes/edges, Quality targets, and Context Pack items where applicable.
- Compare V2.0 artifact hashes before and after the phase. Unless the phase explicitly plans a V2.0 rebuild, hashes must remain unchanged.
- Compare HTTP/MCP/CLI stable fields when the phase exposes all three.
- Verify structured error envelopes for missing or unknown targets.
- Verify public responses do not leak absolute repo/workspace paths.
- Verify `lifecycle/sources.json` is not created or mutated by V2 codebase artifacts.
- Run phase-specific tests.
- Run required V1/V2 regression tests.
- Run `git diff --check -- .`.
- Produce a phase audit report with PRD/spec/false-acceptance review.

Required structured error codes:

- `V20_CLOSURE_NOT_VERIFIED`
- `V20_ARTIFACT_MISSING`
- `SNAPSHOT_NOT_FOUND`
- `DEVWIKI_PAGE_NOT_FOUND`
- `GRAPH_NODE_NOT_FOUND`
- `QUALITY_RULE_NOT_FOUND`
- `UNSUPPORTED_TARGET_TYPE`

## 4. Phase 8: DevWiki Baseline

### Development

- Add DevWiki artifact paths under `workspace/assets/codebase/{codebase_id}/devwiki`.
- Add page model, planner, builder, Markdown renderer, persistence, and service modules.
- Generate required pages:
  - `project-overview`
  - `architecture`
  - `public-surface`
  - `http-api`
  - `mcp-tools`
  - `cli`
  - `storage`
  - `build-pipeline`
  - `developer-onboarding`
- Add HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages/{page_slug}`
- Add MCP:
  - `knowledge_devwiki_build`
  - `knowledge_devwiki_read`
- Add CLI:
  - `knowledge code devwiki build`
  - `knowledge code devwiki pages`
  - `knowledge code devwiki read`

### Acceptance

- All required pages are generated as JSON and Markdown.
- Each page has `schema_version`, `workspace_id`, `codebase_id`, `snapshot_id`, `page_id`, `slug`, `title`, `sections`, `evidence`, `needs_review`, `stale`, `confidence`, and timestamps.
- Each section has `section_id`, `generated_from`, `source_artifact_refs`, evidence, `needs_review`, and confidence.
- If `generated_from = llm_synthesis`, the section has evidence or is marked `needs_review` and is not high-confidence.
- `project-overview` reuses Phase 7 overview facts.
- `public-surface`, `http-api`, `mcp-tools`, and `cli` reuse inventory facts.
- `architecture` and `developer-onboarding` cite symbols, imports, overview, or `needs_review`.
- JSON and Markdown are rendered from the same page model.
- JSON section count equals Markdown major section count for required pages.
- Markdown evidence references cover all important JSON section evidence and do not add important facts absent from JSON.
- Stale behavior is verified: if latest snapshot differs from page snapshot, page reads as `stale = true`.
- HTTP/MCP/CLI read the same `page_id`, `slug`, `snapshot_id`, and evidence counts.
- Missing V2.0 artifacts return `V20_ARTIFACT_MISSING` rather than triggering a silent repo scan.
- Tests:

```bash
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py
python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py
```

### Stop Conditions

- Stop if DevWiki requires LLM-only claims without evidence.
- Stop if DevWiki artifact shape conflicts with V1 LLMWiki semantics.
- Stop if required pages cannot cite evidence or `needs_review`.

## 5. Phase 9: Code Graph Baseline

### Development

- Add graph artifact paths under `workspace/assets/codebase/{codebase_id}/graph`.
- Add graph model, builder, neighbor reader, Mermaid renderer, persistence, and service modules.
- Build deterministic graph from snapshot, inventory, symbols, trace, overview, DevWiki, and context-pack metadata.
- Add HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/neighbors`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid`
- Add MCP:
  - `knowledge_code_graph_build`
  - `knowledge_code_graph_snapshot`
  - `knowledge_code_graph_neighbors`
  - `knowledge_code_graph_mermaid`
- Add CLI:
  - `knowledge code graph build`
  - `knowledge code graph snapshot`
  - `knowledge code graph neighbors`
  - `knowledge code graph mermaid`

### Acceptance

- Graph artifacts exist: `graph.json`, `nodes.jsonl`, `edges.jsonl`, `summary.json`, and Mermaid files.
- Required node types exist for current repo.
- Required edge types exist for deterministic relationships.
- Unsupported edge types do not exist.
- `unsupported_edge_count == 0`.
- `edge_coverage_by_type` reports non-zero counts for deterministic edge classes available in the current repo: `CONTAINS`, `DEFINES`, `IMPORTS`, `EXPOSES_ROUTE`, `REGISTERS_MCP_TOOL`, `EXPOSES_CLI_COMMAND`, `IMPLEMENTS_CAPABILITY`, `DOCUMENTED_BY`, and `EVIDENCED_BY`.
- Every edge has `extractor`, `confidence`, and evidence or `needs_review`.
- Neighbor query works for at least one file, symbol, HTTP route, MCP tool, CLI command, capability, DevWiki page, and evidence span.
- Mermaid export is non-empty and references real graph nodes.
- Mermaid node IDs exist in `nodes.jsonl`.
- Mermaid export passes a parser smoke or syntax smoke.
- Mermaid export does not contain absolute paths.
- Graph EvidenceSpan nodes reference real V2.0 evidence records.
- Graph DevWikiPage nodes reference real DevWiki page IDs.
- Graph reads return `stale = true` when graph snapshot differs from latest snapshot.
- Tests:

```bash
python3 -m pytest backend/tests/test_v2_code_graph_baseline.py
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py
python3 -m pytest backend/tests/test_v2_codebase_trace.py
```

### Stop Conditions

- Stop if implementation would claim full call graph, data flow, control flow, runtime trace, or type inference.
- Stop if graph cannot trace public surfaces to evidence for core capabilities.

## 6. Phase 10: Code Knowledge Quality Governance Extension

### Development

- Add quality artifact paths under `workspace/assets/codebase/{codebase_id}/quality`.
- Add feedback, rule, review, plan, persistence, and service modules.
- Support V2.1 target types and rule types from `docs/V2.x/V2_1_TARGET_PRD.md`.
- Add approved-rule read-time consumption for DevWiki, Code Graph, and Agent Context Pack outputs.
- Add HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/summary`
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/build`
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rule_id}/review`
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/plan`
- Add MCP and CLI equivalents.

### Acceptance

- Feedback can be recorded for DevWiki page/section, public surface, capability, symbol, graph edge, and context-pack item.
- Rule build produces deterministic draft rules from feedback.
- Review can approve/reject/revoke rules.
- Plan generation reports impacted DevWiki pages, graph nodes/edges, and context pack items.
- Approved rules are visible in read outputs without mutating original V2.0 artifacts or V2.1 source artifacts.
- Original DevWiki, Graph, and Context artifacts have unchanged hashes before and after feedback, rule build, approval, rejection, revoke, and plan generation.
- Approved rules add `governed_by` or `applied_rules` to read outputs.
- Revoked rules no longer affect read outputs.
- Plan JSON lists impacted targets but does not directly rewrite target artifacts.
- Quality target IDs resolve to real DevWiki pages/sections, graph nodes/edges, public surfaces, symbols, or context items.
- Tests:

```bash
python3 -m pytest backend/tests/test_v2_code_quality_governance.py
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py backend/tests/test_v2_code_graph_baseline.py
python3 -m pytest backend/tests/test_v2_agent_context_pack.py
```

### Stop Conditions

- Stop if quality rules overwrite source artifacts instead of producing governance artifacts.
- Stop if rules can suppress evidence without recording a plan impact.

## 7. Phase 11: Minimum Read-only Frontend

Current status: implemented and accepted. Final implementation acceptance is recorded in `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_11_IMPLEMENTATION_ACCEPTANCE_REPORT.md`.

### Development

- Add Project Intelligence read-only views to the existing Knowledge Console.
- Show DevWiki page list/detail.
- Show Code Graph summary and Mermaid preview.
- Show Quality summary, feedback/rule counts, and correction plan impact.
- Show Agent Context Pack summary/readback.
- Keep backend HTTP/MCP/CLI as the stable Agent contracts.

### Acceptance

- Frontend build passes.
- Page text fits at desktop and mobile widths.
- Frontend calls backend APIs rather than duplicating artifact logic.
- No frontend-only claims appear without backend evidence.
- Frontend displays backend-provided evidence counts, stale status, `needs_review`, and unresolved states.
- Frontend does not locally compute authoritative graph node counts, quality status, page confidence, or evidence counts.
- API-returned unresolved or `needs_review` items are visible and not hidden by UI formatting.
- Phase 11 implementation acceptance report records backend payload source, frontend build result, and remaining findings.
- Tests:

```bash
npm run build --prefix frontend
python3 -m pytest backend/tests/test_public_surface_guard.py
```

### Stop Conditions

- Stop if frontend requires new backend behavior not covered by V2.1 PRD.
- Stop if UI becomes an editing surface for graph or wiki content.

## 8. Phase 12: V2.1 Closure Acceptance

Current status: accepted. Closure evidence is recorded in `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_12_AUDIT_REPORT.md` and `docs/V2.x/V2_1_CLOSURE_AUDIT_REPORT.md`.

### Development

- No new product capabilities.
- Create a closure audit report based on real repo E2E.
- Freeze public surface counts and artifact inventory.
- Produce `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_12_AUDIT_REPORT.md`.
- Produce `docs/V2.x/V2_1_CLOSURE_AUDIT_REPORT.md`.

### Acceptance

Run:

```bash
python3 -m pytest backend/tests
npm run build --prefix frontend
git diff --check -- .
```

Closure report must include:

- Commands run.
- Artifacts inspected.
- PRD coverage matrix for US-101 through US-106.
- DevWiki pages generated.
- Graph node/edge counts.
- Quality feedback/rules/plan counts.
- HTTP/MCP/CLI convergence summary.
- Frontend build result.
- Phase 11 implementation acceptance status.
- PRD deviations.
- Architecture deviations.
- False-acceptance risks.
- V2.0 artifact hash gate results.
- Artifact schema validation results.
- Cross-link integrity results.
- Structured error envelope results.
- Open questions.

V2.1 is accepted only if no fatal or major findings remain.

## 9. False Acceptance Rejection

Reject V2.1 completion if any of these occur:

- Any phase uses only mock data.
- Artifacts are returned in memory but not persisted.
- DevWiki pages have important claims without evidence or `needs_review`.
- Code Graph includes unsupported semantic relationships.
- Quality governance mutates original V2.0 artifacts.
- Quality governance mutates original DevWiki, Graph, or Context artifacts during rule application.
- HTTP passes but MCP/CLI are not tested for phase public surfaces.
- Frontend build is skipped after frontend changes.
- Frontend hides backend `needs_review` or unresolved states.
- Public output leaks absolute repo/workspace paths.
- V1 regression fails.
- V2.1 implementation expands `data_service.py` or `service.py` with core logic.
- V2.1 implementation silently rebuilds V2.0 fact artifacts when required artifacts are missing.
