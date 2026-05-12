# V1.6 Interface Convergence Plan

更新时间：2026-05-12

## Baseline

V1.5 已完成 query、distill、source trace 的 shared contract 收敛，并开放首批 target HTTP route。V1.6 的接口收敛从这些 accepted contracts 出发。

## Convergence Rules

- MCP remains primary.
- CLI `knowledge ...` is the human operator entrypoint.
- target HTTP uses workspace-scoped URLs.
- compatibility HTTP `/api/v1/knowledge/*` remains retained.
- new surfaces must reuse existing shared helpers or MCP handlers.
- payloads must converge before public routes are opened.

## Capability Plan

| capability | V1.5 state | V1.6 convergence target |
| --- | --- | --- |
| workspace | MCP + CLI + compatibility HTTP | target HTTP write routes with operation/envelope consistency |
| source | MCP + CLI + compatibility HTTP | target HTTP import/list/remove with stable `source_id` |
| build | MCP + CLI + compatibility HTTP | target HTTP start/status/cancel with stable `operation_id` |
| query | MCP + CLI + compatibility HTTP + target HTTP | harden existing contract |
| distill | MCP + CLI + compatibility HTTP + target HTTP | harden existing contract |
| trace | MCP + CLI + compatibility HTTP + target HTTP | harden existing contract |
| graph | MCP graph tools already exist；CLI exposes snapshot；target HTTP graph advanced not open | graph advanced target HTTP / CLI minimal surfaces where not yet open |
| session | MCP session tools already exist；target HTTP/session CLI not open | cross-surface Session GraphRAG public contract convergence |
| quality | MCP + CLI + compatibility HTTP | target HTTP write routes after lifecycle/graph/session decisions |

## Drift Guards

Each convergence slice must include tests that prevent:

- duplicate payload assembly across surfaces。
- route opening without documented contract。
- CLI command opening without public surface audit。
- MCP tool addition without registry count update。
- stable contract dependence on internal filesystem layout。
