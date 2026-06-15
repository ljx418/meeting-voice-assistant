# V2.39-V2.45 Architecture Scale + Semantic Hardening Closure Audit Report

## Verdict

Accepted for the current worktree scope.

V2.39-V2.45 is accepted as the staged architecture-scale and semantic-hardening line. The accepted scope covers large-project scale handling, language provider contract, workflow/runtime candidates, relationship chains, document semantics, token budget/context cache, project profile/taxonomy, and continuous real-repo regression artifacts.

This closure does not claim full call graph, data flow, control flow, runtime tracing, type inference, production runtime topology, or complete recovery of human design intent.

## Accepted Phase Evidence

| Phase | Scope | Acceptance Evidence |
|---|---|---|
| V2.39 / Phase 116 | Large project scale profile | `V2_39_PHASE_116_SCALE_PROFILE_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.40 / Phase 117 | Language provider contract | `V2_40_PHASE_117_LANGUAGE_PROVIDER_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.41 / Phase 118 | Workflow/runtime candidates | `V2_41_PHASE_118_WORKFLOW_RUNTIME_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.42 / Phase 119 | Relationship chain v3 | `V2_42_PHASE_119_RELATIONSHIP_CHAIN_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.43 / Phase 120 | Document semantics v3 | `V2_43_PHASE_120_DOCUMENT_SEMANTICS_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.44 / Phase 121 | Token budget optimizer + context cache | `V2_44_PHASE_121_TOKEN_CACHE_ACCEPTANCE_AUDIT_REPORT.md` |
| V2.45 / Phase 122 | Profile/taxonomy + continuous regression | `V2_45_PHASE_122_PROFILE_TAXONOMY_REGRESSION_ACCEPTANCE_AUDIT_REPORT.md` |

## Final Regression Evidence

Latest scoped regression:

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_45_profile_taxonomy_regression.py \
  backend/tests/test_v2_44_token_budget_context_cache.py \
  backend/tests/test_v2_43_document_semantics.py \
  backend/tests/test_v2_42_relationship_chain_v3.py \
  backend/tests/test_v2_41_workflow_runtime_candidates.py \
  backend/tests/test_v2_40_language_provider_contract.py \
  backend/tests/test_public_surface_guard.py \
  backend/tests/test_session_ingest_query_build_contract_plan.py \
  backend/tests/test_data_service_mcp.py
27 passed, 25 skipped
```

MCP frontend contract parity:

```text
same: true
missing: []
extra: []
```

## Real Repo Coverage

The closure used real repositories where available:

- `data_service`
- `harnessOS`
- `codexPat`

Final V2.45 regression matrix E2E accepted all three repositories with no-hardcode audit passing and no public path leaks.

## PRD / Architecture Review

The implementation matches the V2.39-V2.45 PRD and target architecture at the accepted scope:

- Large-project artifacts are generated as persisted assets rather than transient reports.
- Python AST remains mandatory; non-mandatory providers remain contract-bound.
- Workflow/runtime outputs remain candidates and are not production runtime topology.
- Relationship chains remain shallow implementation/evidence paths and are not full call graphs.
- Drawio/document semantics remain document claims and are not code facts.
- Token budget optimization preserves evidence or needs_review.
- Project-specific vocabulary belongs in profile/taxonomy artifacts and is not hardcoded into generic extractors.

## False-Acceptance Review

Rejected false-green cases during this line:

- public path leakage in V2.43 document semantic labels;
- V2.44 context pack accepted while token_estimate exceeded max_tokens;
- V2.45 generic module hardcoding sample project terms;
- route/tool additions without public surface contract updates.

All listed blockers were fixed before closure.

## Open Findings

No fatal or major findings remain for V2.39-V2.45.

Minor follow-ups:

- Provide a clearer UI explanation when optimized context packs omit all reading-order details under very small budgets.
- Render profile/taxonomy differences in a future human review page.
