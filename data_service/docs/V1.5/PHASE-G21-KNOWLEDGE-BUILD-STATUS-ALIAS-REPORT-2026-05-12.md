# PhaseG21 Knowledge Build Status Alias Report

日期：2026-05-12

## 范围

PhaseG21 只开放 `knowledge build status` 只读 alias。

本阶段不新增 MCP tool，不新增 HTTP route，不开放 `knowledge build start/cancel`。

## 实现

- 新增 `_add_build_lifecycle_parser`，只挂载到 `_build_knowledge_parser()`。
- `data_service` 兼容 CLI 顶层命令集合保持不变。
- `knowledge build status` 转调现有 `knowledge_build_status` handler。
- 输出继续复用 MCP operation envelope 与 sanitizer。

## Contract

目标命令：

```text
knowledge build status --workspace-root ./workspaces --workspace-id research-vault --operation-id op_123
```

稳定响应 envelope：

```text
workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data
```

operation data 稳定字段：

```text
mode / stage / progress / error / retryable / artifact_refs / debug_paths
```

## 出门验证

- API 专项回归：`27 passed`
- MCP 专项回归：`30 passed`
- Data Service/API/MCP 组合回归：`128 passed`
- Frontend build：通过
- Draw.io XML：通过

## 对外能力检查

- 新增公开能力：仅 `knowledge build status` CLI alias。
- 未新增 MCP tool。
- 未新增 HTTP route。
- 未开放 `knowledge build start/cancel`。
- 未开放 `knowledge distill/graph/trace`。
- `data_service` CLI 顶层命令集合保持不变。

## 下一步

后续按 PhaseG22 已完成 `knowledge graph snapshot` 只读 alias，PhaseG23 已完成 `knowledge trace source` 只读 alias，PhaseG24 已固化 `knowledge graph` advanced 子命令迁移窗口，PhaseG25 已开放 `knowledge workspace create/archive` 写入型 CLI alias，PhaseG26 已开放 `knowledge source import/remove` 写入型 CLI alias，PhaseG27 已开放 `knowledge build start/cancel` 写入型 CLI alias，PhaseG28 已开放 MCP `knowledge_distill_preview`，PhaseG29 已开放 MCP `knowledge_source_trace`。PhaseG30 已开放首批目标 HTTP route，下一步进入 PhaseG31 V1.5 收口验收。
