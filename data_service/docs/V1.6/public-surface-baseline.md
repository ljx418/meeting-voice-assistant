# V1.6 Public Surface Baseline

更新时间：2026-05-12

本文件固化 V1.5 accepted 状态，作为 V1.6 规划和实现的公开面基线。

## Project Positioning

`data_service` 是 MCP-first local knowledge governance microservice。它不是 personal knowledge app，也不是 end-user knowledge consumption app。上层 meeting、ASR、interview、learning、IDE plugin 或 agent workflow 只能通过 MCP / CLI / HTTP 调用服务，不应成为 `data_service` 的生产依赖。

## V1.5 Accepted Baseline

| surface | V1.5 baseline |
| --- | --- |
| MCP | 40 tools |
| CLI | top-level commands remain `build / graph / quality / query / source / trace / workspace` |
| compatibility HTTP | `/api/v1/knowledge/*` retained |
| target HTTP | exactly 3 routes |
| console | `/knowledge` service governance console |

## Target HTTP Baseline

V1.5 当前只开放：

- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

V1.6 尚未开放：

- workspace/source/build write target HTTP routes
- graph advanced target HTTP routes
- quality write target HTTP routes
- session target HTTP routes

## Contract Baseline

外部 contract 只能稳定依赖：

- `workspace_id`
- `source_id`
- `session_id`
- `operation_id`
- `artifact_ref`
- request / response envelope
- normalized error code / message / retryable

内部 filesystem path、workspace layout、artifact layout 只能作为 debug 或 console-only 字段出现，不属于稳定外部 contract。

## Guardrail

V1.6 的每个实现阶段都必须证明：

- 没有隐藏性新增 MCP tool。
- 没有隐藏性新增 HTTP route。
- 没有隐藏性新增 CLI command。
- 旧 `/api/v1/knowledge/*` 兼容入口没有被破坏。
- `/knowledge` 没有被重新定义为终端用户知识消费 App。
