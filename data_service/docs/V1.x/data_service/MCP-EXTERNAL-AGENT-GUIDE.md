# Local Knowledge Governance Service MCP 外部 Agent 调用说明

更新时间：2026-05-07

## 目的

本文面向外部 Agent / Harness 工程，说明如何通过当前项目提供的 `data_service.mcp_stdio` MCP server 创建、构建、查询和治理一个本地知识 workspace。

`data_service` 是当前兼容包名和实现承载层；项目定位是独立的 MCP-first Local Knowledge Governance Service。

外部 Agent 不需要理解本项目内部的 `workspace/row / llmwiki / graphrag / quality` 目录结构，也不应直接写这些产物目录。所有操作应通过 MCP tools 完成。

## 启动方式

MCP server 入口：

```bash
cd /Users/Zhuanz/Desktop/workspace/data_service/backend
python3 -m data_service.mcp_stdio
```

运行前依赖：

- 推荐使用已安装 `backend/requirements.txt` 的 data_service venv。
- 真实 build 会触发 LLMWiki / GraphRAG 依赖；如果 venv 缺少 GraphRAG 相关依赖，MCP 链路可能在 `knowledge_build_start -> knowledge_build_status` 阶段失败。
- 外部 Agent 应优先保持同一 MCP stdio session 存活，直到 build operation 进入终态；operation state 会落盘，server 重启或 worker 中断后的遗留 running operation 会按 `failed / retryable / server_interrupted` 语义暴露给调用方。

推荐环境变量：

```bash
export DATA_SERVICE_WORKSPACE_ROOT=/path/to/managed/workspaces
export DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS=/path/to/managed
export DATA_SERVICE_ALLOWED_SOURCE_ROOTS=/path/to/source/files
```

说明：

- `DATA_SERVICE_WORKSPACE_ROOT`：外部 Agent 创建 workspace 的根目录。
- `DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS`：允许访问的 workspace 根目录 allowlist。
- `DATA_SERVICE_ALLOWED_SOURCE_ROOTS`：允许导入 source 文件的根目录 allowlist。
- 所有路径都会做 realpath 校验，symlink escape 会被拒绝。

## 统一 Envelope

lifecycle tools 和 v2 tools 返回统一 JSON envelope：

```json
{
  "workspace_id": "string",
  "operation_id": "string|null",
  "status": "ok|queued|running|completed|failed|cancelled|blocked",
  "warnings": [],
  "artifact_refs": [],
  "next_actions": [],
  "data": {}
}
```

状态语义：

- `ok`：同步操作成功。
- `queued`：build 已排队。
- `running`：build 正在执行。
- `completed`：operation 已完成。
- `failed`：operation 失败，查看 `data.error`。
- `cancelled`：operation 已取消。
- `blocked`：业务可预期失败，例如路径越权、归档 workspace 写入、未知 source/operation。

未知 tool、严重 schema 错误仍可能由 MCP 协议层返回 error；业务级错误优先返回 `blocked` envelope。

## 推荐调用链路

外部 Agent 推荐使用以下顺序：

1. `knowledge_workspace_create`
2. `knowledge_source_import`
3. `knowledge_build_start`
4. `knowledge_build_status`
5. `knowledge_query_v2`
6. `knowledge_quality_feedback_v2`
7. `knowledge_correction_rules_v2`
8. `knowledge_review_correction_rule_v2`
9. `knowledge_correction_plan_v2`
10. `knowledge_workspace_archive`

## Lifecycle Tools

### `knowledge_workspace_create`

创建或幂等注册一个 workspace。

Input：

```json
{
  "name": "Project Knowledge",
  "root": null,
  "owner": "harness",
  "tags": ["demo"]
}
```

Output `data`：

```json
{
  "workspace_path": "...",
  "capabilities": {
    "ingest": true,
    "query": true,
    "quality_feedback": true,
    "build": true
  }
}
```

说明：

- `workspace_id` 由 `name` slug 派生。
- 同名 workspace 幂等复用。
- 外部 Agent 后续优先使用 `workspace_id`，避免直接依赖本地路径。

