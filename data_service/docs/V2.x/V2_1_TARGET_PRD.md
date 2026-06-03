# V2.1 Target PRD: Project Intelligence Expansion

> Product target: Local Knowledge Governance Service V2.1.
> Baseline: V2.0 Agent-callable MVP is accepted on the current worktree by `docs/V2.x/V2_0_CLOSURE_AUDIT_REPORT.md`.
> V2.1 expands V2.0 artifacts into DevWiki, Code Graph, Code Knowledge Quality Governance, and a minimum read-only frontend.
> Current closure status: Phase 8-12 are accepted for the current worktree.

## 0. Phase 8 Entry Gate

V2.1 development may start only after the V2.0 closure baseline is verified in the current repository.

Required gate checks:

- `docs/V2.x/V2_0_CLOSURE_AUDIT_REPORT.md` exists and has no open fatal or major finding.
- Current real repo can regenerate or read accepted V2.0 artifacts.
- Required V2.0 artifacts exist for the active codebase: snapshot, file manifest, inventory, capabilities, symbols, imports, evidence, overview, and at least one context pack.
- V2.1 services must fail with structured errors when required V2.0 artifacts are missing.
- V2.1 services must not silently rebuild or reinterpret V2.0 fact artifacts during DevWiki, Code Graph, Quality, or frontend phases.

## 1. Product Goal

V2.1 turns the V2.0 project intelligence artifacts into a readable, navigable, and governable project knowledge layer.

V2.0 proved that an Agent can import a repo, build deterministic facts, trace evidence, and request an Agent Context Pack. V2.1 adds durable project pages, a baseline code graph, governance workflows for code intelligence artifacts, and a minimal frontend surface for human review.

## 2. Users

- External Coding Agent: reads DevWiki pages, queries graph neighbors, and requests trace-backed development context.
- Documentation Agent: generates or refreshes project pages from deterministic artifacts.
- Developer/Maintainer: reviews public surfaces, architecture, graph relationships, stale pages, and governance findings.
- Tech Lead: governs quality of project summaries, DevWiki claims, public surface mappings, and Agent context packs.

## 3. V2.1 In Scope

V2.1 must include:

1. DevWiki Baseline.
2. Code Graph Baseline.
3. Code Knowledge Quality Governance Extension.
4. Minimum read-only Project Intelligence frontend.
5. HTTP/MCP/CLI access for DevWiki, Code Graph, and Quality Extension.
6. Real repository end-to-end acceptance using `/Users/Zhuanz/Desktop/workspace/data_service`.
7. Full backend regression, frontend build, artifact inspection, and PRD/spec/false-acceptance review.

Current implementation status:

- DevWiki Baseline: implemented and accepted.
- Code Graph Baseline: implemented and accepted.
- Code Knowledge Quality Governance Extension: implemented and accepted.
- Minimum read-only Project Intelligence frontend: accepted.
- V2.1 final closure: accepted for the current worktree.

## 4. V2.1 Out of Scope

The following must not be claimed in V2.1:

- Full call graph.
- Data flow analysis.
- Control flow analysis.
- Runtime tracing.
- Type inference.
- IDE plugin behavior.
- Interactive graph editing.
- Automatic code modification or PR submission.
- Multi-tenant SaaS behavior.
- Full artifact migration framework.

## 5. User Stories

### US-101: Build DevWiki

As a documentation Agent, I can build project DevWiki pages from V2.0 artifacts so humans and Agents can read stable, evidence-backed project documentation.

Acceptance:

- Required pages are generated.
- Each page has `snapshot_id`, sections, evidence, `needs_review`, stale status, confidence, JSON artifact, and Markdown artifact.
- Important claims are backed by evidence or marked `needs_review`.
- Pages are generated from V2.0 artifacts, not LLM-only prose.
- Each section declares `generated_from`, `source_artifact_refs`, evidence, and `needs_review`.
- JSON and Markdown are rendered from the same page model and must not diverge in important claims.

### US-102: Read DevWiki

As an Agent or developer, I can list and read DevWiki pages through HTTP/MCP/CLI.

Acceptance:

- Page index can be read.
- Page can be read by slug.
- HTTP/MCP/CLI return stable `page_id`, `slug`, `snapshot_id`, `stale`, and evidence counts.
- Public output uses repo-relative paths.

