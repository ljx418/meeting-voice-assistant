# V2.4 Development and Acceptance Plan

> Scope: V2.4 Code-Derived Architecture Inference.
> Baseline: accepted V2.0/V2.1 artifacts and current V2.3 architecture abstraction implementation.
> Rule: each phase requires real-repo E2E, artifact inspection, PRD/spec review, and false-acceptance review before the next phase starts.

Date: 2026-06-02

## 1. Phase Sequence

```text
Phase 18  V2.4 documentation, target architecture, schemas, and gates
Phase 19  Code role and layer inference                         implemented and accepted
Phase 20  Boundary and pattern candidate detection               implemented and accepted
Phase 21  Code-derived architecture model and design-code drift   implemented and accepted
Phase 22  HTTP/MCP/CLI and views                              implemented and accepted; quality overlay deferred
Phase 23  Real-repo E2E, HarnessOS comparison, and V2.4 closure accepted
Phase 24  Architecture quality overlay                         implemented and accepted
```

No implementation phase may start until its phase-specific pre-development audit has no open fatal or major findings.

## 2. Shared Entry Criteria

Every V2.4 phase must verify:

- V2.0 closure report exists and has no open fatal/major finding.
- V2.1 closure report exists and has no open fatal/major finding.
- V2.3 architecture abstraction artifacts can be built or read for the target repo when design sources exist.
- Required V2.0/V2.1 artifact hashes are recorded before phase work.
- The phase does not require source registry semantic changes.
- The phase does not require V2.4 core logic in `backend/data_service/service.py`.
- The phase does not require V2.4 routes in `backend/app/api/v1/data_service.py`.

## 3. Shared Acceptance Rules

Every phase must:

- Use `/Users/Zhuanz/Desktop/workspace/data_service` as a real repo input.
- Use `/Users/Zhuanz/Desktop/workspace/harnessOS` as a second real repo input when HarnessOS validation is relevant.
- Inspect generated artifacts on disk.
- Validate artifact schema, not just file existence.
- Validate cross-link integrity for evidence, graph nodes, design nodes, code roles, and drift findings.
- Compare prior artifact hashes before and after phase execution.
- Verify public payloads and views use repo-relative paths.
- Verify HTTP/MCP/CLI stable IDs/counts agree when the phase exposes all three.
- Run focused tests and V1/V2 regression smoke.
- Run `git diff --check -- .`.
- Produce PRD/spec review and false-acceptance review.

False-acceptance failures:

- Empty role/model/pattern output accepted as success.
- High-confidence architecture conclusion has no evidence.
- Low-confidence output counted as successful architecture recognition.
- LLM-only architecture prose treated as fact.
- Unsupported full call graph/data flow/control flow/type inference is claimed.
- HTML view displays facts not present in persisted artifacts.
- HarnessOS validation only repeats Drawio labels and does not infer from code.
- V2.4 mutates V2.0/V2.1/V2.3 artifacts without an explicit audited rebuild.

## 4. Phase 18: Documentation, Schemas, and Gates

### Development

- Create V2.4 target PRD, target architecture, development and acceptance plan, gap analysis, document audit report, and target-state Drawio.
- Update V2.x README, broad V2 PRD, full remaining plan, and full document audit report.
- Define role, layer, boundary, pattern, code-derived model, and drift finding schema expectations.
- Define public HTTP/MCP/CLI target surfaces.

### Acceptance

- V2.4 documents consistently define V2.4 as code-derived architecture inference.
- V2.4 scope does not reopen V2.0/V2.1/V2.3 acceptance.
- Target architecture explicitly separates design-side model and code-derived model.
- Drawio covers target architecture, pipeline, drift comparison, milestones, and gates.
- Document audit has no open fatal or major finding.

## 5. Phase 19: Code Role and Layer Inference

Status: implemented and accepted.

### Development

- Add role classifier and layer inferer under the existing architecture package.
- Consume V2.0 inventory, symbols, trace, and V2.1 graph artifacts.
- Produce `code_roles.jsonl` and `code_layers.jsonl`.
- Record signals, evidence, confidence, and `needs_review`.

### Acceptance

