# V2.40 Phase 117 Language Provider Acceptance Plan

## 1. Acceptance Definition

Phase 117 passes only if provider status, symbol facts, reference facts, public contracts, and real repo E2E all pass without fatal or major findings.

## 2. Required Automated Tests

Focused tests:

```text
backend/tests/test_v2_40_language_provider_contract.py
```

The test suite must verify:

- Python AST provider emits accepted symbol facts with valid line ranges.
- Syntax error files produce isolated warning/blocker rows.
- TS/JS fixture emits baseline symbol/reference facts.
- tree-sitter and LSP return `provider_unavailable` when not configured.
- No provider unavailable row is counted as accepted.
- Public payload contains no absolute path, secret, token, or raw traceback.
- HTTP/MCP/CLI outputs are consistent for stable counts and artifact refs.

Regression tests:

```text
backend/tests/test_public_surface_guard.py
backend/tests/test_session_ingest_query_build_contract_plan.py
backend/tests/test_data_service_mcp.py
```

## 3. Real Repo E2E

Must run on:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
/Users/Zhuanz/Desktop/workspace/codexPat
```

Acceptance expectations:

- data_service: Python provider accepted; symbol facts non-empty.
- HarnessOS: provider attempts are recorded; unsupported/unavailable languages are structured, not fatal.
- codexPat: TS/JS baseline attempts are recorded; unsupported languages are structured, not fatal.

If a repo is unavailable in the environment, the result must be `structured_unavailable`, not `accepted`.

## 4. False-Green Rejection

Reject Phase 117 if:

- provider status says accepted without executable provider output;
- tree-sitter/LSP missing is reported as accepted;
- token overlap is treated as accepted code fact;
- accepted facts lack path or line evidence;
- syntax error in one file fails the entire repo;
- public output leaks absolute local paths;
- HTTP passes but MCP/CLI are untested;
- tests use mock-only data without real repo E2E.

## 5. Exit Criteria

- Focused tests pass.
- Contract regression tests pass.
- Real repo E2E results are recorded.
- Artifact inspection confirms all three V2.40 artifacts exist and read back.
- PRD/spec review has no fatal or major findings.
- False-green audit has no fatal or major findings.
