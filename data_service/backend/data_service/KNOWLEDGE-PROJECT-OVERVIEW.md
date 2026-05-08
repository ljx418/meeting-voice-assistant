# 当前知识治理服务介绍

更新时间：2026-05-07

## 1. 项目目标

当前知识库项目已从原会议应用语境中抽象为独立的 MCP-first 本地知识治理服务，可作为最小可分粒度单独拆包、迁移和部署。

本服务负责把外部应用传入的文本、文档块、会议转写和代码分析产物，以及本地文件夹中的多格式文件，转化为：

- 可追溯知识单元
- 实体关系图谱
- 可读 Wiki
- 质量规则
- 可检索上下文

会议、学习、面试、代码理解等上层应用通过 MCP / CLI / HTTP 调用本服务。本服务不端到端实现这些上层应用，也不要求外部调用方理解内部 workspace 结构。

## 2. 项目边界

包含 workspace / tenant 管理、source registry、多格式解析、normalize pipeline、distill、实体识别、关系提取、GraphRAG、LLMWiki、Source Trace、Quality Governance、MCP Server、CLI、HTTP API 和服务治理控制台。

不包含会议录音、ASR、说话人分离、实时字幕、完整会议 UI、学习平台 UI、题库平台、面试实时助手 UI、IDE 插件、代码托管平台、大型静态分析器或通用 Agent 工作流编排。

会议场景只处理已经转写后的文本。代码理解场景优先接收 README、file tree、symbols、imports、call graph、class graph、API routes、dependency graph 等外部分析产物。

## 3. 当前实现承载层

```text
External Apps / Agents / CLI / Console
        |
        | MCP / HTTP / CLI
        v
backend/data_service
        |
        +--> backend/app/llmwiki
        |
        +--> backend/app/graphrag
        |
        +--> summary / trace / quality artifacts
```

- `backend/data_service`：Knowledge Governance Service 当前实现承载层。
- `backend/app/llmwiki`：可读 Wiki 固化引擎。
- `backend/app/graphrag`：内置 GraphRAG 执行与图谱查询服务。
- `/knowledge`：Knowledge Service Console，服务治理控制台。

## 4. Workspace / Tenant

`Workspace = Tenant = 一个受控的本地知识空间`。

外部稳定 contract 使用 `workspace_id`。每个 workspace 可绑定本地 `root_path`，服务递归扫描该路径下全部受支持文件。`root_path` 可在控制台展示，但不作为稳定外部 ID。

## 5. 数据流水线

目标 pipeline：

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

当前实现仍保留 `row / extract / normalize / distill / llmwiki_compile / graphrag_index / summary` 阶段名，并逐步映射到目标 pipeline。

## 6. 外部调用原则

1. 不依赖会议项目模块。
2. 不依赖上层应用状态。
3. 不暴露内部文件布局为稳定 API。

外部应用只能依赖 MCP / CLI / HTTP contract。
