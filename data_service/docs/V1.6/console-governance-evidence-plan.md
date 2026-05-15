# V1.6-F1 Console Governance Evidence Plan

更新时间：2026-05-15

## Scope

V1.6-F1 is a documentation, evidence, and guard baseline sync phase. It opens no public surface and changes no frontend behavior.

F1 depends on V1.6-E5 accepted. If E5 is not accepted, F1 is blocked.

F1 does not add backend routes, MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, frontend behavior, or `/knowledge` behavior. `/knowledge` remains the service governance console, not an end-user knowledge consumption app.

## Evidence Matrix

| phase | status | public surface delta | target HTTP count | MCP count | CLI top-level/nested diff | governance evidence | remaining boundary |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| V1.5 immutable baseline | accepted | baseline 3 target routes | 3 | 40 | top-level `build / graph / quality / query / source / trace / workspace`; nested baseline unchanged | `public-surface-baseline.json` remains immutable; `/api/v1/knowledge/*` compatibility retained | baseline JSON must not be rewritten as current surface |
| V1.6-A Public Surface Guard | completed | +0; guard only, not a route overlay | 3 | 40 | none | public surface guard scans MCP, CLI, HTTP, target HTTP and compatibility retention | no business capability added |
| V1.6-B lifecycle target HTTP | completed | B1/B2/B3 overlays +11 workspace/source/build lifecycle routes | 14 | 40 | none | phase overlays and focused lifecycle tests | no graph/session/quality route opened by B |
| V1.6-C graph advanced | completed | C1/C2/C3/C4 overlays +4 graph routes; CLI nested graph additions | 18 | 40 | top-level none; nested graph additions accepted | graph neighbors/community/query/session inspection tests and stable projection docs | graph routes remain bounded and do not rewrite MCP baseline |
| V1.6-D1 session contract planning | completed | +0; planning and hardening only, not a route overlay | 18 | 40 | none | `session-graphrag-contract-plan.md` and focused contract tests | no session lifecycle route added by D1 |
| V1.6-D2 session lifecycle | completed | D2 overlay +5 create/list/get/close/delete routes | 23 | 40 | none | lifecycle focused tests and non-path projection rules | no ingest/query/build in D2 |
| V1.6-D3 session ingest/query/build planning | completed | +0; planning and guard only, not a route overlay | 23 | 40 | none | `session-ingest-query-build-contract-plan.md` matrix and guard tests | D4/D5/D6 must remain split |
| V1.6-D4/D5/D6 session scoped routes | completed | D4 ingest + D5 query + D6 build overlays +5 routes | 28 | 40 | none | focused ingest/query/build tests, real operation ids, artifact refs | no quality target HTTP opened by D |
| V1.6-E quality governance | completed through E5 | E1 feedback + E2 rules + E3 review + E4 plan + E5 rules-build overlays +7 routes | 35 | 40 | none | quality focused tests and non-destructive governance reports | correction apply remains not opened |
| V1.6-F1 console governance evidence baseline | completed by this phase | +0; docs/tests/report only | 35 | 40 | none | this matrix, focused evidence-plan test, drawio sync | no frontend behavior change |
| V1.6-F2 console governance polish | planned | +0 expected unless separately scoped and accepted | 35 expected | 40 expected | none expected | future console evidence display validation | not implemented in F1 |

Current accepted target HTTP route count:

```text
V1.5 baseline 3
+ A guard 0
+ B1/B2/B3 overlays 11
+ C1/C2/C3/C4 overlays 4
+ D1 planning 0
+ D2 overlay 5
+ D3 planning 0
+ D4/D5/D6 overlays 5
+ E1/E2/E3/E4/E5 overlays 7
= 35
```

Compressed evidence summary: A guard: +0; B1/B2/B3 overlays +11; C1/C2/C3/C4 overlays +4; D1 planning +0; D2 overlay +5; D3 planning +0; D4/D5/D6 overlays +5; E1/E2/E3/E4/E5 overlays +7; current target HTTP route count = 35.

## Console Governance Evidence Rules

- `/knowledge` remains a service governance console.
- F1 does not modify frontend files or `/knowledge` static assets.
- F1 does not add backend public surface.
- F1 does not add routes, MCP tools, CLI commands, or CLI subcommands.
- F1 does not define raw internal path, workspace layout, artifact physical path, cache path, raw diagnostics, raw logs, or raw storage layout as external contract.
- F2 remains planned and must not be described as implemented.

## Focused Guard

`backend/tests/test_console_governance_evidence_plan.py` verifies:

- the evidence matrix exists;
- route count remains 35;
- MCP tool count remains 40;
- CLI top-level and nested diffs remain none;
- V1.5 baseline is immutable;
- no new backend public surface is introduced by F1;
- no frontend behavior change is introduced by F1;
- `/knowledge` remains service governance console;
- F2 remains planned, not implemented;
- internal path/layout is not documented as external contract.
