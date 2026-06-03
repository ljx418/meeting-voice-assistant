# V2 Phase 9 Acceptance Plan: Code Graph Baseline

> Phase: 9 / Code Graph Baseline.
> Track: V2.1 Project Intelligence Expansion.
> Status: pre-development acceptance plan.

## 1. Required E2E Flow

Use real repository data:

1. Create managed workspace in a temp root.
2. Import `/Users/Zhuanz/Desktop/workspace/data_service` as codebase.
3. Build accepted V2.0 artifacts.
4. Build Phase 8 DevWiki pages.
5. Build Code Graph.
6. Read graph snapshot.
7. Query neighbors for a file, symbol, HTTP route, MCP tool, CLI command, capability, DevWiki page, and evidence span.
8. Read Mermaid export.
9. Inspect graph artifacts on disk.
10. Compare HTTP/MCP/CLI stable fields.
11. Verify public output does not leak repo/workspace absolute paths.
12. Run V1/V2 regression.
13. Complete PRD/spec/false-acceptance review.

## 2. Required Assertions

- graph artifacts exist and are non-empty
- node types include deterministic current-repo node types
- edge types include deterministic current-repo edge types
- `unsupported_edge_count == 0`
- every edge has `edge_id`, `from_id`, `to_id`, `relation`, `extractor`, `confidence`, and evidence or `needs_review`
- `edge_coverage_by_type` reports non-zero counts for deterministic relationships available in current repo
- Mermaid references only node IDs present in `nodes.jsonl`
- Mermaid output is non-empty and does not contain absolute paths
- Graph EvidenceSpan nodes reference real V2.0 evidence records
- Graph DevWikiPage nodes reference real Phase 8 pages
- Missing V2.0/DevWiki artifacts return structured errors
- V2.0 and DevWiki artifact hashes are unchanged by graph build/read
- no source registry mutation

## 3. Required Tests

```bash
python3 -m pytest backend/tests/test_v2_code_graph_baseline.py
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py backend/tests/test_v2_codebase_trace.py
python3 -m pytest backend/tests/test_public_surface_guard.py
npm run build --prefix frontend
python3 -m pytest backend/tests
git diff --check -- .
```

## 4. False Acceptance Rejection

Reject Phase 9 if any are true:

- only mock data is used
- graph artifacts are returned in memory but not persisted
- unsupported edge types appear
- Mermaid references phantom nodes
- graph contains important relationships without evidence or `needs_review`
- HTTP passes but MCP/CLI are not tested
- public output leaks absolute paths
- graph build mutates V2.0 or DevWiki source artifacts
- V1 regression fails
- graph implementation is a single monolithic file