### US-103: Build Code Graph

As a developer, I can build a baseline code graph that connects files, modules, symbols, public surfaces, capabilities, DevWiki pages, and evidence spans.

Acceptance:

- Graph contains deterministic node and edge types only.
- Every edge has extractor and confidence.
- Graph is persisted as JSON and can export Mermaid.
- Graph does not claim full call graph, data flow, control flow, runtime dispatch, or type inference.

### US-104: Query Graph Neighbors

As an Agent, I can query neighbors of a file, symbol, surface, capability, or DevWiki page.

Acceptance:

- Neighbor query returns nodes, edges, evidence, and unresolved items.
- Queries are available through HTTP/MCP/CLI.
- Unknown IDs return structured errors.

### US-105: Govern Code Intelligence Quality

As a maintainer, I can provide feedback and generate correction rules for V2.1 artifacts.

Acceptance:

- Feedback target types include DevWiki page/section, public surface, capability, code symbol, code graph edge, and Agent Context Pack item.
- Rule types include missing evidence, stale snapshot, wrong surface mapping, wrong capability mapping, doc-code mismatch, low-confidence inference, and overbroad context.
- Approved rules can be consumed by DevWiki, graph, and context-pack readers as read-time overlays only.
- Quality Governance must not mutate V2.0 fact artifacts or V2.1 DevWiki/Graph/Context source artifacts when applying approved rules.

### US-106: Review V2.1 in Frontend

As a developer, I can use the Knowledge Console to inspect the V2.1 project intelligence artifacts.

Acceptance:

- Frontend offers read-only views for DevWiki, Code Graph summary, Quality summary, and Context Pack summary.
- Frontend does not become the only access path; HTTP/MCP/CLI remain primary for Agents.
- Frontend build passes.

### US-107: Close V2.1

As a maintainer, I can verify that V2.1 matches the PRD and has no open fatal or major findings.

Acceptance:

- Phase 11 implementation acceptance has no open fatal or major findings.
- Phase 12 real-repository E2E is run or explicitly documented with residual risk.
- DevWiki, Graph, Quality, frontend, HTTP/MCP/CLI, artifact inspection, public path hygiene, and false-acceptance checks are covered by closure evidence.
- V2.1 closure report is marked `PASS` only when no fatal or major findings remain.

## 6. Required DevWiki Pages

V2.1 DevWiki must generate at least:

- `project-overview`
- `architecture`
- `public-surface`
- `http-api`
- `mcp-tools`
- `cli`
- `storage`
- `build-pipeline`
- `developer-onboarding`

Page fields:

```json
{
  "schema_version": "v2.1",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "page_id": "devwiki:project-overview",
  "slug": "project-overview",
  "title": "Project Overview",
  "sections": [],
  "evidence": [],
  "needs_review": [],
  "source_artifact_refs": [],
  "stale": false,
  "confidence": 0.9,
  "created_at": "string",
  "updated_at": "string"
}
```

Each section must include:

```json
{
  "section_id": "string",
  "title": "string",
  "body": "string",
  "generated_from": "overview | inventory | symbols | trace | graph | manual_rule | llm_synthesis",
  "source_artifact_refs": [],
  "evidence": [],
  "needs_review": [],
  "confidence": 0.9
}
```

If `generated_from` is `llm_synthesis`, the section must either include supporting evidence or be marked `needs_review`; it must not be presented as a high-confidence fact without evidence.

## 7. Required Code Graph Baseline

Node types:

- `Codebase`
- `Snapshot`
- `Folder`
- `File`
- `Module`
- `Class`
- `Function`
- `Method`
- `Import`
- `HTTPRoute`
- `MCPTool`
- `CLICommand`
- `FrontendPage`
- `Capability`
- `DevWikiPage`
- `EvidenceSpan`
- `AgentContextPack`

Edge types:

- `CONTAINS`
- `DEFINES`
- `IMPORTS`
- `EXPOSES_ROUTE`
- `REGISTERS_MCP_TOOL`
- `EXPOSES_CLI_COMMAND`
- `HANDLED_BY`
- `IMPLEMENTS_CAPABILITY`
- `DOCUMENTED_BY`
- `EVIDENCED_BY`
- `GENERATED_FROM`
- `SUMMARIZED_IN`
- `GOVERNED_BY`

