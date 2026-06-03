# V2 Phase 12 Acceptance Plan: V2.1 Closure

> Phase: 12 / V2.1 Closure Acceptance.
> Track: V2.1 Project Intelligence Expansion.
> Status: planned acceptance gate.

## 1. Required E2E Flow

Use the real repository:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Required flow:

1. Verify V2.0 closure inputs.
2. Import or read the current codebase asset.
3. Generate or read snapshot, inventory, symbols, trace, overview, and context pack artifacts.
4. Build or read DevWiki pages.
5. Build or read Code Graph artifacts and Mermaid export.
6. Record quality feedback, build rules, review rules, and generate quality plan.
7. Build frontend.
8. Inspect persisted artifacts.
9. Compare HTTP/MCP/CLI stable fields for V2.1 public surfaces.
10. Produce final closure audit report.

## 2. Required Assertions

V2.1 closure passes only if:

- V2.0 closure report exists and has no open fatal or major finding.
- Phase 8, Phase 9, and Phase 10 audit reports are accepted.
- Phase 11 implementation acceptance has no open fatal or major finding.
- DevWiki required pages exist as JSON and Markdown.
- Code Graph artifacts include graph JSON, nodes JSONL, edges JSONL, summary JSON, and Mermaid export.
- Quality artifacts include feedback, rules, reviews, plan, and summary.
- Required HTTP/MCP/CLI V2.1 interfaces exist and converge on stable identifiers and counts.
- DevWiki evidence references resolve to real evidence artifacts.
- Graph EvidenceSpan nodes resolve to real evidence artifacts.
- Quality targets resolve to real DevWiki, Graph, Surface, Symbol, or Context objects.
- Unsupported graph relations are absent.
- Public outputs do not leak absolute repo/workspace paths.
- Source registry is not created or modified by V2 codebase artifact flows.
- Frontend build passes.

## 3. Required Commands

Focused closure commands:

```bash
python3 -m pytest backend/tests/test_v2_devwiki_baseline.py -q
python3 -m pytest backend/tests/test_v2_code_graph_baseline.py -q
python3 -m pytest backend/tests/test_v2_code_quality_governance.py -q
python3 -m pytest backend/tests/test_v2_project_overview.py backend/tests/test_v2_agent_context_pack.py -q
python3 -m pytest backend/tests/test_public_surface_guard.py backend/tests/test_data_service_mcp.py -q
npm run build --prefix frontend
git diff --check -- .
```

Final closure command:

```bash
python3 -m pytest backend/tests -q
```

If the final closure command cannot run because of environment limits, the closure audit must document:

- command attempted
- interpreter and dependency context
- exact failure
- whether focused V2.1 tests still pass
- residual risk

## 4. False Acceptance Rejection

Reject V2.1 closure if:

- Any required phase is only planned or pre-gated, not accepted.
- Real repo E2E is skipped.
- Artifact inspection is skipped.
- DevWiki has high-confidence important claims without evidence or `needs_review`.
- Graph includes unsupported semantic relations.
- Quality governance mutates source artifacts instead of producing read-time overlays.
- HTTP passes but MCP/CLI are untested for V2.1 surfaces.
- Frontend build is skipped after frontend changes.
- Risk states are hidden in frontend or generated reports.
- Closure report has open fatal or major findings.

## 5. Acceptance Decision

Final states:

- `PASS`: all required assertions pass and no fatal/major findings remain.
- `BLOCKED`: any fatal/major finding remains.
- `CONDITIONAL`: only allowed for non-product environmental issues with focused V2.1 tests passing and residual risk explicitly documented.
