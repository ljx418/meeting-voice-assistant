# Local Knowledge Governance Service 执行路线图

更新时间：2026-05-07

## 目标

把当前 `data_service + llmwiki + graphrag + quality + MCP` 体系收敛为独立的 MCP-first 本地知识治理服务。

本服务对外提供数据查询、关系提取、知识库固化、图谱查询、Source Trace、质量治理和可检索上下文，不端到端实现会议、学习、面试、代码理解等应用。

## 总原则

### 原则 1：外部只依赖 MCP / CLI / HTTP

- 外部应用不得直接读写 workspace 内部文件。
- `workspace_id` 是稳定外部 ID。
- `root_path` 是绑定目录和控制台展示字段。

### 原则 2：不依赖上层应用模块

- 可以接收会议转写文本，但不 import meeting app 代码。
- 可以接收代码分析产物，但不承担 IDE、代码托管或大型静态分析器职责。
- 学习、面试、代码助手等上层应用只能传入数据或查询请求。

### 原则 3：先稳定数据契约，再升级算法和界面

顺序：

1. 稳定 workspace/source/build/query/quality contract。
2. 稳定 distill 和 graph schema。
3. 升级 typed distill units、格式解析和控制台。

## 架构阶段

### Phase 1：稳定双引擎工作流

状态：完成。

已完成 ingest、distill、LLMWiki、GraphRAG、summary 主链路。

### Phase 2：正式化中间层

状态：完成。

已完成 distill v1.1、manifest/schema/sources/units、source profile、profile_debug、low-signal 观测。

### Phase 3：GraphRAG 职责收口

状态：完成。

`app.graphrag` 已成为默认 graph execution owner。Graph snapshot/query 默认通过 `app.graphrag.service` bridge 返回。

### Phase 4：MCP / Agent 化收口

状态：完成并作为回归基线。

已完成：

- workspace/source/build lifecycle tools
- v2 envelope tools
- workspace 级 build queue
- blocked error contract
- external HarnessOS stdio MCP E2E

### Phase 5：Knowledge Governance Productization

状态：进行中。

已完成：

- `Phase 5.1` GraphRAG 图谱质量面板
- `Phase 5.2` Workspace & Source Manager
- `Phase 5.3` Refresh Operation UI
- `Phase 5.4` Source Distill Trace
- `Phase 5.5` Directory Watcher
- `Phase 5.6` Low Signal Audit

下一步：

- `Phase 5.7` Knowledge Service Console Productization
- `Phase 5.8` Format Expansion：docx、yaml/yml
- `Phase 5.9` Typed Distill Units

### Phase 6：Interface Convergence

目标：

- MCP 作为默认主入口。
- CLI 和 HTTP 与 MCP 共用语义。
- 保留当前 `data_service` / `/api/v1/knowledge/*` 兼容入口。
- 规划未来 `knowledge` CLI 和 workspace-scoped HTTP。

## 核心模型目标

- Workspace
- Source
- SourceBlock
- NormalizedDocument
- DistillUnit
- Claim
- Concept
- Decision
- Task
- Workflow
- Entity
- Relation
- Community
- WikiPage
- GraphSnapshot
- RetrievalHit
- TraceEdge
- QualityIssue
- Feedback
- CorrectionRule
- CorrectionPlan

## typed distill units 目标

- `definition`
- `concept`
- `claim`
- `decision`
- `task`
- `workflow`
- `constraint`
- `risk`
- `example`
- `misconception`
- `entity_evidence`
- `relation_evidence`
- `meeting_summary`
- `code_symbol`
- `code_dependency`
- `code_call_edge`
- `architecture_note`

## 当前验证基线

- 外部 HarnessOS MCP 验收：create -> import -> build -> poll -> query_v2 -> feedback_v2 -> rules_v2 -> review_v2 -> correction_plan_v2 -> archive。
- 真实知识库：`/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split`。
- 当前 data_service/API/MCP 回归命令：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```
