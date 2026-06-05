# V2.7 Real Repo E2E Acceptance Matrix

> Real-repository acceptance matrix for V2.7.
> Phase 49, Phase 50, Phase 51, Phase 52, Phase 53, Phase 54, and Phase 55 are accepted.

Date: 2026-06-04

## 0. Phase 49-54 Real E2E Result

Accepted by `V2_7_PHASE_49_ACCEPTANCE_AUDIT_REPORT.md`:

| Repo | Document assets | Required Phase 49 evidence |
| --- | ---: | --- |
| `data_service` | 318 | V2.7 PRD and target architecture found; no absolute path leak |
| HarnessOS | 628 | V4 Drawio and V6 document found; no absolute path leak |

Accepted by `V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md`:

| Repo | Claims | Relations | Required Phase 50 evidence |
| --- | ---: | ---: | --- |
| `data_service` | 20085 | 16704 | Markdown/table/interface/non-goal/acceptance claims extracted; no absolute path leak |
| HarnessOS | 18367 | 13476 | real document claims and drawio relations extracted; no absolute path leak |

Accepted by `V2_7_PHASE_51_ACCEPTANCE_AUDIT_REPORT.md`:

| Repo | Findings | Severity counts | Overall status | Required Phase 51 evidence |
| --- | ---: | --- | --- | --- |
| `data_service` | 988 | major: 263, minor: 725 | `needs_review` | quality findings and summary generated; no absolute path leak |
| HarnessOS | 1621 | major: 194, minor: 1427 | `needs_review` | quality findings and summary generated; no absolute path leak |

Accepted by `V2_7_PHASE_52_ACCEPTANCE_AUDIT_REPORT.md`:

| Repo | Alignments | Drift rows | Matched | Weak matches | Token-only rows | Required Phase 52 evidence |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `data_service` | 20827 | 13478 | 7349 | 725 | 719 | accepted matches have document and code evidence; token-only rows stay weak; no absolute path leak |
| HarnessOS | 18635 | 13989 | 4646 | 812 | 808 | accepted matches have document and code evidence; token-only rows stay weak; no absolute path leak |

Accepted by `V2_7_PHASE_53_ACCEPTANCE_AUDIT_REPORT.md`:

| Repo | Target nodes | Current nodes | Diff nodes | Edges | HTML bytes | Mermaid bytes | Required Phase 53 evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `data_service` | 180 | 180 | 220 | 77 | 64294 | 15382 | target/current/diff sections visible; rendered node refs resolve; no absolute path leak |
| HarnessOS | 180 | 180 | 220 | 91 | 65253 | 15645 | target/current/diff sections visible; rendered node refs resolve; no absolute path leak |

Accepted by `V2_7_PHASE_54_ACCEPTANCE_AUDIT_REPORT.md`:

| Repo | Feedback added | Approved rules | Missing target rejected | Revoked rule removed from plan | Hash unchanged | Required Phase 54 evidence |
| --- | ---: | ---: | --- | ---: | --- | --- |
| `data_service` | 3 | 3 | yes | yes | yes | read-time overlay only; claims/alignment/reconstruction artifacts unchanged |
| HarnessOS | 3 | 3 | yes | yes | yes | read-time overlay only; claims/alignment/reconstruction artifacts unchanged |

Accepted by `V2_7_CLOSURE_AUDIT_REPORT.md`.

## 1. Required Repositories

V2.7 closure requires real E2E on:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

Mock-only runs cannot satisfy V2.7 acceptance.

## 2. Pre-Gates

Before any V2.7 phase is accepted:

- `docs/V2.x/V2_6_CLOSURE_AUDIT_REPORT.md` exists.
- V2.6 artifacts are readable or missing status is structured.
- The HarnessOS path resolves exactly as `/Users/Zhuanz/Desktop/workspace/harnessOS`.
- V4/V6 HarnessOS document samples are present or explicitly marked `fixture_unavailable`.
- Source registry, original documents, and prior V2 artifacts pass hash gate.

## 3. Acceptance Matrix