### `knowledge_workspace_list`

列出 `DATA_SERVICE_WORKSPACE_ROOT` 下的 workspace。

Input：

```json
{
  "owner": "harness",
  "tag": "demo",
  "limit": 50
}
```

### `knowledge_workspace_describe`

读取 workspace 状态、layout、summary、engine status、latest build 和 quality 状态。

Input：

```json
{
  "workspace_id": "project-knowledge"
}
```

### `knowledge_workspace_archive`

归档 workspace，不物理删除数据。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "reason": "acceptance done"
}
```

归档后：

- describe/query 等读操作仍可用。
- import/remove/build/review/feedback 等写类操作返回 `blocked`。

### `knowledge_source_import`

把外部文件或文本导入受控 source area。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "paths": ["/path/to/source.md"],
  "texts": [
    {
      "title": "Harness Note",
      "content": "# Harness Note\n\nKnowledge content.",
      "metadata": {"kind": "fixture"}
    }
  ],
  "metadata": {"owner": "harness"}
}
```

Output `data.sources[]`：

```json
{
  "source_id": "src_xxx",
  "sha256": "string",
  "title": "string",
  "status": "imported|duplicate",
  "path": "string|null"
}
```

说明：

- 文件路径必须在 `DATA_SERVICE_ALLOWED_SOURCE_ROOTS` 内。
- 重复内容按 `sha256` 幂等处理，不创建重复 source record。
- 不直接写入 generated LLMWiki / GraphRAG 产物目录。

### `knowledge_source_list`

列出 workspace source。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "status": "active",
  "limit": 100
}
```

### `knowledge_source_remove`

软删除 source，不删除历史 build artifacts。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "source_id": "src_xxx",
  "reason": "obsolete"
}
```

### `knowledge_build_start`

启动非阻塞 build operation。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "mode": "full"
}
```

可选 `mode`：

- `full`
- `incremental`
- `graph_only`
- `llmwiki_only`

说明：

- tool 会立即返回 `operation_id`。
- 同一 workspace 的 build 串行排队，不并发写产物目录。
- 外部 Agent 应使用 `knowledge_build_status` 轮询。

### `knowledge_build_status`

轮询 build operation。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "operation_id": "op_xxx"
}
```

Output `data`：

```json
{
  "mode": "full",
  "stage": "queued|source_import|distill|llmwiki|graphrag|quality_plan|completed|failed|cancelled",
  "progress": 0.0,
  "error": null,
  "retryable": true,
  "artifacts": []
}
```

说明：

- 如果 MCP server 中断时有 running operation，后续会标记为 `failed`，并返回 `retryable=true` 与 `error.type=server_interrupted`。
- unknown operation 返回 `blocked`。

### `knowledge_build_cancel`

取消 queued/running build。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "operation_id": "op_xxx",
  "reason": "no longer needed"
}
```

说明：

- queued operation 可立即取消。
- running operation 在阶段边界响应 cancel。
- completed operation 会返回当前终态并附带 warning。

## V2 Envelope Tools

外部 Agent 推荐使用 v2 tools，因为它们统一返回 envelope。

### `knowledge_query_v2`

查询知识库。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "query": "要查询的问题",
  "mode": "hybrid",
  "top_k": 8
}
```

可选 `mode`：

- `llmwiki`：阅读型、页面型问题优先。
- `graphrag`：关系型、实体网络型问题优先。
- `hybrid`：默认混合模式。

Output：

- envelope 的 `data` 是旧 `knowledge_query` payload。
- `data.hits[]` 包含命中标题、snippet、source、score、meta。
- `data.engine_payloads` 包含底层引擎 payload。

### `knowledge_quality_summary_v2`

读取质量状态、近期 feedback、correction rules、approved correction plan。

Input：

```json
{
  "workspace_id": "project-knowledge"
}
```

### `knowledge_quality_feedback_v2`

