# V2.9 Gap Analysis

> Current-vs-target gap analysis for V2.9.

Date: 2026-06-05

## 1. Current V2.8 Baseline

V2.8 has accepted:

- readable architecture dashboard;
- graph aggregation and filtered views;
- code fact chains and runtime boundaries;
- signal ranking and review queue v2;
- intent evidence;
- Architecture Context Pack v2;
- real E2E on `data_service` and HarnessOS.

## 2. Remaining Gaps Addressed by V2.9

| Gap | Current behavior | V2.9 target | Phase |
| --- | --- | --- | --- |
| HarnessOS line evidence | code fact chains generated but accepted chains = 0 | public surface evidence v2 improves accepted evidence or reports blockers | 63 |
| implementation path depth | entrypoint chains only | shallow capability/surface/module/test relationship paths | 64 |
| ranking noise | many major/pinned items | grouping, calibration, severity normalization | 65 |
| human report readability | readable dashboard but limited audit narrative | richer five-section human review report | 66 |
| agent consumption | context pack v2 | context pack v3 with V2.9 relationships and calibrated risk | 67 |

## 3. Major Risks

- evidence extractor may overclaim heuristic matches;
- ranking calibration may hide major/fatal findings;
- human report may become polished but unsupported;
- HarnessOS may not expose enough deterministic patterns;
- context pack may drop evidence under token pressure.

## 4. Risk Controls

- accepted evidence requires repo-relative path and line range;
- heuristic relationships stay `needs_review`;
- major/fatal findings remain pinned;
- human report nodes resolve to persisted artifacts;
- token budget omits unsupported recommendations.

## 5. V2.9 Completion Gap

At document-development time, all V2.9 functionality is planned, not implemented. Completion requires Phase 63-68 implementation, real E2E, and final closure audit.
