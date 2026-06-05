# V2.8 Development and Acceptance Plan

> V2.8 is currently in documentation development.
> This plan defines phases, audit rules, and acceptance gates before business-code implementation.

Date: 2026-06-04

## 1. Phase Overview

| Phase | Name | Outcome |
| --- | --- | --- |
| 56 | Visual Architecture Reading UX | Human-readable dashboard and chart-rich HTML report |
| 57 | Architecture Graph Aggregation / Layout / Filtering | Clustered graph views and filters for large projects |
| 58 | Deeper Code Fact Extraction | Entry chains, service paths, dependency clusters, runtime hints |
| 59 | Large Project Signal Ranking | Ranked architecture signals and review queue v2 |
| 60 | Design Intent Evidence and Doc Quality v2 | Intent evidence model and document conflict detection |
| 61 | Architecture Context Pack v2 | Agent-readable task-aware architecture context |
| 62 | V2.8 Closure Acceptance | Full PRD coverage, real E2E, false-green audit |

## 2. Shared Implementation Rules

Before each implementation phase:

- write phase development plan, acceptance plan, and pre-implementation audit;
- verify previous phase accepted with no open fatal/major finding;
- verify V2.0-V2.7 source artifacts are readable;
- record source artifact hashes;
- define real data acceptance for `data_service` and HarnessOS.

After each implementation phase:

- run focused tests;
- run public contract regression;
- run real E2E on `data_service` and HarnessOS;
- inspect disk artifacts;
- run PRD/spec review;
- run false-acceptance review;
- write phase acceptance audit report.

## 3. Shared Stop Conditions

Stop and ask for human confirmation if any of these appear:

- implementation needs to change V2.0-V2.7 artifact semantics;
- accepted architecture output would rely on LLM-only or token-only evidence;
- report chart cannot trace nodes back to persisted artifacts;
- runtime hints are being promoted to deterministic facts;
- major/fatal finding would be hidden by ranking or summary;
- direct project source paths, secrets, or local absolute paths leak in public output;
- HarnessOS E2E cannot run with real data.

## 4. Required Real E2E

Each phase must use:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

Mock-only acceptance is rejected.

## 5. Public Contract Scope

V2.8 must align HTTP, MCP, and CLI reads for:

- views build/read;
- graph summary;
- ranking;
- context pack v2.

Every public response must expose:

- `schema_version`;
- `workspace_id`;
- `codebase_id`;
- `snapshot_id`;
- artifact refs;
- warnings;
- unresolved items;
- redaction state.

## 6. Closure Criteria

V2.8 is complete when:

- Phase 56-62 are accepted;
- `V2_8_FULL_PRD_COVERAGE_MATRIX.md` has no pending in-scope row;
- `V2_8_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md` cites real artifacts for both repos;
- `V2_8_DOCUMENT_AUDIT_REPORT.md` reports no fatal/major document gap;
- target PRD, architecture, plan, gap, drawio, and coverage matrix are consistent.
