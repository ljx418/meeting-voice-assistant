# V2.19 Phase 85 Artifact Schema & Public Contract Development Plan

## 1. 阶段目标

Phase 85 的目标是把 V2.0-V2.18 已有 project-intelligence artifacts 收敛成可审计的 artifact contract registry，并生成 validation report。它不重建上游事实、不修复 artifact 内容，只报告 schema、JSON/JSONL、schema_version、artifact_refs 和三端 stable fields 风险。

## 2. 输入

- 已登记 codebase asset。
- snapshot / inventory / symbols / trace / overview / context / architecture / coding-agent / platform artifacts。
- V2.18 Product Console artifact。
- 当前 MCP tool registry、HTTP routes、CLI commands。

## 3. 输出

```text
workspace/assets/codebase/{codebase_id}/platform/contracts/artifact_contract_registry.json
workspace/assets/codebase/{codebase_id}/platform/contracts/validation_report.json
```

## 4. 设计

新增模块：

```text
backend/data_service/code_assets/platform/contracts.py
```

复用模块：

```text
backend/data_service/code_assets/platform/persistence.py
backend/data_service/mcp_code_platform_tools.py
backend/data_service/cli_code_platform.py
backend/app/api/v1/code_assets_platform.py
```

新增接口：

```text
HTTP:
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/contracts/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/contracts

MCP:
knowledge_code_platform_contracts_build
knowledge_code_platform_contracts_read

CLI:
knowledge code platform contracts-build
knowledge code platform contracts
```

## 5. 实现任务

1. Artifact family discovery：扫描 codebase artifact root 下已知 `.json` / `.jsonl` 文件。
2. Schema registry：按 artifact path/family 记录 `artifact_family`、`format`、`schema_version_present`、`status`。
3. Validator runner：验证 JSON/JSONL 格式和 required metadata。
4. Ref integrity checker：检查 `artifact_refs` 是否是结构化列表，缺失则进入 warning/unresolved。
5. Public contract reader：三端统一读取 registry/report，返回 V2 envelope。

## 6. 非目标

- 不自动修复 artifact。
- 不推断 artifact 中不存在的事实。
- 不要求历史遗留 artifact 全部通过；可标记 partial / missing_schema_version / invalid_json。
- 不阻塞 V2.19 通过，只要 validator 能真实报告风险并保护新增 platform artifacts。

## 7. 开发边界

- 业务逻辑必须放在 `code_assets/platform/`。
- 旧 HTTP/MCP/CLI 文件只做薄注册和转发。
- 不修改 source registry。
- 不改写 V2.0-V2.18 既有 artifacts。
