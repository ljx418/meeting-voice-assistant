# V2.16 Phase 77 开发计划：Semantic Provider Orchestrator

## 1. 阶段定位

Phase 77 在 Phase 76 provider registry 之上，建立语义 provider 编排层。它的目标不是完整静态分析，而是把已有 AST baseline facts 和 provider provenance 组织成 Coding Agent 可消费的语义事实。

## 2. In Scope

- AST provider 作为 mandatory baseline。
- 从 V2.11 Actionability definitions / references 生成 provider facts。
- 每条 fact 带 provider、extractor、confidence、evidence。
- optional providers 不可用时输出 structured blocker。
- 生成 merged semantic index 和 provider conflict artifact。
- HTTP / MCP / CLI build/read。

## 3. Out of Scope

- 完整调用图。
- 数据流、控制流、类型推断。
- LSP 实时服务。
- tree-sitter / Jedi / LSP 的真实 adapter。
- runtime execution。

## 4. Artifact

```text
workspace/assets/codebase/{codebase_id}/coding_agent/v2_16/semantic/
  provider_facts.jsonl
  merged_semantic_index.json
  provider_conflicts.jsonl
```

## 5. 接口

HTTP：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/semantic/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/semantic
```

MCP：

```text
knowledge_code_semantic_providers_build
knowledge_code_semantic_providers_read
```

CLI：

```text
knowledge code coding-agent semantic-build
knowledge code coding-agent semantic
```

## 6. 出门条件

- AST provider facts 非空。
- optional provider blocker 非空或明确 configured unavailable。
- merged index 可读回。
- provider conflicts artifact 落盘，即使为空。
- 无 forbidden relation claim。
- HTTP / MCP / CLI parity 通过。
