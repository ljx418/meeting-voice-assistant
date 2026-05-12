# PhaseG27 Build Write CLI Contract Report

日期：2026-05-12

## 阶段目标

开放 `knowledge build start/cancel` 写入型 CLI alias，使 build operation 的目标 CLI 与既有 MCP build lifecycle handler 对齐。

## 实现范围

- 新增 `knowledge build start`。
  - 支持 `--mode full|incremental|graph_only|llmwiki_only`。
  - 转调 `knowledge_build_start` handler。
- 保留 `knowledge build status`。
  - 继续转调 `knowledge_build_status` handler。
- 新增 `knowledge build cancel`。
  - 支持 `--operation-id` 和 `--reason`。
  - 转调 `knowledge_build_cancel` handler。

## 不变项

- 不新增 MCP tool。
- 不新增 HTTP route。
- 不改变 MCP `knowledge_build_start/status/cancel` contract。
- 不改变 HTTP `/api/v1/knowledge/build/*` 兼容入口。
- 不开放 MCP `knowledge_distill_preview`。
- 不开放 MCP `knowledge_source_trace`。

## 出门验证

- PhaseG27 目标用例：`2 passed`。
- 阶段回归：
  - API：`33 passed`。
  - MCP：`30 passed`。
  - Data Service/API/MCP 组合回归：`134 passed`。
  - 前端 build：通过。
  - drawio XML：通过。

## 对外能力检查

本阶段只扩大 `knowledge` CLI 的 build 能力组：

```text
knowledge build start
knowledge build status
knowledge build cancel
```

MCP registry、HTTP route 集合、operation envelope 和 handler name 均保持不变。

## 下一阶段

PhaseG28 已开放 MCP `knowledge_distill_preview`，PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放首批目标 HTTP route，下一步进入 PhaseG31 V1.5 收口验收。
