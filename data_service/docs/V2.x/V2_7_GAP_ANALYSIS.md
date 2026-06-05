# V2.7 Gap Analysis: Documentation-Code Architecture Governance

> Gap analysis for V2.7 documentation development.
> Phase 49, Phase 50, Phase 51, Phase 52, Phase 53, Phase 54, and Phase 55 are accepted.

Date: 2026-06-04

## 0. Current Gap Status

Closed in Phase 49:

- Document discovery as a first-class document asset registry.
- Document authority metadata baseline.
- Markdown, Mermaid, and Drawio document asset registration.
- HTTP/MCP/CLI public registry reads.

Closed in Phase 50:

- Claim-level Markdown and Drawio extraction.
- Document relation extraction.
- Confidence and review metadata for weak diagram/document claims.
- HTTP/MCP/CLI public claims reads.

Closed in Phase 51:

- Document quality evaluation.
- Quality finding summary with severity and finding-type counts.
- Major/fatal findings blocking `high_quality`.
- HTTP/MCP/CLI public quality reads.

Closed in Phase 52:

- Document-code alignment v2.
- Drift reporting with `designed_not_found_in_code` and `code_not_documented`.
- Token-only matches kept as weak matches.
- HTTP/MCP/CLI public alignment reads.

Closed in Phase 53:

- Target/current/diff reconstructed architecture model.
- Safe HTML architecture report.
- Safe Mermaid diff view.
- Rendered node and edge resolution against persisted model artifacts.
- HTTP/MCP/CLI public reconstructed/view reads.

Remaining gap status:

- no in-scope V2.7 MVP capability gap remains after Phase 55 closure.

## 1. Executive Summary

Current Project Intelligence can identify code-derived architecture roles, lightweight large-project facts, architecture sources, document assets, document claims, document relations, document quality findings, conservative document-code alignment, target/current/diff reconstructed architecture views, and read-time governance overlays for V2.7 document-code targets. Phase 55 closure is accepted for the current V2.7 scope.

The core gap is not code parsing. The core gap is governance of architecture claims:

```text
What the documents say
vs
What the code shows
vs
What evidence proves
vs
What still needs human review
```

## 2. Capability Gap Matrix

| Capability | Current state | Target V2.7 state | Gap severity |
| --- | --- | --- | --- |
| Document discovery | Implemented in Phase 49 | First-class document asset registry with doc type, version, phase and scope | closed |
| Document authority | Implemented as Phase 49 baseline | Authority role, authority level, supersession and stale handling | closed |
| Markdown understanding | Implemented in Phase 50 | Claim-level extraction from PRD, architecture, gap, plan and audit docs | closed |
| Drawio understanding | Implemented in Phase 50 | Structured architecture claims, relations, statuses, governance and gate hints | closed |
| Document quality | Implemented in Phase 51 | Completeness, consistency, evidence, freshness, scope and acceptance quality findings | closed |
| Design-code matching | Implemented in Phase 52 | Evidence-backed claim-to-code and code-to-doc coverage with stable statuses | closed |
| Target/current/diff reconstruction | Implemented in Phase 53 | Reconstructed model, HTML report, and Mermaid diff from document claims, code facts, alignment and drift | closed |
| Governance integration | Implemented in Phase 54 | V2.7 document-code targets resolve in quality feedback/rules/plan and approved rules apply as read-time overlay | closed |
| Closure acceptance | Implemented in Phase 55 | Full PRD coverage matrix and closure audit accepted | closed |
| Target/current split | Implemented in Phase 53 | Separate target architecture from current code architecture and diff | closed |
| Architecture reconstruction | Implemented in Phase 53 | Reconstructed model from document claims, code facts and alignment | closed |
| Cross-link integrity | Implemented for current V2.7 scope | All docs, claims, relations, alignments, model nodes and views must resolve | closed |
| Governance | Implemented in Phase 54 | Governance covers docs, claims, alignments and reconstructed nodes | closed |
| Public contract | Implemented through Phase 54 | V2.7 doc architecture reads over HTTP/MCP/CLI | closed |
| E2E validation | Implemented through Phase 55 | data_service + HarnessOS document-code architecture reconstruction and closure rollup | closed |

## 3. Current Strengths to Reuse

