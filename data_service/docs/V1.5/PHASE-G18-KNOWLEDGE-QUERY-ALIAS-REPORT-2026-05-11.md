# PhaseG18 Knowledge Query Alias Report

日期：2026-05-11

## 范围

PhaseG18 只开放一个最小 `knowledge` alias 能力组：`knowledge query`。

本阶段不新增 MCP tool，不新增 HTTP route，不改变 query 响应字段集合。`data_service query` 继续作为兼容入口保留。

## 实现

- 抽出 `_add_query_parser`，让 `data_service query` 与 `knowledge query` 复用同一套 argparse 参数定义。
- `_build_knowledge_parser()` 顶层 choices 从 `{"quality"}` 扩展为 `{"quality", "query"}`。
- `knowledge query` 继续走 `_run_parsed_args()` 中的 query 分支，并复用 `run_query_contract`。
- 未开放 `knowledge workspace/source/build/distill/graph/trace`。

## Contract

目标命令：

```text
knowledge query PhaseG18 --workspace-id research-vault --mode hybrid --top-k 3
```

稳定响应字段：

```text
mode / query / answer / hits / engine_payloads
```

## 出门验证

- API 专项回归：`24 passed`
- MCP 专项回归：`30 passed`
- Data Service/API/MCP 组合回归：`125 passed`
- Frontend build：通过
- Draw.io XML：通过

## 对外能力检查

- 新增公开能力：仅 `knowledge query` CLI alias。
- 未新增 MCP tool。
- 未新增 HTTP route。
- 未改变 `knowledge_query` / `/api/v1/knowledge/query` / `data_service query` 响应字段集合。
- `knowledge` 顶层仍只允许 `quality` 与 `query`，避免隐式开放 workspace/source/build/distill/graph/trace。

## 下一步

PhaseG19 建议评估 `knowledge workspace` 只读 alias，或继续补充 `knowledge query` 的迁移窗口文档；仍按最小能力组单独设计、单独验收。
