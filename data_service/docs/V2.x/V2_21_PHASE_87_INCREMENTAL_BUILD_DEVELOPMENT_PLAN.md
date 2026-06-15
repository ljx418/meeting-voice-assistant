# V2.21 Phase 87 Incremental Build & Large Repo Performance Development Plan

## 1. 阶段目标

Phase 87 的目标是补齐平台产品化层的增量构建规划能力：基于两个已存在的 repo snapshot，生成可审计的 changed files、artifact cache decision、build impact plan 和 scan budget report。

本阶段不承诺真正执行选择性重建，也不替代已有 V2.14 `incremental_diff`。Phase 87 只把已有 snapshot diff 能力提升为平台层可读、可审计、可被后续 CI/console/Agent 消费的增量构建计划。

## 2. 输入

- Codebase asset。
- Snapshot A：`from_snapshot_id`。
- Snapshot B：`to_snapshot_id`。
- Snapshot files manifest。
- Existing artifact roots under `workspace/assets/codebase/{codebase_id}`。
- Existing V2.14 incremental diff service。

## 3. 输出

```text
platform/incremental/incremental_build_plan.json
platform/incremental/cache_decisions.jsonl
platform/incremental/scan_profile.json
```

## 4. 实现任务

1. 新增 `platform/incremental.py`。
2. 复用 `CodingAgentActionabilityService.build_incremental_diff` 读取 Snapshot A/B 差异。
3. 生成 artifact family dependency policy：
   - snapshot / inventory / symbols / trace / overview / context / devwiki / graph / architecture / coding-agent / platform。
4. 根据 changed file 类型输出 cache decisions：
   - `reuse`
   - `refresh`
   - `invalidate`
   - `full_rebuild_required`
5. 输出 scan budget：
   - file count
   - changed file count
   - changed LOC approximation
   - language distribution
   - budget status
6. 挂载 HTTP/MCP/CLI：
   - build
   - read
7. 补测试：
   - service-level changed-file detection。
   - HTTP/MCP/CLI parity。
   - no absolute path。
   - no silent unsafe reuse。

## 5. Public Contract

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/incremental/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/incremental
```

MCP:

```text
knowledge_code_platform_incremental_build
knowledge_code_platform_incremental_read
```

CLI:

```text
knowledge code platform incremental-build
knowledge code platform incremental
```

## 6. Non-goals

- 不执行真实选择性 rebuild。
- 不声称所有 artifact dependency 都是完整语义依赖。
- 不做 runtime call graph、data flow、control flow。
- 不在 changed file 存在时静默 reuse 相关 artifact。

## 7. 架构边界

- 新逻辑放在 `backend/data_service/code_assets/platform/incremental.py`。
- `backend/app/api/v1/code_assets_platform.py` 只做薄路由。
- `mcp_code_platform_tools.py` 只做工具分发。
- 不修改 `backend/app/api/v1/data_service.py`。
- 不修改 `backend/data_service/service.py`。
- 不污染 source registry。
