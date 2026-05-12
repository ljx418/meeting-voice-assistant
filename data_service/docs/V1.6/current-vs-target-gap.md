# Data Service V1.6 Current vs Target Gap

更新时间：2026-05-12

## Baseline

V1.5 已 accepted，并作为 V1.6 的冻结基线。V1.5 已闭环的 MCP handler 模块化、GraphRAG service 边界、contract hardening、typed distill units、format expansion、console governance、query/distill/trace shared contracts 和 PhaseG31 closure acceptance 不再作为 V1.6 gap。

## Current State

- MCP tool count：40。
- CLI 顶层命令保持 `build / graph / quality / query / source / trace / workspace`。
- compatibility HTTP `/api/v1/knowledge/*` 保留。
- target HTTP 只开放 query / distill / source trace。
- MCP graph/session tools already exist in the V1.5 baseline；`knowledge graph` CLI 当前只开放 `snapshot`，graph advanced target HTTP / CLI minimal surfaces 尚未开放。
- session capability 仍以 MCP-first 为主；V1.6 不新增 session MCP tools，target HTTP/session CLI 与跨入口 Session GraphRAG public contract 仍待收敛。
- quality governance 已有 MCP / CLI / compatibility HTTP 能力，target HTTP write routes 未开放。
- `/knowledge` 是 service governance console。

## Target State

- 每个新公开能力都有明确 MCP / CLI / HTTP / target HTTP contract。
- target HTTP 分阶段补齐 lifecycle、graph advanced、quality write、session。
- Graph advanced 以最小子命令逐步开放，不直接暴露内部 GraphRAG layout。
- Session GraphRAG public contract 使用 `session_id`、`operation_id`、`artifact_ref` 和 envelope。
- Quality target HTTP write routes 保持 non-destructive governance 语义。
- Console 使用治理语义展示状态、trace、quality、contracts 和 artifacts。

## V1.6 Gap List

| gap | current | target | priority |
| --- | --- | --- | --- |
| public surface guard | PhaseG31 audit is report-based | repeatable guard before every V1.6 slice | P0 |
| target HTTP lifecycle write | compatibility HTTP exists | workspace/source/build target HTTP write routes | P1 |
| graph advanced public surface | MCP graph tools exist；CLI only exposes `knowledge graph snapshot`；target HTTP graph advanced not open | target HTTP / CLI minimal surfaces for neighbors/community/query/session where not yet open | P1 |
| session GraphRAG contract | MCP session tools exist；cross-surface contract still MCP-first | stable public contract convergence across selected surfaces | P1 |
| quality target HTTP write | compatibility HTTP + CLI | target HTTP quality write routes | P2 |
| artifact_ref normalization | V1.5 contract accepted | stronger cross-surface normalization checks | P2 |
| operation lifecycle consistency | V1.5 envelope accepted | lifecycle consistency across new target routes | P2 |
| console governance polish | governance console exists | clearer V1.6 state and target-surface evidence | P3 |

## Explicitly Not Implemented Yet

The following are V1.6 candidates only until an implementation phase opens and accepts them:

- graph advanced target HTTP / CLI minimal surfaces where not yet open
- workspace/source/build target HTTP write routes
- graph advanced target HTTP routes
- quality write target HTTP routes
- session target HTTP routes
- cross-surface Session GraphRAG public contract convergence
