# 项目验收计划

更新时间：2026-04-30

## 验收目标

用户验收的目标是确认真实资料可以稳定变成一个可阅读、可查询、可看图谱的本地知识库。

Phase 3 完成后的重点不是新增单点功能，而是确认：

- `data_service` 只作为统一编排入口
- `llmwiki` 负责可读知识页面
- `app.graphrag` 负责图谱 snapshot / query / community / materialization
- CLI、HTTP API、`/knowledge`、MCP 面向上层保持稳定结构

当前 Phase 3 结论：

- graph snapshot / query 默认经 `app.graphrag.service` bridge 返回
- graph query model 与 community assembly 已由 `app.graphrag.service.data_service_query_model` 提供
- 默认 graph state 物化已通过 `app.graphrag.service.materialize_workspace_graph_state`
- 默认 graph execution owner 已固定为 `app.graphrag`
- `data_service` 保留 ingest 编排、contract staging 与统一查询入口
- 2026-04-29 阶段验收结果见 [PHASE-3-ACCEPTANCE-REPORT.md](./PHASE-3-ACCEPTANCE-REPORT.md)

当前 LLMWiki 标题质量结论：

- 2026-04-29 已完成标题质量第一轮阶段验收，记录见 [LLMWIKI-TITLE-QUALITY-REPORT-2026-04-29.md](./LLMWIKI-TITLE-QUALITY-REPORT-2026-04-29.md)
- 真实知识库验证中 `bad_source_titles = 0`、`bad_page_titles = 0`
- 聊天 JSON、mapping readable Markdown、普通 JSON `title` 字段、中文短标题均已有回归覆盖
- 2026-04-29 已完成 topic 质量第一轮阶段验收，记录见 [LLMWIKI-TOPIC-QUALITY-REPORT-2026-04-29.md](./LLMWIKI-TOPIC-QUALITY-REPORT-2026-04-29.md)
- 真实知识库验证中 `bad_topic_titles = 0`
- 2026-04-29 已完成页面结构第一轮阶段验收，记录见 [LLMWIKI-PAGE-STRUCTURE-REPORT-2026-04-29.md](./LLMWIKI-PAGE-STRUCTURE-REPORT-2026-04-29.md)
- title-only topic 不再重复写成 `Facts`
- 2026-04-29 已完成 source 页面结构第一轮阶段验收，记录见 [LLMWIKI-SOURCE-STRUCTURE-REPORT-2026-04-29.md](./LLMWIKI-SOURCE-STRUCTURE-REPORT-2026-04-29.md)
- title-only source 不再重复写成 `Core Conclusion / Evidence`

当前 GraphRAG CLI preflight 结论：

- 2026-04-29 已补 native CLI 健康检查，记录见 [GRAPHRAG-CLI-PREFLIGHT-REPORT-2026-04-29.md](./GRAPHRAG-CLI-PREFLIGHT-REPORT-2026-04-29.md)
- `app.graphrag` compat indexed 是可用基线
- native Microsoft GraphRAG CLI indexed 是增强验收
- 当前本机 `/usr/local/bin/graphrag` 指向已不存在的 `/tmp/graphrag_patched.py`，因此 preflight 明确返回 `graphrag_cli_broken`

当前 `/knowledge` 质量反馈入口结论：

- 2026-04-30 已完成质量反馈与人工校正入口第一版，记录见 [KNOWLEDGE-QUALITY-FEEDBACK-REPORT-2026-04-30.md](./KNOWLEDGE-QUALITY-FEEDBACK-REPORT-2026-04-30.md)
- 2026-04-30 已完成质量反馈到 draft 校正规则第一版，记录见 [QUALITY-CORRECTION-RULES-REPORT-2026-04-30.md](./QUALITY-CORRECTION-RULES-REPORT-2026-04-30.md)
- 人工反馈落盘到 `workspace/quality/feedback.jsonl`
- draft 校正规则落盘到 `workspace/quality/correction_rules.json`
- `summary.json.quality.manual_feedback` 可展示反馈总量、action 分布和 target type 分布
- `summary.json.quality.correction_rules` 可展示规则总量、状态分布和规则类型分布
- `/knowledge` 可从当前页面、图节点、distill source、当前查询快速带入反馈对象

