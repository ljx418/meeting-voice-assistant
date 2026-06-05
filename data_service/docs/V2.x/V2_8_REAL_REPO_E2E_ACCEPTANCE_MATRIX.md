# V2.8 Real Repo E2E Acceptance Matrix

> Real-repository acceptance matrix for V2.8.
> Updated after Phase 62 closure validation.

## 1. Required Repositories

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

## 2. Phase Matrix

| Phase | Capability | data_service required evidence | HarnessOS required evidence | Acceptance status |
| --- | --- | --- | --- | --- |
| 56 | readable architecture dashboard | Accepted: 6 charts, 80 hotspots, HTML + Mermaid, no path/script leak | Accepted: 6 charts, 80 hotspots, HTML + Mermaid, no path/script leak | accepted |
| 57 | graph aggregation/filtering | Accepted: 580 nodes, 12 edges, 67 clusters, 6 views, unsupported edges = 0 | Accepted: 580 nodes, 10 edges, 23 clusters, 6 views, unsupported edges = 0 | accepted |
| 58 | deeper code facts | Accepted: 405 chains, 325 accepted, 5 boundaries | Accepted with reviewable gaps: 178 chains, 0 accepted, 178 needs_review due missing line evidence | accepted |
| 59 | signal ranking | Accepted: 300 ranking items, 200 queue items, reason codes visible | Accepted: 300 ranking items, 200 queue items, reason codes visible | accepted |
| 60 | design-intent evidence | Accepted: 1440 intent rows across documented/code/audit/mismatch | Accepted: 1275 intent rows; code-observed rows remain needs_review where line evidence is missing | accepted |
| 61 | context pack v2 | Accepted: task_context pack, 63 items, 8 sections, small budget omits items | Accepted: task_context pack, 57 items, 8 sections, unresolved evidence visible | accepted |
| 62 | closure | Coverage matrix accepted | Coverage matrix accepted with explicit needs_review caveats | accepted |

## 3. False-Green Rejection

| False-green case | Result |
| --- | --- |
| mock-only repo accepted | reject |
| copied drawio shown as code fact | reject |
| chart node lacks persisted artifact | reject |
| token-only match accepted | reject |
| major finding hidden by ranking | reject |
| runtime hint shown as deterministic call | reject |
| context pack recommendation lacks evidence or needs_review | reject |
| local absolute path leak | reject |
| V2.0-V2.7 source artifact silently changed | reject |

## 4. HarnessOS Specific Checks

HarnessOS E2E must verify:

- graph views are clustered for large document/code volume;
- V4/V6 design docs influence documented target intent but do not become code facts;
- public surface and workflow runtime chains are traceable where code evidence exists;
- unresolved architecture intent remains visible;
- default report is readable without opening raw JSON artifacts.
