# V2.19 Phase 85 Artifact Schema & Public Contract Acceptance Audit Report

## 1. 审计结论

结论：通过。

Phase 85 已实现 artifact contract registry 与 validation report。服务可以扫描 codebase artifact root 下的 JSON / JSONL artifacts，报告格式合法性、schema_version、artifact_refs 和 validation findings，并通过 HTTP、MCP、CLI 三端读取。

## 2. 本阶段实现范围

新增能力：

- Artifact contract registry：`artifact_contract_registry.json`
- Validation report：`validation_report.json`
- JSON / JSONL validator。
- schema_version 检查。
- artifact_refs 结构检查。
- invalid JSON / invalid JSONL row / missing schema_version findings。
- 自身 contract 输出排除，避免重复 build 产生自引用抖动。

新增接口：

- HTTP:
  - `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/contracts/build`
  - `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/contracts`
- MCP:
  - `knowledge_code_platform_contracts_build`
  - `knowledge_code_platform_contracts_read`
- CLI:
  - `knowledge code platform contracts-build`
  - `knowledge code platform contracts`

新增/修改模块：

- `backend/data_service/code_assets/platform/contracts.py`
- `backend/data_service/code_assets/platform/persistence.py`
- `backend/app/api/v1/code_assets_platform.py`
- `backend/data_service/mcp_code_platform_tools.py`
- `backend/data_service/cli_code_platform.py`
- `backend/tests/test_v2_19_artifact_contracts.py`

## 3. 真实数据 E2E 验收

真实仓库输入：

- `/Users/Zhuanz/Desktop/workspace/data_service`

临时 workspace：

- `/private/tmp/data_service_v219_e2e/real_ws`

验收结果：

```text
workspace_id: data_service_v219_real_e2e
codebase_id: codebase_data_service_v219
snapshot_id: snap_25d18409bed7f1bdaedb
checked_count: 6
passed_count: 6
warning_count: 0
failed_count: 0
finding_count: 0
artifact_refs: 2
```

脱敏检查：

```text
rg "/Users/Zhuanz/Desktop/workspace/data_service|/private/tmp/data_service_v219_e2e" /private/tmp/data_service_v219_e2e/real_ws/assets/codebase/codebase_data_service_v219/platform/contracts
no matches
```

## 4. 自动化测试结果

已执行：

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_19_artifact_contracts.py -q
2 passed

PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_18_platform_console.py -q
2 passed

PYTHONPATH=backend python3 -m pytest backend/tests/test_public_surface_guard.py -q
5 passed

cd frontend && npm run build
passed

PYTHONPATH=backend python3 -m pytest backend/tests -q
460 passed

git diff --check -- .
passed
```

## 5. PRD 规格检视

对照 `V2_18_24_PLATFORM_PRODUCTIZATION_PRD.md` 和 V2.19 artifact schema 文档：

- Artifact family discovery：已实现。
- Schema registry：已实现。
- Validator runner：已实现。
- JSONL row validation：已实现，并有 invalid row 负向测试。
- schema_version missing finding：已实现，并有负向测试。
- artifact_refs integrity checker：已实现基础结构检查。
- HTTP/MCP/CLI read parity：已实现并测试。
- validator 只报告不修复：已遵守。

未进入本阶段范围：

- V2.20 MCP tool discovery。
- V2.21 incremental build/performance。
- V2.22 provider plugin system。
- V2.23 governance workflow。
- V2.24 production readiness closure。

## 6. False-Green 审计

拒绝项检查：

- 空 registry 算通过：未触发；focused 和真实 E2E 均要求 `checked_count > 0`。
- invalid JSONL 未被发现：未触发；负向 fixture 已捕获。
- missing schema_version 被标 accepted：未触发；负向 fixture 已捕获。
- 自身输出导致重复 build 抖动：已发现并修复；contract 输出被排除在扫描范围外。
- HTTP 通过但 MCP/CLI 未测：未触发；parity 测试覆盖三端。
- public output 泄露绝对路径：未触发；测试和真实 E2E grep 均通过。
- 旧大文件膨胀：未触发；主逻辑位于 `code_assets/platform/contracts.py`。

## 7. 审计意见

Phase 85 可视为完成并通过验收。

下一阶段进入前建议：

1. 为 V2.20 Phase 86 生成专项 development / acceptance / pre-implementation audit 文档。
2. Phase 86 的 MCP tool catalog 应消费当前 `all_tool_specs()`，并把 V2.18/V2.19 platform tools 纳入 catalog。
3. 继续把 “registry count == current tool registry count” 作为硬验收门槛。
