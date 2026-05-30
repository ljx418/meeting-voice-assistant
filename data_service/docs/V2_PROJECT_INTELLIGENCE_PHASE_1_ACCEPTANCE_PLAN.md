# V2 Phase 1 Acceptance Plan: Codebase Registry + Artifact Foundation

## Summary

Phase 1 验收必须使用当前真实 repo 路径，不允许只用 mock 或纯 unit test 替代。验收 artifacts 写入临时 workspace，不得写回当前 repo。

## Real Data Scope

真实 codebase path：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

验收 workspace root：

```text
/private/tmp/data_service_v2_phase1_workspace
```

## Required E2E Checks

### HTTP E2E

- 创建临时 workspace。
- `POST /api/workspaces/{workspace_id}/codebases` 导入当前 repo。
- 验证返回 `status=ok`, `codebase_id`, `artifact_refs`。
- 验证 `workspace/assets/codebase/{codebase_id}/codebase.json` 存在。
- 再次导入同一路径，返回同一 `codebase_id`。
- 归档后 list/describe 显示 `archived`。

### MCP E2E

- 通过 `MCPToolDispatcher.call_tool("knowledge_codebase_import", ...)` 导入当前 repo。
- 验证 envelope 与 HTTP 关键字段一致。
- 验证 archived workspace 返回 blocked。

### CLI E2E

- 执行 `knowledge code import --workspace-id ... --path ...`。
- 验证 stdout 是 JSON。
- 验证导入结果与 artifact 一致。

### Failure Paths

- 非 allowed root 路径返回 `PATH_NOT_ALLOWED`。
- 冲突 `codebase_id` 返回 `CODEBASE_ID_CONFLICT`。
- 不存在路径返回 blocked/failed，并包含明确 error code。
- archived workspace 禁止 import。

### Non-regression

- V1 source registry 不受影响。
- `lifecycle/sources.json` 不因 codebase import 变化。
- 现有 source/MCP smoke tests 不破坏。

## Acceptance Commands

```bash
cd backend
python -m pytest tests/test_v2_codebase_registry.py tests/test_v2_codebase_http.py tests/test_v2_codebase_mcp.py tests/test_v2_codebase_cli.py
python -m pytest tests/test_data_service_mcp.py tests/test_target_http_source.py
```

如果现有 unrelated dirty tests 影响结果，必须在验收报告中标注，不得把失败忽略为通过。

