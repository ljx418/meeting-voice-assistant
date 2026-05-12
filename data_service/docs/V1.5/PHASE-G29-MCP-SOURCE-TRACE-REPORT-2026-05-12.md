# PhaseG29 MCP Source Trace Report

日期：2026-05-12

## 阶段目标

开放 MCP `knowledge_source_trace`，使 Source Trace 的 MCP / HTTP / CLI 三入口复用同一个 shared serializer。

## 实现范围

- 新增 MCP tool：`knowledge_source_trace`。
- tool schema 固定为：
  - `workspace` / `workspace_id`
  - `source_id`
  - `limit`
- handler 直接复用 `source_trace_payload`。
- 前端 MCP contract 快照同步新增该 tool。

## 不变项

- 不新增 HTTP route。
- 不新增 CLI command。
- 不改变 HTTP `/api/v1/knowledge/source/trace` 响应形态。
- 不改变 CLI `knowledge trace source` 响应形态。
- 不开放 graph advanced 子命令。

## 出门验证

- PhaseG29 目标用例：`7 passed`。
- 阶段回归：
  - API：`33 passed`。
  - MCP：`32 passed`。
  - Data Service/API/MCP 组合回归：`136 passed`。
  - 前端 build：`npm run build` 通过。
  - drawio XML：`docs/V1.5/current-vs-target-gap.drawio` 与 `docs/V1.5/data-service-v1.5-roadmap.drawio` 解析通过。

## 对外能力检查

本阶段只扩大 MCP 工具集合：

```text
knowledge_source_trace
```

HTTP route、CLI parser、`knowledge` console script 公开面均保持不变。

## 下一阶段

PhaseG30 已开放首批目标 HTTP route：`/api/workspaces/{workspace_id}/query`、`/api/workspaces/{workspace_id}/distill`、`/api/workspaces/{workspace_id}/sources/{source_id}/trace`。下一步进入 PhaseG31 V1.5 收口验收。