- V2.0 deterministic code facts and evidence trace.
- V2.1 graph and quality governance.
- V2.4 architecture roles/layers/boundaries/patterns and drift.
- V2.6 scale profile, taxonomy, review queue and large-project views.
- Existing drawio and Markdown architecture source discovery.
- Existing HTML/Mermaid rendering approach.

## 4. Current Weaknesses

### 4.1 Document registry and claim baseline closed

Phase 49 now creates a governed document inventory with type, phase, scope, status and stale signals. Phase 50 now extracts document claims and relations. Phase 51 now evaluates document quality. Phase 52 now aligns document claims to code facts conservatively.

Remaining risk:

- extracted document claims can still be overbroad or weak;
- quality findings identify review risks but do not prove implementation by themselves;
- Phase 53 must preserve weak/missing alignment states instead of rendering them as accepted architecture.

V2.7 must continue to keep target architecture, implementation plan, audit status, acceptance result and historical reference separate.

### 4.2 Claim extraction and alignment are accepted but not reconstruction

Drawio labels, Markdown sections, bullets, tables, API matrices, acceptance gates and diagram edges are now extracted as document claims and relations.

Remaining risk:

- extracted claims are still document-side facts until Phase 52 matched them with code evidence;
- copied diagrams must remain document claims, not code-inferred architecture;
- forbidden claims and non-goals must continue to constrain later acceptance.

### 4.3 Document quality is governed but not closure

Phase 51 automatically evaluates document quality and emits quality findings.

Remaining risk:

- major quality findings require review;
- quality findings can block accepted alignment status;
- unsupported claims must not enter accepted Agent Context Pack as implemented facts.

### 4.4 Alignment confidence remains a rendering risk

Phase 52 now uses stronger match strategies and explicit status taxonomy. Token overlap can still suggest candidate matches, but it remains `weak_match` and cannot prove implementation. Phase 53 now renders target/current/diff views from persisted artifacts without treating copied drawio content as code-derived architecture.

Closed risk controls:

- Phase 54 governance overlays are read-time annotations and do not hide weak/missing/code-only rows;
- governance rules do not mutate source artifacts;
- weak matches remain reviewable and do not become false-green architecture facts in governed reads.

### 4.5 Views can be misread

V2.6 views show useful audit artifacts but can be misread as target project architecture. V2.7 views must explicitly separate:

- target architecture from documents;
- current architecture from code;
- diff and unresolved items from alignment findings.

### 4.6 Safety and integrity are not explicit enough

Generated HTML/Mermaid views need escaping and node integrity checks. V2.7 must validate every rendered node against persisted reconstructed model artifacts and must hash-gate prior V2 artifacts and original docs.

## 5. Required V2.7 Gaps to Close

1. Add document asset registry. Closed in Phase 49.
2. Add architecture claim extraction. Closed in Phase 50.
3. Add document relation extraction. Closed in Phase 50.
4. Add document quality evaluator. Closed in Phase 51.
5. Add doc-code alignment v2. Closed in Phase 52.
6. Add target/current/diff reconstructed architecture model. Closed in Phase 53.
7. Add V2.7 HTML/Mermaid views. Closed in Phase 53.
8. Add V2.7 quality governance targets. Closed in Phase 54.
9. Add remaining HTTP/MCP/CLI read contracts for governance integration. Closed in Phase 54.
10. Add real-repo closure audit. Closed in Phase 55.
11. Continue source artifact hash gates. Closed for V2.7 in Phase 54/55.
12. Add HTML/Mermaid rendering safety checks. Closed for Phase 53 views.
13. Add cross-link integrity validators. Closed for V2.7 in Phase 55.

## 6. Stop Conditions

Stop implementation and request human review if:

- target architecture cannot be separated from current code architecture;
- the implementation needs LLM-only architecture claims without evidence;
- copied original diagrams are being presented as code-reconstructed architecture;
- accepted doc-code matches rely only on weak token overlap;
- HarnessOS E2E requires mock data to pass.

## 7. Readiness Assessment

V2.7 closure is accepted by `V2_7_CLOSURE_AUDIT_REPORT.md`. Governance overlays remain read-time only and preserve weak/missing states from Phase 52/53 artifacts.
