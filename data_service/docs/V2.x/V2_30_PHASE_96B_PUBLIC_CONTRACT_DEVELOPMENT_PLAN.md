# V2.30 Phase 96B 开发计划：Architecture Intent 公共合同补齐

阶段：V2.30 / Phase 96B
范围：补齐 V2.25-V2.30 architecture intent artifacts 的 HTTP / MCP / CLI 调用入口。
状态：进入实现前基线。

## 1. 目标

Phase 91-96 已完成 architecture source model、diagram claims、proof graph、intent inference、diagram-code verification、report、context pack、governance overlay 的 artifact/readback 链路，但公共合同仍标记为 `not_implemented`。

本阶段目标是把这些能力暴露为稳定的 Agent 可调用入口：

- HTTP：build/read/confirm/revoke。
- MCP：同等能力的 tool specs 与 handler。
- CLI：同等能力的 JSON 输出命令。
- 三端输出保持 schema_version、workspace_id、codebase_id、snapshot_id、artifact_refs、counts、warnings、unresolved 的语义一致。

## 2. 不做什么

- 不修改 Phase 91-96 的 artifact 语义。
- 不把 architecture intent 逻辑塞入 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。
- 不声称从代码自动恢复完整人类设计意图。
- 不把 `token_overlap_only`、文档标签或 drawio 节点当作 accepted code evidence。
- 不把 HTTP-only 验收冒充三端验收。

## 3. 设计

新增 focused service：

```text
backend/data_service/code_assets/architecture_intent/service.py
```

职责：

- 复用 Phase 91-96 builder/readback 函数。
- 封装 build pipeline：
  source model -> diagram claims -> proof graph -> intent inference -> diagram verification -> context pack v4 -> report。
- 提供 public payload helper，统一 HTTP/MCP/CLI 输出。
- 对 governance confirm/revoke 提供薄封装。

新增 HTTP router：

```text
backend/app/api/v1/code_assets_architecture_intent.py
```

新增 MCP module：

```text
backend/data_service/mcp_code_architecture_intent_tools.py
```

新增 CLI module：

```text
backend/data_service/cli_code_architecture_intent.py
```

允许修改：

- `backend/app/api/__init__.py`：只做 router include。
- `backend/data_service/mcp_code_tools.py`：只做 tool specs 聚合与 delegation。
- `backend/data_service/cli_code.py`：只做 parser 挂载与 dispatch。

## 4. 目标接口

HTTP：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/report
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/context-pack
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/verification
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/proof-graph
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/confirm
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/revoke
```

MCP：

```text
knowledge_architecture_intent_build
knowledge_architecture_intent_report
knowledge_architecture_context_pack_v4
knowledge_diagram_code_verification
knowledge_architecture_proof_graph
knowledge_architecture_intent_confirm
knowledge_architecture_intent_revoke
```

CLI：

```text
knowledge code architecture-intent build
knowledge code architecture-intent report
knowledge code architecture-intent context-pack
knowledge code architecture-intent verification
knowledge code architecture-intent proof-graph
knowledge code architecture-intent confirm
knowledge code architecture-intent revoke
```

## 5. 验收输入

必须使用真实仓库：

- `/Users/Zhuanz/Desktop/workspace/data_service`
- `/Users/Zhuanz/Desktop/workspace/harnessOS`

如果 HarnessOS 路径不可读，必须记录为 structured blocker，不能用 mock 替代。

## 6. 出门条件

- 三端可 build/read architecture intent report。
- 三端稳定字段一致。
- confirm/revoke 为 read-time overlay，不改写 Phase 91-95 source artifacts。
- public payload 不泄露绝对路径、secret、traceback。
- focused tests、V2.25-30 regression、backend full tests 通过或记录环境性阻塞。
