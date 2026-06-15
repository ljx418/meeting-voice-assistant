# V2.21 Phase 87 Incremental Build & Large Repo Performance Acceptance Plan

## 1. 验收结论规则

Phase 87 只有在以下条件全部满足时才能 accepted：

- 使用真实 snapshot A/B 或真实文件变更 fixture 验收。
- `changed_files` 非空时相关 artifact 不得全部标记 `reuse`。
- 每个 cache decision 必须有 reason。
- HTTP/MCP/CLI 输出 stable fields 一致。
- artifact 落盘并可 readback。
- public payload 不泄露本机绝对路径、secret、raw traceback。
- 全量 regression 通过。

## 2. Focused Tests

必须新增并通过：

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_21_incremental_build.py -q
```

测试点：

1. 修改单个 fixture 文件后，Snapshot B 与 Snapshot A 不同。
2. build plan 能识别 changed file。
3. cache decisions 包含 `refresh` 或 `invalidate`，不能全部 `reuse`。
4. full rebuild reason 在需要时显式出现。
5. `incremental_build_plan.json`、`cache_decisions.jsonl`、`scan_profile.json` 落盘。
6. readback 与 build payload 稳定字段一致。

## 3. 三端契约验收

HTTP/MCP/CLI 必须一致：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `from_snapshot_id`
- `to_snapshot_id`
- `changed_file_count`
- `cache_decision_count`
- `artifact_refs` count
- `warnings` count
- `unresolved` count

## 4. 真实仓库 E2E

真实输入：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

E2E 流程：

1. 导入当前 repo 到临时 workspace。
2. 生成 Snapshot A。
3. 在临时 repo copy 中修改一个真实 tracked-like 文件。
4. 生成 Snapshot B。
5. 生成 incremental build plan。
6. 检查 changed file、cache decisions、scan budget、artifact refs。
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

- 只比较 snapshot_id，不比较 file manifest。
- changed file 未出现在 `changed_files`。
- changed file 存在但所有 artifacts 都标记 `reuse`。
- cache decision 缺少 reason。
- skipped/blocked 被写成 passed。
- 使用 mock-only 数据替代真实 repo E2E。
- 输出绝对路径。
- 破坏 V2.18-V2.20 平台功能。
