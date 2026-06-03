# V2 Phase 2 Audit Report: Pre-Development Gate

> Phase: 2 / PR2 Repo Snapshot + File Manifest.
> Status: pre-development audit.

## 1. Audit Inputs

- `docs/V2.x/V2_0_TARGET_ARCHITECTURE.md`
- `docs/V2.x/V2_0_TARGET_PRD.md`
- `docs/V2.x/V2_0_TARGET_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_0_PHASE_2_7_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_2_DEVELOPMENT_PLAN.md`
- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_2_ACCEPTANCE_PLAN.md`

## 2. PRD Spec Review

Phase 2 maps to V2.0 Target PRD US-002: Generate Repo Snapshot.

Required PRD capabilities covered:

- generate repo snapshot
- persist snapshot artifacts
- stable snapshot ID for unchanged content
- changed content detection
- sensitive file skip
- real repo acceptance

Out of scope remains correct:

- inventory
- symbols
- mapping/evidence
- overview
- context pack
- DevWiki
- Code Graph
- Quality Governance Extension

## 3. Architecture Boundary Review

Planned implementation uses V2 code asset modules and existing code asset router/tool/CLI extension points.

Architecture gates:

| Gate | Status |
|---|---|
| No V2 core routes in `backend/app/api/v1/data_service.py` | planned compliant |
| No V2 core logic in `backend/data_service/service.py` | planned compliant |
| No substantial CLI logic in `backend/data_service/__main__.py` | planned compliant |
| No mutation of `lifecycle/sources.json` | planned compliant |
| Public outputs use repo-relative paths | planned compliant |
| V2 artifacts self-excluded from snapshot scan | planned compliant |

## 4. False Acceptance Risk Review

Key risks and required controls:

| Risk | Control |
|---|---|
| Snapshot ID changes every run because artifacts are scanned into the repo. | Required artifact self-exclusion test. |
| Secret files enter `files.jsonl`. | Required `SENSITIVE_SKIPPED` test. |
| Snapshot appears successful but artifacts are not persisted. | Required disk inspection. |
| Tests only use fixtures. | Required current repo E2E. |
| Public response leaks absolute paths. | Required path leak assertions. |
| Source registry is polluted. | Required before/after `lifecycle/sources.json` check. |

## 5. Audit Findings

| Severity | Finding | Required Closure |
|---|---|---|
| note | Existing worktree may contain unrelated changes from prior phases or other projects. | Before committing Phase 2, use path-limited staging and changed-file review. |
| note | Snapshot hash inputs must be documented in implementation output. | Include hash inputs in `snapshot.json`. |

No open `fatal` or `major` findings are identified in the Phase 2 plan.

## 6. Decision

Phase 2 may enter implementation after the user accepts this pre-development gate.

Implementation must return to this report after development and append:

- changed files
- commands run
- artifact paths inspected
- failures and rework
- PRD deviations
- architecture deviations
- false acceptance risk assessment
- final decision

## 7. Post-Implementation Summary

> Status: implemented and accepted for Phase 2.
> Review basis: V2.0 acceptance is governed by `docs/V2.x/V2_0_TARGET_PRD.md`, not the older broad V2 PRD unless explicitly referenced.

Phase 2 added a deterministic codebase snapshot service under the V2 code asset boundary.

Implemented capabilities:

- `CodebaseSnapshotService` scans imported codebases and persists snapshot artifacts.
- Snapshot artifacts are written under:
  - `workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/snapshot.json`
  - `workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/files.jsonl`
  - `workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/stats.json`
  - `workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/warnings.jsonl`
- HTTP routes:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots/{snapshot_id}`
- MCP tool:
  - `knowledge_codebase_snapshot`
- CLI command:
  - `knowledge code snapshot`

## 8. Changed Files Reviewed

Phase 2 relevant changed files:

