# V2.22 Phase 88 Provider Plugin System Development Plan

## 1. 阶段目标

Phase 88 目标是把已有 V2.16 provider registry 能力产品化为平台层 Provider Plugin System：

- 固定 provider capability / execution contract。
- 明确 `health_known != execution_supported`。
- AST provider 是 mandatory baseline。
- tree-sitter / Jedi / LSP 是 optional provider，未配置或无 adapter 时必须 structured unavailable / unsupported。
- 输出平台层 provider capability 与 execution contract artifacts。

## 2. 输入

- Existing V2.16 `ProviderCapabilityRegistryService`。
- Codebase snapshot。
- Current provider availability。
- Existing semantic provider facts。

## 3. 输出

```text
platform/providers/provider_capabilities.json
platform/providers/provider_execution_contract.json
```

## 4. 实现任务

1. 新增 `backend/data_service/code_assets/platform/providers.py`。
2. 复用 V2.16 provider registry，生成平台层 provider capability artifact。
3. 输出 execution contract：
   - ProviderExecutionRequest
   - ProviderExecutionResult
   - ProviderError
   - health/config/execution separation。
4. 新增 HTTP/MCP/CLI：
   - provider build
   - provider read
5. 补测试：
   - AST mandatory ready。
   - optional providers unavailable/unsupported 不得 accepted。
   - health-known provider without adapter returns unsupported。
   - public payload no path/secret。

## 5. Public Contract

HTTP:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/providers/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/providers
```

MCP:

```text
knowledge_code_platform_providers_build
knowledge_code_platform_providers_read
```

CLI:

```text
knowledge code platform providers-build
knowledge code platform providers
```

## 6. Non-goals

- 不新增 tree-sitter/Jedi/LSP 的真实执行 adapter。
- 不调用外部 LLM provider。
- 不把 package importable 误写成 execution accepted。
- 不输出 secret、endpoint、raw traceback。

## 7. 架构边界

- Provider 产品化逻辑放在 `code_assets/platform/providers.py`。
- V2.16 provider registry 继续作为底层事实源。
- 不修改 ResearchNotebook provider contract。
- 不修改 legacy large service/router 文件。
