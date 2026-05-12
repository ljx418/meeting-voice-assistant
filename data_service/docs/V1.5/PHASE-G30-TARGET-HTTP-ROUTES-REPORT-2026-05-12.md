# PhaseG30 Target HTTP Routes Report

日期：2026-05-12

## 阶段目标

开放首批 `/api/workspaces/{workspace_id}/...` 目标 HTTP route，让 HTTP 入口具备 `workspace_id` first 的外部 contract，同时保留旧 `/api/v1/knowledge/*` 兼容入口。

## 实现范围

首批只开放共享 contract 已成熟的三个能力：

- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

## 不变项

- MCP 仍是默认主入口。
- 旧 `/api/v1/knowledge/query`、`/api/v1/knowledge/distill`、`/api/v1/knowledge/source/trace` 不废弃。
- 不改变旧 HTTP route 响应字段集合。
- 不新增 CLI command。
- 不新增 MCP tool。
- 不开放 workspace/source/build 写入型目标 HTTP route。
- 不开放 graph advanced / quality write / session 目标 HTTP route。

## Contract 复用

- Query 目标 route 复用 `run_query_contract`。
- Distill 目标 route 复用 `run_distill_contract`。
- Source Trace 目标 route 复用 `source_trace_payload`。

## 出门验证

- PhaseG30 目标用例：`1 passed`。
- 阶段回归：
  - API：`34 passed`。
  - MCP：`32 passed`。
  - Data Service/API/MCP 组合回归：`137 passed`。
  - 前端 build：`npm run build` 通过。
  - drawio XML：`docs/V1.5/current-vs-target-gap.drawio` 与 `docs/V1.5/data-service-v1.5-roadmap.drawio` 解析通过。

## 对外能力检查

本阶段只扩大 HTTP route 集合：

```text
POST /api/workspaces/{workspace_id}/query
POST /api/workspaces/{workspace_id}/distill
GET  /api/workspaces/{workspace_id}/sources/{source_id}/trace
```

MCP tool registry、CLI parser 和旧 HTTP 兼容入口保持不变。

## 下一阶段

PhaseG31 进入 V1.5 收口验收：全量后端回归、前端 build、必要截图验收、公开面扫描、drawio/md 一致性检查和 V1.5 总结报告。
