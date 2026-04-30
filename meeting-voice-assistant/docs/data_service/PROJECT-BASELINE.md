# 项目最新基线文档

更新时间：2026-04-30

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
- `distill v1.1` 已完成，包含 `schema.json / manifest.json / sources / units`
- `distill` 预览 API / CLI 已支持精细筛选和 source 级解释字段
- title-only / low-content source 已能产出保守的 `question / entity / topic / note / fact_candidate / risk`
- title-only 实体归并第二轮已覆盖产品、机构、赛事、工具、语言、公司类标题
- `profile_debug.title_normalization` 已能解释标题收缩过程
- `LLMWiki` 标题质量第一轮已完成：聊天 JSON 可从 user question 派生标题，source/page 标题不再稳定暴露 UUID、`conversation id`、字面量 `title` 或 `Untitled Source`
- `LLMWiki` topic 质量第一轮已完成：topic anchor 优先识别产品/工具/专有名词，真实知识库验证 `bad_topic_titles=0`
- `LLMWiki` 页面结构第一轮已完成：topic 页面区分 `Overview / Source Signals / Evidence Notes`，title-only source 不再重复写成 `Facts`
- `LLMWiki` source 页面结构第一轮已完成：title-only source 不再把标题写成 `Core Conclusion / Evidence`，而是进入 `Source Signals`
- GraphRAG runner / bridge / materializer / shared query model 已接通
- GraphRAG native CLI preflight 已补齐：会执行 `graphrag --version`，能区分 `graphrag_cli_not_found` 与 `graphrag_cli_broken`
- graph snapshot / query 默认经 `app.graphrag.service` bridge 返回，payload source 固定为 `app.graphrag.bridge`
- `data_service` 默认 GraphRAG 适配器已不再直接导入 compat materializer，graph state 物化统一通过 `app.graphrag.service.materialize_workspace_graph_state`
- 默认 graph execution owner 已固定为 `app.graphrag`
- `/knowledge` 已完成第一轮统一工作台体验
- `/knowledge` 质量反馈与人工校正入口第一版已完成：workspace 新增 `quality/feedback.jsonl`，API 新增 feedback submit/list，summary 质量面板新增 `manual_feedback`
- 质量反馈到校正规则第一版已完成：workspace 新增 `quality/correction_rules.json`，`rename_suggest / merge_suggest / mark_noise / needs_review` 可生成 draft 规则

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
- GraphRAG native CLI 当前诊断：`graphrag_cli_broken`，本机 `/usr/local/bin/graphrag` 指向已不存在的 `/tmp/graphrag_patched.py`
- 248 distilled units
- 85 entities
- 76 themes
- 131 relationships
- `title_derived_conclusion_count`: 0
- `zero_unit_count`: 8 / 86，作为后续低信号 source 质量优化观察项
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
- 继续观察 8 个低信号 `0 unit` source
- 在不误产强结论的前提下继续提升 title-only / low-content source 覆盖率

3. `/knowledge` 产品化
- 图谱质量面板继续增强
- 人工校正入口和 draft 校正规则第一版已完成，下一步做规则审核与消费
- MCP / Agent tools 精细化

## 当前文档入口

- [Data Service 文档入口](./README.md)
- [项目当前架构状态](./CURRENT-STATUS.md)
- [当前与目标架构 Gap](./current-vs-target-gap.md)
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