| Phase | Capability | data_service evidence | HarnessOS evidence | Required result |
| --- | --- | --- | --- | --- |
| 49 | Document registry | V2.x PRD, architecture, gap, plan, audit and drawio docs found; historical docs not promoted | V4/V5/V6 design docs and drawio found; path case verified | non-empty registry with doc types and authority metadata |
| 50 | Claim extraction | V2.7 target architecture claims extracted with confidence policy | V4 headless workflow and V6 planes extracted | non-empty claims with evidence and block provenance |
| 51 | Document quality | 345 docs, 20638 claims, 17183 relations, 988 findings; `overall_status=needs_review` | 634 docs, 18390 claims, 13480 relations, 1621 findings; `overall_status=needs_review` | accepted by `V2_7_PHASE_51_ACCEPTANCE_AUDIT_REPORT.md`; major findings block `high_quality` |
| 52 | Doc-code alignment | 20827 alignments, 13478 drift rows, 7349 matched, 10194 designed-not-found, 200 code-not-documented | 18635 alignments, 13989 drift rows, 4646 matched, 10531 designed-not-found, 200 code-not-documented | accepted by `V2_7_PHASE_52_ACCEPTANCE_AUDIT_REPORT.md`; token-only matches remain weak; no path leaks |
| 53 | Architecture reconstruction | 180 target nodes, 180 current nodes, 220 diff nodes, 77 edges, 64294-byte HTML, 15382-byte Mermaid | 180 target nodes, 180 current nodes, 220 diff nodes, 91 edges, 65253-byte HTML, 15645-byte Mermaid | accepted by `V2_7_PHASE_53_ACCEPTANCE_AUDIT_REPORT.md`; HTML/Mermaid generated; no path leaks; edge nodes resolve |
| 53 | Reconstructed architecture report | target/current/diff HTML and Mermaid generated with escaping | target/current/diff HTML and Mermaid generated with escaping | non-empty visual report with evidence and resolvable nodes |
| 54 | Governance integration | 3 feedback records, 3 approved rules, missing target rejected, revoked rule removed from plan, artifact hashes unchanged | 3 feedback records, 3 approved rules, missing target rejected, revoked rule removed from plan, artifact hashes unchanged | accepted by `V2_7_PHASE_54_ACCEPTANCE_AUDIT_REPORT.md`; read-time overlay only |
| 55 | Closure | full PRD matrix and closure audit accepted | full PRD matrix and closure audit accepted | accepted by `V2_7_CLOSURE_AUDIT_REPORT.md`; no fatal/major open findings |

## 4. HarnessOS Specific Checks

HarnessOS acceptance must verify:

- V4 headless workflow chain is extracted as document claims when present;
- V6 target architecture planes are extracted as document claims when present;
- the system distinguishes target design documents from current implementation code;
- missing or weak code evidence remains `needs_review`;
- copied drawio/source diagram nodes are labeled as document claims, not code-inferred facts.
- path case is recorded and checked.
- missing V4/V6 fixture cannot be counted as accepted E2E.

## 5. data_service Specific Checks

data_service acceptance must verify:

- V2.7 documents are discovered and classified;
- V2.0-V2.6 documents remain available as prior-phase documentation assets;
- V2.5/V2.6 documents are marked historical or supporting unless supersession evidence says otherwise;
- V2.7 target PRD and target architecture claims are extracted;
- V2.7 acceptance gates are recognized;
- generated views are based on persisted artifacts only.

## 6. False-Green Rejection Matrix

| False-green pattern | Required rejection |
| --- | --- |
| Mock docs replace real repo docs | reject |
| Empty document registry marked accepted | reject |
| Drawio copied as reconstructed code architecture | reject |
| Token overlap only marked accepted | reject |
| Claim without evidence marked accepted | reject |
| Low-confidence match hidden from review queue | reject |
| Generated view contains unpersisted architecture claim | reject |
| HTML or Mermaid contains unescaped document text injection | reject |
| Missing V2.6 artifacts silently replaced with mock data | reject |
| Historical document promoted to current authority without supersession evidence | reject |
| Absolute path or secret appears in public output | reject |
| Existing V2 artifacts silently rewritten | reject |

## 7. Cross-Link Integrity Requirements

Closure must verify:

- all claim `doc_id` values resolve;
- all relation endpoints resolve;
- all accepted alignment `code_ref` values resolve;
- all reconstructed nodes resolve to document claim, code fact or explicit inference;
- all HTML/Mermaid nodes resolve to reconstructed model nodes.

## 8. Closure Evidence Requirements

Each accepted Phase 55 coverage row must cite:

- command or test name;
- artifact path or artifact ref;
- repository used;
- doc evidence count;
- code evidence count;
- unresolved count;
- audit report path.