提交受控质量反馈。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "target_type": "entity|source|page|query|community",
  "target_id": "target-id",
  "action": "needs_review|rename_suggest|merge_suggest|mark_noise|confirm_good|note",
  "label": "optional label",
  "suggested_value": "optional canonical value",
  "reason": "why this feedback is needed",
  "metadata": {}
}
```

说明：

- feedback 写入 workspace quality 层。
- 不改写原始 source。
- 对 archived workspace 返回 `blocked`。

### `knowledge_correction_rules_v2`

列出质量校正规则。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "status": "draft",
  "limit": 100
}
```

可选 `status`：

- `draft`
- `approved`
- `rejected`
- `archived`
- `revoked`

### `knowledge_review_correction_rule_v2`

审核一条 correction rule。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "rule_id": "rule_xxx",
  "status": "approved",
  "reviewer": "agent",
  "note": "review note"
}
```

### `knowledge_correction_plan_v2`

读取或显式重建 approved correction plan。

Input：

```json
{
  "workspace_id": "project-knowledge",
  "rebuild": false
}
```

说明：

- `rebuild=false` 时只读，不隐式写 workspace。
- 需要重建时显式传 `rebuild=true`。

## 兼容 Tools

以下旧 tools 仍保留，响应格式不强制 envelope：

- `knowledge_ingest`
- `knowledge_query`
- `knowledge_quality_summary`
- `knowledge_correction_plan`
- `knowledge_quality_feedback`
- `knowledge_correction_rules`
- `knowledge_review_correction_rule`

外部 Agent 新接入时应优先使用 lifecycle tools + v2 tools。

## 安全规则

- 每次 MCP call 独立校验 workspace，不依赖上一次调用的隐式上下文。
- workspace 必须在 allowed roots 内。
- source path 必须在 allowed source roots 内。
- symlink escape、path traversal、超大文件、超大 text payload 会被拒绝。
- correction plan 默认读时治理，不自动改写原始 source。
- LLMWiki markdown 默认不通过 MCP 落盘改写。

## 外部 Agent 最小伪代码

```text
create = call("knowledge_workspace_create", {name: "Project Knowledge"})
workspace_id = create.workspace_id

call("knowledge_source_import", {
  workspace_id,
  texts: [{title: "Note", content: "# Note\n\nContent"}]
})

build = call("knowledge_build_start", {workspace_id, mode: "full"})
operation_id = build.operation_id

repeat:
  status = call("knowledge_build_status", {workspace_id, operation_id})
  if status.status in ["completed", "failed", "blocked", "cancelled"]:
    break

query = call("knowledge_query_v2", {
  workspace_id,
  query: "Content",
  mode: "hybrid",
  top_k: 8
})

feedback = call("knowledge_quality_feedback_v2", {
  workspace_id,
  target_type: "query",
  target_id: "Content",
  action: "note",
  reason: "acceptance feedback"
})

rules = call("knowledge_correction_rules_v2", {workspace_id, status: "draft"})
plan = call("knowledge_correction_plan_v2", {workspace_id, rebuild: false})
call("knowledge_workspace_archive", {workspace_id, reason: "done"})
```

## 当前验证基线

最近验证：

- `python3.12 -m pytest backend/tests/test_data_service_mcp.py -q`：`14 passed`
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：`74 passed, 14 skipped`
- `python3 -m pytest backend/tests/test_llmwiki.py -q`：`34 passed`

外部 HarnessOS 真实验收：

- 链路：`knowledge_workspace_create -> knowledge_source_import -> knowledge_build_start -> knowledge_build_status -> knowledge_query_v2 -> knowledge_quality_feedback_v2 -> knowledge_correction_rules_v2 -> knowledge_review_correction_rule_v2 -> knowledge_correction_plan_v2 -> knowledge_workspace_archive`
- `workspace_id`: `harnessosrealdataserviceacceptance4`
- `operation_id`: `op_fb639a7aee3c`
- final `status`: `ok`
- `warnings`: `[]`
- HarnessOS fake MCP workflow：`1 passed`
- Pack/connector fake MCP：`14 passed`
- gateway/stdio 相关：`4 passed`
