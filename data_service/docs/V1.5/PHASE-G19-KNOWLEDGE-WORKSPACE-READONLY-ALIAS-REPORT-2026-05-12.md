# PhaseG19 Knowledge Workspace Read-Only Alias Report

日期：2026-05-12

## 范围

PhaseG19 只开放 `knowledge workspace` 的只读 alias：

- `knowledge workspace list`
- `knowledge workspace describe`

本阶段不新增 MCP tool，不新增 HTTP route，不开放 `knowledge workspace create/archive`。

## 实现

- 新增 `_add_workspace_lifecycle_parser`，只挂载到 `_build_knowledge_parser()`。
- `data_service` 兼容 CLI 顶层命令集合保持不变。
- `knowledge workspace list` 转调现有 `knowledge_workspace_list` handler。
- `knowledge workspace describe` 转调现有 `knowledge_workspace_describe` handler。
- 输出继续复用 MCP envelope 与 sanitizer，内部路径只进入 `debug_paths` / `artifact_refs[].debug_path`。

## Contract

目标命令：

```text
knowledge workspace list --workspace-root ./workspaces --owner harness --limit 50
knowledge workspace describe --workspace-root ./workspaces --workspace-id research-vault
knowledge workspace describe --workspace /absolute/path/to/workspace
```

稳定响应 envelope：

```text
workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data
```

## 出门验证

- API 专项回归：`25 passed`
- MCP 专项回归：`30 passed`
- Data Service/API/MCP 组合回归：`126 passed`
- Frontend build：通过
- Draw.io XML：通过

## 对外能力检查

- 新增公开能力：仅 `knowledge workspace list/describe` CLI alias。
- 未新增 MCP tool。
- 未新增 HTTP route。
- 未开放 `knowledge workspace create/archive`。
- 未开放 `knowledge source/build/distill/graph/trace`。
- `data_service` CLI 顶层命令集合保持不变。

## 下一步

PhaseG20 建议评估 `knowledge source list` 只读 alias，或继续固化 workspace 写入迁移窗口；仍按最小能力组单独设计、单独验收。
