# V2.8 Target PRD: Architecture Reading UX and Deep Project Intelligence

> Generated for V2.8 documentation development.
> Business code implementation is not part of this document update.
> V2.8 extends V2.7 with readable architecture reports, graph aggregation, deeper code facts, ranking, and evidence-backed design-intent views.

Date: 2026-06-04

## 1. Product Positioning

V2.8 turns the V2.7 documentation-code architecture governance layer into a human-readable and agent-readable architecture intelligence experience.

V2.7 can register architecture documents, extract claims, evaluate document quality, align document claims with code facts, reconstruct target/current/diff architecture, and feed governance. Its main gaps are report readability, graph usability, code fact depth, large-project noise, and limited design-intent evidence beyond documents.

V2.8 does not replace IDEs, Sourcegraph/OpenGrok-style code search, or human C4 modeling. It improves the project intelligence service so maintainers and agents can quickly understand a large project, inspect architecture relationships, trace evidence, and see where design claims and code facts diverge.

## 2. Current Baseline

V2.8 starts from accepted V2.7 artifacts:

- document registry, claims, relations, quality findings, alignment, drift, reconstructed model, HTML/Mermaid views;
- V2.6 scale profile, lightweight facts, taxonomy, review queue, large-project views;
- V2.4 code-derived roles, layers, boundaries, patterns, drift;
- V2.0/V2.1 codebase registry, public surface, symbols, trace, graph, quality governance.

V2.8 must consume these artifacts and may enrich them. It must not silently mutate V2.0-V2.7 source artifacts.

## 3. Target Users

- Maintainer / Tech Lead: needs a readable architecture report, not thousands of raw claims.
- External Coding Agent: needs task-aware architecture context with evidence.
- Documentation Agent: needs ranked doc-code gaps and design-intent evidence.
- Architecture Reviewer: needs clustered diagrams and filters for target/current/diff.
- Auditor: needs proof that charts, summaries, and recommendations are backed by persisted artifacts.

## 4. User Stories

### US-028-001: Readable architecture report

As a maintainer, I want a report with charts, diagrams, and summaries, so I can understand a large project without reading every raw artifact.

Acceptance:

- report first screen shows project summary, key architecture layers, public capabilities, top risks, and evidence counts;
- report includes architecture overview, capability map, doc-code drift map, quality chart, and hotspot tables;
- every visible chart node resolves to a persisted artifact;
- report text is escaped and path-redacted.

### US-028-002: Aggregated architecture graph views

As a reviewer, I want graph views grouped by layer, capability, folder/module, document authority, and confidence, so large projects are readable.

Acceptance:

- graph clusters are persisted and traceable;
- filters support confidence band, severity, unmatched claims, public surfaces, and governance state;
- weak and token-only matches never appear as accepted architecture relationships.

### US-028-003: Deeper code fact chains

As a coding agent, I want route/tool/CLI entrypoint chains and runtime boundary hints, so I can follow how public capabilities map to implementation modules.

Acceptance:

- extracts route -> handler -> service module, MCP tool -> dispatcher -> handler, CLI command -> handler/service;
- extracts import dependency clusters and config/runtime/deployment boundary hints;
- accepted code facts include source file and line evidence;
- runtime or interaction hints are confidence-scored and marked `needs_review` unless deterministic.

### US-028-004: Large-project signal ranking

As a maintainer, I want ranked architecture signals and review queues, so I can inspect the highest-value gaps first.

Acceptance:

- ranking uses document authority, public surface importance, evidence density, drift severity, code centrality, recency, and confidence;
- major/fatal findings cannot be hidden by a favorable score;
- ranking reasons are exposed, not opaque.

### US-028-005: Design-intent evidence view

As an auditor, I want to distinguish documented intent, code-observed implementation, audit-accepted state, and unresolved mismatch.

Acceptance:

- no output claims pure code recovery of human intent;
- each intent conclusion has document evidence, code evidence, audit evidence, or `needs_review`;
- document conflicts are detected across PRD, target architecture, gap analysis, audit report, and drawio.

### US-028-006: Architecture Context Pack v2

As an external agent, I want a task-aware architecture context pack with diagrams, ranked facts, risks, and evidence.

Acceptance:

- context pack references V2.8 dashboard, graph, ranking, code fact chains, intent evidence, and review queue;
- every recommendation has evidence or `needs_review`;
- small token budgets do not preserve unsupported recommendations after dropping evidence.

## 5. Functional Scope

V2.8 in scope:

1. Multi-chart architecture reading dashboard.
2. Graph aggregation, layout, and filtering.
3. Deeper deterministic code fact chains and guarded runtime hints.
4. Large-project signal ranking and review queue v2.
5. Design-intent evidence and document conflict view.
6. Architecture Context Pack v2.
7. HTTP/MCP/CLI read contracts for V2.8 artifacts.
8. Real-repo E2E on `data_service` and HarnessOS.
9. PRD/spec review, false-acceptance review, closure coverage matrix.

V2.8 out of scope:

1. Full call graph, data flow, control flow, runtime tracing, or type inference.
2. IDE-grade code navigation.
3. Automatic architecture refactoring or document rewriting.
4. Treating copied drawio content as code-derived architecture evidence.
5. Hiding low-confidence matches inside polished diagrams.

## 6. Target Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_8/
  architecture_reading_dashboard.json
  architecture_graph_summary.json
  architecture_graph_clusters.json
  architecture_graph_views/{view_id}.json
  architecture_code_fact_chains.jsonl
  architecture_runtime_boundaries.jsonl
  architecture_signal_ranking.json
  architecture_review_queue_v2.json
  architecture_intent_evidence.jsonl
  architecture_context_pack_v2/{pack_id}.json
  views/
    architecture_reading_report.html
    architecture_overview.svg
    architecture_capability_map.mmd
    architecture_drift_map.mmd
```

## 7. Public Interfaces

HTTP target:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/{view_id}
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/graph/summary
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/ranking
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/context-pack
```

MCP target:

```text
knowledge_code_architecture_views_build
knowledge_code_architecture_views
knowledge_code_architecture_graph_summary
knowledge_code_architecture_ranking
knowledge_code_architecture_context_pack_v2
```

CLI target:

```text
knowledge code architecture views build
knowledge code architecture views list
knowledge code architecture graph summary
knowledge code architecture ranking
knowledge code architecture context-pack
```

## 8. Success Criteria

V2.8 is complete when:

1. `data_service` and HarnessOS both generate non-empty V2.8 dashboard, graph, ranking, code fact chain, intent evidence, context pack, and HTML view artifacts.
2. HTML report is readable by a human reviewer and includes multiple charts plus target/current/diff navigation.
3. Large HarnessOS graphs are clustered or filtered rather than flattened into unreadable node lists.
4. Accepted code fact chains have source evidence and line ranges.
5. Runtime hints and design-intent conclusions are confidence-scored and reviewable.
6. Ranking exposes reasons and does not hide major/fatal findings.
7. Context Pack v2 contains only evidence-backed or explicitly reviewable recommendations.
8. HTTP/MCP/CLI public outputs are aligned.
9. No V2.0-V2.7 source artifacts are silently mutated.
10. Closure audit has no open fatal or major findings.
