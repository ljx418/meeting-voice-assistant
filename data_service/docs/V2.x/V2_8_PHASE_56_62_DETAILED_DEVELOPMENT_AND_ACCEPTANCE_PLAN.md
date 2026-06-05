# V2.8 Phase 56-62 Detailed Development and Acceptance Plan

> Decision-complete phase plan for V2.8 implementation after document audit approval.

## Phase 56: Visual Architecture Reading UX

Development:

- build `architecture_reading_dashboard.json`;
- render `views/architecture_reading_report.html`;
- render `views/architecture_overview.svg`;
- add chart sections for summary, capability map, quality severity, drift distribution, hotspots, evidence coverage;
- keep V2.7 target/current/diff sections but improve navigation and scannability.

Acceptance:

- HTML includes at least six chart or diagram sections;
- every chart node has artifact refs;
- first screen explains project summary, core architecture, top risks, and evidence counts;
- labels are escaped and local paths redacted;
- data_service and HarnessOS reports are generated and opened/inspected.

## Phase 57: Architecture Graph Aggregation / Layout / Filtering

Development:

- build `architecture_graph_summary.json`;
- build `architecture_graph_clusters.json`;
- build `architecture_graph_views/{view_id}.json`;
- support layer, capability, folder/module, document authority, confidence, and severity views;
- add filter metadata and expansion provenance.

Acceptance:

- HarnessOS graph is clustered, not just flat capped nodes;
- cluster nodes expose member counts and source refs;
- filters produce deterministic node/edge subsets;
- weak/token-only matches are not accepted edges;
- Mermaid/SVG view nodes resolve to persisted graph view nodes.

## Phase 58: Deeper Code Fact Extraction

Development:

- build `architecture_code_fact_chains.jsonl`;
- build `architecture_runtime_boundaries.jsonl`;
- extract HTTP route -> handler -> service chain;
- extract MCP tool -> dispatcher -> handler chain;
- extract CLI command -> handler/service chain;
- extract import dependency clusters and config/runtime/deployment hints.

Acceptance:

- accepted chains contain source file and line range evidence;
- runtime hints are `needs_review` unless deterministic;
- import edges are not labeled runtime calls;
- samples cover HTTP, MCP, CLI, config, tests, and service modules.

## Phase 59: Large Project Signal Ranking

Development:

- build `architecture_signal_ranking.json`;
- build `architecture_review_queue_v2.json`;
- rank by document authority, public surface importance, evidence density, drift severity, centrality, recency, and confidence;
- expose reason codes for each score.

Acceptance:

- top-N outputs are deterministic;
- major/fatal findings always appear in high-priority review queue;
- ranking reason codes are visible;
- score does not convert weak evidence into accepted evidence.

## Phase 60: Design Intent Evidence and Doc Quality v2

Development:

- build `architecture_intent_evidence.jsonl`;
- extend doc quality checks for target/current mixing, missing acceptance gates, superseded docs, drawio-without-text, PRD/architecture/gap/audit conflicts;
- model states: documented intent, code-observed implementation, audit-accepted state, mismatch, needs_review.

Acceptance:

- no output claims pure code recovery of human design intent;
- each intent row has evidence or `needs_review`;
- document conflicts are persisted and shown in report;
- drawio-only intent remains reviewable unless supported by text/code evidence.

## Phase 61: Architecture Context Pack v2

Development:

- build `architecture_context_pack_v2/{pack_id}.json`;
- support project brief and task context modes;
- include diagrams, ranked facts, relevant chains, drift, risks, tests, and evidence;
- enforce token budget.

Acceptance:

- every recommendation has evidence or `needs_review`;
- small token budgets do not leave unsupported recommendations;
- pack cites dashboard, graph, ranking, chain, and intent artifacts;
- HTTP/MCP/CLI read parity passes.

## Phase 62: V2.8 Closure Acceptance

Development:

- update coverage matrix, E2E matrix, gap analysis, document audit;
- run all focused, contract, and real E2E tests;
- inspect artifacts and public payloads.

Acceptance:

- no in-scope pending row remains;
- data_service and HarnessOS accepted artifacts are cited;
- no fatal/major audit finding remains;
- V2.8 does not claim IDE-grade navigation, full static analysis, or pure code-derived design intent recovery.
