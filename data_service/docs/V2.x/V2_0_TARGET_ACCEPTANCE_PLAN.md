# V2.0 Target Acceptance Plan: Agent-callable Project Intelligence MVP

> This plan accepts V2.0 only. V2.1 Expansion items are not blockers.

## 1. Acceptance Inputs

- Real codebase: `/Users/Zhuanz/Desktop/workspace/data_service`
- Temporary workspace root: `/private/tmp/data_service_v2_0_acceptance`
- Required public entrypoints: HTTP, MCP, CLI
- Required regression suites: backend tests and frontend build when frontend contract changes

## 2. End-to-End Acceptance Flow

```text
1. Import current repo as codebase.
2. Generate repo snapshot.
3. Build public surface inventory.
4. Build Python symbol index.
5. Build mapping and evidence trace.
6. Read artifacts through HTTP/MCP/CLI using V2ReadEnvelope.
7. Generate Project Overview.
8. Generate Agent Context Pack in project_brief and task_context modes.
9. Inspect artifacts on disk.
10. Run V1 regression smoke tests.
11. Complete PRD/spec/audit review.
```

## 3. Phase Acceptance Summary

| Phase | Acceptance Gate |
|---|---|
| 2 Snapshot | Stable snapshot ID, changed-content detection, secret skip, important paths, repo-relative warnings |
| 3 Inventory | Golden HTTP/MCP/CLI surfaces, dynamic MCP count, capability taxonomy, route/CLI count baselines, unresolved ratio |
| 4 Symbols | Real line ranges, signatures, stable symbol IDs, syntax error isolation |
| 5 Mapping/Evidence | V1/V2 capability coverage, mapping/evidence coverage metrics, 10 evidence span truth samples, unresolved reason, no absolute paths |
| 6 Convergence | Shared `V2ReadEnvelope` success/error shapes, same counts/IDs/warnings/unresolved/artifact refs across HTTP/MCP/CLI |
| 7 Overview/Context | Overview with evidence, `project_brief`, `task_context`, token budget, evidence-preserving truncation, recommended next steps |

## 4. Required Artifact Inspection

Acceptance must inspect these files on disk:

```text
workspace/assets/codebase/{codebase_id}/codebase.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/snapshot.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/files.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/stats.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/warnings.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/surfaces.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/capabilities.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/alignment_matrix.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbols.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/imports.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mappings.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/evidence.jsonl
workspace/assets/codebase/{codebase_id}/overview.json
workspace/assets/codebase/{codebase_id}/agent_context/{pack_id}.json
```

## 5. Required Tests

Minimum command set for final V2.0 acceptance:

```bash
python3 -m pytest backend/tests
```

If frontend contract files change:

```bash
npm run build --prefix frontend
```

Required V2.0-specific tests:

```bash
python3 -m pytest backend/tests/test_v2_codebase_snapshot.py
python3 -m pytest backend/tests/test_v2_codebase_inventory.py
python3 -m pytest backend/tests/test_v2_codebase_symbols.py
python3 -m pytest backend/tests/test_v2_codebase_trace.py
python3 -m pytest backend/tests/test_v2_codebase_interface_convergence.py
python3 -m pytest backend/tests/test_v2_project_overview.py
python3 -m pytest backend/tests/test_v2_agent_context_pack.py
```

## 6. False Acceptance Rejection

Reject V2.0 acceptance if any of these occur:

- Tests only use mocks and do not import the real repo.
- Artifact files are generated but not read back.
- Snapshot artifacts are included in a later snapshot because self-exclusion failed.
- Empty inventory/symbol/mapping outputs are accepted as success.
- HTTP passes but MCP/CLI are not checked.
- Evidence has file names but no real line ranges.
- Important context pack recommendations lack evidence or `needs_review`.
- Token truncation keeps guidance while dropping the evidence that supports it.
- Absolute paths appear in public HTTP/MCP/CLI outputs.
- V2 artifacts modify `lifecycle/sources.json`.
- Implementation requires adding V2 core logic to `data_service.py` or `service.py`.

## 7. Additional Phase-specific Hard Gates

Phase 2:

- `workspace/assets/codebase/**`, `assets/codebase/**`, and `.data_service/**` are excluded if they appear under the scanned repo.
- `snapshot_id` hash inputs are documented and exclude `generated_at`.
- Dirty fingerprint scope is documented.

Phase 3:

- `capability_id` normalization is documented.
- Golden capabilities include `source_import`, `query`, `build`, `quality`, `graph`, and `codebase_import`.
- Alignment matrix merges HTTP/MCP/CLI surfaces for those golden capabilities.
- Frontend/API-facing extraction is marked `best_effort` and does not block V2.0 core if backend/MCP/CLI evidence is complete.

Phase 4:

- Same file parsed twice produces identical `symbol_id` values.
- Function body-only changes do not change `symbol_id`.
- Signature-change behavior is explicitly tested and documented.
- Same-name nested functions/methods do not collide.

Phase 5:

- `mapping_coverage_by_surface_type` reports `http_api`, `mcp_tool`, and `cli_command` coverage.
- `evidence_coverage_by_capability` reports at least `source_import`, `query`, `build`, `quality`, `graph`, and `codebase_import`.
- `success_mapping_confidence_min` is `0.80`.
- Unresolved reasons use a stable reason taxonomy.

Phase 6:

- `V2ReadEnvelope` has both success and error forms.
- CLI stdout contains JSON envelope; stderr is reserved for process diagnostics.
- `artifact_refs` ordering is stable across HTTP/MCP/CLI.

Phase 7:

- `overview` is the project fact summary; `project_brief` is the compressed Agent-context rendering.
- Output includes `omitted_items` when token budget or evidence constraints remove content.
- Evidence cannot be silently removed while retaining the recommendation it supports.

## 8. Final Decision Template

The final V2.0 audit report must state:

```text
Decision: accepted | rework required | stop for human review
Implemented phases:
Artifacts inspected:
Commands run:
Failures and rework:
PRD deviations:
Architecture deviations:
False acceptance risks:
Open questions:
```
