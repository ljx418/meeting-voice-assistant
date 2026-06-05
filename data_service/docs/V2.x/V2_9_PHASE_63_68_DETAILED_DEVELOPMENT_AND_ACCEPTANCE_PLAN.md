# V2.9 Phase 63-68 Detailed Development and Acceptance Plan

> Detailed execution plan for V2.9 documentation development.
> This document is decision-complete for implementation after external audit.

Date: 2026-06-05

## Phase 63: Public Surface Evidence v2

Package:

- `V2_9_PHASE_63_PUBLIC_SURFACE_EVIDENCE_PACKAGE.md`

Development:

- build `architecture_public_surface_evidence_v2.jsonl`;
- extract line-level evidence from decorators, parser definitions, registry lists, command tables, workflow manifests, console/TUI entrypoints;
- record `extractor`, `confidence`, `line_range`, `needs_review`, and blocker reason.
- apply deterministic extractor catalog and blocker taxonomy from the Phase 63 package.
- verify V2.8 closure/baseline availability before claiming HarnessOS improvement.

Acceptance:

- data_service evidence remains compatible with existing public surface guard;
- HarnessOS accepted evidence improves over V2.8 or structured blockers are recorded;
- every accepted row has repo-relative path and line range;
- no documentation-only claim becomes code evidence.
- at least 20 accepted evidence rows pass line-range truth sampling across real repositories.
- category coverage includes data_service HTTP/MCP/CLI and attempted HarnessOS workflow/console/CLI/TUI/registry patterns.

## Phase 64: Code Relationship Layer v2

Package:

- `V2_9_PHASE_64_CODE_RELATIONSHIP_LAYER_PACKAGE.md`

Development:

- build `architecture_code_relationships_v2.jsonl`;
- build `architecture_module_clusters_v2.json`;
- create shallow capability -> surface -> handler -> module -> test/reference paths;
- classify relationships as `deterministic`, `heuristic`, or `needs_review`.
- use only allowed relationship types from the Phase 64 package.
- include and preserve `semantic_claim` on every relationship row.

Acceptance:

- data_service source import/query/build/quality/code architecture paths are represented where evidence exists;
- HarnessOS workflow/console/CLI paths are represented where evidence exists;
- import dependency is not accepted as runtime call;
- unresolved paths remain visible.
- forbidden full call graph, data flow, control flow, runtime topology, and type inference claims are absent.
- report/context consumers do not render dependency evidence as runtime calls.

## Phase 65: Ranking Calibration v2

Package:

- `V2_9_PHASE_65_RANKING_CALIBRATION_PACKAGE.md`

Development:

- build `architecture_signal_ranking_v2.json`;
- build `architecture_review_queue_v3.json`;
- group duplicate findings;
- normalize severity;
- keep major/fatal pinning;
- expose grouping and calibration metrics.
- expose score components, reason codes, grouping metrics, and pinning invariants.
- expose `hidden_major_count` and `hidden_fatal_count`.

Acceptance:

- major/fatal items remain visible;
- duplicate groups reduce top-N noise;
- every item has score components and reason codes;
- weak evidence remains reviewable and does not become accepted.
- grouping preserves all evidence refs and source finding ids.
- `hidden_major_count = 0` and `hidden_fatal_count = 0`.

## Phase 66: Human Review Report v2

Package:

- `V2_9_PHASE_66_HUMAN_REVIEW_REPORT_PACKAGE.md`

Development:

- build `architecture_human_review_report_v2.json`;
- render `views/architecture_human_review_report_v2.html`;
- render `views/architecture_evidence_heatmap.mmd`;
- render `views/architecture_capability_entrypoint_map.mmd`;
- include target/current/drift/evidence/review queue sections.
- render HTML and Mermaid from persisted report JSON only.
- run JSON -> HTML/Mermaid consistency checks.

Acceptance:

- report is human-readable without opening raw JSON;
- every visible node resolves to persisted artifact refs;
- unresolved and needs-review items are shown;
- HTML/Mermaid text is escaped and path-redacted.
- report includes executive summary, capability map, module cluster map, evidence heatmap, drift board, ranking lanes, and unresolved table.
- HTML/Mermaid contain no node ids absent from persisted report JSON.

## Phase 67: Architecture Context Pack v3

Package:

- `V2_9_PHASE_67_CONTEXT_PACK_V3_PACKAGE.md`

Development:

- build `architecture_context_pack_v3/{pack_id}.json`;
- support `project_brief`, `task_context`, and `architecture_review`;
- include V2.9 evidence, relationships, ranking, human report, tests, implementation guidance;
- enforce evidence-preserving token budget.
- support maintainer, coding agent, documentation agent, and architecture reviewer roles.
- include `source_phase_refs` proving consumption of available Phase 63-66 artifacts.

Acceptance:

- every recommendation has evidence or `needs_review`;
- small token budget omits unsupported recommendations;
- pack references V2.9 artifacts;
- HTTP/MCP/CLI parity passes.
- readback by `pack_id` succeeds and preserves stable ids, warnings, unresolved, and artifact refs.
- token trimming must not retain recommendations after removing their evidence.

## Phase 68: Closure Acceptance

Package:

- `V2_9_PHASE_68_CLOSURE_PACKAGE.md`

Development:

- update V2.9 coverage matrix;
- update real E2E matrix;
- update gap analysis;
- update document audit;
- write `V2_9_PHASE_68_CLOSURE_AUDIT_REPORT.md`.

Acceptance:

- no in-scope pending row remains;
- data_service and HarnessOS accepted artifacts are cited;
- no fatal/major audit finding remains;
- V2.9 does not claim IDE-grade navigation, full static analysis, full call graph, data flow, control flow, runtime tracing, type inference, or pure code-derived design intent recovery.
- every accepted row has test command, artifact path, data_service result, HarnessOS result, and audit report ref.
