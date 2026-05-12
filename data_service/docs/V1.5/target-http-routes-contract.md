# Target HTTP Routes Contract

日期：2026-05-12

## 定位

PhaseG30 开放首批 workspace-scoped 目标 HTTP route，用于把 HTTP 入口从 path-first 的 `/api/v1/knowledge/*` 逐步迁移到 `workspace_id` first 的 `/api/workspaces/{workspace_id}/...`。

MCP 仍是默认主入口；目标 HTTP route 是兼容 HTTP 客户端的稳定外部 contract，不取代 MCP。

## PhaseG30 首批开放范围

| 能力 | 目标 HTTP route | 兼容入口 | 复用 contract |
| --- | --- | --- | --- |
| query | `POST /api/workspaces/{workspace_id}/query` | `POST /api/v1/knowledge/query` | `run_query_contract` |
| distill | `POST /api/workspaces/{workspace_id}/distill` | `POST /api/v1/knowledge/distill` | `run_distill_contract` |
| source trace | `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace` | `POST /api/v1/knowledge/source/trace` | `source_trace_payload` |

## 请求约束

- 目标 route 从 path 中读取 `workspace_id`。
- 请求体不再接受 `workspace` path 作为主 contract 字段。
- `query`、`distill` 和 `source trace` 的响应字段必须与兼容入口完全一致。
- `source trace` 使用 GET route，`limit` 使用 query parameter。
- `workspace_id` 解析仍受 `DATA_SERVICE_WORKSPACE_ROOT` 和 workspace path 校验约束保护。

## 兼容窗口

旧 `/api/v1/knowledge/*` 兼容入口不废弃。

兼容窗口内：

- 控制台继续使用现有入口，除非单独进入前端迁移阶段。
- 旧客户端不需要立即切换。
- 新目标 route 必须复用 shared contract helper，不允许重新组装 payload。
- 新目标 route 不允许改变旧入口响应字段集合。

## 非目标

PhaseG30 不开放以下目标 route：

- workspace/source/build 写入型目标 HTTP route。
- graph advanced 目标 HTTP route。
- quality 写入型目标 HTTP route。
- session 目标 HTTP route。

这些能力继续保留在 MCP-first 计划中，后续阶段按最小能力组评估。

## 出门验证

PhaseG30 的最小出门验证必须覆盖：

- 目标 query route 与旧 query route payload 完全一致。
- 目标 distill route 与旧 distill route payload 完全一致。
- 目标 source trace route 与旧 source trace route payload 完全一致。
- 旧 `/api/v1/knowledge/query`、`/api/v1/knowledge/distill`、`/api/v1/knowledge/source/trace` 路由仍存在。
- `current-vs-target-gap.md`、`current-vs-target-gap.drawio` 和 V1.5 roadmap drawio 同步更新。

## PhaseG31 Closure Audit

PhaseG31 已完成 V1.5 收口验收。当前 target HTTP 仍只开放 query / distill / source trace 三个 route；workspace/source/build 写入型 target route、graph advanced target route、quality write target route 和 session target route 均未开放，作为 V1.6 candidates 仅记录不实现。
