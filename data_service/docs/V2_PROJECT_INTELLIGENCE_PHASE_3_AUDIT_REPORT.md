# V2 Phase 3 Audit Report: Pre-Development Gate

> Phase: 3 / Public Surface Inventory.
> Status: pre-development audit.

## 1. Audit Inputs

- `docs/V2_0_TARGET_ARCHITECTURE.md`
- `docs/V2_0_TARGET_PRD.md`
- `docs/V2_0_TARGET_ACCEPTANCE_PLAN.md`
- `docs/V2_0_PHASE_2_7_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V2_PROJECT_INTELLIGENCE_PHASE_3_DEVELOPMENT_PLAN.md`
- `docs/V2_PROJECT_INTELLIGENCE_PHASE_3_ACCEPTANCE_PLAN.md`
- Phase 2 accepted audit: `docs/V2_PROJECT_INTELLIGENCE_PHASE_2_AUDIT_REPORT.md`

## 2. PRD Spec Review

Phase 3 maps to V2.0 Target PRD public surface inventory requirements.

Required PRD capabilities covered by the plan:

- deterministic project surface extraction
- HTTP route inventory
- MCP tool inventory
- CLI command inventory
- capability grouping
- HTTP/MCP/CLI alignment matrix
- source evidence path and line range where deterministically available
- unresolved/low-confidence reporting
- real repo acceptance

Out of scope remains correct:

- Python symbol index
- surface-to-symbol mapping
- evidence trace graph
- Project Overview
- Agent Context Pack
- DevWiki
- Code Graph
- Quality Governance Extension

No major PRD deviation is identified.

## 3. Architecture Boundary Review

Planned implementation uses V2 code asset modules and existing Phase 1/2 extension points.

Architecture gates:

| Gate | Status |
|---|---|
| No Phase 3 routes in `backend/app/api/v1/data_service.py` | planned compliant |
| No Phase 3 core logic in `backend/data_service/service.py` | planned compliant |
| No substantial CLI logic in `backend/data_service/__main__.py` | planned compliant |
| Inventory artifacts remain under `workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/` | planned compliant |
| No mutation of `lifecycle/sources.json` | planned compliant |
| No LLM dependency | planned compliant |
| Frontend inventory is best effort and does not block core HTTP/MCP/CLI inventory | planned compliant |

## 4. False Acceptance Risk Review

Key risks and required controls:

| Risk | Control |
|---|---|
| Inventory is non-empty but misses critical public services. | Golden HTTP/MCP/CLI surface assertions are required. |
| MCP inventory drifts from actual registry. | Required count equals `len(all_tool_specs())`. |
| Capability alignment is fragmented by naming variants. | Required normalized taxonomy and golden capability merge tests. |
| Empty artifacts are accepted. | Required artifact disk inspection and non-empty counts by surface type. |
| Line ranges are fabricated. | Required line range presence only when deterministically extracted; otherwise unresolved reason. |
| Frontend inventory becomes a blocker due to best-effort static analysis. | Explicitly mark frontend inventory as best effort for V2.0 Phase 3. |
| Public payload leaks absolute paths. | Required path leak tests across HTTP/MCP/CLI. |
| V2 inventory writes into V1 source registry. | Required source registry unchanged assertion. |

## 5. Audit Findings

| Severity | Finding | Required Closure |
|---|---|---|
| note | Existing worktree contains unrelated modified/untracked files from prior work and neighboring projects. | Use path-limited staging and changed-file review before commit. |
| note | Phase 3 will increase MCP and target HTTP counts. | Update contract baselines and frontend contract only after implementing the actual surfaces. |
| note | Frontend/API static inventory can be incomplete in V2.0. | Mark unresolved or best-effort; do not claim complete frontend surface coverage. |

No open `fatal` or `major` findings are identified in the Phase 3 plan.

## 6. Decision

Phase 3 may enter implementation after this pre-development gate.

Implementation must return to this report after development and append:

- changed files
- commands run
- artifact paths inspected
- golden surface evidence
- failures and rework
- PRD deviations
- architecture deviations
- false acceptance risk assessment
- final decision
