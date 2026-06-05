# V2.8 Gap Analysis

> Current-vs-target gap analysis for V2.8.

## 1. Current V2.7 Baseline

V2.7 has accepted:

- document registry;
- architecture claim and relation extraction;
- document quality evaluation;
- document-code alignment;
- target/current/diff reconstructed model;
- HTML and Mermaid report;
- governance integration.

## 2. Remaining Gaps Addressed by V2.8

| Gap | Current behavior | V2.8 target | Phase |
| --- | --- | --- | --- |
| report readability | report is artifact-heavy and list-like | chart-rich reading dashboard | 56 |
| graph usability | capped target/current/diff nodes | clustered graph views and filters | 57 |
| code fact depth | symbols, surfaces, alignments | entrypoint chains and boundary hints | 58 |
| large-project noise | thousands of claims/drift rows | ranking and top review queues | 59 |
| design-intent clarity | mostly document-derived claims | documented/code/audit/mismatch intent model | 60 |
| agent consumption | general context artifacts | Architecture Context Pack v2 | 61 |

## 3. Major Risks

- polished diagrams may hide weak evidence;
- ranking may bury high-severity findings;
- runtime hints may be mistaken for deterministic calls;
- graph clusters may lose evidence traceability;
- Context Pack v2 may drop evidence under token pressure.

## 4. Risk Controls

- persisted artifact refs for every chart node;
- confidence and `needs_review` visible in every public view;
- major/fatal findings always pinned;
- deterministic vs inferred code facts separated;
- token budget must remove unsupported recommendations with their evidence.

## 5. V2.8 Completion Gap

Phase 56-62 implementation and real E2E validation have been completed.

Closed gaps:

- readable dashboard and charts;
- graph aggregation and filtered views;
- deterministic code fact chains and runtime boundary hints;
- signal ranking and review queue v2;
- evidence-backed intent model;
- Architecture Context Pack v2;
- HTTP/MCP/CLI public access for V2.8 capabilities.

Remaining non-blocking limitations:

- HarnessOS code fact chains are generated but remain `needs_review` where source line evidence is missing;
- V2.8 still does not claim full call graph, data flow, control flow, type inference, IDE-grade navigation, or pure code-derived human intent recovery;
- ranking calibration can be improved in future phases, because current real data produces many major/pinned review items.
