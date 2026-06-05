# V2.7 Phase 50 Acceptance Audit Report

> Acceptance audit for Phase 50 Architecture Claim Extractor.
> Real repository data was used for end-to-end validation.
> This report does not claim Phase 51-55 completion.

Date: 2026-06-04

## Result

Result: accepted for Phase 50.

Phase 50 now provides deterministic architecture claim and relation extraction from the Phase 49 document registry. It extracts Markdown headings, bullets, tables, interface lists, acceptance gates, non-goals, Mermaid edges, and Drawio nodes/edges into persisted V2.7 artifacts with evidence, confidence, and review state.

## Scope Accepted

Accepted:

- Architecture document claim extraction from Markdown.
- Architecture document relation extraction from Markdown containment and Drawio edges.
- Drawio-derived labels preserved as document claims, not code-derived facts.
- Confidence ceilings for heading/table/list/interface/diagram-derived claims.
- `needs_review` on diagram-derived and low-confidence claims.
- Repository-relative evidence paths.
- Local absolute path redaction in public claim labels.
- HTTP / MCP / CLI document claim build/read access.
- Structured missing-artifact error for claim reads before build.

Not accepted in this phase:

- Document quality scoring.
- Document-code alignment.
- Target/current/diff reconstruction report.
- Governance feedback/rules integration.
- Claiming document claims as implemented code architecture.

## Implementation Evidence

Key files:

- `backend/data_service/code_assets/architecture/doc_claim_extractor.py`
- `backend/data_service/code_assets/architecture/service.py`
- `backend/data_service/code_assets/architecture/persistence.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/app/api/v1/code_assets_architecture.py`
- `backend/data_service/mcp_code_architecture_tools.py`
- `backend/data_service/cli_code_architecture.py`
- `frontend/src/data/mcpContract.ts`
- `backend/tests/test_v2_7_document_registry.py`

Persisted artifacts:

- `architecture/docs/architecture_doc_claims.jsonl`
- `architecture/docs/architecture_doc_relations.jsonl`

Public interfaces:

- HTTP `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims/build`
- HTTP `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims`
- MCP `knowledge_code_architecture_doc_claims_build`
- MCP `knowledge_code_architecture_doc_claims`
- CLI `knowledge code architecture docs-claims-build`
- CLI `knowledge code architecture docs-claims`

## Deviations Found And Closed

| Finding | Severity | Resolution |
| --- | --- | --- |
| Phase 50 claim labels could include absolute paths copied from source document text. | major | Claim label cleaning now redacts local absolute paths as `[REDACTED_LOCAL_PATH]` while preserving repo-relative evidence paths. |
| Public route and MCP contract tests did not include Phase 50 routes/tools. | minor | Route baselines, MCP tool count, session contract test, and frontend MCP contract snapshot were updated. |

No open fatal or major finding remains for Phase 50.

## Real Repository E2E

Command executed against real repositories with workspace output under `/private/tmp/v27_phase50_e2e_okdywj2m`.

Results:

| Repo | Status | Document count | Claim count | Relation count | Path leak |
| --- | ---: | ---: | ---: | ---: | ---: |
| `data_service` | pass | 337 | 20085 | 16704 | false |
| `harnessOS` | pass | 632 | 18367 | 13476 | false |

Observed output:

```json
{
  "data_service": {
    "snapshot_id": "snap_90f0a1a424b6a94a73a8",
    "documents": 337,
    "claims": 20085,
    "relations": 16704,
    "absolute_path_leaked": false,
    "redacted_local_path_count": 49
  },
  "harnessOS": {
    "snapshot_id": "snap_17a8c2754621c4d1dbd9",
    "documents": 632,
    "claims": 18367,
    "relations": 13476,
    "absolute_path_leaked": false,
    "redacted_local_path_count": 40
  }
}
```

## Test Evidence

Commands:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_registry.py
/usr/bin/python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_v2_7_document_registry.py backend/tests/test_v2_6_architecture_scale_profile.py
/usr/bin/python3 -m pytest backend/tests/test_session_ingest_query_build_contract_plan.py
git diff --check -- backend/data_service/code_assets/artifacts.py backend/data_service/code_assets/architecture/persistence.py backend/data_service/code_assets/architecture/service.py backend/data_service/code_assets/architecture/doc_claim_extractor.py backend/app/api/v1/code_assets_architecture.py backend/data_service/mcp_code_architecture_tools.py backend/data_service/cli_code_architecture.py backend/tests/test_v2_7_document_registry.py backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py backend/tests/test_session_ingest_query_build_contract_plan.py frontend/src/data/mcpContract.ts
```

Results:

- `backend/tests/test_v2_7_document_registry.py`: 4 passed.
- Combined V2.7 / MCP / public-surface / V2.6 regression suite: 23 passed, 25 skipped.
- `backend/tests/test_session_ingest_query_build_contract_plan.py`: 3 passed.
- `git diff --check`: passed.

## PRD / Spec Review

Phase 50 aligns with V2.7 PRD scope:

- It extracts architecture claims from project documents.
- It records claim provenance and confidence.
- It keeps drawio-derived items as document claims.
- It keeps document claims separate from code facts.
- It does not perform document-code alignment or architecture reconstruction.

No PRD expansion was introduced.

## False Acceptance Review

Rejected false-green scenarios:

- Claim extraction accepted with empty artifacts: rejected by focused tests and real E2E counts.
- Mock-only claim extraction accepted: rejected by real `data_service` and `harnessOS` runs.
- Drawio copied as code-derived evidence: rejected by claim `needs_review` and document-derived labeling.
- Non-goal / acceptance gate dropped: rejected by focused tests.
- Absolute local paths leaked in public claim payload: rejected by focused tests and real E2E.
- HTTP-only implementation accepted: rejected by HTTP/MCP/CLI focused tests.

## Exit Decision

Phase 50 is complete and accepted.

Phase 51 may begin only after the Phase 51 pre-implementation audit is rechecked against the Phase 50 accepted artifacts. Phase 51 must not treat claim extraction as document quality acceptance; it must produce explicit quality findings and summary artifacts.
