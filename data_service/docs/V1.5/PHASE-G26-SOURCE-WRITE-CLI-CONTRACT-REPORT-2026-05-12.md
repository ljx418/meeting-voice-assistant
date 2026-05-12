# PhaseG26 Source Write CLI Contract Report

日期：2026-05-12

## 阶段目标

开放 `knowledge source import/remove` 写入型 CLI alias，使 source registry 的目标 CLI 与既有 MCP source lifecycle handler 对齐。

## 实现范围

- 新增 `knowledge source import`。
  - 支持 `--path` 重复参数。
  - 支持单条 `--text`、`--title` 和 `--metadata-json`。
  - 转调 `knowledge_source_import` handler。
- 新增 `knowledge source remove`。
  - 支持 `--source-id` 和 `--reason`。
  - 转调 `knowledge_source_remove` handler。
- 保留 `knowledge source list`，继续转调 `knowledge_source_list` handler。

## 不变项

- 不新增 MCP tool。
- 不新增 HTTP route。
- 不改变 MCP `knowledge_source_import/list/remove` contract。
- 不改变 HTTP `/api/v1/knowledge/sources/*` 兼容入口。
- 不开放 `knowledge build start/cancel`。
- 不开放 MCP `knowledge_source_trace`。

## 出门验证

- PhaseG26 目标用例：`2 passed`。
- 阶段回归：
  - API：`32 passed`。
  - MCP：`30 passed`。
  - Data Service/API/MCP 组合回归：`133 passed`。
  - 前端 build：通过。
  - drawio XML：通过。

## 对外能力检查

本阶段只扩大 `knowledge` CLI 的 source 能力组：

```text
knowledge source import
knowledge source list
knowledge source remove
```

MCP registry、HTTP route 集合、source envelope 和 handler name 均保持不变。

## 下一阶段

PhaseG27 已开放 `knowledge build start/cancel` 写入型 CLI contract，PhaseG28 已开放 MCP `knowledge_distill_preview`，PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放首批目标 HTTP route，下一步进入 PhaseG31 V1.5 收口验收。
