# V2.45 Phase 122 Profile / Taxonomy + Continuous Regression Acceptance Audit Report

## Verdict

Accepted.

Phase 122 is accepted for the current worktree scope. The implementation persists project profile, taxonomy registry, real repo regression matrix, no-hardcode audit, and closure report artifacts. It also exposes HTTP/MCP/CLI read/build contracts and verifies that project-specific sample terms do not leak into generic architecture extractor modules.

## Implemented Scope

- Project profile artifact with project family, terms, entrypoint patterns, workflow patterns, and authority rules.
- Taxonomy registry with capability terms, architecture terms, and risk labels.
- Real repo regression matrix covering data_service, HarnessOS, and codexPat.
- No-hardcode audit over generic architecture modules.
- Closure audit Markdown artifact.
- HTTP/MCP/CLI access.

## Public Surfaces

- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_45/profile-regression`
- MCP:
  - `knowledge_code_architecture_profile_regression_build`
  - `knowledge_code_architecture_profile_regression`
- CLI:
  - `knowledge code architecture profile-regression-build`
  - `knowledge code architecture profile-regression`

## Artifacts

Artifacts are written under:

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_45/
```

Files:

- `project_profiles/{profile_id}.json`
- `taxonomy_registry.json`
- `real_repo_regression_matrix.json`
- `no_hardcode_audit.json`
- `closure_audit_report.md`

## Test Evidence

Focused tests:

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_45_profile_taxonomy_regression.py
2 passed
```

Regression tests:

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

## Real Repo E2E

Real repositories:

- `data_service`
- `harnessOS`
- `codexPat`

Final E2E results:

| Repo | Status | Matrix Projects | Accepted Count | Structured Unavailable | No-Hardcode | Findings | Path Leak |
|---|---:|---:|---:|---:|---:|---:|---:|
| data_service | accepted | 3 | 3 | 0 | passed | 0 | false |
| harnessOS | accepted | 3 | 3 | 0 | passed | 0 | false |
| codexPat | accepted | 3 | 3 | 0 | passed | 0 | false |

## PRD / Spec Review

Phase 122 requirements were met:

- project profile can be created and read;
- taxonomy registry can be created and read;
- real_repo_regression_matrix contains data_service, HarnessOS, and codexPat;
- no-hardcode audit runs against generic architecture modules;
- profile-specific terms are allowed in profile artifacts but not generic extractor hardcode;
- public outputs do not leak absolute paths;
- coverage matrix has accepted rows backed by tests and audit reports.

## False-Acceptance Review

Rejected false-green cases:

- accepting regression without real repo matrix rows;
- embedding sample project names in generic extractor modules;
- marking no-hardcode audit accepted without scanning;
- accepted coverage rows without test/audit evidence;
- public payloads leaking local filesystem paths.

## Open Findings

No fatal or major findings remain for Phase 122.

Minor follow-up:

- Future stages should distinguish profile-level domain vocabulary from globally reusable taxonomy terms in the UI.
