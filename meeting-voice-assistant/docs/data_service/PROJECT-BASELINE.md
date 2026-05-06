# 项目最新基线文档

更新时间：2026-05-06

## 当前项目定位

项目当前基线是本地知识库 Data Service，而不是单一会议语音助手能力。

用户把原始资料写入一次后，系统负责完成：

- `data_service`：统一 ingest、workspace layout、distill、summary、API / CLI / MCP 编排
- `llmwiki`：生成可阅读 source / topic / conversation 页面，并提供本地检索
- `app.graphrag`：负责 graph snapshot / query / community / materialization 的图谱能力收口
- `/knowledge`：作为知识库工作台展示 summary、distill、LLMWiki 页面、GraphRAG 图谱和查询结果

## 当前完成基线

- `Phase 1` 基础收口已完成
- `Phase 2` distill 正式中间层已完成阶段性验收，验收记录见 [PHASE-2-ACCEPTANCE-REPORT.md](./PHASE-2-ACCEPTANCE-REPORT.md)
- `Phase 3` GraphRAG 职责收口已完成阶段性验收，验收记录见 [PHASE-3-ACCEPTANCE-REPORT.md](./PHASE-3-ACCEPTANCE-REPORT.md)
- `Phase 4` MCP / Agent 化收口已通过外部 HarnessOS 真实 stdio MCP 端到端验收；当前作为回归基线保留
- `Phase 5` 知识产品化已完成 `Phase 5.1` 图谱质量面板第一版；当前产品目标升级为“顺手的个人知识库管理产品”，下一步推进 Workspace & Source Manager、Refresh Operation UI、Source Distill Trace 和 Directory Watcher
- `distill v1.1` 已完成，包含 `schema.json / manifest.json / sources / units`
- `distill` 预览 API / CLI 已支持精细筛选和 source 级解释字段
- title-only / low-content source 已能产出保守的 `question / entity / topic / note / fact_candidate / risk`
- distill 低信号 source 观测与保守补强第一版已完成：source profile、manifest、summary 和 `/knowledge` 均可展示 `zero_unit`、zero-unit 原因分布与 title fallback 覆盖统计；真实知识库临时验收 `zero_unit_count=0` 且 `title_derived_conclusion_count=0`
- title-only 实体归并第二轮已覆盖产品、机构、赛事、工具、语言、公司类标题
- `profile_debug.title_normalization` 已能解释标题收缩过程
- `LLMWiki` 标题质量第一轮已完成：聊天 JSON 可从 user question 派生标题，source/page 标题不再稳定暴露 UUID、`conversation id`、字面量 `title` 或 `Untitled Source`
- `LLMWiki` topic 质量第一轮已完成：topic anchor 优先识别产品/工具/专有名词，真实知识库验证 `bad_topic_titles=0`
- `LLMWiki` 页面结构第一轮已完成：topic 页面区分 `Overview / Source Signals / Evidence Notes`，title-only source 不再重复写成 `Facts`
- `LLMWiki` source 页面结构第一轮已完成：title-only source 不再把标题写成 `Core Conclusion / Evidence`，而是进入 `Source Signals`
- GraphRAG runner / bridge / materializer / shared query model 已接通
- GraphRAG native CLI preflight 已补齐：会执行真实 CLI 健康检查；本机 `/usr/local/bin/graphrag` 已恢复为 `graphrag.cli.main:app` 真实入口；GraphRAG 3.0.8 不支持全局 `--version`，preflight 已改为 `graphrag --help`
- graph snapshot / query 默认经 `app.graphrag.service` bridge 返回，payload source 固定为 `app.graphrag.bridge`
- graph snapshot 已新增 `quality_diagnostics`，可返回 `top_communities / weak_communities / isolated_nodes / low_value_nodes / summary`，每个诊断对象包含可直接进入质量反馈的 `feedback_target`
- `data_service` 默认 GraphRAG 适配器已不再直接导入 compat materializer，graph state 物化统一通过 `app.graphrag.service.materialize_workspace_graph_state`
- 默认 graph execution owner 已固定为 `app.graphrag`
- `/knowledge` 已完成第一轮统一工作台体验
- `/knowledge` 质量反馈与人工校正入口第一版已完成：workspace 新增 `quality/feedback.jsonl`，API 新增 feedback submit/list，summary 质量面板新增 `manual_feedback`
- 质量反馈到校正规则第一版已完成：workspace 新增 `quality/correction_rules.json`，`rename_suggest / merge_suggest / mark_noise / needs_review` 可生成 draft 规则
- 质量校正规则审核第一版已完成：draft 规则可进入 `approved / rejected / archived`，重新生成规则不会重置已审核状态
- approved 校正规则消费第一版已完成：workspace 新增 `quality/correction_plan.json`，Graph 快照、GraphRAG query、LLMWiki read page 读取时可应用 suppress / rename / merge 展示治理策略；每条 action 已记录 Graph nodes / Graph edges / LLMWiki pages 影响范围并在 `/knowledge` 展示；GraphRAG query 已返回 `quality_plan.query_hit_impact` 并在查询卡片展示 filtered / rewritten 计数
- LLMWiki 读时治理第一版已完成：ingest/compile 默认不改写生成 markdown，read page / query 读取时应用 approved rename / merge / suppress 展示治理
- 质量规则回滚第一版已完成：规则状态新增 `revoked`，approved 规则可撤回并立即从 `correction_plan.json` 移除，非 approved 规则可重新置为 draft
- topic 合并策略第一版已完成：approved merge 命中旧 topic/page markdown 时会写入 `quality_merged_into`，canonical 页面会追加 `Merged Topic Signals`，旧页面不删除以保护既有链接
- MCP / Agent 质量治理 tools 安全收紧版已完成：MCP stdio server 可读取质量 summary、校正规则、approved correction plan 与 action impact，可提交受控 feedback、执行受控审核；读取 correction plan 不隐式写 workspace
- MCP 化知识库生命周期管理第一版已完成并通过外部 HarnessOS 真实接入验收：新要求来自 `../harnessOS/docs/architecture/data-service-mcp-codex-handoff.md`；面向外部 Harness 工程新增 workspace 创建/列出/描述/归档、source 导入/列出/停用、build 启动/状态/取消等 tools；保留既有 MCP tools 兼容性，并新增 `knowledge_ingest_v2 / knowledge_query_v2 / knowledge_quality_*_v2 / knowledge_correction_*_v2` envelope tools；业务可预期失败统一返回 `blocked` envelope；build 已改为 workspace 级队列与 `operation_id + status polling`，支持排队、取消和 `server_interrupted` retryable 恢复；外部 HarnessOS 已在持久化 MCP stdio session 内跑通 create -> import -> build_start -> build_status(completed) -> query_v2 -> feedback_v2 -> correction_rules_v2 -> review_correction_rule_v2 -> correction_plan_v2 -> archive
- `Phase 5.1` GraphRAG 图谱质量面板第一版已完成：`/knowledge` 已展示 Top Communities、Weak Communities、Isolated Nodes、Low Value Nodes，并支持从诊断项快速带入 `needs_review / mark_noise / merge_suggest / rename_suggest` 反馈；点击诊断项可定位图节点或社区

