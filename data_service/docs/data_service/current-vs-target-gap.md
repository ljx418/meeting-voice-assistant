# Local Knowledge Governance Service 当前与目标架构 Gap

更新时间：2026-05-07

## 总体结论

当前仓库已经具备独立本地知识治理服务的主体能力：MCP、CLI、HTTP、workspace/source/build lifecycle、distill、LLMWiki、GraphRAG、Source Trace、Quality Governance 和目录扫描。

主要差距不再是“能不能形成知识库”，而是要把旧的个人知识库产品叙事收敛为稳定的数据服务边界，并补齐服务治理控制台、workspace contract、typed distill units 和格式扩展。

## 当前架构

```text
MCP / CLI / HTTP / Console
  -> backend/data_service
  -> distill
  -> backend/app/llmwiki
  -> backend/app/graphrag
  -> summary / trace / quality
```

当前定位：

- `backend/data_service` 是 Knowledge Governance Service 当前实现承载层。
- `backend/app/llmwiki` 是可读 Wiki 固化引擎。
- `backend/app/graphrag` 是内置 GraphRAG 执行与图谱查询服务。
- `/knowledge` 是服务治理控制台，而不是用户知识消费 App。

## 目标架构

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

## Gap 1：命名和文档边界

当前：

- 代码包名仍是 `data_service`。
- 部分历史文档仍使用个人知识库产品、会议应用上下文或旧 `/knowledge` 叙述。

目标：

- 文档统一使用 Local Knowledge Governance Service / Knowledge Governance Service。
- 明确 `data_service` 是当前实现承载层和兼容入口。
- 不做大规模破坏性重命名，直到 MCP / CLI / HTTP 新入口有迁移计划和兼容 shim。

## Gap 2：Workspace / Tenant Contract

当前：

- 已有 `workspace_id`、workspace path、bound paths、source manifest 和 lifecycle operations。
- 部分 API 仍允许直接传 `workspace` path。

目标：

- `workspace_id` 是稳定外部 ID。
- `root_path` 是绑定目录和控制台展示字段。
- 外部应用不依赖内部 workspace 文件布局。
- 后续 HTTP / CLI / MCP 逐步收敛到 workspace-scoped 语义。

## Gap 3：服务治理控制台

当前：

- `/knowledge` 已能展示 summary、query、LLMWiki、GraphRAG、distill、Source Trace 和 quality。
- 历史定位偏终端用户知识消费产品。

目标：

- `/knowledge` 定义为 Knowledge Service Console。
- 一级导航建议：Overview、Workspaces、Sources、Build Operations、Distill Units、Wiki Artifacts、GraphRAG、Trace Explorer、Quality Governance、MCP Debugger、Settings。
- 控制台关注服务治理状态：workspace 列表、root_path、递归扫描数量、source registry、failed/unreadable/low-signal sources、build operation、GraphRAG 质量、Trace、Correction Rules 和 MCP/HTTP/CLI 调试。

## Gap 4：多格式解析

当前已支持：

- `json`
- `txt`
- `md`
- `html`
- `csv`
- `pdf`
- `ppt`
- `pptx`

目标还需补齐：

- `docx`
- `yaml` / `yml`

复杂多模态输入由外部适配器处理后传入本服务，例如 OCR 文本、视频转写、代码分析产物和结构化 JSON。

## Gap 5：typed distill units

当前：

- `DistilledUnitKind` 包含 `fact_candidate / question / conclusion / step / example / note / risk / entity_candidate / relation_candidate / topic_candidate`。

目标：

- 将 distill schema 从通用 unit 逐步升级为 typed distill units。
- 目标类型包括 `definition / concept / claim / decision / task / workflow / constraint / risk / example / misconception / entity_evidence / relation_evidence / meeting_summary / code_symbol / code_dependency / code_call_edge / architecture_note`。
- typed units 是支撑会议、学习、面试和代码理解四类上层应用的关键。

## Gap 6：目标 workspace layout

当前：

- 已有 `distill/`、`llmwiki/`、`graphrag/`、`summary/`、`quality/`、`lifecycle/`。

目标：

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

目标布局仅作为内部演进方向。外部调用方只能依赖 MCP / CLI / HTTP。

## Gap 7：接口语义统一

当前：

- MCP lifecycle/v2 tools 已成熟。
- CLI 和 HTTP 仍保留当前 `data_service` / `/api/v1/knowledge/*` 兼容语义。

目标：

- MCP 是默认主入口，CLI 和 HTTP 与 MCP 共享语义。
- 目标 MCP tools 覆盖 workspace/source/build/query/retrieve/graph/distill/quality。
- 目标 CLI 形如 `knowledge workspace list`、`knowledge build --workspace`、`knowledge query --workspace`。
- 目标 HTTP 形如 `/api/workspaces/{id}/query`、`/graph`、`/quality`。
- 兼容入口保留到迁移窗口结束。

## 硬规则

1. 不依赖会议项目模块。可以接收会议转写文本，但不能 import meeting app 的代码。
2. 不依赖上层应用状态。面试、学习、代码助手都只能传入数据或查询请求。
3. 不暴露内部文件布局为稳定 API。workspace 内部存储可以演进；外部只认 MCP / CLI / HTTP contract。
