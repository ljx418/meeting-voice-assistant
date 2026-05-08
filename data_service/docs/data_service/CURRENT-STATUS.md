# Local Knowledge Governance Service 当前状态

更新时间：2026-05-08

## 一句话定义

本项目是一个独立的 MCP-first 本地知识治理服务，负责把外部应用传入的文本、文档块、会议转写和代码分析产物，转化为可追溯的知识单元、实体关系图谱、可读 Wiki、质量规则和可检索上下文，为会议、学习、面试、代码理解等应用提供统一数据底座。

## 当前定位

当前知识库项目已从原会议应用语境中抽象为独立服务单元，可作为最小可分粒度单独拆包、迁移、部署和运行。本服务只提供数据治理能力，不端到端实现会议、学习、面试、代码助手等上层应用。

上层应用必须通过 MCP / CLI / HTTP 调用本服务，不允许直接读写内部 workspace 文件结构。

## 当前实现承载层

| 模块 | 当前定位 |
| --- | --- |
| `backend/data_service` | Knowledge Governance Service 当前实现承载层，负责 workspace/source/build lifecycle、distill、summary、query 聚合、quality artifacts、CLI 和 MCP server |
| `backend/app/api/v1/data_service.py` | HTTP API 边界，当前兼容 `/api/v1/knowledge/*` |
| `backend/app/llmwiki` | 可读 Wiki 固化引擎，负责 source/topic/conversation 页面、本地检索和 provenance |
| `backend/app/graphrag` | 内置 GraphRAG 执行与图谱查询服务，负责 graph snapshot/query/community/materialization |
| `/knowledge` | Knowledge Service Console，服务治理控制台；当前前端源码在外部项目中，本仓库保留后端 API 和文档定位 |

## 已具备能力

- MCP stdio server：lifecycle tools、v2 envelope tools、旧 tools 兼容。
- Session MCP MVP：支持 `knowledge_session_create/get/list/close/delete`、结构化
  `knowledge_session_ingest`、session build、session graph snapshot、neighbors、
  community summary、session query 和 actor summary。会议应用已经通过该 MCP contract
  恢复会议级 speaker-aware GraphRAG 接入。
- CLI：`python -m data_service ingest/query/summary/distill/boundary/graphrag-execute`。
- HTTP API：workspace/source/build/query/graph/distill/trace/quality/reset 等能力。
- workspace lifecycle：create/list/describe/archive。
- source lifecycle：import/list/remove，支持导入式 source 和目录绑定。
- build operation queue：workspace 级排队、状态轮询、取消、blocked、server_interrupted 恢复。
- 目录扫描：受控扫描绑定目录，产生 new/modified/deleted/unreadable/unchanged。
- distill v1.1：source profile、unit kind、provenance、low_signal、zero_unit、profile_debug。
- LLMWiki：source/topic/conversation 页面，可读知识固化和读时质量治理。
- GraphRAG：内置 graph execution owner、compat materializer、graph snapshot、graph query model。
- Source Trace：串联 source、distill units、Wiki pages、GraphRAG nodes/edges/communities。
- Quality Governance：feedback、correction rules、review、correction plan、read-time governance、rollback。
- Low Signal Audit：低信号 source、标题派生强语义 unit、长标题泄漏和 GraphRAG top community 泄漏检查。

## 当前支持格式

已实现：

- `json`
- `txt`
- `md` / `markdown`
- `html` / `htm`
- `csv`
- `pdf`
- `ppt`
- `pptx`

下一阶段格式扩展：

- `docx`
- `yaml` / `yml`

外部适配器可先处理复杂输入，再传入本服务，例如音频转写文本、视频转写文本、OCR 后文本、大型代码仓库分析产物、结构化 JSON。

## Workspace / Tenant 模型

`Tenant = Workspace = 一个受控的本地知识空间`。

目标模型：

- `workspace_id`: 外部稳定 ID
- `display_name`
- `root_path`: 绑定的本地文件夹路径，可在控制台展示
- `path_fingerprint`
- `created_at`
- `updated_at`
- `status`
- `archived`
- `scan_state`
- `build_state`

当前实现已具备 `workspace_id`、workspace path、bound paths、source manifest、operations 和 archive 语义。文档与后续 API 设计以 `workspace_id` 为稳定 contract，避免外部依赖内部目录。

## 架构目标

```text
External Apps / Agents / CLI / Console
  -> MCP / HTTP / CLI
  -> Knowledge Governance Service
  -> Workspace & Tenant Manager
  -> Source Registry
  -> Multi-format Parser
  -> Normalize Pipeline
  -> Distill Engine
  -> Entity & Relation Extractor
  -> LLMWiki Builder
  -> GraphRAG Service
  -> Retrieval Service
  -> Source Trace Service
  -> Quality Governance Service
  -> Artifact Store
  -> Local Workspace Store
```

## 数据流水线

目标 v2 pipeline：

```text
discover
  -> parse
  -> normalize
  -> distill
  -> extract_entities
  -> extract_relations
  -> build_wiki
  -> build_graphrag
  -> summarize
  -> quality_diagnostics
  -> publish_artifacts
```

当前实现阶段映射：

| 当前阶段 | v2 目标阶段 |
| --- | --- |
| `row` / directory scan | `discover` |
| LLMWiki extractors | `parse` |
| normalized readable docs | `normalize` |
| `distill` | `distill` |
| entity/theme candidates | `extract_entities` |
| relation candidates / materializer | `extract_relations` |
| `llmwiki_compile` | `build_wiki` |
| `graphrag_index` | `build_graphrag` |
| `summary` | `summarize` |
| quality diagnostics / correction plan | `quality_diagnostics` / `publish_artifacts` |

## 当前产物布局与目标布局

当前主要产物：

- `workspace/distill/`
- `workspace/llmwiki/`
- `workspace/graphrag/`
- `workspace/summary/`
- `workspace/quality/`
- `workspace/lifecycle/`

目标布局：

```text
workspace/
├── manifest.json
├── sources/
├── normalized/
├── distill/
├── graph/
├── graphrag/
├── wiki/
├── retrieval/
├── trace/
└── quality/
```

目标布局是内部演进方向，不是外部 API。外部调用方只能依赖 MCP / CLI / HTTP contract。

## 边界规则

1. 不依赖会议项目模块。可以接收会议转写文本，但不能 import meeting app 的代码。
2. 不依赖上层应用状态。会议、面试、学习、代码助手只能传入数据或查询请求。
3. 不暴露内部文件布局为稳定 API。workspace 内部存储可以演进；外部只认 MCP / CLI / HTTP contract。

## 下一阶段

当前主线调整为 `Phase 5.7 Knowledge Service Console Productization`：

- 将 `/knowledge` 重新定位为 Local Knowledge Service Console。
- 服务治理控制台展示 workspace、source registry、scan/build 状态、GraphRAG 图谱质量、Source Trace、Distill Units、Wiki artifacts、Quality Feedback、Correction Rules、Correction Plan、MCP/HTTP/CLI 调试状态。
- 不把 `/knowledge` 继续推进为普通用户的个人知识消费 App。

并行推进：

- `docx` 与 `yaml/yml` 格式扩展。
- typed distill units 升级。
- GraphRAG owner 边界继续下沉。
- Session GraphRAG 从 MVP 启发式抽取继续升级到正式 distill / relation extractor /
  source trace 管线，并保持 MCP contract 不破坏。