## 外部 HarnessOS MCP 验收基线

验收结论：外部 HarnessOS 已通过 stdio MCP 方式完成 data_service knowledge 工作流真实端到端验收。调用方仅依赖 opaque `workspace_id` 和 MCP tools，未直接读写内部 workspace。统一 envelope 在 lifecycle/v2 tools 中可被 Harness 正常解析，build queue 可通过 `operation_id` 轮询到 `completed`，query/feedback/rules/review/plan/archive 全链路均返回 `ok`。

验收记录：

- `workspace_id`: `harnessosrealdataserviceacceptance4`
- `operation_id`: `op_fb639a7aee3c`
- final `status`: `ok`
- `warnings`: `[]`
- 覆盖链路：`knowledge_workspace_create -> knowledge_source_import -> knowledge_build_start -> knowledge_build_status -> knowledge_query_v2 -> knowledge_quality_feedback_v2 -> knowledge_correction_rules_v2 -> knowledge_review_correction_rule_v2 -> knowledge_correction_plan_v2 -> knowledge_workspace_archive`
- HarnessOS 侧已补持久化 `McpStdioSession`，避免一次性 MCP 进程退出导致 data_service build queue 状态丢失
- 真实验收前置条件：data_service venv 需要完整安装 `backend/requirements.txt`；否则 build 阶段可能因 GraphRAG 依赖缺失失败

## 当前真实知识库验证基线

验证数据集：

