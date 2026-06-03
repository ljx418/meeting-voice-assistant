# V2 Phase 8 Development Plan: DevWiki Baseline

> Phase: 8 / DevWiki Baseline.
> Track: V2.1 Project Intelligence Expansion.
> Status: cleared for implementation after V2.0 closure gate.
> Governing references: `docs/V2.x/V2_1_TARGET_PRD.md`, `docs/V2.x/V2_1_TARGET_ARCHITECTURE.md`, `docs/V2.x/V2_1_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`, `docs/V2.x/V2_0_CLOSURE_AUDIT_REPORT.md`.

## 1. Objective

Add a deterministic DevWiki baseline on top of accepted V2.0 artifacts so humans and agents can read project pages backed by snapshot, inventory, symbol, trace, overview, and context-pack evidence.

Phase 8 must not replace Project Overview or Agent Context Pack. It should produce navigable pages derived from accepted artifacts.

## 1.1 Entry Gate Result

Phase 8 entry gate was run on 2026-06-01.

Gate evidence:

```bash
python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py backend/tests/test_v2_codebase_interface_convergence.py -q
```

Result:

```text
5 passed
```

`docs/V2.x/V2_0_CLOSURE_AUDIT_REPORT.md` exists and states V2.0 Agent-callable MVP closure is PASS for the current worktree. Phase 8 implementation may proceed, subject to post-implementation real-repo E2E and false-acceptance review.

## 2. Scope

In scope:

- generate DevWiki index and pages
- support page read by slug
- include `snapshot_id`, evidence, confidence, and stale status
- expose HTTP/MCP/CLI read/build access
- verify with current repository as real data

Out of scope:

- Code Graph Baseline
- Code Quality Governance Extension
- frontend read-only console
- LLM-only wiki generation
- full documentation site publishing
- bidirectional editing

## 3. Proposed Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/devwiki/index.json
workspace/assets/codebase/{codebase_id}/devwiki/pages/{page_slug}.json
workspace/assets/codebase/{codebase_id}/devwiki/pages/{page_slug}.md
```

Every artifact must include:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `page_id`
- `slug`
- `title`
- `sections`
- `evidence`
- `needs_review`
- `stale`
- `confidence`
- `created_at`

## 4. Baseline Pages

Required MVP pages:

- `project-overview`
- `architecture`
- `public-surface`
- `http-api`
- `mcp-tools`
- `cli`
- `storage`
- `build-pipeline`
- `developer-onboarding`

## 5. Proposed Modules

```text
backend/data_service/code_assets/devwiki/model.py
backend/data_service/code_assets/devwiki/planner.py
backend/data_service/code_assets/devwiki/builder.py
backend/data_service/code_assets/devwiki/renderer_markdown.py
backend/data_service/code_assets/devwiki/persistence.py
backend/data_service/code_assets/devwiki/service.py
```

Existing modules to extend:

```text
backend/data_service/code_assets/artifacts.py
backend/app/api/__init__.py
backend/app/api/v1/code_assets_devwiki.py
backend/data_service/mcp_code_devwiki_tools.py
backend/data_service/mcp_code_tools.py
backend/data_service/cli_code_devwiki.py
backend/data_service/cli_code.py
frontend/src/data/mcpContract.ts
```

Tests:

```text
backend/tests/test_v2_devwiki_baseline.py
```

## 6. HTTP/MCP/CLI Surface

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages/{page_slug}
```

MCP:

```text
knowledge_devwiki_build
knowledge_devwiki_read
```

CLI:

```text
knowledge code devwiki build
knowledge code devwiki pages
knowledge code devwiki read
```

## 7. Implementation Sequence

1. Add DevWiki artifact paths.
2. Add page model and page planner.
3. Build deterministic page sections from Phase 2-7 artifacts without silently rebuilding missing V2.0 facts.
4. Add section-level `generated_from`, `source_artifact_refs`, evidence, `needs_review`, and confidence.
5. Render JSON and Markdown pages from the same page model.
6. Persist index and pages.
7. Add thin HTTP routes in `code_assets_devwiki.py`.
8. Add MCP tools through a thin DevWiki tool module and register names/specs in the existing code tool entrypoint.
9. Add CLI subcommands through `cli_code_devwiki.py`.
10. Add real-repo E2E tests including JSON/Markdown consistency, stale behavior, and missing artifact error behavior.
11. Update public surface guard and frontend MCP contract if required.
12. Run targeted backend tests, V1/V2 regression tests, and frontend build if frontend-facing contracts change.
13. Complete post-implementation PRD/spec/false-acceptance review.

## 8. Stop Conditions

Stop for human confirmation if:

- V2.0 closure report is missing or V2.0 real-repo E2E gate fails.
- DevWiki page generation requires unsupported LLM synthesis.
- required pages cannot cite evidence or `needs_review`.
- Phase 8 would require modifying `backend/app/api/v1/data_service.py` or `backend/data_service/service.py`.
- DevWiki artifact shape conflicts with existing LLMWiki semantics.
- DevWiki would need to mutate V2.0 fact artifacts to pass acceptance.