Unsupported edge types must not appear in V2.1:

- `CALLS`
- `DATA_FLOW`
- `CONTROL_FLOW`
- `RUNTIME_TRACE`
- `TYPE_INFERRED`

Graph acceptance must include:

- `unsupported_edge_count == 0`
- `edge_coverage_by_type` for deterministic edge types.
- Mermaid exports reference node IDs that exist in graph artifacts.
- Mermaid exports must not contain absolute paths.

## 8. Required Quality Governance Extension

Target types:

- `codebase`
- `repo_snapshot`
- `code_file`
- `code_symbol`
- `code_route`
- `code_mcp_tool`
- `code_cli_command`
- `public_surface`
- `capability`
- `devwiki_page`
- `devwiki_section`
- `agent_context_pack`
- `agent_context_item`
- `code_graph_node`
- `code_graph_edge`

Rule types:

- `wrong_summary`
- `missing_evidence`
- `stale_snapshot`
- `wrong_capability_mapping`
- `wrong_surface_mapping`
- `missing_public_surface`
- `doc_code_mismatch`
- `low_confidence_inference`
- `overbroad_agent_context`
- `unsafe_path_exposure`

Quality read-time overlay rules:

- Original V2.0 artifacts are immutable during V2.1 quality read operations.
- Original DevWiki, Graph, and Context Pack artifacts are immutable during rule application.
- Read outputs may include `governed_by`, `applied_rules`, and `plan_refs`.
- Rejected or revoked rules must not affect read outputs.
- Plans may list impacted targets but must not directly modify target artifacts.

Required structured errors:

- `V20_CLOSURE_NOT_VERIFIED`
- `V20_ARTIFACT_MISSING`
- `SNAPSHOT_NOT_FOUND`
- `DEVWIKI_PAGE_NOT_FOUND`
- `GRAPH_NODE_NOT_FOUND`
- `QUALITY_RULE_NOT_FOUND`
- `UNSUPPORTED_TARGET_TYPE`

## 9. Required Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages/{page_slug}
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/neighbors
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/graph/mermaid
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/feedback
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/summary
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/build
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/rules/{rule_id}/review
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/quality/plan
```

MCP:

```text
knowledge_devwiki_build
knowledge_devwiki_read
knowledge_code_graph_build
knowledge_code_graph_snapshot
knowledge_code_graph_neighbors
knowledge_code_graph_mermaid
knowledge_code_quality_feedback
knowledge_code_quality_summary
knowledge_code_quality_rules_build
knowledge_code_quality_rule_review
knowledge_code_quality_plan
```

CLI:

```text
knowledge code devwiki build
knowledge code devwiki pages
knowledge code devwiki read
knowledge code graph build
knowledge code graph snapshot
knowledge code graph neighbors
knowledge code graph mermaid
knowledge code quality feedback
knowledge code quality summary
knowledge code quality rules build
knowledge code quality rule review
knowledge code quality plan
```

## 10. Completion Definition

V2.1 is complete when:

1. Current repository can build DevWiki, Code Graph, and Code Quality artifacts from accepted V2.0 artifacts.
2. DevWiki pages are readable through HTTP/MCP/CLI and have evidence or `needs_review`.
3. Code Graph exposes JSON, neighbors, and Mermaid without unsupported semantic claims.
4. Code Quality Governance can record feedback, build rules, review rules, and generate a consumption plan for V2.1 target types.
5. Frontend read-only views expose V2.1 artifacts without becoming the primary Agent contract.
6. Cross-link integrity passes for DevWiki evidence, Graph EvidenceSpan nodes, Graph DevWikiPage nodes, and Quality targets.
7. Artifact schema validation passes for DevWiki, Graph, Quality, and frontend API payloads.
8. V2.0 artifact hash gate proves V2.1 phases did not mutate V2.0 fact artifacts unless an explicit rebuild was planned and audited.
9. Full backend regression passes.
10. Frontend build passes.
11. Artifact inspection uses real repository data.
12. PRD/spec/false-acceptance audit has no open fatal or major findings.
