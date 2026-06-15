# V2.42 Phase 119 Relationship Chain v3 Acceptance Audit Report

## 1. Audit Verdict

Status: **accepted**

Phase 119 implemented and validated V2.42 relationship chain artifacts for capability / entrypoint / handler / dependency / test / document-claim reading paths.

This phase does **not** claim full call graph, data flow, control flow, type inference, or production runtime topology. `candidate_hint` and other heuristic edges remain reviewable reading aids and are explicitly protected by `needs_review`.

## 2. Scope Implemented

- New persisted artifacts:
  - `architecture/v2_42/relationship_chains_v3.jsonl`
  - `architecture/v2_42/relationship_chain_summary.json`
  - `architecture/v2_42/forbidden_edge_scan.json`
- New service methods:
  - `ArchitectureService.build_relationship_chains_v3`
  - `ArchitectureService.read_relationship_chains_v3`
- New HTTP routes:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_42/relationship-chains`
- New MCP tools:
  - `knowledge_code_architecture_relationship_chains_v3_build`
  - `knowledge_code_architecture_relationship_chains_v3`
- New CLI commands:
  - `knowledge code architecture relationship-chains-v3-build`
  - `knowledge code architecture relationship-chains-v3`

## 3. PRD / Spec Review

| Requirement | Result | Evidence |
| --- | --- | --- |
| Build shallow relationship chain, not full call graph | Passed | Allowed edge catalog excludes runtime/data/control/type-inferred edges. |
| Use V2.40 language facts and V2.41 workflow/runtime candidates | Passed | Builder consumes language symbol/reference facts and workflow/runtime/entrypoint candidates. |
| Support projects without public HTTP/MCP/CLI surfaces | Passed | Service no longer hard-fails on empty surface inventory; candidate chains or blockers are used. |
| Forbidden edge scan | Passed | `forbidden_edge_count = 0`, `unsupported_edge_count = 0` in focused and real E2E. |
| Heuristic edges cannot be mistaken for runtime topology | Passed | `heuristic_without_review = 0`; candidate chains include `CANDIDATE_REQUIRES_REVIEW`. |
| HTTP/MCP/CLI parity | Passed | Focused tests cover service, HTTP, MCP, CLI read/build. |
| Public payload path safety | Passed | Focused and real E2E checks found no repo/workspace absolute path leak. |

No fatal or major PRD deviation remains open.

## 4. Automated Test Evidence

Commands executed:

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_42_relationship_chain_v3.py
```

Result:

```text
2 passed
```

Regression command:

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_42_relationship_chain_v3.py \
  backend/tests/test_v2_41_workflow_runtime_candidates.py \
  backend/tests/test_v2_40_language_provider_contract.py \
  backend/tests/test_public_surface_guard.py \
  backend/tests/test_session_ingest_query_build_contract_plan.py \
  backend/tests/test_data_service_mcp.py
```

Result:

```text
21 passed, 25 skipped
```

MCP frontend contract parity:

```text
same: True
missing: []
extra: []
```

## 5. Real Repository E2E Evidence

Real repositories were scanned and built through snapshot, inventory, symbol index, V2.40 language providers, V2.41 workflow/runtime candidates, optional document claims, and V2.42 relationship chains.

| Repository | Status | Chain Count | Accepted Chains | Forbidden Edges | Unsupported Edges | Heuristic Edges | Heuristic Without Review | Path Leak |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| data_service | accepted | 552 | 552 | 0 | 0 | 203 | 0 | false |
| harnessOS | accepted | 10 | 10 | 0 | 0 | 11 | 0 | false |
| codexPat | accepted | 10 | 10 | 0 | 0 | 10 | 0 | false |

Interpretation:

- `data_service` produces evidence-rich capability chains from public surfaces and handlers.
- `harnessOS` and `codexPat` currently rely mainly on candidate chains; these are accepted as reviewable reading chains, not as production runtime topology.
- No repository produced forbidden edge types.

## 6. False Acceptance Review

Rejected false-green conditions:

- No `runtime_call`, `data_flow`, `control_flow`, `production_topology`, or `type_inferred_dependency` edge is emitted.
- Empty public surface inventory no longer causes a hard failure, but also does not invent HTTP/MCP/CLI facts.
- Candidate-based chains are explicitly marked reviewable through heuristic `needs_review`.
- Accepted relationship chains do not claim complete call graph or complete execution flow.
- Public JSON does not leak absolute repository or workspace paths.

## 7. Corrective Action Closed During Phase

Finding: Projects without accepted public surfaces failed with `INVENTORY_NOT_FOUND`, which was too strict for V2.42 because Phase 119 must support workflow/runtime/entrypoint candidate chains.

Fix: `ArchitectureService.build_relationship_chains_v3` now requires snapshot files, but allows empty surfaces and falls back to candidate chains or blockers.

Finding: Candidate chains could be read as strong facts when candidate determinism was inherited from upstream extractors.

Fix: Candidate-chain `candidate_hint` edges are forced to `heuristic` and include `CANDIDATE_REQUIRES_REVIEW`.

## 8. Exit Criteria

Phase 119 exit criteria are met:

- Focused tests passed.
- Shared regression tests passed.
- HTTP/MCP/CLI contracts are registered and parity-checked.
- Real data E2E passed for `data_service`, `harnessOS`, and `codexPat`.
- PRD/spec review found no open fatal or major deviation.
- False acceptance review passed.

Next phase may proceed to **Phase 120 / V2.43 Document Semantic Parser v3** after its phase-specific pre-implementation audit remains fatal/major clear.