## 必跑自动化验收

从项目根目录运行：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

通过标准：

- 测试全部通过
- 允许出现既有 `urllib3` LibreSSL warning
- 不允许出现 Data Service API、distill、GraphRAG bridge 相关失败

## Phase 2 阶段验收：distill 正式中间层

Phase 2 的目标是确认 `distill` 已经可以作为正式中间契约层独立验收，而不是确认 GraphRAG owner 最终收口或 LLMWiki 页面质量全部完成。

推荐验收 workspace：

```bash
/tmp/data-service-phase2-acceptance-20260429
```

从 `backend/` 目录运行：

```bash
python3 -m data_service ingest \
  --workspace /tmp/data-service-phase2-acceptance-20260429 \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

通过标准：

- `distill/schema.json`、`distill/manifest.json`、`distill/sources/`、`distill/units/distilled_units.jsonl` 全部生成
- `schema_version` 为 `1.1`
- source 级记录包含 `profile / profile_debug / unit_kind_counts`
- unit 级记录包含 `kind / authority / source_weight / source_density_score / provenance`
- CLI / API 预览能展示 `profile_debug / provenance_summary / units_by_kind / top_units`
- title-only / low-content source 不再大面积退化为 `0 unit`，且不再产出 title-derived 强 `conclusion`
- `llmwiki` 与 `graphrag` 都通过 `input_contract.json` 消费同一套 distill 产物

2026-04-29 阶段验收结果见：

- [PHASE-2-ACCEPTANCE-REPORT.md](./PHASE-2-ACCEPTANCE-REPORT.md)

## 真实知识库端到端验收

从 `backend/` 目录运行：

```bash
python3 -m data_service ingest \
  --workspace /tmp/data-service-acceptance \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

通过标准：

- 能稳定读取真实 source
- `llmwiki: success`
- `graphrag: indexed`
- `summary / distill / llmwiki / graphrag` 产物完整生成
- 图谱规模不出现明显倒退或异常膨胀

当前参考基线：

- 86 sources
- 248 distilled units
- 85 entities
- 76 themes
- 131 relationships
- bad source titles: 0
- bad page titles: 0
- bad topic titles: 0
- topic source signal pages: 79
- topic facts pages: 0
- source signal pages: 86
- source evidence pages: 0
- GraphRAG execution result reason: `graphrag_cli_broken` on current machine, compat state remains indexed

## CLI 查询验收

LLMWiki 查询（用于验证页面检索链路，不绑定 Phase 2 的 VSCode 样例）：

```bash
python3 -m data_service query "conversation" \
  --workspace /tmp/data-service-acceptance \
  --mode llmwiki \
  --top-k 5
```

GraphRAG 查询：

```bash
python3 -m data_service query "VSCode" \
  --workspace /tmp/data-service-acceptance \
  --mode graphrag \
  --top-k 5
```

Hybrid 查询：

```bash
python3 -m data_service query "VSCode" \
  --workspace /tmp/data-service-acceptance \
  --mode hybrid \
  --top-k 5
```

通过标准：

- `llmwiki` 能返回页面或 passage
- source/page 标题不应稳定暴露 UUID、`conversation id`、字面量 `title` 或 `Untitled Source`
- `graphrag` 能返回 entity / theme / relationship
- `hybrid` 能同时组合 LLMWiki 和 GraphRAG 结果
- GraphRAG payload 包含 `nodes / edges / communities / stats / hits`
- GraphRAG payload source 为 `app.graphrag.bridge`

## GraphRAG Native CLI 增强验收

增强验收用于确认 Microsoft GraphRAG 原生 CLI 可用，不等同于 Data Service 可用基线。

通过标准：

