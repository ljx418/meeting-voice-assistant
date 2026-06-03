# V2.4 Target PRD: Code-Derived Architecture Inference

> Generated from repository analysis.
> Business code was not modified by this document.
> Important claims include source evidence where possible.

Date: 2026-06-02

## 1. Product Positioning

V2.4 extends Project Intelligence from "architecture document alignment" to "code-derived architecture inference".

V2.3 can parse architecture sources such as Drawio and Markdown, build a design-side architecture model, and compare it to code facts. V2.4 must additionally infer architecture roles, layers, boundaries, pattern candidates, and design-code drift from code artifacts even when architecture documents are missing or incomplete.

V2.4 is not a full static-analysis engine. It must not claim complete call graphs, data-flow graphs, control-flow graphs, runtime dispatch resolution, or type inference.

## 2. Current Baseline

The implementation baseline before V2.4:

- V2.0 provides codebase registry, snapshot, public surface inventory, symbol index, evidence trace, project overview, and agent context pack.
- V2.1 provides DevWiki, Code Graph, Code Quality Governance, and read-only project intelligence UI.
- V2.3 provides architecture source scanning, Drawio/Markdown architecture parsing, design model building, design-code alignment, findings, and HTML/Mermaid views.

Repository evidence for the V2.3 implementation shape:

- `backend/data_service/code_assets/architecture/service.py`
- `backend/data_service/code_assets/architecture/model_builder.py`
- `backend/data_service/code_assets/architecture/aligner.py`
- `backend/data_service/code_assets/architecture/drawio_parser.py`
- `backend/data_service/code_assets/architecture/markdown_parser.py`
- `backend/data_service/mcp_code_architecture_tools.py`
- `backend/app/api/v1/code_assets_architecture.py`
- `backend/data_service/cli_code_architecture.py`

## 3. Target Users

- External Coding Agent: needs a reliable architecture context before changing code.
- Project Understanding Agent: needs to summarize architecture when diagrams are missing or stale.
- Maintainer / Tech Lead: needs drift findings between intended design and actual code organization.
- Code Review Agent: needs likely architecture boundary violations and affected layers.
- Documentation Agent: needs code-derived architecture facts for DevWiki and onboarding pages.

## 4. User Stories

### US-024-001: Build code-derived architecture model

As an external Agent, I want to build an architecture model from code artifacts, so I can understand the actual project architecture without relying on Drawio or Markdown design documents.

Acceptance:

- The build consumes accepted V2.0/V2.1 artifacts and current V2.3 architecture artifacts when available.
- The output contains roles, layers, boundaries, pattern candidates, evidence, confidence, and unresolved items.
- The output works when architecture source documents are absent.

### US-024-002: Identify architecture roles and layers

As a maintainer, I want modules/files/symbols/public surfaces grouped into architecture roles and layers, so I can see whether the implementation shape matches the intended architecture.

Acceptance:

- Interface roles include HTTP, MCP, CLI, and frontend surfaces.
- Application/service/domain/infrastructure/governance/storage/runtime/test/docs roles are represented when evidence exists.
- Unknown or low-confidence roles are explicit, not silently treated as successful inference.

### US-024-003: Detect architecture patterns

As a Coding Agent, I want pattern candidates such as FastAPI router, MCP registry, CLI command group, provider adapter, artifact store, pipeline, governance gate, DevWiki, Code Graph, and Context Pack, so I can reuse existing implementation patterns.

Acceptance:

- Every high-confidence pattern has deterministic signals and evidence.
- Pattern detection is heuristic and evidence-backed.
- Unsupported patterns are marked `needs_review` or low confidence.

### US-024-004: Compare design model and code-derived model

As a Tech Lead, I want to compare documented architecture with inferred code architecture, so I can detect stale diagrams, missing implementation, undocumented code layers, and role mismatches.

Acceptance:

