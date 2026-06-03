# 项目最新基线文档

更新时间：2026-05-07

## 当前项目定位

项目当前基线是独立的 MCP-first 本地知识治理服务，而不是会议助手页面，也不是端到端个人知识库 App。

本服务负责：

- 接收外部应用传入的文本、文档块、会议转写和代码分析产物。
- 递归扫描 workspace 绑定文件夹下的受支持文件。
- 生成可追溯 distill units、实体关系图谱、可读 Wiki、质量规则和可检索上下文。
- 通过 MCP / CLI / HTTP 为会议、学习、面试、代码理解等上层应用提供统一数据底座。

本服务不负责：

- 会议录音、ASR、说话人分离、实时字幕、会议 UI。
- 学习平台、题库平台、面试实时助手、IDE 插件。
- 原始代码仓库托管、大型静态分析器或通用 Agent 工作流编排。

## 当前完成基线

- `Phase 1` 稳定双引擎工作流已完成。
- `Phase 2` distill 正式中间层已完成阶段性验收。
- `Phase 3` GraphRAG 职责收口已完成阶段性验收。
- `Phase 4` MCP / Agent 化收口已通过外部 HarnessOS 真实 stdio MCP 端到端验收。
- `Phase 5.1` GraphRAG 图谱质量面板第一版已完成。
- `Phase 5.2` Workspace & Source Manager 第一版已完成。
- `Phase 5.3` Refresh Operation UI 第一版已完成。
- `Phase 5.4` Source Distill Trace 第一版已完成。
- `Phase 5.5` Directory Watcher 第一版已完成。
- `Phase 5.6` Low Signal Audit 第一版已完成。

## 当前实现承载层

- `backend/data_service` 是 Knowledge Governance Service 当前实现承载层。
- `backend/app/llmwiki` 是可读 Wiki 固化引擎。
- `backend/app/graphrag` 是内置 GraphRAG 执行与图谱查询服务。
- `/api/v1/knowledge/*` 是当前 HTTP 兼容边界。
- `/knowledge` 是服务治理控制台，不是终端用户应用。

## 外部契约基线

外部调用方只依赖：

- MCP tools
- CLI commands
- HTTP API
- `workspace_id`
- `operation_id`
- source/query/quality payload

外部调用方不能依赖：

- `workspace/distill`
- `workspace/llmwiki`
- `workspace/graphrag`
- `workspace/quality`
- 任何内部文件布局或生成产物路径

## Workspace / Tenant 基线

`Workspace = Tenant = controlled local knowledge space`。

当前实现已支持 managed workspace、source manifest、bound paths、operation state 和 archive。目标 contract 继续以 `workspace_id` 为稳定 ID，`root_path` 作为绑定目录和控制台展示字段。

## 外部 HarnessOS MCP 验收基线

外部 HarnessOS 已通过 stdio MCP 完成真实端到端验收。调用方仅依赖 opaque `workspace_id` 和 MCP tools，未直接读写内部 workspace。

验收链路：

```text
knowledge_workspace_create
-> knowledge_source_import
-> knowledge_build_start
-> knowledge_build_status
-> knowledge_query_v2
-> knowledge_quality_feedback_v2
-> knowledge_correction_rules_v2
-> knowledge_review_correction_rule_v2
-> knowledge_correction_plan_v2
-> knowledge_workspace_archive
```

验收记录：

- `workspace_id`: `harnessosrealdataserviceacceptance4`
- `operation_id`: `op_fb639a7aee3c`
- final `status`: `ok`
- `warnings`: `[]`

## 真实知识库验证基线

参考数据集：

```text
/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

最近验证结果：

- 86 sources
- `llmwiki: success`
- `graphrag: indexed`
- graph execution owner: `app.graphrag`
- 293 distilled units
- 85 entities
- 76 themes
- 131 relationships
- `title_derived_conclusion_count`: 0
- `zero_unit_count`: 0 / 86
- `bad_source_titles`: 0
- `bad_page_titles`: 0
- `bad_topic_titles`: 0

## 当前仍在推进

1. `Phase 5.7 Knowledge Service Console Productization`
- 把 `/knowledge` 重新定位为服务治理控制台。
- 展示 workspace/source/build/distill/wiki/graph/trace/quality/MCP 调试状态。
- 不再以个人知识消费产品为主目标。

2. 格式扩展
- 新增 `docx` extractor。
- 新增 `yaml/yml` extractor 或结构化文本解析。

3. typed distill units
- 从当前通用 unit kind 逐步升级到 `definition / concept / claim / decision / task / workflow / constraint / risk / example / misconception / entity_evidence / relation_evidence / meeting_summary / code_symbol / code_dependency / code_call_edge / architecture_note`。

4. GraphRAG 边界
- 继续把 graph quality plan 适配和 graph query model 收口到 `backend/app/graphrag`。

## 当前文档入口

- [Data Service 文档入口](./README.md)
- [当前架构状态](./CURRENT-STATUS.md)
- [V1.5 当前与目标架构 Gap](../V1.5/current-vs-target-gap.md)
- [开发计划](./2026-04-26-data-service-execution-roadmap.md)
- [验收计划](./ACCEPTANCE-PLAN.md)
- [剩余开发计划](./REMAINING-DEVELOPMENT-PLAN-2026-04-30.md)
