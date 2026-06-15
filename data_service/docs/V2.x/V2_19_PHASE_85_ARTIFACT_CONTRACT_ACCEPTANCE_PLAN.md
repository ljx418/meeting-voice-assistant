# V2.19 Phase 85 Artifact Schema & Public Contract Acceptance Plan

## 1. 验收结论要求

Phase 85 只有在以下条件满足时才能通过：

- Contract registry 和 validation report 均落盘。
- 至少覆盖当前 codebase artifact root 下的主要 `.json` / `.jsonl` artifacts。
- Product Console artifacts 必须通过 schema_version / JSON / artifact_refs 检查。
- 历史 artifact 若缺 schema_version，不得伪装通过，必须进入 findings。
- HTTP/MCP/CLI 三端读取的 stable fields 一致。
- 真实 data_service 仓库 E2E 通过。

## 2. 自动化测试

新增测试：

```text
backend/tests/test_v2_19_artifact_contracts.py
```

必须覆盖：

- service build/read。
- invalid JSON fixture fails。
- invalid JSONL row fails。
- missing schema_version reported。
- platform_console artifact accepted。
- HTTP/MCP/CLI parity。
- public output 不泄露 repo/workspace 绝对路径。

## 3. 真实数据 E2E

真实输入：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

步骤：

1. 临时 workspace 导入 data_service。
2. 生成 snapshot。
3. 构建 V2.18 Product Console。
4. 构建 V2.19 contract registry。
5. 读取 validation report。
6. 检查 output 不含绝对路径。

通过标准：

- `artifact_contract_registry.json` 存在。
- `validation_report.json` 存在。
- `checked_count > 0`。
- `platform_console` family 状态为 `covered` 或 `passed`。
- 若存在历史缺陷，必须以 finding/unresolved 显示。

## 4. 回归测试命令

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_19_artifact_contracts.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_18_platform_console.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_public_surface_guard.py -q
cd frontend && npm run build
PYTHONPATH=backend python3 -m pytest backend/tests -q
git diff --check -- .
```

## 5. PRD/规格检视

对照：

- `V2_18_24_PLATFORM_PRODUCTIZATION_PRD.md`
- `V2_18_24_PLATFORM_PRODUCTIZATION_TARGET_ARCHITECTURE.md`
- `V2_18_24_PLATFORM_PRODUCTIZATION_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md`
- `V2_18_24_PLATFORM_PRODUCTIZATION_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md`

## 6. False-Green 拒绝项

以下情况必须拒绝验收：

- validator 自动修复 artifact 后算通过。
- skipped validation 算通过。
- 空 registry 算通过。
- invalid JSON/JSONL 未被发现。
- 缺 schema_version 被标记 accepted。
- artifact_refs 缺失但没有 warning/unresolved。
- HTTP 通过但 MCP/CLI 未测。
- public output 泄露本地绝对路径。
