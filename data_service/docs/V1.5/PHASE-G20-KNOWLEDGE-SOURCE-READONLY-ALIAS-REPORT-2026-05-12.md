# PhaseG20 Knowledge Source Read-Only Alias Report

日期：2026-05-12

## 范围

PhaseG20 只开放 `knowledge source list` 只读 alias。

本阶段不新增 MCP tool，不新增 HTTP route，不开放 `knowledge source import/remove`。

## 实现

- 新增 `_add_source_lifecycle_parser`，只挂载到 `_build_knowledge_parser()`。
- `data_service` 兼容 CLI 顶层命令集合保持不变。
- `knowledge source list` 转调现有 `knowledge_source_list` handler。
- 输出继续复用 MCP envelope 与 source registry contract。

## Contract

目标命令：

```text
knowledge source list --workspace-root ./workspaces --workspace-id research-vault --status active --limit 100
```

稳定响应 envelope：

```text
workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data
```

source item 稳定字段：

```text
source_id / sha256 / title / status / low_signal / ingest_status
```

## 出门验证

- API 专项回归：`26 passed`
- MCP 专项回归：`30 passed`
- Data Service/API/MCP 组合回归：`127 passed`
- Frontend build：通过
- Draw.io XML：通过

## 对外能力检查

- 新增公开能力：仅 `knowledge source list` CLI alias。
- 未新增 MCP tool。
- 未新增 HTTP route。
- 未开放 `knowledge source import/remove`。
- 未开放 `knowledge build/distill/graph/trace`。
- `data_service` CLI 顶层命令集合保持不变。

## 下一步

PhaseG21 建议评估 `knowledge build status` 只读 alias，或继续固化 source 写入迁移窗口；仍按最小能力组单独设计、单独验收。
