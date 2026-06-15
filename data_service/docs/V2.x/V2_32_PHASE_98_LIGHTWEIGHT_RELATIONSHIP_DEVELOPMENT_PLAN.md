# V2.32 Phase 98 开发计划：Lightweight Relationship Graph

阶段：V2.32 / Phase 98
前置阶段：Phase 97 Task-Aware Navigation Index accepted
目标：为 Coding Agent 构建轻量、可追踪、语义克制的关系层，用于后续影响分析、测试选择、阅读包和 Agent handoff。

## 1. 阶段目标

Phase 98 只生成浅层关系：

- `surface_handled_by`
- `handler_dispatch`
- `registry_declared`
- `config_declared`
- `module_imports_module`
- `symbol_references_symbol`
- `test_references_symbol`
- `capability_related_to_surface`
- `method_call_candidate`
- `direct_call_ast`
- `heuristic_related`
- `dynamic_unresolved`

阶段不做：

- full call graph
- data flow
- control flow
- runtime topology
- type inference
- production runtime trace

## 2. 输入

读取已验收 artifacts：

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/files.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/surfaces.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/symbols.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/imports.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/evidence.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/mappings.jsonl
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/navigation_index.json
```

缺失必需输入时返回 structured blocker，不允许空成功。

## 3. 输出

```text
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/relationship_graph.json
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/relationships.jsonl
workspace/assets/codebase/{codebase_id}/coding_agent/task_navigation/relationship_blockers.jsonl
```

每条 relationship 必须包含：

- stable `relationship_id`
- `relationship_type`
- source_ref / target_ref
- `confidence`
- `semantic_limit`
- `truth_status`
- `evidence_refs`
- repo-relative `line_range` 或 structured blocker
- `needs_review`

## 4. 实现设计

新增 focused modules：

```text
backend/data_service/code_assets/coding_agent_navigation/
  relationship_graph.py
  relationship_persistence.py
```

继续复用：

```text
backend/data_service/code_assets/coding_agent_navigation/service.py
```

最小挂载：

- HTTP：`code_assets_coding_agent.py`
- MCP：`mcp_code_coding_agent_tools.py`
- CLI：`cli_code_coding_agent.py`

禁止修改：

- `backend/app/api/v1/data_service.py`
- `backend/data_service/service.py`

## 5. 关系构建策略

### 5.1 确定性关系

- surface + mapping/symbol：`surface_handled_by`
- MCP/CLI/HTTP registry 声明：`registry_declared`
- imports artifact：`module_imports_module`
- test 文件名 / import / symbol text reference：`test_references_symbol`
- capability 字段与 surface：`capability_related_to_surface`

### 5.2 AST 直连候选

仅对 Python AST 做有限检测：

- function body 中直接调用已知函数名，输出 `direct_call_ast`。
- 方法名或属性调用无法确定目标时输出 `method_call_candidate` 或 `dynamic_unresolved`。
- 必须标注 `semantic_limit = direct_syntax` 或 `heuristic_only`。

### 5.3 动态不可解析

对以下情况输出 blocker：

- dynamic dispatch
- reflection / getattr
- plugin registry 未能解析到 handler
- generated runtime route
- external framework magic

## 6. 公共接口

```text
HTTP:
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships

MCP:
knowledge_code_task_relationships_build
knowledge_code_task_relationships_read

CLI:
knowledge code coding-agent relationships-build
knowledge code coding-agent relationships
```

## 7. 风险控制

| 风险 | 处理 |
| --- | --- |
| import dependency 被写成 runtime call | `module_imports_module` 必须标 `static_reference` |
| token overlap 伪造关系 | token-only 只能 `heuristic_related` + `needs_review` |
| AST 无法解析动态调用 | `dynamic_unresolved` blocker |
| HarnessOS 项目特化 | extractor 必须按通用 pattern 工作 |
| public path leak | 输出 repo-relative path |

## 8. 完成定义

Phase 98 完成需满足：

- artifacts 落盘并可回读。
- forbidden relationship count = 0。
- data_service 至少有 accepted relationships。
- HarnessOS 有 accepted relationships 或 structured blockers。
- HTTP/MCP/CLI 三端读取一致。
- PRD/spec/false-green audit 无 open fatal/major。
