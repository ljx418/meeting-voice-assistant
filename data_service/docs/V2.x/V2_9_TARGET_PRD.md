# V2.9 Target PRD: Architecture Evidence Hardening and Human Review UX

> Generated for V2.9 documentation development.
> Business code implementation is not part of this document update.
> V2.9 extends accepted V2.8 closure with stronger evidence extraction, ranking calibration, human-readable architecture review, and context-pack hardening.

Date: 2026-06-05

## 1. Product Positioning

V2.9 turns V2.8's architecture reading experience into a stronger architecture review and evidence hardening layer for large projects.

V2.8 is accepted for readable dashboards, graph aggregation, code fact chains, ranking, intent evidence, and Architecture Context Pack v2. Its closure audit records two non-blocking limitations:

- HarnessOS code fact chains are generated but remain `needs_review` because deterministic line-level public-surface evidence is missing.
- Ranking produces many pinned items because upstream quality/drift artifacts classify many findings as major.

V2.9 addresses those limitations and improves human review quality without claiming full static analysis, full call graph, data flow, control flow, runtime tracing, type inference, or automatic recovery of human design intent from code.

## 2. Current Baseline

V2.9 starts from accepted V2.8 Phase 56-62 artifacts:

- architecture reading dashboard;
- clustered graph views;
- code fact chains and runtime boundaries;
- signal ranking and review queue v2;
- intent evidence;
- Architecture Context Pack v2;
- real E2E on `data_service` and HarnessOS.

V2.9 must consume V2.0-V2.8 artifacts and may enrich them. It must not silently mutate V2.0-V2.8 source artifacts.

## 3. Target Users

- Maintainer / Tech Lead: needs a clearer architecture review report that separates accepted evidence from reviewable gaps.
- External Coding Agent: needs stronger implementation paths and evidence-backed task guidance.
- Documentation Agent: needs code/document drift prioritized without duplicate noise.
- Architecture Reviewer: needs public surfaces, modules, workflows, and tests grouped into understandable evidence paths.
- Auditor: needs proof that every accepted conclusion has code/document evidence or remains `needs_review`.

## 4. User Stories

### US-029-001: Public Surface Evidence v2

As an architecture reviewer, I want line-level evidence for HTTP routes, MCP tools, CLI commands, workflow entrypoints, and console/TUI entrypoints, so public capabilities can be traced to implementation files.

Acceptance:

- extracts deterministic evidence from Python decorators, argparse/typer/click-style parsers, registry lists, command tables, workflow manifests, and lightweight console entrypoints;
- every accepted evidence row includes repo-relative path and line range;
- unsupported or ambiguous entries are marked `needs_review`;
- HarnessOS accepted code fact chains improve over V2.8, or a structured blocker is reported.

### US-029-002: Code Relationship Layer v2

As a coding agent, I want shallow implementation paths from capability to public surface to handler/module/test evidence, so I can understand how a feature is implemented without requiring full call graph.

Acceptance:

- builds capability -> public surface -> handler -> local module -> test/reference paths where evidence exists;
- builds module dependency clusters;
- separates deterministic relationships from heuristic relationships;
- import dependencies are not labeled runtime calls.

### US-029-003: Ranking Calibration v2

As a maintainer, I want ranking to reduce duplicate noise while preserving major/fatal risks, so review queues are actionable.

Acceptance:

- major/fatal findings remain pinned;
- duplicate or near-duplicate findings are grouped;
- score components and reason codes remain public;
- ranking output reports calibration metrics and does not convert weak evidence into accepted evidence.

### US-029-004: Human Review Report v2

As a human reviewer, I want a polished HTML architecture review with clear diagrams and evidence lanes, so I can understand the project without opening raw JSON artifacts.

Acceptance:

- report includes capability-to-entrypoint map, module cluster map, evidence coverage heatmap, doc-code drift board, ranking priority lanes, and unresolved evidence table;
- report visibly separates target architecture, current code facts, drift, evidence, and audit queue;
- every visible chart node resolves to a persisted artifact;
- `needs_review` and unresolved items are visible, not hidden.

### US-029-005: Architecture Context Pack v3

As an external agent, I want V2.9 context packs with better implementation paths, calibrated risks, and human review notes, so I can plan safe code changes.

Acceptance:

- context pack references V2.9 evidence, relationship, ranking, human report, and unresolved artifacts;
- every recommendation has evidence or `needs_review`;
- small token budgets omit unsupported recommendations rather than dropping evidence;
- HTTP/MCP/CLI reads are aligned.

## 5. Functional Scope

V2.9 in scope:

1. Public surface evidence extraction v2.
2. Shallow code relationship layer v2.
3. Ranking calibration and review queue v3.
4. Human review report v2 with richer charts.
5. Architecture Context Pack v3.
6. HTTP/MCP/CLI read contracts for V2.9 artifacts.
7. Real-repo E2E on `data_service` and HarnessOS.
8. PRD/spec review, false-acceptance review, closure coverage matrix.

V2.9 out of scope:

1. Full call graph, data flow, control flow, runtime tracing, or type inference.
2. IDE-grade search/navigation replacement.
3. Automatic architecture refactoring or document rewriting.
4. Treating drawio/document labels as code-derived evidence.
5. Accepting heuristic relationships as deterministic runtime behavior.

## 6. Target Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_9/
  architecture_public_surface_evidence_v2.jsonl
  architecture_code_relationships_v2.jsonl
  architecture_module_clusters_v2.json
  architecture_signal_ranking_v2.json
  architecture_review_queue_v3.json
  architecture_human_review_report_v2.json
  architecture_context_pack_v3/{pack_id}.json
  views/
    architecture_human_review_report_v2.html
    architecture_evidence_heatmap.mmd
    architecture_capability_entrypoint_map.mmd
```

## 7. Public Interfaces

HTTP target:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/evidence
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/relationships
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/ranking
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/report
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_9/context-pack/{pack_id}
```

MCP target:

```text
knowledge_code_architecture_evidence_v2_build
knowledge_code_architecture_evidence_v2
knowledge_code_architecture_relationships_v2_build
knowledge_code_architecture_relationships_v2
knowledge_code_architecture_ranking_v2_build
knowledge_code_architecture_ranking_v2
knowledge_code_architecture_human_report_v2_build
knowledge_code_architecture_human_report_v2
knowledge_code_architecture_context_pack_v3
knowledge_code_architecture_context_pack_v3_read
```

CLI target:

```text
knowledge code architecture evidence-v2-build
knowledge code architecture evidence-v2
knowledge code architecture relationships-v2-build
knowledge code architecture relationships-v2
knowledge code architecture ranking-v2-build
knowledge code architecture ranking-v2
knowledge code architecture human-report-v2-build
knowledge code architecture human-report-v2
knowledge code architecture context-pack-v3
knowledge code architecture context-pack-v3-read
```

## 8. Success Criteria

V2.9 is complete when:

1. `data_service` and HarnessOS both generate non-empty V2.9 evidence, relationship, ranking, human report, and context pack artifacts.
2. HarnessOS accepted code fact or relationship evidence improves over V2.8, or closure reports a structured blocker with exact missing evidence categories.
3. Ranking v2 groups duplicate findings and still pins major/fatal risks.
4. Human Review Report v2 is readable without opening raw JSON and visibly separates target/current/drift/evidence/review queue.
5. Context Pack v3 contains only evidence-backed or explicitly reviewable recommendations.
6. HTTP/MCP/CLI public outputs are aligned.
7. No V2.0-V2.8 source artifacts are silently mutated.
8. Closure audit has no open fatal or major findings.
