# V2.8 Phase 61-62 Context Pack and Closure Specification

> Development, acceptance, and pre-implementation audit specification for Phase 61 and Phase 62.

## 1. Phase 61 Goal

Create Architecture Context Pack v2 for agents and maintainers, using V2.8 dashboard, graph, ranking, code fact chains, intent evidence, and review queues.

## 2. Phase 61 Required Implementation

- Build `architecture_context_pack_v2/{pack_id}.json`.
- Support modes:
  - `project_brief`
  - `task_context`
- Render JSON and Markdown from the same internal model.
- Enforce token budget with evidence preservation.

## 3. Phase 61 Acceptance

- every recommendation has evidence or `needs_review`;
- small token budget removes unsupported recommendations rather than keeping evidence-free guidance;
- pack cites source artifacts;
- HTTP/MCP/CLI read parity passes.

## 4. Phase 62 Goal

Close V2.8 with full PRD coverage, real E2E, public contract parity, false-green audit, and no open fatal/major finding.

## 5. Phase 62 Required Implementation

- Update `V2_8_FULL_PRD_COVERAGE_MATRIX.md`;
- update `V2_8_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md`;
- update `V2_8_GAP_ANALYSIS.md`;
- write final V2.8 closure audit report;
- run focused tests, contract tests, and real E2E.

## 6. Phase 62 Acceptance

- no in-scope pending row remains;
- accepted rows cite test command, artifact path, artifact count, real repo evidence, and audit report;
- public outputs contain no local paths or secrets;
- V2.0-V2.7 source artifact hash gate passes;
- V2.8 does not claim IDE-grade navigation, full static analysis, or pure code-derived design intent recovery.

## 7. False-Green Rejection

Reject closure if:

- accepted row lacks evidence;
- mock-only run is counted as E2E;
- HTTP works but MCP/CLI parity is untested;
- context pack has unsupported recommendations;
- chart/report contains unpersisted facts;
- old artifacts are silently rewritten.
