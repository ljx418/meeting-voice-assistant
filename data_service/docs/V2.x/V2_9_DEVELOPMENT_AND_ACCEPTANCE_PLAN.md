# V2.9 Development and Acceptance Plan

> V2.9 is currently in documentation development.
> Business code implementation must not begin until this document set passes external audit.

Date: 2026-06-05

## 1. Phase Overview

| Phase | Name | Goal |
| --- | --- | --- |
| 63 | Public Surface Evidence v2 | Improve deterministic line-level public-surface evidence, especially for HarnessOS |
| 64 | Code Relationship Layer v2 | Build shallow capability/surface/module/test relationship paths |
| 65 | Ranking Calibration v2 | Reduce duplicate ranking noise without hiding major/fatal risks |
| 66 | Human Review Report v2 | Produce richer human-readable HTML/Mermaid architecture review |
| 67 | Architecture Context Pack v3 | Produce task-aware context packs from V2.9 artifacts |
| 68 | Closure Acceptance | Complete PRD coverage, real E2E, false-green audit |

## 2. Shared Development Rules

- Use existing V2.0-V2.8 artifacts as inputs.
- Do not silently mutate V2.0-V2.8 source artifacts.
- Store V2.9 outputs under `architecture/v2_9`.
- Keep HTTP/MCP/CLI handlers thin.
- Keep deterministic evidence separate from heuristic `needs_review`.
- Use real `data_service` and HarnessOS repositories for acceptance.

## 3. Shared Acceptance Rules

Every phase must:

- run focused tests;
- inspect persisted artifacts;
- compare HTTP/MCP/CLI payloads where applicable;
- run real E2E on `data_service` and HarnessOS;
- verify V2.8 baseline artifact availability before Phase 63 implementation;
- verify V2.0-V2.8 input artifact hashes are not silently changed;
- verify public payloads do not leak absolute local paths;
- run PRD/spec review and false-green review;
- produce a phase acceptance audit report.

Required automated or scripted checks:

```text
test_v2_9_v28_baseline_availability.py
test_v2_9_public_surface_truth_sampling.py
test_v2_9_public_surface_category_coverage.py
test_v2_9_artifact_immutability_hash_gate.py
test_v2_9_forbidden_relationship_types.py
test_v2_9_relationship_semantic_claims.py
test_v2_9_ranking_major_fatal_pinning.py
test_v2_9_report_no_unpersisted_nodes.py
test_v2_9_report_renderer_consistency.py
test_v2_9_context_pack_token_budget_evidence.py
test_v2_9_context_pack_source_phase_refs.py
test_v2_9_public_payload_redaction.py
test_v2_9_http_mcp_cli_error_parity.py
```

## 4. Stop Conditions

Stop and request human review if:

- HarnessOS is unavailable and the phase would otherwise use mocks;
- V2.8 baseline artifacts are unavailable and the phase would otherwise claim improvement;
- a V2.9 artifact rewrites V2.0-V2.8 source artifacts;
- a heuristic relationship is promoted to accepted deterministic evidence;
- relationship output emits an invalid `semantic_claim`;
- ranking hides a fatal/major item;
- human report hides `needs_review`;
- human report renderer emits nodes absent from persisted report JSON;
- context pack guidance lacks evidence and is not marked `needs_review`;
- context pack omits V2.9 `source_phase_refs`;
- public payload leaks local paths, secrets, or raw tracebacks.

## 5. Public Contract

V2.9 must align HTTP, MCP, and CLI reads for:

- public surface evidence v2;
- code relationships v2;
- ranking v2;
- human review report v2;
- context pack v3.

Public responses must expose:

- `schema_version`;
- `workspace_id`;
- `codebase_id`;
- `snapshot_id`;
- stable ids;
- artifact refs;
- warning/unresolved counts;
- redaction status;
- structured errors.

## 6. Completion Definition

V2.9 is complete when:

- `V2_9_FULL_PRD_COVERAGE_MATRIX.md` has no pending in-scope row;
- `V2_9_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md` cites real data_service and HarnessOS artifacts;
- `V2_9_DOCUMENT_AUDIT_REPORT.md` reports no fatal/major document gap;
- `V2_9_PHASE_68_CLOSURE_AUDIT_REPORT.md` reports no open fatal/major implementation finding;
- target PRD, architecture, plan, gap, drawio, and coverage matrix are consistent.
