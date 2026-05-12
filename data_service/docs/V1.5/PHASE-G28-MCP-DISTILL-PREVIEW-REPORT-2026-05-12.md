# PhaseG28 MCP Distill Preview Report

日期：2026-05-12

## 阶段目标

开放 MCP `knowledge_distill_preview`，使 distill preview 的 MCP / HTTP / CLI 三入口复用同一个 shared contract。

## 实现范围

- 新增 MCP tool：`knowledge_distill_preview`。
- tool schema 对齐现有 distill preview 参数：
  - `workspace` / `workspace_id`
  - `source_id`
  - `limit`
  - `kind`
  - `typed_unit_type`
  - `min_importance`
  - `llm_enriched_only`
  - `authority`
  - `min_source_weight`
  - `min_source_density`
- handler 直接复用 `run_distill_contract`。
- 前端 MCP contract 快照同步新增该 tool。

## 不变项

- 不新增 HTTP route。
- 不新增 CLI command。
- 不改变 HTTP `/api/v1/knowledge/distill` 响应形态。
- 不改变 CLI `data_service distill` 响应形态。
- 不开放 MCP `knowledge_source_trace`。

## 出门验证

- PhaseG28 目标用例：`4 passed`。
- 阶段回归：
  - API：`33 passed`。
  - MCP：`31 passed`。
  - Data Service/API/MCP 组合回归：`135 passed`。
  - 前端 build：通过。
  - drawio XML：通过。

## 对外能力检查

本阶段只扩大 MCP 工具集合：

```text
knowledge_distill_preview
```

HTTP route、CLI parser、`knowledge` console script 公开面均保持不变。

## 下一阶段

PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放首批目标 HTTP route，下一步进入 PhaseG31 V1.5 收口验收。
