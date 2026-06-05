# V2.8 Phase 56 Visual Architecture Reading UX Spec

> Development, acceptance, and pre-implementation audit specification for Phase 56.

## 1. Goal

Create a human-readable architecture dashboard and HTML report that allows a reviewer to quickly understand project architecture, key risks, and evidence without opening raw JSON artifacts.

## 2. Required Implementation

- Build `architecture_reading_dashboard.json`.
- Build `views/architecture_reading_report.html`.
- Build `views/architecture_overview.svg`.
- Include at least six chart sections defined in `V2_8_VIEW_AND_GRAPH_SPEC.md`.
- Preserve V2.7 target/current/diff sections as detailed drill-down.

## 3. Required Data Sources

- V2.7 reconstructed model.
- V2.7 document quality findings.
- V2.7 alignment and drift artifacts.
- V2.0/V2.1 public surfaces and evidence where available.
- V2.6 taxonomy and scale summary where available.

## 4. Acceptance Gates

- data_service and HarnessOS both generate report artifacts.
- first screen includes project summary, core architecture, top risks, and evidence counts.
- every chart node/edge resolves to persisted artifact refs.
- HTML contains no raw `<script>` from source documents.
- public output contains no local absolute path.
- empty chart sections show explicit empty state.

## 5. Pre-Implementation Audit

Before implementation:

- confirm V2.7 closure report exists;
- confirm required source artifacts exist or structured missing-artifact behavior is specified;
- confirm no business logic will be placed in route/MCP/CLI registration files;
- confirm no chart can be generated from unpersisted facts.

## 6. False-Green Rejection

Reject Phase 56 if:

- HTML looks polished but chart nodes lack evidence;
- report copies HarnessOS drawio as code-derived architecture;
- major findings disappear from summary;
- report only passes on mock fixtures;
- generated view leaks local absolute paths.
