# V1.x Remaining Plan Document Audit Report

> Generated from repository analysis.
> Audit scope: V1.x remaining development and acceptance plan after V1.6 closure.
> Business code is not modified by this audit.

Date: 2026-05-31

## 1. Audit Scope

Audited documents and evidence:

- `docs/V1.x/V1_X_REMAINING_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `docs/V1.6/current-vs-target-gap.md`
- `docs/V1.6/README.md`
- `docs/V1.7/README.md`
- `docs/V1.7/research-notebook-source-preview-contract.md`
- `docs/V1.8/README.md`
- `docs/V1.8/research-notebook-document-unit-contract.md`
- `docs/V1.6/public-surface-overlays/v1_9_research_notebook_evidence_spans.json`
- target HTTP tests under `backend/tests/test_target_http_*.py`
- ResearchNotebook router at `backend/app/api/v1/research_notebook.py`

## 2. Audit Conclusion

Conclusion: conditionally pass.

The new V1.x remaining plan is consistent with the repository's key facts:

- V1.6 is closed and should not absorb new backend public surface.
- V1.7 and V1.8 are already implemented as ResearchNotebook backend contract enablement phases.
- V1.9 has a route overlay and tests but lacks formal phase documentation.
- Later ResearchNotebook target HTTP capabilities exist in code/tests and need formal phase docs plus closure reports before being treated as accepted V1 milestones.

No fatal specification conflicts were found in the plan. The main risk is documentation lag: several implemented target HTTP contracts are protected by tests but not yet represented by phase-specific V1.x docs.

## 3. Findings

| Severity | Finding | Evidence | Required Action |
| --- | --- | --- | --- |
| major | V1.9 EvidenceSpan has overlay and tests but no `docs/V1.9/` contract package. | `docs/V1.6/public-surface-overlays/v1_9_research_notebook_evidence_spans.json:1-11`; `backend/tests/test_target_http_evidence_spans.py:55-68` | Create V1.9 README, contract, acceptance report, and reconcile route count. |
| major | Post-V1.8 ResearchNotebook routes exist in code/tests without a single V1.x public surface freeze manifest. | `backend/app/api/v1/research_notebook.py:28-139` | Add V1.x manifest during closure phase. |
| major | Several tests use historical labels such as V1.3, V1.4, V1.5, V1.6, while this repository's public V1.6 is already closed. | `backend/tests/test_target_http_folder_collections.py:42-151`; `backend/tests/test_target_http_url_sources.py:50-118` | Treat these labels as ResearchNotebook sub-version labels unless formalized in V1.x docs. |
| minor | V1.7/V1.8 docs are concise and implemented, but each lacks a dedicated closure audit report. | `docs/V1.7/README.md:3-10`; `docs/V1.8/README.md:1-4` | Add closure reports if these are release milestones. |
| minor | V1.x and V2 boundaries need to remain explicit to prevent scope bleed. | `docs/V2.x/V2_0_TARGET_PRD.md` and V1.x plan scope section | Repeat non-goals in every V1.x phase plan. |

## 4. Specification Consistency Checks

| Check | Result | Notes |
| --- | --- | --- |
| V1.6 closure boundary respected | pass | Plan states no new V1.6 backend public surface. |
| V1.7 source preview scope respected | pass | Plan uses only capabilities and source preview routes. |
| V1.8 DocumentUnit scope respected | pass | Plan keeps EvidenceSpan disabled until V1.9. |
| V1.9 EvidenceSpan route identified | pass | Plan uses exact overlay route. |
| MCP/CLI expansion controlled | pass | Every phase defaults to no MCP or CLI additions. |
| Compatibility route expansion controlled | pass | Every phase defaults to no new `/api/v1/knowledge/*` routes. |
| Real-data acceptance required | pass | Plan requires target HTTP tests with real workspace/source setup. |
| Path and secret leakage guarded | pass | Plan repeats no internal path and no provider secret gates. |
| V2 scope excluded | pass | Plan explicitly excludes project intelligence capabilities. |

## 5. False Acceptance Risk Review

| Risk | Level | Mitigation in Plan |
| --- | --- | --- |
| Tests pass but route is undocumented. | high | Every phase requires README, contract, and audit report. |
| Evidence refs exist but do not resolve. | high | V1.9 and later require source detail, unit detail, and evidence detail resolution. |
| AI-generated answers preserve claims but lose evidence. | high | V1.10 requires evidence refs on generated claims and fallback without evidence loss. |
| Folder or URL intake leaks local paths. | high | V1.11 requires no path leakage in every response. |
| Provider health leaks API key. | high | V1.13 requires sanitized provider metadata and secret checks. |
| V1.x quietly adds MCP/CLI tools. | medium | Every phase requires public surface guard and no MCP/CLI additions unless approved. |
| V1.x duplicates V2 project intelligence scope. | medium | V1.x plan defines explicit non-goals and closure handoff to V2. |

## 6. Required Follow-Up Before Further V1 Development

Before implementing or accepting the next V1.x phase, complete:

1. Create `docs/V1.9/README.md`.
2. Create `docs/V1.9/research-notebook-evidence-span-contract.md`.
3. Create `docs/V1.9/PHASE-V1.9-EVIDENCE-SPAN-CONTRACT-REPORT.md`.
4. Reconcile V1.9 public surface count against V1.6 closure count plus V1.7 and V1.8 additions.
5. Decide whether V1.10+ phase numbering should track data_service V1.x or ResearchNotebook frontend/backend sub-version labels.

## 7. Audit Decision

The plan is acceptable as a planning baseline, with the following condition:

V1.9 documentation and public surface reconciliation must be completed before any new V1.x feature phase is claimed as accepted.

There are no fatal audit findings. There are major documentation alignment findings, but the plan explicitly identifies them and gives remediation steps.