```text
/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

最近验证结果：

- 86 sources
- `llmwiki: success`
- `graphrag: indexed`
- graph execution owner: `app.graphrag`
- GraphRAG native CLI 当前诊断：preflight 可返回 `healthy=true`；native index 如因配置或输入失败，会进入 `app_graphrag_compat_after_cli_failure`，不再是 `/tmp/graphrag_patched.py` wrapper 故障
- 293 distilled units（低信号保守补强后最新临时验收）
- 85 entities
- 76 themes
- 131 relationships
- `title_derived_conclusion_count`: 0
- `zero_unit_count`: 0 / 86（低信号保守补强临时验收）
- zero-unit 优化已具备诊断字段：`low_signal_reason_counts / zero_unit_sources / title_fallback_source_counts`
- `bad_source_titles`: 0
- `bad_page_titles`: 0
- `bad_topic_titles`: 0
- `topic_source_signal_pages`: 79
- `topic_facts_pages`: 0
- `source_signal_pages`: 86
- `source_evidence_pages`: 0

代表性质量样例：

- `758e5c7e-..._Hermes配置微信飞书401认证错误解决 -> Hermes配置微信飞书401认证错误解决`
- `7dece57f-..._社招 -> 社招`
- `已安装VSCode选项验证 -> VSCode`
- `小米SU7玻璃防晒性能解析 -> 小米SU7`
- `股市S1含义解析 -> 股市S1`
- `税后50万计算税前工资 -> 税前工资`
- `User seeks clarification on creample term -> creample`
- `中国民营航天公司上市进展及股东情况 -> 中国民营航天公司`
- `美加墨世界杯小组赛时间 -> 美加墨世界杯`
- `TypeScript中的多态与复态解析 -> TypeScript`
- `鸿蒙手机Python自动化测试代码示例 -> Python / 鸿蒙手机`
- `超聚变公司股权结构及背景介绍 -> 超聚变公司`

## 当前仍在推进

1. `LLMWiki` 质量提升
- topic 合并策略
- source/topic 页面结构继续观察
- distill 质量向页面层传导

2. `distill` 质量观察
- 抽查低信号 title fallback 的页面可读性和图谱噪音
- 在不误产强结论的前提下继续提升 title-only / low-content source 覆盖率

3. Phase 4：MCP / Agent 化收口
- 外部 HarnessOS 真实 stdio MCP 验收已通过；当前作为回归基线保留
- lifecycle tools 已新增 `knowledge_workspace_* / knowledge_source_* / knowledge_build_*`
- v2 envelope tools 已新增，旧 tools 保持兼容
- build 采用 workspace 级队列，operation state 落盘，可轮询 `queued / running / completed / failed / blocked / cancelled`
- archived workspace 写操作返回 `blocked`
- 外部验收链路已覆盖 create/import/build/poll/query/feedback/rules/review/plan/archive，最终 `status=ok`、`warnings=[]`
- 当前验证：`python3.12 -m pytest backend/tests/test_data_service_mcp.py -q` 为 `14 passed`
- Data Service / API / MCP 回归：`74 passed, 14 skipped`
- LLMWiki 回归：`34 passed`

4. Phase 5：`/knowledge` 产品化
- 图谱质量面板第一版已完成；当前主推进项是个人知识库管理产品化
- 目标固定为同时支持“目录即知识库”和“导入式知识库”
- 先做手动首次刷新/增量刷新与异步 operation UI，再做目录监听和待刷新队列
- source 详情需要展示 `原始文件 -> distill units -> LLMWiki 页面 -> GraphRAG 节点/社区` 的可追溯流水线
- 人工校正入口、draft 校正规则、审核动作、approved 规则消费和回滚第一版已完成
- 继续让图谱问题一键进入 `feedback -> correction_rules -> review -> correction_plan -> read-time governance` 闭环
- 继续把 GraphRAG quality plan 适配向 `app.graphrag.service` owner 边界下沉

## 当前文档入口

- [Data Service 文档入口](./README.md)
- [项目当前架构状态](./CURRENT-STATUS.md)
- [当前与目标架构 Gap](./current-vs-target-gap.md)
- [个人知识库管理产品 Gap 文档](./PERSONAL-KNOWLEDGE-PRODUCT-GAP-2026-05-06.md)
- [当前与目标差异图](./current_vs_target_flow.drawio)
- [当前架构图](./diagrams/01_current_architecture.drawio)
- [目标架构图](./diagrams/02_target_architecture.drawio)
- [开发计划](./2026-04-26-data-service-execution-roadmap.md)
- [验收计划](./ACCEPTANCE-PLAN.md)
- [Phase 2 验收报告](./PHASE-2-ACCEPTANCE-REPORT.md)
- [Phase 3 验收报告](./PHASE-3-ACCEPTANCE-REPORT.md)
- [LLMWiki 标题质量阶段报告](./LLMWIKI-TITLE-QUALITY-REPORT-2026-04-29.md)
- [GraphRAG CLI Preflight 阶段报告](./GRAPHRAG-CLI-PREFLIGHT-REPORT-2026-04-29.md)
- [LLMWiki Topic 质量阶段报告](./LLMWIKI-TOPIC-QUALITY-REPORT-2026-04-29.md)
- [LLMWiki 页面结构阶段报告](./LLMWIKI-PAGE-STRUCTURE-REPORT-2026-04-29.md)
- [LLMWiki Source 页面结构阶段报告](./LLMWIKI-SOURCE-STRUCTURE-REPORT-2026-04-29.md)
- [Knowledge 质量反馈入口阶段报告](./KNOWLEDGE-QUALITY-FEEDBACK-REPORT-2026-04-30.md)
- [Quality Correction Rules 阶段报告](./QUALITY-CORRECTION-RULES-REPORT-2026-04-30.md)
- [Quality Rule Review 阶段报告](./QUALITY-RULE-REVIEW-REPORT-2026-04-30.md)
- [Quality Correction Plan 阶段报告](./QUALITY-CORRECTION-PLAN-REPORT-2026-04-30.md)
- [MCP / Agent 质量治理 Tools 阶段报告](./MCP-AGENT-TOOLS-REPORT-2026-04-30.md)
- [低信号 Source 观测阶段报告](./LOW-SIGNAL-SOURCE-OBSERVABILITY-REPORT-2026-04-30.md)
- [GraphRAG 图谱质量面板阶段报告](./GRAPHRAG-GRAPH-QUALITY-PANEL-REPORT-2026-05-06.md)
- [剩余开发计划](./REMAINING-DEVELOPMENT-PLAN-2026-04-30.md)
