# V2.16 Phase 76 开发计划：Provider Capability Registry

## 1. 阶段定位

Phase 76 是 V2.16 的第一个实现阶段，目标是建立 Coding Agent 能力供应商注册表，让系统能够稳定回答：

- 当前有哪些语义分析、运行验证、报告生成、patch sandbox 相关 provider。
- 哪些 provider 是 mandatory baseline。
- 哪些 provider 只是 known / configured，但没有 execution adapter。
- 哪些 provider 可以真实执行。
- provider 不可用时应该返回什么结构化 blocker，而不是静默降级或伪造成功。

本阶段不实现 tree-sitter、Jedi、LSP、真实 patch apply、完整调用图、数据流、控制流或类型推断。

## 2. 输入基线

- V2.11-V2.15 Coding Agent artifacts：actionability、patch plan、runtime registry、incremental diff、workbench。
- V2.16 总 PRD、目标架构、artifact schema、验收计划。
- 真实 data_service 代码仓与现有测试夹具。

## 3. 开发范围

1. 新增 Provider Capability Registry artifact。
2. 输出 provider capability matrix。
3. 输出 provider decision records。
4. 明确 AST provider 为 mandatory and execution supported。
5. 明确 tree-sitter / Jedi / LSP 为 optional unavailable unless configured。
6. 明确 runtime profile、workbench renderer、patch preview sandbox 的当前 provider 状态。
7. HTTP / MCP / CLI 增加 provider registry build/read 能力。
8. 公共 payload 不泄露绝对路径、secret、raw traceback。

## 4. Artifact 设计

存储根：

```text
workspace/assets/codebase/{codebase_id}/coding_agent/v2_16/providers/
```

核心文件：

```text
capability_registry.json
decision_records.jsonl
```

最小字段：

```json
{
  "schema_version": "v2.16",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "summary": {
    "provider_count": 0,
    "mandatory_count": 0,
    "execution_supported_count": 0,
    "available_count": 0,
    "unavailable_count": 0,
    "unsupported_count": 0
  },
  "providers": [],
  "decision_records": [],
  "warnings": [],
  "unresolved": [],
  "artifact_refs": []
}
```

## 5. 接口计划

HTTP：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/providers/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/providers
```

MCP：

```text
knowledge_code_provider_registry_build
knowledge_code_provider_registry_read
```

CLI：

```text
knowledge code coding-agent providers-build
knowledge code coding-agent providers
```

## 6. 架构约束

- 不修改 `backend/app/api/v1/data_service.py`。
- 不把 provider 实现塞进 route handler。
- 不写入 source registry。
- 不改写 V2.0-V2.15 artifacts。
- optional provider 不可用必须输出 structured unavailable / unsupported，而不是假成功。

## 7. 出门条件

- provider registry artifact 落盘并可读回。
- AST provider 为 mandatory available。
- tree-sitter / Jedi / LSP 在未配置时为 optional unavailable / unsupported。
- HTTP / MCP / CLI 输出关键字段一致。
- 真实 data_service 夹具通过 E2E。
- V2.11-V2.15 focused regression 不退化。
- 无 fatal / major PRD 偏移。