- `data_service` role output identifies HTTP, MCP, CLI, frontend, artifact store, graph, DevWiki, quality, overview/context, and architecture modules where present.
- Interface roles map to public surfaces from inventory.
- High-confidence roles have evidence references.
- Low-confidence or unknown roles are explicit.
- Role/layer artifact schema validation passes.
- Sampled evidence references resolve to real repo-relative files and valid line ranges.

## 6. Phase 20: Boundary and Pattern Candidate Detection

Status: implemented and accepted.

### Development

- Add boundary inferer and pattern detector.
- Infer package, adapter, storage, governance, and public-surface boundaries.
- Detect pattern candidates: FastAPI router, MCP registry, CLI command group, provider adapter, artifact store, pipeline, quality gate, Context Pack, DevWiki, Code Graph, architecture alignment.
- Produce `code_boundaries.jsonl` and `pattern_candidates.jsonl`.

### Acceptance

- `data_service` detects FastAPI router, MCP tooling, CLI command group, artifact persistence, quality governance, DevWiki, Code Graph, and Context Pack where present.
- Pattern candidates include deterministic signals and evidence.
- Boundary records include member IDs and cross-boundary edges when available.
- Unsupported pattern claims are low confidence or `needs_review`.
- Pattern output does not claim runtime flow or full call graph.

## 7. Phase 21: Code-Derived Model and Design-Code Drift

Status: implemented and accepted.

### Development

- Add code model builder to aggregate roles, layers, boundaries, and patterns.
- Add drift analyzer comparing V2.3 design-side architecture model to V2.4 code-derived model.
- Produce `code_derived_model.json` and `design_code_drift.jsonl`.

### Acceptance

- Code-derived model builds without requiring Drawio or Markdown design sources.
- HarnessOS code-derived model builds from code facts.
- When HarnessOS design sources exist, drift analyzer compares design-side planes/components to code-derived roles/layers/patterns.
- Drift finding types include design-only, code-only, role mismatch, boundary leak, pattern mismatch, and low-confidence role findings where applicable.
- Each high-confidence drift finding has design evidence, code evidence, or both, depending on finding type.
- Low-confidence drift is marked `needs_review` and does not count as a hard mismatch.

## 8. Phase 22: Public Interfaces, Views, and Governance Integration

Status: implemented and accepted for public interfaces and views. Quality overlay was completed later in Phase 24.

### Development

- Add HTTP/MCP/CLI build/read endpoints for V2.4 artifacts.
- Extend architecture renderer to generate code-derived Mermaid and HTML views.
- Add read-time Quality overlay support for architecture roles/patterns/drift if current quality service supports target typing.

### Acceptance

- HTTP/MCP/CLI return stable IDs and counts for model, roles, patterns, drift, and views.
- Missing model or missing artifact returns structured error instead of silent rebuild.
- HTML view renders key nodes, layers, patterns, and drift summaries from persisted artifacts.
- Mermaid references real code-derived architecture node IDs.
- Public views do not contain absolute paths.
- Quality overlay does not mutate V2.4 source artifacts.

## 9. Phase 23: V2.4 Closure

Status: accepted.

### Development

- Run final E2E on `data_service`.
- Run final E2E on HarnessOS.
- Compare project-generated architecture analysis with Codex static review observations.
- Produce V2.4 closure audit report.

### Acceptance

- All V2.4 artifacts are generated, read back, and schema-validated.
- Real-repo E2E passes on both repos.
- PRD coverage matrix shows all V2.4 in-scope capabilities complete or explicitly deferred.
- False-acceptance review has no open fatal or major risk.
- Regression tests pass.
- V2.4 closure report lists changed files, commands run, artifact paths, test results, limitations, and open human review questions.

## 10. Required Tests

Expected test groups:

```bash
python3 -m pytest backend/tests/test_v2_architecture_abstraction.py
python3 -m pytest backend/tests/test_v2_code_architecture_inference.py
python3 -m pytest backend/tests/test_data_service_mcp.py
python3 -m pytest backend/tests/test_public_surface_guard.py
python3 -m pytest backend/tests/test_v2_code_graph_baseline.py
python3 -m pytest backend/tests/test_v2_codebase_trace.py
```

If a listed test file does not exist at implementation time, the implementing phase must create an equivalent focused test before acceptance.
