# V2.44 Phase 121 Token Budget Optimizer + Context Cache Acceptance Audit Report

## Verdict

Accepted.

Phase 121 is accepted for the current worktree scope. Acceptance was granted only after a false-green budget issue was found and fixed: an earlier real-repo E2E run produced evidence-preserving packs, but `token_estimate` still exceeded `max_tokens` for HarnessOS. The optimizer now trims recommendations, reading order, and omitted-item details until the resulting pack fits the requested budget while preserving recommendation evidence or `needs_review`.

## Implemented Scope

- V2.44 optimized architecture context pack.
- Token budget ledger with before/after estimates, kept counts, omitted count, cache key, cache hit, and source artifact hash.
- Context cache index keyed by task, role, mode, max_tokens, snapshot, and source artifact hash.
- Evidence-preserving trim:
  - recommendations keep `evidence_refs` or `needs_review`;
  - low-priority recommendations are omitted before evidence is removed;
  - reading order may be trimmed under tight budget;
  - omitted items always include a reason.
- JSON and Markdown pack persistence from the same artifact.
- HTTP/MCP/CLI read and create contracts.

## Public Surfaces

- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_44/context-pack-optimized/{pack_id}`
- MCP:
  - `knowledge_code_architecture_context_pack_optimized`
  - `knowledge_code_architecture_context_pack_optimized_read`
- CLI:
  - `knowledge code architecture context-pack-optimized`
  - `knowledge code architecture context-pack-optimized-read`

## Artifacts

Artifacts are written under:

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_44/
```

Files:

- `token_budget_ledger.json`
- `context_cache_index.json`
- `context_pack_optimized/{pack_id}.json`
- `context_pack_optimized/{pack_id}.md`

## Test Evidence

Focused tests:

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_44_token_budget_context_cache.py
2 passed
```

Regression tests:

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_44_token_budget_context_cache.py \
  backend/tests/test_v2_43_document_semantics.py \
  backend/tests/test_v2_42_relationship_chain_v3.py \
  backend/tests/test_v2_41_workflow_runtime_candidates.py \
  backend/tests/test_v2_40_language_provider_contract.py \
  backend/tests/test_public_surface_guard.py \
  backend/tests/test_session_ingest_query_build_contract_plan.py \
  backend/tests/test_data_service_mcp.py
25 passed, 25 skipped
```

MCP frontend contract parity:

```text
same: true
missing: []
extra: []
```

Diff whitespace check:

```text
git diff --check -- <Phase 121 scoped files>
passed
```

## Real Repo E2E

Real repositories:

- `data_service`
- `harnessOS`
- `codexPat`

Final E2E results with `max_tokens=700`:

| Repo | Status | Cache Hit | Token Estimate | Max Tokens | Budget OK | Recommendations | Reading Order | Omitted Items | Evidence Policy OK | Path Leak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| data_service | accepted | true | 644 | 700 | true | 1 | 1 | 1 | true | false |
| harnessOS | accepted | true | 514 | 700 | true | 1 | 0 | 2 | true | false |
| codexPat | accepted | true | 649 | 700 | true | 1 | 1 | 1 | true | false |

HarnessOS required trimming all reading-order details under the 700-token budget. This is accepted because the pack preserved an evidence-backed or review-marked recommendation and recorded omitted reasons.

## PRD / Spec Review

Phase 121 requirements were met:

- token_budget_ledger is persisted;
- context_cache_index is persisted;
- repeated task produces cache hit bound to source artifact hash;
- low max_tokens does not retain a recommendation without evidence or needs_review;
- omitted_items include reasons;
- JSON/Markdown are persisted for the same pack;
- HTTP/MCP/CLI surfaces are available and covered by parity tests.

## False-Acceptance Review

Rejected false-green cases:

- cache hit without source artifact hash binding;
- token metrics present but pack still exceeding max_tokens;
- recommendation retained after evidence removal;
- omitted item without reason;
- HTTP route added without public surface guard update;
- MCP tool added without frontend contract parity.

The phase initially failed the stricter real E2E budget gate for HarnessOS and was fixed before acceptance.

## Open Findings

No fatal or major findings remain for Phase 121.

Minor follow-up:

- Later phases should expose a more human-readable explanation when reading_order is fully omitted under very small budgets.