- `backend/data_service/code_assets/snapshot.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/app/api/v1/code_assets.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`
- `backend/data_service/mcp_common.py`
- `backend/tests/test_v2_codebase_snapshot.py`
- `backend/tests/test_v2_codebase_http.py`
- `backend/tests/test_v2_codebase_mcp.py`
- `backend/tests/test_v2_codebase_cli.py`
- `backend/tests/test_data_service_api.py`
- `backend/tests/test_data_service_mcp.py`
- `backend/tests/test_public_surface_guard.py`
- `backend/tests/test_session_graphrag_contract.py`
- `backend/tests/test_session_ingest_query_build_contract_plan.py`
- `backend/tests/test_target_http_session_query.py`
- `backend/tests/test_v16_closure_acceptance.py`
- `backend/tests/test_console_governance_evidence_plan.py`
- `frontend/src/data/mcpContract.ts`
- `frontend/src/pages/KnowledgePage.vue`
- `backend/app/static/knowledge_console/index.html`
- `backend/app/static/knowledge_console/assets/index-CqGvrFk1.css`
- `backend/app/static/knowledge_console/assets/index-CyBGcI0H.js`

Architecture gate note:

- No Phase 2 snapshot route was added to `backend/app/api/v1/data_service.py`.
- No Phase 2 core snapshot logic was added to `backend/data_service/service.py`.
- CLI snapshot logic remains in `backend/data_service/cli_code.py`; `backend/data_service/__main__.py` was not expanded for Phase 2.
- Existing worktree contains unrelated pre-existing modifications outside this Phase 2 file set; path-limited staging is required before commit.

## 9. Verification Commands Run

Static compile:

```bash
python3 -m compileall -q backend/data_service/code_assets backend/app/api/v1/code_assets.py backend/data_service/mcp_code_tools.py backend/data_service/cli_code.py backend/tests/test_v2_codebase_snapshot.py
```

Focused Phase 2 and contract regression:

```bash
python3 -m pytest backend/tests/test_v2_codebase_snapshot.py backend/tests/test_v2_codebase_http.py backend/tests/test_v2_codebase_mcp.py backend/tests/test_v2_codebase_cli.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py
```

Result:

```text
67 passed, 103 warnings
```

Frontend build:

```bash
npm run build
```

Result:

```text
vue-tsc && vite build passed
```

Full backend regression:

```bash
python3 -m pytest backend/tests
```

Result:

```text
331 passed, 617 warnings
```

## 10. Failures And Rework

Initial focused regression found three failures:

- public response sanitizer treated language stats key `files` as a path leak and produced `debug_paths`
- one CLI contract test still expected Phase 1 code commands only
- frontend governance evidence test still expected `MCP 44` / target HTTP `35`

Fixes:

- adjusted `mcp_common` sanitizer to allow scalar `files` counters while still hiding dict/list file path payloads
- updated CLI contract baselines to include `knowledge code snapshot`
- updated frontend governance evidence to `MCP 45` and target HTTP `38`

Initial full backend regression then found two remaining failures:

- another CLI contract test still expected Phase 1 code commands only
- sanitizer allowance for `files` was too broad for directory scan dict payloads

Fixes:

- updated the remaining CLI contract test to include `snapshot`
- tightened `files` sanitizer allowance to scalar-only values

Final reruns passed.

## 11. Artifact Inspection

Automated real-data tests inspect disk artifacts through `backend/tests/test_v2_codebase_snapshot.py`:

- verifies `snapshot.json`, `files.jsonl`, `stats.json`, and `warnings.jsonl` exist
- reads `files.jsonl` from disk and verifies current repo files such as `backend/data_service/code_assets/registry.py`
- verifies `.git/**` and self artifact paths such as `workspace/assets/codebase/**` are excluded
- verifies `.env` is recorded as `SENSITIVE_SKIPPED` in `files.jsonl` and `warnings.jsonl`
- verifies repeated generation without content changes preserves `snapshot_id`
- verifies a controlled content change in a temporary repo changes `snapshot_id` and file hash
- verifies `lifecycle/sources.json` is not created by snapshot generation

## 12. PRD Spec Review

Phase 2 remains aligned with V2.0 Target PRD US-002.

Confirmed:

- real repo snapshot generation is implemented
- snapshot artifacts are persisted and readable
- `snapshot_id` excludes `created_at` and git dirty status; it changes with deterministic content fingerprint, scan policy hash, or commit SHA
- sensitive files and self artifacts are skipped
- HTTP/MCP/CLI all expose snapshot generation
- current repo E2E is covered by automated tests

Still intentionally out of scope:

- Phase 3 Public Surface Inventory
- Phase 4 Python Symbol Index
- Phase 5 Surface-to-Symbol Mapping and Evidence Trace
- Phase 6 read convergence beyond snapshot
- Phase 7 Project Overview and Agent Context Pack
- V2.1 DevWiki, Code Graph, Quality Governance, frontend read-only pages

