# V2.15 PRD: Interactive Review Workbench

## 1. Product Goal

V2.15 creates a human-readable review workbench for Coding Agent evidence. It turns V2.11-V2.14 artifacts into inspectable views for evidence, risks, blockers, patch plans, runtime results, incremental drift, and context export.

The workbench is a consumer of persisted backend artifacts. It is not a source of truth and must not create facts that are absent from backend payloads.

## 2. Users and User Experience

Primary users:

- Maintainer reviewing project actionability.
- Coding Agent preparing implementation context.
- Code Reviewer auditing patch plan readiness.
- Test Agent checking validation evidence.
- Architecture Reviewer inspecting drift and blockers.

End-of-phase target experience:

1. User builds a workbench for `data_service` or a large project.
2. User opens an HTML report.
3. User can inspect capability graph, evidence links, risk lanes, blockers, patch plans, runtime evidence, incremental drift, and exported context.
4. User can see what is accepted, what needs review, and what is blocked.
5. User can export an evidence-preserving context package for another Agent.

## 3. In Scope

- Backend workbench payload.
- HTML review workbench.
- Mermaid capability graph.
- Evidence click-through IDs.
- Risk lanes.
- Blocker board.
- Runtime and incremental summary sections.
- Context export payload.
- Real `data_service` and large-project E2E.

## 4. Out of Scope

- Frontend as a fact source.
- Free-form graph editing.
- Automatic code or document rewriting.
- Hiding low-confidence or blocked findings for visual polish.
- Claiming unresolved facts as accepted.

## 5. Functional Requirements

### FR-001 Workbench Payload

The payload includes:

- project summary;
- capability map;
- surface/symbol/file/test graph refs;
- patch plan refs;
- runtime evidence refs;
- incremental drift refs;
- risk lanes;
- blocker board;
- context export options.

### FR-002 HTML Report

The HTML report renders from persisted payload only. It must escape document labels, code snippets, paths, and graph labels.

### FR-003 Mermaid Graph

The graph must use stable artifact IDs for nodes. Every visible node must resolve to persisted backend payload.

### FR-004 Context Export

Context export must preserve evidence. If token budget is small, it may omit lower-priority items but cannot keep recommendations while removing their evidence.

## 6. Completion Definition

V2.15 is complete when:

- workbench payload, HTML, Mermaid, and context export artifacts are persisted;
- every visible fact resolves to an artifact ID;
- blockers and `needs_review` are visible;
- public output has no absolute paths, secrets, raw tracebacks, or unescaped unsafe labels;
- data_service and one large project produce readable reports or structured blockers;
- HTTP/MCP/CLI parity passes;
- no open fatal or major finding remains.