- `graphrag --version` 返回 0
- `python3 -m data_service ingest ...` 的 graph execution 不再返回 `graphrag_cli_not_found` 或 `graphrag_cli_broken`
- 如果 native index 失败，返回中必须包含 `cli_health` 与 `cli_error`，能定位是 preflight 失败还是 index 阶段失败

当前本机状态：

- `/usr/local/bin/graphrag` 存在
- 但该 shim 指向 `/tmp/graphrag_patched.py`
- `/tmp/graphrag_patched.py` 不存在
- native CLI 增强验收未通过，compat 可用基线通过

## `/knowledge` 人工验收

打开前端 `/knowledge` 页面后检查：

- summary 能加载
- distill source 预览能加载
- LLMWiki 页面列表与页面内容能加载
- GraphRAG 图谱能加载
- 图谱支持缩放、拖拽、适应视图、社区选中联动
- 查询框可以正常执行 `llmwiki / graphrag / hybrid`
- 质量反馈面板可以提交 `needs_review / rename_suggest / merge_suggest / mark_noise / confirm_good / note`
- 点击页面、图节点、distill source、当前查询后，反馈对象能自动带入
- 提交反馈后最近反馈列表出现新记录
- 刷新 summary 后，`quality.manual_feedback.feedback_count` 增加
- 点击“生成规则”后，`rename_suggest / merge_suggest / mark_noise / needs_review` 反馈能进入“待审核规则”
- `quality.correction_rules.rule_count` 与待审核规则列表数量一致
- 页面无明显遮挡、错位、空白卡片或异常报错

## 质量样例验收

真实知识库中以下标题应稳定收缩到核心实体：

- `小米SU7玻璃防晒性能解析 -> 小米SU7`
- `中国民营航天公司上市进展及股东情况 -> 中国民营航天公司`
- `美加墨世界杯小组赛时间 -> 美加墨世界杯`
- `已安装VSCode选项验证 -> VSCode`
- `TypeScript中的多态与复态解析 -> TypeScript`
- `鸿蒙手机Python自动化测试代码示例 -> Python / 鸿蒙手机`
- `超聚变公司股权结构及背景介绍 -> 超聚变公司`

不应再稳定出现为强实体或强主题的噪音：

- 裸 `SU7`
- `已安装VSCode选项验证`
- `中的多态与复态`
- `鸿蒙手机Python自动化测试代码示例`
- `背景介绍`

LLMWiki 页面标题不应再稳定出现：

- UUID 前缀标题
- `conversation id`
- 字面量 `title`
- `Untitled Source`

LLMWiki topic 标题不应再稳定出现：

- `已安装...`
- `免费...`
- `User seeks clarification...`
- `税后 万...`
- 只剩数值单位或动作词的残片标题

LLMWiki topic 页面结构应满足：

- title-only topic 使用 `Source Signals`
- 不把来源标题重复写成 `Facts`
- 与 `Source Signals` 重复的内容不再进入 `Evidence Notes`

LLMWiki source 页面结构应满足：

- title-only source 使用 `Source Signals`
- 不把来源标题重复写成 `Core Conclusion`
- 与 `Source Signals` 重复的内容不再进入 `Evidence`

## 每次较大开发后的同步动作

每次完成较大开发进展后，统一执行：

- 回归测试
- 真实知识库端到端验证
- 更新 [PROJECT-BASELINE.md](./PROJECT-BASELINE.md)
- 更新 [CURRENT-STATUS.md](./CURRENT-STATUS.md)
- 更新 [current-vs-target-gap.md](./current-vs-target-gap.md)
- 更新 [2026-04-26-data-service-execution-roadmap.md](./2026-04-26-data-service-execution-roadmap.md)
- 更新 [current_vs_target_flow.drawio](./current_vs_target_flow.drawio)

如果架构边界发生变化，再同步：

- [01_current_architecture.drawio](./diagrams/01_current_architecture.drawio)
- [02_target_architecture.drawio](./diagrams/02_target_architecture.drawio)
