# V2 Phase 8 Acceptance Plan: DevWiki Baseline

> Phase: 8 / DevWiki Baseline.
> Track: V2.1 Project Intelligence Expansion.
> Status: cleared pre-development acceptance plan.

## 1. Required E2E Flow

Use real repository data:

1. Create managed workspace in a temp root.
2. Import `/Users/Zhuanz/Desktop/workspace/data_service` as codebase.
3. Build accepted Phase 2-7 artifacts.
4. Build DevWiki pages.
5. Read DevWiki index.
6. Read each required page by slug.
7. Inspect JSON and Markdown artifacts on disk.
8. Compare HTTP/MCP/CLI stable fields.
9. Verify public output does not leak repo/workspace absolute paths.
10. Run V1/V2 regression.
11. Complete PRD/spec/false-acceptance review.

## 2. Required Assertions

- all required pages are generated
- each page contains `snapshot_id`
- each page contains evidence or `needs_review`
- each page contains `stale`
- each page contains section-level `generated_from`, `source_artifact_refs`, evidence, `needs_review`, and confidence
- page body is generated from deterministic artifacts, not unsupported prose
- `project-overview` reuses Phase 7 overview facts
- `public-surface`, `http-api`, `mcp-tools`, and `cli` reuse inventory surfaces
- `architecture` and `developer-onboarding` cite symbols, imports, overview, or `needs_review`
- JSON and Markdown pages are consistent
- JSON section count equals Markdown major section count for required pages
- Markdown does not introduce important facts absent from JSON
- page read by slug returns the same `page_id` and `snapshot_id` through HTTP/MCP/CLI
- missing V2.0 artifacts return structured `V20_ARTIFACT_MISSING` or `SNAPSHOT_NOT_FOUND`
- stale behavior is verified when latest snapshot differs from page snapshot
- V2.0 fact artifact hashes are unchanged by DevWiki build/read
- no source registry mutation

## 3. Required Tests

```bash
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py
python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py
python3 -m pytest backend/tests/test_v2_codebase_interface_convergence.py
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py
npm run build --prefix frontend
python3 -m pytest backend/tests
git diff --check -- .
```

## 4. False Acceptance Rejection

Reject Phase 8 if any are true:

- only mock data is used
- pages are generated without real Phase 2-7 artifacts
- pages contain important claims without evidence or `needs_review`
- page artifacts are not read back from disk
- HTTP passes but MCP/CLI are not tested
- DevWiki build silently rebuilds missing V2.0 facts
- DevWiki read hides stale or `needs_review` state
- public output leaks absolute paths
- V1 regression fails
- DevWiki is implemented as a single monolithic file that combines planning, rendering, and persistence
