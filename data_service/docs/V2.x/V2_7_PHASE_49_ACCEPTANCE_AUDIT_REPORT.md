# V2.7 Phase 49 Acceptance Audit Report

> Acceptance audit for Phase 49 Document Asset Registry.
> Real repository data was used for end-to-end validation.
> This report does not claim Phase 50-55 completion.

Date: 2026-06-04

## Result

Result: accepted for Phase 49.

Phase 49 now provides a V2.7 document asset registry for architecture governance inputs. It discovers Markdown, Mermaid, and Drawio document assets from accepted codebase snapshots, classifies document type and authority, persists registry artifacts, and exposes read/build access through HTTP, MCP, and CLI.

## Scope Accepted

Accepted:

- Document asset registry artifact generation.
- Markdown / Drawio / Mermaid document candidate discovery.
- Repository-relative `repo_path` in public payloads.
- Current V2.7 target documents classified as primary target authority.
- Prior V2.x documents classified as historical references.
- Drawio documents included in snapshot and document registry input.
- HTTP / MCP / CLI document registry read/build access.
- Structured missing-artifact error for registry reads before build.

Not accepted in this phase:

- Architecture claim extraction.
- Document quality scoring.
- Document-code alignment.
- Target/current/diff reconstruction report.
- Governance feedback/rules integration.

## Implementation Evidence

Key files:

- `backend/data_service/code_assets/architecture/doc_registry.py`
- `backend/data_service/code_assets/architecture/service.py`
- `backend/data_service/code_assets/architecture/persistence.py`
- `backend/data_service/code_assets/snapshot.py`
- `backend/app/api/v1/code_assets_architecture.py`
- `backend/data_service/mcp_code_architecture_tools.py`
- `backend/data_service/cli_code_architecture.py`
- `frontend/src/data/mcpContract.ts`
- `backend/tests/test_v2_7_document_registry.py`

Persisted artifacts:

- `architecture/docs/architecture_docs.jsonl`
- `architecture/docs/architecture_doc_sources.jsonl`

Public interfaces:

- HTTP `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/build`
- HTTP `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs`
- MCP `knowledge_code_architecture_docs_build`
- MCP `knowledge_code_architecture_docs_list`
- CLI `knowledge code architecture docs-build`
- CLI `knowledge code architecture docs`

## Deviations Found And Closed

| Finding | Severity | Resolution |
| --- | --- | --- |
| `V2_7` filenames were parsed as `V2` because the parent `docs/V2.x` directory was matched first. | major | Version extraction now scans all candidates and chooses the most specific version. |
| `.drawio` files were not included in default snapshot scanning, so document registry could not discover architecture diagrams. | major | `.drawio` and `.mmd` were added to default snapshot include extensions and language mapping. |
| Public envelope redacts generic `path` fields. | minor | Document assets now include `repo_path` for safe repo-relative public output while internal artifacts keep `path`. |
| MCP frontend contract snapshot drifted after adding two tools. | minor | `frontend/src/data/mcpContract.ts` updated to include V2.7 document registry MCP tools. |

No open fatal or major finding remains for Phase 49.

## Real Repository E2E

Command executed against real repositories with workspace output under `/private/tmp/v27_phase49_real_workspace`.

Results:

| Repo | Status | Document count | Key assertions |
| --- | ---: | ---: | --- |
| `data_service` | pass | 318 | V2.7 PRD found, V2.7 target architecture found, no absolute repo path in public payload. |
| `harnessOS` | pass | 628 | V4 Drawio found, V6 document found, no absolute repo path in public payload. |

Observed counts:

```json
{
  "data_service": {
    "document_count": 318,
    "doc_type_counts": {
      "acceptance_plan": 62,
      "audit_report": 50,
      "development_plan": 45,
      "drawio": 12,
      "gap_analysis": 6,
      "handoff_summary": 1,
      "prd": 14,
      "readme": 9,
      "target_architecture": 8,
      "unknown_architecture_doc": 111
    }
  },
  "harnessOS": {
    "document_count": 628,
    "doc_type_counts": {
      "acceptance_plan": 69,
      "audit_report": 66,
      "development_plan": 82,
      "drawio": 51,
      "gap_analysis": 8,
      "handoff_summary": 8,
      "prd": 26,
      "readme": 34,
      "target_architecture": 275,
      "unknown_architecture_doc": 9
    }
  }
}
```

## Test Evidence

Commands:

```bash
/usr/bin/python3 -m pytest backend/tests/test_v2_7_document_registry.py
/usr/bin/python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py
/usr/bin/python3 -m pytest backend/tests/test_v2_codebase_snapshot.py
```

Results:

- `backend/tests/test_v2_7_document_registry.py`: 2 passed.
- `backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py`: 12 passed, 25 skipped.
- `backend/tests/test_v2_codebase_snapshot.py`: 6 passed.

## PRD / Spec Review

Phase 49 aligns with V2.7 PRD scope:

- It treats project documents as first-class architecture governance inputs.
- It keeps document claims separate from code facts.
- It does not claim architecture reconstruction or doc-code alignment.
- It preserves prior V2.x documents as historical unless explicitly V2.7 authority.
- It uses real `data_service` and `harnessOS` repositories for acceptance.

No PRD expansion was introduced.

## False Acceptance Review

Rejected false-green scenarios:

- Empty document registry accepted: rejected by focused tests and real E2E counts.
- Mock-only registry accepted: rejected by real `data_service` and `harnessOS` runs.
- Drawio copied as code-derived evidence: not applicable in Phase 49; drawio is only registered as document asset.
- Historical V2.x docs treated as current target authority: rejected by focused tests.
- Absolute repo path leaked in public payload: rejected by focused tests and real E2E.
- HTTP-only implementation accepted: rejected by HTTP/MCP/CLI focused test.

## Exit Decision

Phase 49 is complete and accepted.

Phase 50 may begin only after a Phase 50-specific development plan, acceptance plan, and pre-implementation audit are created and audited against the V2.7 PRD. Phase 50 must not treat document registry entries as accepted architecture claims without claim-level evidence and confidence policy.
