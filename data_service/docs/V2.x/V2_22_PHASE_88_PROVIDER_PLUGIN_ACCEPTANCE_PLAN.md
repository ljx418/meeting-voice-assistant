# V2.22 Phase 88 Provider Plugin System Acceptance Plan

## 1. 验收结论规则

Phase 88 只有在以下条件全部满足时才能 accepted：

- AST provider must be ready and execution-supported。
- optional provider unavailable / unsupported must not be accepted。
- provider capability artifact and execution contract artifact must persist to disk and read back。
- HTTP/MCP/CLI stable fields must match。
- real `data_service` repo E2E must pass。
- public payload must not expose local paths, secrets, endpoints, or raw tracebacks。
- full regression must pass。

## 2. Focused Tests

必须新增并通过：

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_22_provider_plugins.py -q
```

测试点：

1. `semantic:python_ast` is mandatory, configured, execution-supported, and ready。
2. `semantic:tree_sitter` / `semantic:jedi` / `semantic:lsp` are not accepted unless execution-supported。
3. `health_known` does not imply `execution_supported`。
4. Execution contract includes stable error codes。
5. Public payload redaction。

## 3. 三端契约验收

HTTP/MCP/CLI 必须一致：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `provider_count`
- `ready_count`
- `optional_unavailable_count`
- `unsupported_count`
- `artifact_refs` count
- `warnings` count
- `unresolved` count

## 4. 真实仓库 E2E

真实输入：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

E2E 流程：

1. 导入当前 repo。
2. 生成 snapshot。
3. build platform provider artifacts。
4. read back provider capabilities and execution contract。
5. assert AST accepted baseline。
6. assert optional providers are unavailable/unsupported unless configured and adapter-supported。
7. redaction scan。

## 5. 回归验收

必须执行：

```bash
npm run build
PYTHONPATH=backend python3 -m pytest backend/tests -q
git diff --check -- .
```

## 6. False-Green Rejection

以下情况必须判定失败：

- optional provider package importable but no adapter, yet marked accepted。
- health-known provider counted as execution-ready。
- AST provider missing or not ready。
- provider-disabled path counted as provider-backed success。
- public payload leaks secret/path/traceback。
- mock-only data used as final acceptance。