No major PRD deviation was found.

## 13. False Acceptance Risk Assessment

| Risk | Assessment |
|---|---|
| Mock-only validation | closed; tests scan the current repo and a controlled temporary repo |
| Empty snapshot accepted | closed; tests assert Python/Markdown stats and real file records |
| Artifact not persisted | closed; tests read all four artifact files from disk |
| `snapshot_id` changes due to timestamps | closed; repeat generation asserts stable `snapshot_id` |
| Content changes not detected | closed; controlled file modification changes snapshot identity and file hash |
| Secret leakage | closed; `.env` is skipped and warning-recorded |
| Self-artifact feedback loop | closed; `workspace/assets/codebase/**` is excluded when inside repo |
| Public absolute path leak | closed; HTTP/MCP/CLI payload tests assert no absolute repo/workspace path values |
| Source registry pollution | closed; tests assert `lifecycle/sources.json` is not created |
| V1 regression | closed; full backend test suite passed |

## 14. Final Decision

Phase 2 passes implementation and acceptance.

Open fatal findings: none.

Open major findings: none.

Phase 3 must not start implementation until its own development plan, acceptance plan, and pre-development audit are produced and reviewed.

## 15. Post-Review Closure

After the initial Phase 2 acceptance, a code-review pass identified additional quality risks:

| Severity | Finding | Closure |
|---|---|---|
| blocker | Unknown `codebase_id` could return an empty snapshot list instead of a controlled failure. | `read_snapshot()` and `list_snapshots()` now validate the codebase registry before reading artifacts. |
| blocker | `snapshot_id` could be destabilized by git dirty status from generated artifacts when workspace output lives inside the repo. | `snapshot_id` now excludes dirty status and is based on deterministic identity inputs only. Dirty state remains metadata via `dirty_fingerprint`. |
| major | JSONL artifact writes were direct writes and could leave partial files. | `write_jsonl()` now writes through a temporary file and `os.replace()`. |
| major | `scan_policy` accepted malformed `include` / `exclude` values. | `validate_scan_policy()` rejects non-list patterns, non-string entries, non-positive size limits, and unsupported binary policies. |
| major | Self-artifact exclusion did not cover `workspace/{workspace_id}/assets/codebase/**`. | Self-exclusion now covers both `workspace/assets/codebase/**` and `workspace/*/assets/codebase/**`. |
| major | Sensitive detection could skip normal code files containing `token` in their path. | Token skip is narrowed to high-confidence token files; `token_service.py` remains included. |
| major | Snapshot list ordering was directory-name based rather than latest-first by metadata. | Snapshot listing now sorts by `created_at` descending. |
| major | Full backend regression exposed an existing non-atomic target HTTP operation write race. | `backend/app/api/v1/data_service.py` `_write_json()` now uses temporary file + `os.replace()` to prevent partial operation reads. |

Additional protection tests were added to `backend/tests/test_v2_codebase_snapshot.py`:

- repo-local workspace artifact stability
- unknown codebase controlled failure
- invalid scan policy rejection
- latest-first snapshot listing
- `.env` skip with `SENSITIVE_SKIPPED`
- `token_service.py` included as normal code
- JSONL artifact parse/readback remains covered by disk inspection tests
- target HTTP build status no longer reads partially-written operation files

Additional focused regression:

```bash
python3 -m pytest backend/tests/test_v2_codebase_snapshot.py
```

Result:

```text
6 passed
```

Additional Phase 2 contract regression:

```bash
python3 -m pytest backend/tests/test_v2_codebase_snapshot.py backend/tests/test_v2_codebase_http.py backend/tests/test_v2_codebase_mcp.py backend/tests/test_v2_codebase_cli.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py
```

Result:

```text
70 passed, 103 warnings
```

Additional race regression:

```bash
python3 -m pytest backend/tests/test_target_http_build.py::test_v16b3_build_target_http_start_status_and_no_path_leakage backend/tests/test_v2_codebase_snapshot.py
```

Result:

```text
7 passed, 14 warnings
```

Final full backend regression:

```bash
python3 -m pytest backend/tests
```

Result:

```text
334 passed, 617 warnings
```

Post-review final decision:

- Open fatal findings: none.
- Open major findings: none.
- Phase 2 remains accepted after review closure.
