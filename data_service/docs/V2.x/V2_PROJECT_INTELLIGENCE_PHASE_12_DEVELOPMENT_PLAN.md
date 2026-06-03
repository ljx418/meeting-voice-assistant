# V2 Phase 12 Development Plan: V2.1 Closure Acceptance

> Phase: 12 / V2.1 Closure Acceptance.
> Track: V2.1 Project Intelligence Expansion.
> Status: planned closure phase.

## 1. Phase Goal

Phase 12 closes V2.1. It does not add product capabilities. It proves that the implemented V2.1 system matches the V2.1 PRD, architecture, public interfaces, artifact contracts, and false-acceptance gates.

## 2. Inputs

Required inputs:

- Accepted V2.0 closure report.
- Accepted Phase 8 DevWiki audit.
- Accepted Phase 9 Code Graph audit.
- Accepted Phase 10 Code Quality Governance audit.
- Phase 11 implementation acceptance report with no open fatal or major findings.
- Current real repository at `/Users/Zhuanz/Desktop/workspace/data_service`.

## 3. Closure Work

Phase 12 must:

- Re-run or verify V2.0 closure gate on the current repository.
- Build or read V2.1 DevWiki, Code Graph, Quality, and frontend review artifacts.
- Inspect persisted artifacts on disk.
- Compare HTTP/MCP/CLI public surfaces and stable response fields.
- Validate artifact schemas for DevWiki, Graph, Quality, and Context references.
- Validate cross-link integrity across evidence, pages, graph nodes/edges, quality targets, and context pack items.
- Verify V2.0 fact artifact hashes are not changed by V2.1 read/build operations unless an explicit rebuild is planned and audited.
- Verify public responses do not leak absolute repo/workspace paths.
- Verify source registry isolation.
- Produce final PRD coverage and architecture deviation tables.

## 4. Output Documents

Phase 12 produces:

- `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_12_AUDIT_REPORT.md`
- `docs/V2.x/V2_1_CLOSURE_AUDIT_REPORT.md`
- Updated `docs/V2.x/V2_1_DOCUMENT_AUDIT_REPORT.md`
- Updated `docs/V2.x/V2_1_SELF_AUDIT_RESULT.html`

## 5. Implementation Boundaries

Phase 12 must not:

- Add new DevWiki page types.
- Add graph semantic relationships beyond the V2.1 PRD.
- Add quality rule types beyond the V2.1 PRD.
- Convert frontend into an editing UI.
- Modify V2.0 fact artifacts as part of read-time validation.
- Treat generated prose without evidence or `needs_review` as accepted fact.

If closure finds a product defect, return to the owning phase rather than silently changing Phase 12 scope.
