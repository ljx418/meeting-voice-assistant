# Knowledge Service Console Gap 文档

日期：2026-05-07

## 目标产品描述

目标不是普通用户个人知识库 App，而是 Local Knowledge Service Console：服务治理控制台。

控制台用于让开发者、运维者和上层应用集成者查看本地知识治理服务的状态：

- 当前 workspace / tenant 列表
- 每个 workspace 的 `workspace_id` 和绑定 `root_path`
- 递归扫描文件数量
- source registry
- 文件收录状态
- failed / unreadable / low-signal sources
- 最近 build operation 状态
- GraphRAG 图谱质量
- entity / relation / community 数量
- Source Trace
- Distill Units
- Wiki artifacts
- Quality Feedback
- Correction Rules 审核队列
- Correction Plan
- MCP / HTTP / CLI 调用状态

控制台不是会议、学习、面试或代码助手入口。那些上层应用通过 MCP / CLI / HTTP 调用本服务。

## 当前已具备能力

- MCP lifecycle tools
- HTTP workspace/source/build/query/graph/distill/trace/quality API
- CLI ingest/query/summary/distill/boundary/graphrag-execute
- workspace/source lifecycle
- build operation queue
- directory scan
- distill v1.1
- Source Trace
- LLMWiki artifacts
- GraphRAG snapshot/query
- quality feedback/rules/review/plan
- low-signal audit

## 主要 Gap

### Gap 1：控制台信息架构仍需服务治理化

目标一级导航：

- Overview
- Workspaces
- Sources
- Build Operations
- Distill Units
- Wiki Artifacts
- GraphRAG
- Trace Explorer
- Quality Governance
- MCP Debugger
- Settings

当前需要避免继续把 UI 组织成个人知识消费路径。

### Gap 2：Workspace / Tenant 总览

目标：

- `workspace_id` 是主标识。
- `root_path` 作为绑定路径展示。
- 展示 scan_state、build_state、archived、source_count、last_build。

### Gap 3：Source Registry 和扫描状态

目标：

- 递归扫描文件数量。
- new / modified / deleted / unreadable。
- pending / indexed / failed / disabled / low_signal。
- source_type：document、meeting_transcript、code_analysis_artifact、raw_text、structured_json。

### Gap 4：MCP Debugger

目标：

- 展示当前 MCP tool 分组。
- 展示输入输出 envelope 示例。
- 展示最近调用状态和 blocked/error 语义。

### Gap 5：Trace Explorer

目标：

```text
source
  -> normalized document
  -> distill units
  -> wiki pages
  -> graph entities / relations / communities
  -> retrieval hits
  -> quality impacts
```

### Gap 6：格式扩展状态

目标：

- 控制台展示当前支持格式和计划支持格式。
- 当前已支持 json/txt/md/html/csv/pdf/ppt/pptx。
- 下一阶段补 docx、yaml/yml。

## 验收口径

控制台达到以下能力后，才算进入服务治理产品化：

1. 不暴露内部 workspace 目录作为外部 contract。
2. 能以 `workspace_id` 管理租户。
3. 能看到每个 workspace 的 root_path、扫描状态、构建状态和 source 状态。
4. 能查看 distill、wiki、graph、trace、quality 的服务产物状态。
5. 能调试 MCP / HTTP / CLI 调用边界。
6. 不把会议、学习、面试、代码助手作为自身端到端业务流程。
