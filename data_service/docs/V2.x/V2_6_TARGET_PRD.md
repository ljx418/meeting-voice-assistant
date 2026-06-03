# V2.6 Target PRD: Large-Scale Architecture Abstraction Hardening

> Generated from V2.4/V2.5 closure review and large-project architecture abstraction goals.
> Business code was not modified by this document.
> V2.6 is a Project Intelligence engineering-hardening phase, not a ResearchNotebook backend phase.

Date: 2026-06-03

## 1. Product Positioning

V2.6 turns the existing Project Intelligence architecture inference capability into a more reliable large-project architecture audit service.

V2.4 introduced code-derived architecture inference: roles, layers, boundaries, pattern candidates, design-code drift, and HTML/Mermaid views. V2.6 does not replace that. It hardens the capability for larger repositories by adding scale profiling, lightweight multi-language/config facts, taxonomy governance, review queues, and safer Agent-facing summaries.

V2.6 is not a full static-analysis platform. It must not claim:

- full call graph;
- full data flow;
- full control flow;
- runtime dispatch resolution;
- compiler-grade type inference;
- complete recovery of human architecture design intent.

## 2. Current Baseline

V2.6 starts from these accepted baselines:

- V2.0: codebase registry, snapshot, inventory, symbol index, evidence trace, project overview, Agent Context Pack.
- V2.1: DevWiki, Code Graph, Quality Governance, read-only project intelligence views.
- V2.4: code-derived architecture inference and design-code drift.
- V2.5: ResearchNotebook backend PRD closure with explicit classifications; V2.5 is not reopened by V2.6.

Important V2.4 limitations that V2.6 addresses:

- large-project outputs can become too large for direct consumption;
- multi-language projects only have strong Python symbol facts;
- config/deployment/schema facts are not first-class architecture inputs;
- taxonomy and confidence handling are not mature enough for broad architecture audit;
- review queues for ambiguous architecture inference need stronger public contracts;
- HTML/Mermaid views need a large-project mode focused on key nodes and evidence.

## 3. Target Users

- External Coding Agent: needs bounded architecture context for large repos.
- Maintainer / Tech Lead: needs high-level architecture roles, boundaries, and risk areas.
- Code Review Agent: needs architecture-impact signals without full static analysis.
- Documentation Agent: needs reliable architecture facts for onboarding and DevWiki updates.
- Audit Agent: needs confidence, evidence, and false-green rejection rules.

## 4. User Stories

### US-026-001: Build large-project architecture scale profile

As an external Agent, I want a scale profile for a codebase, so I can know whether architecture artifacts are safe to consume directly or require summary/page mode.

Acceptance:

- profile includes file count, LOC, languages, artifact sizes, build durations, warning counts, confidence distribution, skipped paths, and needs_review counts;
- output is persisted as `architecture_scale_profile.json`;
- public payload uses repo-relative paths and no secrets;
- large artifacts are summarized by default.

### US-026-002: Extract lightweight multi-language/config facts

As a maintainer, I want basic facts from TS/JS/Vue/config/deployment files, so Python-only symbol coverage does not hide key architecture entrypoints.

Acceptance:

- TS/JS/Vue facts cover files, imports, exports, route/API-client hints, and frontend entrypoints where deterministic;
- config/deployment facts cover package manifests, pyproject, Dockerfile, compose, k8s, CI workflow, env examples, and schema-like files;
- non-Python facts are lightweight and evidence-backed;
- unsupported semantic claims are marked `needs_review`.

### US-026-003: Govern architecture taxonomy and confidence

As a Tech Lead, I want a default architecture taxonomy and a review queue, so architecture inference can be audited before being treated as accepted.

Acceptance:

- default taxonomy covers interface, application, domain, infrastructure, governance, runtime, artifact, test, and docs;
- low-confidence role/layer/boundary/pattern findings enter `architecture_review_queue.jsonl`;
- accepted summaries must exclude unresolved low-confidence facts unless explicitly marked;
- taxonomy override is allowed through persisted artifact, not ad hoc UI-only rules.

### US-026-004: Generate large-project architecture review views

As a reviewer, I want compact HTML/Mermaid views, so I can inspect key architecture nodes and risks without reading huge raw artifacts.

Acceptance:

- views are generated from persisted artifacts only;
- views show scale profile, key roles, key boundaries, key patterns, risk counts, and review queue samples;
- Mermaid node IDs must exist in persisted artifacts;
- no view may create new architecture claims not present in artifacts.

### US-026-005: Feed safe architecture summaries into Agent Context Pack

As a Coding Agent, I want large-project architecture summaries in context packs, so I can start work with architecture constraints and risks.

Acceptance:

- context pack includes summarized scale profile, key roles, boundaries, patterns, and review risks;
- token budget trimming cannot retain architecture advice while dropping its evidence;
- unsupported or low-confidence claims are marked `needs_review`.

## 5. Functional Scope

V2.6 in scope:

1. Architecture scale profile.
2. Lightweight TS/JS/Vue facts.
3. Config/deployment/schema inventory.
4. Architecture taxonomy artifact.
5. Architecture review queue.
6. Large-project HTML/Mermaid views.
7. Agent Context Pack architecture summary integration.
8. HTTP/MCP/CLI reads for V2.6 artifacts.
9. Real-repo E2E on `data_service` and HarnessOS.
10. Document, PRD, specification, false-acceptance, and closure audit.

V2.6 out of scope:

1. Full static analysis.
2. Full cross-language call graph.
3. Full dependency injection resolution.
4. Full runtime topology.
5. IDE plugin behavior.
6. Automatic architecture refactoring.
7. Cloud provider or ResearchNotebook V2.5 reopening.

## 6. Target Artifact Layout

V2.6 artifacts live under the existing codebase architecture root:

```text
workspace/assets/codebase/{codebase_id}/architecture/
  architecture_scale_profile.json
  config_inventory.jsonl
  deployment_inventory.jsonl
  schema_inventory.jsonl
  architecture_taxonomy.json
  architecture_review_queue.jsonl
  views/
    architecture_large_project_overview.html
    architecture_key_boundaries.mmd
```

Every artifact must include or reference:

- `schema_version`;
- `workspace_id`;
- `codebase_id`;
- `snapshot_id`;
- `source_artifact_refs`;
- `created_at`;
- evidence references;
- confidence or `needs_review`;
- redaction state where relevant.

## 7. Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/profile
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/config
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/deployment
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/review-queue
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/{view_id}
```

MCP:

```text
knowledge_code_architecture_scale_build
knowledge_code_architecture_scale_profile
knowledge_code_architecture_config_inventory
knowledge_code_architecture_deployment_inventory
knowledge_code_architecture_review_queue
```

CLI:

```text
knowledge code architecture scale-build
knowledge code architecture scale-profile
knowledge code architecture config
knowledge code architecture deployment
knowledge code architecture review-queue
```

## 8. Success Criteria

V2.6 is complete when:

1. `data_service` produces a non-empty architecture scale profile, config inventory, deployment inventory, taxonomy, review queue, and large-project view.
2. HarnessOS produces the same artifact classes using real repository data.
3. Public outputs remain summary-first for large artifacts.
4. Low-confidence architecture claims are not counted as accepted facts.
5. Key non-Python/config facts are evidence-backed and explicitly lightweight.
6. Agent Context Pack can consume architecture summaries without evidence loss.
7. HTML/Mermaid views render only persisted facts.
8. No V2.0-V2.5 artifacts are silently rewritten.
9. Focused tests and real-repo E2E pass.
10. Closure audit has no open fatal or major findings.
