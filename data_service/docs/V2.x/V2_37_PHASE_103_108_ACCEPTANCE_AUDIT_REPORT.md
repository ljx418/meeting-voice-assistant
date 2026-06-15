# V2.37 Phase 103-108 Acceptance Audit Report

## Audit Verdict

Status: accepted with environment-limited full-suite testing.

The V2.37 implementation now provides a document-grounded architecture reconstruction pipeline that matches the approved PRD and target architecture:

- Phase 103: Document Authority Registry v2.
- Phase 104: Architecture Claim Graph v2.
- Phase 105: Current Implementation Model.
- Phase 106: Claim-to-Code Verification.
- Phase 107: Reconstruction Report and Agent Brief.
- Phase 108: closure acceptance evidence for the implemented scope.

No fatal or major PRD/spec deviation was found in the implemented V2.37 scope.

## Implemented Surface

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/report
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/verification
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/view
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/brief
```

MCP:

```text
knowledge_code_doc_grounded_architecture_build
knowledge_code_doc_grounded_architecture_report
knowledge_code_doc_grounded_verification
knowledge_code_doc_grounded_architecture_brief
```

CLI:

```text
knowledge code architecture doc-grounded build
knowledge code architecture doc-grounded report
knowledge code architecture doc-grounded verification
knowledge code architecture doc-grounded brief
```

## Artifact Layout

V2.37 artifacts are written under:

```text
workspace/assets/codebase/{codebase_id}/architecture/doc_grounded/
```

Key artifacts:

```text
document_authority_registry.json
documents.jsonl
architecture_claims.jsonl
architecture_claim_relations.jsonl
target_architecture_model.json
current_implementation_model.json
verification_matrix.jsonl
drift_findings.jsonl
reconstruction_report.json
views/document_grounded_architecture_report.html
views/document_grounded_architecture_diff.mmd
views/document_grounded_architecture_diff.svg
briefs/{brief_id}.json
briefs/{brief_id}.md
```

## PRD / Spec Review

Accepted behavior:

- Document claims are kept separate from code facts.
- Drawio nodes are extracted as document-derived claims and are not marked as code facts.
- A verification row can be `supported` only when document evidence and code evidence are both present.
- `token_overlap_only` cannot produce `supported`.
- HTML report renders an inline SVG diagram and does not expose Mermaid source in the user-facing HTML.
- Public payloads use repo-relative paths and do not leak the local repository absolute path.
- V2.37 implementation is isolated in a focused package and does not add core logic to old large service files.

Rejected / not claimed:

- Full recovery of human design intent from code alone.
- Full call graph, data flow, control flow, runtime topology, or type inference.
- HarnessOS-specific hardcoding.
- Automatic rewriting of project docs or target project code.

## Test Evidence

Passed:

```text
pytest -q backend/tests/test_v2_37_doc_grounded_architecture.py
```

Result:

```text
1 passed
```

Passed:

```text
pytest -q backend/tests/test_v2_37_doc_grounded_architecture.py backend/tests/test_public_surface_guard.py
```

Result:

```text
6 passed
```

Passed:

```text
git diff --check -- backend/data_service/code_assets/doc_grounded_architecture \
  backend/app/api/v1/code_assets_doc_grounded_architecture.py \
  backend/app/api/__init__.py \
  backend/data_service/mcp_code_doc_grounded_architecture_tools.py \
  backend/data_service/mcp_code_tools.py \
  backend/data_service/cli_code_architecture.py \
  backend/tests/test_v2_37_doc_grounded_architecture.py \
  backend/tests/test_public_surface_guard.py \
  docs/V2.x/V2_37_PHASE_103_DOC_AUTHORITY_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

Result:

```text
no whitespace errors
```

## Real Repo E2E Evidence

Input repository:

```text
data_service
```

Validation mode:

```text
controlled real input scan
```

Reason:

- The first unrestricted real repo attempt exceeded the practical interactive validation window because it included a large number of historical documents and files.
- The accepted run still used the real `data_service` repository, but constrained scanning to the V2.37 target docs and V2.37 implementation files.
- This verifies real project behavior without converting the E2E into a broad performance benchmark.

Accepted run summary:

```json
{
  "workspace_id": "v237_real_data_service_controlled",
  "codebase_id": "codebase_data_service_v237_controlled",
  "snapshot_id": "snap_12e6d4039feac38dcbc8",
  "document_count": 13,
  "claim_count": 711,
  "current_node_count": 142,
  "supported_count": 115,
  "verification_count": 804,
  "html_has_inline_svg": true
}
```

Hard assertions passed:

- supported rows are non-empty.
- every supported row has document evidence and code evidence.
- HTML report contains inline SVG.
- HTML report does not expose Mermaid source.
- public payload does not leak the local absolute repository path.

## Full Backend Suite Status

Attempted:

```text
pytest -q backend/tests
```

Result under `/usr/bin/python3`:

```text
collection failed because the interpreter is Python 3.9, while backend/pyproject.toml requires Python >= 3.11.
```

Attempted:

```text
PYTHONPATH=backend /usr/local/bin/python3.12 -m pytest -q backend/tests
```

Result:

```text
collection failed because Python 3.12 does not have the project test dependencies installed, including fastapi.
```

Audit interpretation:

- This is an environment/dependency issue, not a V2.37 product failure.
- Focused V2.37 tests and public surface guard passed in the available dependency-bearing environment.
- A fully provisioned Python >= 3.11 test environment is still required for repository-wide test closure.

## False-Acceptance Review

No false-green condition was accepted:

- Synthetic-only testing was not used as the sole evidence; a controlled real `data_service` E2E was run.
- Public surface changes were added to the explicit guard list.
- The full-suite test limitation was reported as an environment blocker, not hidden as a pass.
- No unsupported V2.37 claim was upgraded to a full static-analysis claim.

## Open Findings

Fatal: none.

Major: none.

Minor:

- Full backend suite requires a Python >= 3.11 environment with project dependencies installed. Current local interpreters split compatibility and dependency availability.
- The unrestricted real-repo scan should be revisited as a later performance hardening task; V2.37 functional closure used controlled real input.