- Drift findings are generated only when both sides have enough evidence.
- Findings include design-side evidence when available and code-side evidence when available.
- Low-confidence drift does not count as pass/fail without `needs_review`.

### US-024-005: View architecture inference through HTTP/MCP/CLI and HTML

As an external Agent or maintainer, I want to access the model, roles, patterns, drift, and views through the same public channels as previous V2 capabilities.

Acceptance:

- HTTP, MCP, CLI outputs use stable envelopes and artifact references.
- HTML/Mermaid views are generated from persisted artifacts, not from UI-only calculations.
- Public output uses repo-relative paths and does not leak absolute workspace paths.

## 5. Functional Scope

V2.4 in scope:

1. Code-derived architecture role classification.
2. Code-derived layer inference.
3. Code boundary inference.
4. Architecture pattern candidate detection.
5. Code-derived architecture model build/read.
6. Design model vs code-derived model drift findings.
7. Mermaid and HTML views for key architecture nodes and drift.
8. HTTP/MCP/CLI access.
9. Real-repo E2E on `data_service` and HarnessOS.
10. Document, PRD, specification, and false-acceptance audit.

V2.4 out of scope:

1. Full call graph.
2. Full data-flow/control-flow graph.
3. Runtime dispatch resolution.
4. Full language-server or compiler-grade type inference.
5. Automatic architecture refactoring.
6. Drawing full detailed diagrams equivalent to human-designed Drawio.
7. Treating LLM-only summaries as architecture facts.

## 6. Target Artifact Layout

V2.4 artifacts live under the existing codebase architecture root:

```text
workspace/assets/codebase/{codebase_id}/architecture/
  code_roles.jsonl
  code_layers.jsonl
  code_boundaries.jsonl
  pattern_candidates.jsonl
  code_derived_model.json
  design_code_drift.jsonl
  views/
    code_derived_architecture.mmd
    code_derived_architecture.html
```

Every persisted artifact must include or reference:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `source_artifact_refs`
- `created_at`
- evidence references
- confidence or `needs_review`

## 7. Public Interfaces

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/model
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/roles
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/patterns
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/drift
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/code/views/{view_id}
```

MCP:

```text
knowledge_code_architecture_build
knowledge_code_architecture_model
knowledge_code_architecture_roles
knowledge_code_architecture_patterns
knowledge_code_architecture_drift
knowledge_code_architecture_view
```

CLI:

```text
knowledge code architecture code-build
knowledge code architecture code-model
knowledge code architecture roles
knowledge code architecture patterns
knowledge code architecture drift
knowledge code architecture code-view
```

## 8. Success Criteria

V2.4 is complete when:

1. The service can build a non-empty code-derived architecture model for the current `data_service` repository.
2. The service can build a code-derived architecture model for HarnessOS without requiring Drawio input.
3. The service can compare HarnessOS code-derived architecture to V2.3 design-side architecture when design sources are available.
4. Key interface modules are identified as HTTP/MCP/CLI/frontend roles.
5. Pattern candidates include at least FastAPI router, MCP registry/tooling, CLI command group, artifact store, governance/quality, DevWiki, Code Graph, and Context Pack where present.
6. Every high-confidence role, layer, pattern, and drift finding has evidence.
7. Low-confidence or unresolved architecture claims are explicit.
8. HTTP/MCP/CLI and HTML/Mermaid views read persisted artifacts and agree on stable IDs/counts.
9. No V2.0/V2.1/V2.3 artifact is silently rewritten by V2.4.
10. V2.4 closure audit has no open fatal or major findings.

## 9. Human Review Questions

- What minimum role coverage threshold is acceptable for very large or multi-language repos?
- Should V2.4 use LLM synthesis only for prose rendering, or also for low-confidence role suggestions marked `needs_review`?
- Should HarnessOS seven-plane architecture be treated as a golden external validation target for V2.4 closure?
- Should V2.4 output be allowed to influence Agent Context Pack ranking immediately, or only after a separate V2.5 integration phase?
