# V2.7 Phase 50 ChatGPT Audit Package

> Independent audit package for external review.
> Phase 50 is implemented and internally accepted.
> This package is not a V2.7 closure report.

Date: 2026-06-04

## 1. Audit Conclusion For Review

Internal audit conclusion: Phase 50 Architecture Claim Extractor is accepted.

Accepted scope:

- Deterministic architecture claim extraction from registered Markdown, Mermaid, and Drawio document assets.
- Deterministic document relation extraction from Markdown containment and Drawio/Mermaid edges.
- Claim and relation persistence under V2.7 architecture docs artifacts.
- HTTP, MCP, and CLI build/read access for document claims.
- Real-repository E2E on `data_service` and HarnessOS.
- Public output local path redaction.
- Drawio claims remain document-derived and reviewable; they are not treated as code-derived architecture facts.

Not accepted in Phase 50:

- Document quality evaluation.
- Document-code alignment.
- Target/current/diff architecture reconstruction.
- Governance overlay.
- Full V2.7 closure.

## 2. Key Implementation Files

- `backend/data_service/code_assets/architecture/doc_claim_extractor.py`
- `backend/data_service/code_assets/architecture/service.py`
- `backend/data_service/code_assets/architecture/persistence.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/app/api/v1/code_assets_architecture.py`
- `backend/data_service/mcp_code_architecture_tools.py`
- `backend/data_service/cli_code_architecture.py`
- `frontend/src/data/mcpContract.ts`
- `backend/tests/test_v2_7_document_registry.py`

## 3. Public Interfaces Added In Phase 50

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims
```

MCP:

```text
knowledge_code_architecture_doc_claims_build
knowledge_code_architecture_doc_claims
```

CLI:

```text
knowledge code architecture docs-claims-build
knowledge code architecture docs-claims
```

Artifacts:

```text
workspace/assets/codebase/{codebase_id}/architecture/docs/architecture_doc_claims.jsonl
workspace/assets/codebase/{codebase_id}/architecture/docs/architecture_doc_relations.jsonl
```

## 4. Test Evidence

Commands executed:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_registry.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py
/usr/bin/python3 -m pytest backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_v2_6_architecture_scale_profile.py
git diff --check -- backend/data_service/code_assets/artifacts.py backend/data_service/code_assets/architecture/persistence.py backend/data_service/code_assets/architecture/service.py backend/data_service/code_assets/architecture/doc_claim_extractor.py backend/app/api/v1/code_assets_architecture.py backend/data_service/mcp_code_architecture_tools.py backend/data_service/cli_code_architecture.py backend/tests/test_v2_7_document_registry.py backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py backend/tests/test_session_ingest_query_build_contract_plan.py frontend/src/data/mcpContract.ts docs/V2.x/V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md docs/V2.x/V2_7_TARGET_PRD.md docs/V2.x/V2_7_TARGET_ARCHITECTURE.md docs/V2.x/V2_7_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md docs/V2.x/V2_7_PHASE_49_55_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md docs/V2.x/V2_7_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md docs/V2.x/V2_7_FULL_PRD_COVERAGE_MATRIX.md docs/V2.x/V2_7_DOCUMENT_AUDIT_REPORT.md docs/V2.x/README.md
```

Results:

- `backend/tests/test_v2_7_document_registry.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py`: 16 passed, 25 skipped.
- `backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_v2_6_architecture_scale_profile.py`: 10 passed.
- `git diff --check`: passed.

Note:

- Python emitted a non-failing `urllib3` LibreSSL warning during pytest.

## 5. Real Repository E2E Evidence

Command used a temporary workspace under:

```text
/private/tmp/v27_phase50_chatgpt_audit_66fqnifj
```

Results:

| Repo | Documents | Claims | Relations | Relation integrity | Absolute path leaked | Redacted local path count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `data_service` | 338 | 20162 | 16771 | true | false | 50 |
| HarnessOS | 631 | 18325 | 13443 | true | false | 40 |

Detailed block-type distribution:

```json
{
  "data_service": {
    "source_block_types": {
      "acceptance_gate": 502,
      "bullet": 13725,
      "diagram_node": 352,
      "heading": 3179,
      "interface_list": 679,
      "non_goal": 54,
      "stop_condition": 66,
      "table_row": 1605
    },
    "needs_review_count": 491
  },
  "harnessOS": {
    "source_block_types": {
      "acceptance_gate": 364,
      "bullet": 9454,
      "diagram_node": 774,
      "heading": 4441,
      "interface_list": 158,
      "non_goal": 101,
      "stop_condition": 160,
      "table_row": 2873
    },
    "needs_review_count": 1100
  }
}
```

## 6. PRD / Spec Review

Phase 50 aligns with V2.7 PRD user story `US-027-002`.

Confirmed:

- Claims are extracted from architecture documents.
- Claims include document evidence and confidence.
- Claim source block type is persisted.
- Drawio-derived claims remain reviewable and are not represented as code-derived architecture.
- Non-goals, forbidden claims, and acceptance gates are preserved as first-class claim types.

Not claimed:

- Claims are not treated as implemented code facts.
- Token overlap alignment is not performed in Phase 50.
- Architecture reconstruction is not performed in Phase 50.

## 7. False-Acceptance Review

Rejected false-green cases:

- Empty claim artifacts accepted.
- Mock-only data accepted.
- HTTP-only implementation accepted without MCP/CLI.
- Drawio copied as code-derived architecture.
- Non-goal or acceptance gate dropped.
- Absolute local path leaked in public claim payload.
- Relation endpoints unresolved.

Residual risks for external audit:

- Phase 50 is deterministic and heuristic. It does not guarantee semantic correctness of every extracted claim.
- Large claim counts include low-value bullets from broad documentation sets; Phase 51 quality evaluation is expected to classify low-signal and unsupported claims.
- Drawio relation semantics are limited to labels and mxCell edges; richer design intent remains reviewable.

## 8. Documents To Review With This Package

Recommended external audit set:

1. `docs/V2.x/V2_7_PHASE_50_CHATGPT_AUDIT_PACKAGE.md`
2. `docs/V2.x/V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md`
3. `docs/V2.x/V2_7_PHASE_50_DEVELOPMENT_PLAN.md`
4. `docs/V2.x/V2_7_PHASE_50_ACCEPTANCE_PLAN.md`
5. `docs/V2.x/V2_7_PHASE_50_PRE_IMPLEMENTATION_AUDIT_REPORT.md`
6. `docs/V2.x/V2_7_TARGET_PRD.md`
7. `docs/V2.x/V2_7_TARGET_ARCHITECTURE.md`
8. `docs/V2.x/V2_7_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md`
9. `docs/V2.x/V2_7_FULL_PRD_COVERAGE_MATRIX.md`
10. `docs/V2.x/V2_7_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md`
11. `backend/data_service/code_assets/architecture/doc_claim_extractor.py`
12. `backend/tests/test_v2_7_document_registry.py`

## 9. Exit Decision

Internal decision: Phase 50 is accepted.

Next phase: Phase 51 Document Quality Evaluation may start after rechecking the Phase 51 pre-implementation audit against accepted Phase 50 artifacts.

V2.7 overall is not complete.
