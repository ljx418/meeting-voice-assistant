# V2.9 Phase 63-67 Implementation Acceptance Audit Report

## Status

Accepted with one explicit real-repo blocker:

- `data_service`: accepted for Phase 63-67.
- `HarnessOS`: accepted as structured-blocker behavior, not accepted line-level evidence improvement.

This report does not claim full V2.9 closure by itself. Phase 68 closure must reference this report plus final coverage matrix updates.

## Implemented Scope

Phase 63 Public Surface Evidence v2:

- Added `architecture_public_surface_evidence_v2` artifact generation.
- Accepted evidence requires repo-relative path, valid line range, confidence >= `0.85`, and `truth_check=passed`.
- Missing or invalid line range is persisted as `needs_review` / `blocked`, never converted into accepted evidence.

Phase 64 Code Relationship Layer v2:

- Added shallow relationships: `capability_implemented_by`, `surface_handled_by`, `module_imports_module`, and `module_referenced_by_test`.
- Added `semantic_claim` to separate deterministic bindings, dependency evidence, implementation hints, and heuristic test references.
- Forbidden relationship types remain unsupported: runtime calls, data flow, control flow, runtime topology, and type-inferred dependencies.

Phase 65 Ranking Calibration v2:

- Added ranking and review queue v3 artifacts.
- Fatal/major pinning invariant is enforced.
- `hidden_major_count=0` and `hidden_fatal_count=0` are explicit summary fields and test assertions.

Phase 66 Human Review Report v2:

- Added persisted report JSON plus HTML and Mermaid views.
- HTML text is escaped; Mermaid node IDs are generated from persisted artifact IDs.
- Report renderer records that it introduces no unpersisted facts.

Phase 67 Architecture Context Pack v3:

- Added modes `project_brief`, `task_context`, `architecture_review`.
- Added roles `maintainer`, `coding_agent`, `documentation_agent`, `architecture_reviewer`.
- Added `source_phase_refs=[63,64,65,66]`.
- Every recommendation has `evidence_refs` or `needs_review`.
- Small token budgets omit low-priority recommendations rather than retaining advice with removed evidence.

## Public Surface

HTTP:

- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report/views/{view_id}`
- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack/{pack_id}`

MCP:

- `knowledge_code_architecture_evidence_v2_build`
- `knowledge_code_architecture_evidence_v2`
- `knowledge_code_architecture_relationships_v2_build`
- `knowledge_code_architecture_relationships_v2`
- `knowledge_code_architecture_ranking_v2_build`
- `knowledge_code_architecture_ranking_v2`
- `knowledge_code_architecture_human_report_v2_build`
- `knowledge_code_architecture_human_report_v2`
- `knowledge_code_architecture_human_report_v2_view`
- `knowledge_code_architecture_context_pack_v3`
- `knowledge_code_architecture_context_pack_v3_read`

CLI:

- `knowledge code architecture evidence-v2-build`
- `knowledge code architecture evidence-v2`
- `knowledge code architecture relationships-v2-build`
- `knowledge code architecture relationships-v2`
- `knowledge code architecture ranking-v2-build`
- `knowledge code architecture ranking-v2`
- `knowledge code architecture human-report-v2-build`
- `knowledge code architecture human-report-v2`
- `knowledge code architecture human-report-v2-view`
- `knowledge code architecture context-pack-v3`
- `knowledge code architecture context-pack-v3-read`

## Automated Tests

Commands:

```bash
pytest backend/tests/test_v2_9_architecture_evidence_review.py backend/tests/test_public_surface_guard.py -q
pytest backend/tests/test_v2_7_document_registry.py backend/tests/test_v2_8_reading_dashboard.py backend/tests/test_v2_9_architecture_evidence_review.py -q
git diff --check -- backend/data_service/code_assets/artifacts.py backend/data_service/code_assets/architecture/persistence.py backend/data_service/code_assets/architecture/service.py backend/data_service/code_assets/architecture/surface_evidence_v2.py backend/data_service/code_assets/architecture/code_relationships_v2.py backend/data_service/code_assets/architecture/ranking_calibration_v2.py backend/data_service/code_assets/architecture/human_review_report_v2.py backend/data_service/code_assets/architecture/context_pack_v3.py backend/app/api/v1/code_assets_architecture.py backend/data_service/mcp_code_architecture_tools.py backend/data_service/cli_code_architecture.py backend/tests/test_v2_9_architecture_evidence_review.py backend/tests/test_public_surface_guard.py
```

Results:

- V2.9 focused + public surface guard: `6 passed`.
- V2.7/V2.8/V2.9 adjacent regression: `22 passed`.
- `git diff --check`: passed with no whitespace errors.

## Real Repo E2E

`data_service` current repository:

```json
{
  "codebase_id": "codebase_data_service",
  "snapshot_id": "snap_1f9407235333a1796f97",
  "accepted_evidence": 374,
  "relationship_count": 1165,
  "hidden_major_count": 0,
  "hidden_fatal_count": 0,
  "report_views": [
    "architecture_capability_entrypoint_map.mmd",
    "architecture_evidence_heatmap.mmd",
    "architecture_human_review_report_v2.html"
  ],
  "source_phase_refs": [63, 64, 65, 66]
}
```

`HarnessOS` current repository:

```json
{
  "codebase_id": "codebase_harnessOS",
  "snapshot_id": "snap_35a73ffc4da1eb39e3a9",
  "accepted_evidence": 0,
  "evidence_rows": 120,
  "harnessos_status": "structured_blocker",
  "blocker_counts": {
    "LINE_RANGE_INVALID": 120
  },
  "relationship_count": 715,
  "hidden_major_count": 0,
  "hidden_fatal_count": 0,
  "report_views": [
    "architecture_capability_entrypoint_map.mmd",
    "architecture_evidence_heatmap.mmd",
    "architecture_human_review_report_v2.html"
  ]
}
```

HarnessOS was not falsely accepted as improved line-level evidence. The current result is a valid structured blocker: public-surface candidates exist, but inventory lacks deterministic line ranges.

## PRD / Spec Review

No fatal or major PRD deviation found for Phase 63-67 implementation.

Accepted:

- Evidence claims are line-level only when truth-checked.
- Relationship layer does not claim full call graph, data flow, control flow, runtime topology, or type inference.
- Ranking does not hide fatal/major findings.
- Human report is rendered from persisted report JSON.
- Context Pack v3 consumes V2.9 artifacts and preserves evidence policy.

Known limitation:

- HarnessOS still lacks accepted line-level public surface evidence due to missing deterministic line ranges. This is recorded as a blocker, not a successful extraction.

## False Acceptance Review

Rejected false-green patterns:

- No documentation-only claim is promoted to code evidence.
- No token-overlap-only relationship is marked accepted.
- No import/reference is called a runtime call.
- No recommendation remains without evidence or `needs_review`.
- No HTML/Mermaid view introduces unpersisted architecture facts.
- No absolute repository path was observed in tested public payloads.

## Audit Opinion

Phase 63-67 can proceed to Phase 68 closure review. The primary residual gap is HarnessOS line-range extraction quality, which should be tracked in the V2.9 closure matrix as structured blocker unless fixed by a later extractor.
