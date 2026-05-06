# 2026-04-26 Data Service 双引擎执行路线图

## 目标

把当前已经可用的 `data_service + llmwiki + graphrag + /knowledge` 体系，推进为可持续演进的稳定知识底座。

这份路线图基于当前 [项目最新基线文档](./PROJECT-BASELINE.md) 和历史总计划沉淀，重点不是再讲概念，而是明确：

- 当前先做什么
- 每个阶段的输出物是什么
- 如何判断完成
- 哪些任务有依赖关系

## 总原则

### 原则 1：不碰 `row`

- `row` 只读
- 不改写原始文件
- 不把中间产物回写到原始数据目录

### 原则 2：先稳定数据契约，再升级算法

顺序必须是：

1. 固化 `distill` 和 graph schema
2. 稳定 `llmwiki` / `graphrag` 输入边界
3. 再继续提升图算法和可视化

### 原则 3：`data_service` 优先做上游，不继续无限膨胀

- 编排、workspace、summary、API、MCP 是它的核心职责
- 页面编译逻辑留在 `llmwiki`
- 图谱算法逻辑逐步收回 `graphrag`

## Phase 1：稳定版基线

### 目标

把现在“能跑”的版本，固化成“稳定、可解释、可重复”的版本。

### 任务 1.1：固化 distill schema

当前状态：基础完成

输出物：

- `distilled unit` 字段清单
- `source-level summary` 字段清单
- schema version 字段
- 字段含义说明

具体动作：

- 为 `distill` 增加 `schema_version`
- 区分：
  - source summary
  - unit records
- 明确保留字段：
  - `source_weight`
  - `source_density_score`
  - `authority`
  - `title_flags`
  - `is_title_derived`
  - `is_llm_enriched`
  - `provenance`

验收标准：

- `distill/` 目录可直接读懂
- `llmwiki` 与 `graphrag` 都基于同一套字段消费

### 任务 1.2：继续清理 GraphRAG 噪音

当前状态：第二轮规则已完成，仍需继续观察真实数据

输出物：

- 更新后的 stopwords / theme noise / entity noise 规则
- 更干净的头部社区和实体

具体动作：

- 清理数字前缀中文残片
- 清理纯功能性标题词
- 清理标题状态标记残留
- 对短词、高频泛词、无语义标签降权

验收标准：

- `废弃于` 不进入主题和实体
- 头部社区能稳定浮现 `AI学习`、`投资`、`宏观政策`
- 明显减少 `点分析`、`岁工作` 这类伪主题

### 任务 1.3：提升 LLMWiki 页面质量

当前状态：标题清洗第一轮、topic anchor 第一轮、topic/source 页面结构第一轮已完成

输出物：

- 更自然的 source 标题
- 更稳定的 topic 标题
- 更结构化的页面内容

具体动作：

- 优化 title cleanup
- 强化 source/topic prompt
- 提升 topic 合并规则
- 继续区分 verified / unverified

验收标准：

- 页面标题不再稳定停留在 `conversation id`、UUID、字面量 `title` 或 `Untitled Source`
- topic 页更接近真实主题而不是文件名或动作残片
- title-only topic 不再把来源标题重复写成 `Facts`
- title-only source 不再把来源标题重复写成 `Core Conclusion / Evidence`

### 任务 1.4：补强 summary 观测

当前状态：基础完成

输出物：

- 更丰富的 `summary.json`
- 更可读的 `summary.md`

具体动作：

- 增加数据质量统计：
  - filtered title flags
  - filtered noise entities
  - llm enriched source count
  - top communities
- 区分 ingest 状态和知识状态

验收标准：

- 用户只看 `summary` 就能判断当前 workspace 状态

### Phase 1 当前结论

已完成：

- `distill schema version`
- `workspace/distill/` 正式目录布局
- `manifest.json / schema.json`
- 第二轮 GraphRAG 噪音清理
- LLMWiki source/topic 标题治理第一轮
- `summary.json` 质量观测字段第一轮
- distill 预览 API / CLI
- `distill -> llmwiki/graphrag` 输入边界固定
- boundary audit（能力盘点）
- capability migration table（owner / action / impact）
- graph query model 第一版统一（`graph_model_version`、`nodes / edges / communities / stats / hits`）
- graph execution owner 第一版收口（ingest owner 选择、`execution_owner.json`、`execution_request.json`）
- `app.graphrag` runner 第一版接入（自动尝试执行、`graphrag-execute` CLI、`/api/v1/knowledge/graphrag/execute`）
- `app.graphrag` runner preflight 增强：native CLI 不再只看 `which graphrag`，而是执行真实 CLI 健康检查；当前本机 `/usr/local/bin/graphrag` 已恢复为 `graphrag.cli.main:app`，GraphRAG 3.0.8 使用 `graphrag --help` 作为 preflight
- `app.graphrag` bridge 第一版接管（app owner 模式下的 graph snapshot / query / community / materialization 入口）
- `app.graphrag` materializer 迁入并完成 direct hookup（compat graph DB 写库逻辑本体）
- 共用 graph query model 已抽入 `app.graphrag.service.data_service_query_model`，graph snapshot / query 结构定义进一步收口到 `app.graphrag.service`
- `DataService` 内部重复 graph helper 与直接 compat snapshot/query 路径已删除，graph snapshot / query 默认经 `app.graphrag.service` bridge 返回，CLI/API payload source 固定为 `app.graphrag.bridge`
- `DataService` 默认 GraphRAG 适配器不再直接导入 compat materializer，默认 graph state 物化也经 `app.graphrag.service.materialize_workspace_graph_state`
- `distill v1.1` 质量增强：补 `risk / example / fact_candidate`、低信号聊天过滤、`unit_kind_counts`
- `distill preview` 增加 sources-dir 自恢复，避免与 ingest 并发时因 manifest 瞬时缺失导致空结果
- `distill preview` 新增精细筛选能力：支持 `kind / min_importance / llm_enriched_only / authority / min_source_weight / min_source_density`，并已基于 `知识库/row/deepseek_split` 做端到端验证
- `distill` 正式化收尾增强：source 级预览已补 `profile_debug / provenance_summary / units_by_kind / top_units`，可直接定位“这个 source 为什么被蒸馏成现在这样”；已基于真实知识库 workspace 做 CLI 端到端验证
- `distill` 标题理解增强：source 标题优先读取 JSON/Markdown 内部真实标题；对正文近乎为空但标题有语义的 source，补保守型 `title-derived question`
- `distill` 标题理解第二轮增强：title-only source 不再把标题本身误写成 `conclusion`，并会优先从标题抽核心实体/标签。已在真实知识库中验证：
  - `米醋与白醋的区别及用途 -> 米醋 / 白醋 + question`
  - `四代住宅概念及特点解析 -> 四代住宅 + question`
  - `腱鞘炎就诊科室选择建议 -> 腱鞘炎 + question`
  - `中国高层住宅宜居年限分析 -> 中国高层住宅 + question`
  - `武汉周末小众游推荐 -> 武汉 + question`
  - 三者均不再误产 `conclusion`
- `distill` 标题理解第三轮增强：对 title-only / low-content source 按标题语义补低风险的 `note / fact_candidate / risk`，不补强结论。已在真实知识库中验证：
  - `武汉周末小众游推荐 -> note`
  - `中国核电建设及并网时间数据 -> fact_candidate`
  - `Bose耳机配对问题排查指南 -> risk`
- `distill` title-only 主题映射收口第一轮：对低正文 source 不再提前注入 `投资 / 宏观政策 / 软件开发 / AI学习` 等 broad bucket 主题；真实知识库中的 `中国核电建设及并网时间数据` 已验证从 `投资 + 中国核电` 收敛为仅 `中国核电`
- `distill` 实体归并第一轮：title-only / low-content source 的标题实体已开始收缩到核心实体；真实知识库已验证 `日历App跨端协作技术专利方案 -> 日历`、`股市S1含义解析 -> 股市S1`
- `distill` 实体归并第二轮启动：产品/机构/赛事类 title-only source 继续收缩到核心实体；真实知识库已验证 `小米SU7玻璃防晒性能解析 -> 小米SU7`、`中国民营航天公司上市进展及股东情况 -> 中国民营航天公司`、`美加墨世界杯小组赛时间 -> 美加墨世界杯`，并压掉裸 `SU7` 重复节点；source 级 `profile_debug` 已补 `title_only_excerpt / entity_candidates / theme_labels`
- `distill` 标题到主题细粒度映射继续收紧：工具/语言/公司类 title-only source 不再把安装状态、代码示例、背景介绍、`中的...` 说明片段落成主题或实体；真实知识库已验证 `已安装VSCode选项验证 -> VSCode`、`TypeScript中的多态与复态解析 -> TypeScript`、`鸿蒙手机Python自动化测试代码示例 -> Python / 鸿蒙手机`、`超聚变公司股权结构及背景介绍 -> 超聚变公司`
- `distill` source profile 解释性增强：`profile_debug.title_normalization` 已能解释 title-only 标题收缩过程，包含 `raw_title / normalized_entities / normalized_themes / dropped_fragments / rules_applied`；`schema.json` 已把 `profile_debug` 纳入 source record 字段，CLI/API 预览可直接定位标题为什么只落到核心实体
- 第三轮 GraphRAG 主题噪音治理：`表11试验流程表`、`涨跌逻辑分析`、`搭建指南/配置说明` 等标题功能尾缀主题已在真实知识库重建中被压下
- 第四轮 GraphRAG 主题/实体噪音治理：materializer 不再将 `unit.tags` 重新提升为 entity/theme；`Bose耳机配对问题排查`、`Cursor国内使用限制`、`配置微信飞书`、`User seeks clarification...` 等混合说明型候选已在真实知识库重建中被压下；86 条真实 source 重建后图谱规模进一步收敛到 `53 entities / 59 themes / 104 relationships`
- 第五轮 GraphRAG 主题/实体噪音治理：补充数值驱动标题清洗与残片拒绝，`新能源车1000公里续航发展分析 -> 新能源车`、`中国养老金5000元以上人数分析 -> 中国养老金`，并拒绝 `公里续航发展 / 元以上人数 / 岁被裁退休金计算 / 万贷款` 这类残片；最新 86 条真实 source 重建验证为 `85 entities / 76 themes / 131 relationships`，`小米SU7 / 中国民营航天公司 / 美加墨世界杯 / VSCode / TypeScript / Python / 超聚变公司` 已稳定落图且不再出现裸 `SU7`、`已安装VSCode选项验证`、`中的多态与复态`、`鸿蒙手机Python自动化测试代码示例`、`背景介绍`
- `/knowledge` 第一轮视觉统一：改为对齐首页风格，页面已重写为按组件宽度自动换行的流式卡片结构，清掉了旧的多组分栏样式冲突
- `LLMWiki` 标题质量第一轮：聊天 JSON 无显式标题时从 user question 派生标题；mapping readable Markdown 不再以 UUID 作为 H1；普通 JSON 顶层 `title` 字段使用字段值；两个汉字的中文短标题不再误判为无意义标题。真实知识库端到端验证 `bad_source_titles=0`、`bad_page_titles=0`
- `GraphRAG` CLI preflight 补强：runner 已执行真实 CLI 健康检查；本机 `/usr/local/bin/graphrag` 已从临时 `/tmp/graphrag_patched.py` wrapper 恢复为 `graphrag.cli.main:app` 真实入口；GraphRAG 3.0.8 不支持全局 `--version`，preflight 已改为 `graphrag --help`，当前 healthcheck 可返回 `healthy=true`
- `LLMWiki` topic 质量第一轮：topic slug 与 title 共用产品/工具/专有名词优先的 anchor，拒绝动作词、数值残片和英文句子脚手架；真实知识库端到端验证 `bad_topic_titles=0`
- `LLMWiki` 页面结构第一轮：topic 页面改为 `Overview / Source Signals / Evidence Notes`，title-only source 不再重复写成 `Facts`；真实知识库验证 `topic_source_signal_pages=79`、`topic_facts_pages=0`
- `LLMWiki` source 页面结构第一轮：source 页面改为用 `Source Signals` 承载标题级材料，title-only source 不再重复写成 `Core Conclusion / Evidence`；真实知识库验证 `source_signal_pages=86`、`source_evidence_pages=0`
- `/knowledge` 质量反馈与人工校正入口第一版：workspace 新增 `quality/feedback.jsonl`，HTTP 新增 feedback submit/list，summary 质量字段新增 `manual_feedback`，前端可从页面、图节点、distill source、当前查询快速带入反馈对象
- 质量反馈到 draft 校正规则第一版：workspace 新增 `quality/correction_rules.json`，`rename_suggest / merge_suggest / mark_noise / needs_review` 可生成待审核规则，HTTP 新增 corrections list/build，前端可查看规则队列
- 质量规则审核第一版：HTTP 新增 `quality/corrections/review`，draft 规则可进入 `approved / rejected / archived`，重新 build 会保留既有审核状态，前端已提供批准、拒绝、归档按钮
- approved 校正规则消费第一版：workspace 新增 `quality/correction_plan.json`，HTTP 新增 `quality/corrections/plan`，Graph 快照、GraphRAG query、LLMWiki read page 读取时会应用 suppress / rename / merge 展示治理；action impact 已记录 Graph nodes / Graph edges / LLMWiki pages；GraphRAG query 已返回 `quality_plan.query_hit_impact`；前端已提供“生成消费计划”、影响范围展示和查询治理计数
- LLMWiki 读时消费第一版：LLMWiki ingest/compile 默认不改写生成 markdown；read page / query 读取时应用 quality plan；rename / merge 改写展示文本；suppress 在展示层过滤但不删除页面
- 质量规则回滚第一版：规则状态新增 `revoked`，approved 规则可撤回并立即从 `correction_plan.json` 移除，非 approved 规则可重新置为 draft，前端已提供撤回和重新置草稿操作
- topic 合并策略第一版：approved merge 命中旧 topic/page markdown 时写入 `quality_merged_into`，canonical 页面追加 `Merged Topic Signals`，旧页面不删除以保护既有链接
- MCP / Agent 质量治理 tools 安全收紧版：MCP stdio server 已新增质量 summary、correction plan、feedback、rules、review tools，Agent 可读取质量计划与影响范围、提交受控反馈、审核规则；读取 correction plan 不隐式写 workspace
- distill 低信号 source 观测与保守补强第一版：source profile、manifest、summary、`/knowledge` 已新增 zero-unit 诊断、原因分布和 title fallback 覆盖统计；基于真实 low-signal reasons 补规则后，临时验收 `zero_unit_count=0 / 86`，`title_derived_conclusion_count=0`

当前下一步：

- `Phase 2` 与 `Phase 3` 已完成阶段性验收，后续不再把新能力继续堆进 `data_service`
- `Phase 4：MCP / Agent 化收口` 已通过外部 HarnessOS 真实 stdio MCP 验收，当前作为回归基线保留
- 已补面向外部 Harness 工程的 MCP 生命周期 tools，让另一个工程能创建、构建、查询和治理独立知识库；真实验收已覆盖 create/import/build/poll/query/feedback/rules/review/plan/archive
- 已新增 v2 envelope tools，旧 tools 保持兼容
- 已将 build start 改为 workspace 级 queue + operation polling，避免同 workspace 并发写产物
- `Phase 5.1` GraphRAG 图谱质量面板已完成第一版，`distill` 与 `/knowledge` 的下一轮产品化工作转入低信号 source 回归抽查、GraphRAG owner 边界下沉和质量运营体验打磨

## 接下来的开发计划

完整剩余开发计划见 [REMAINING-DEVELOPMENT-PLAN-2026-04-30.md](./REMAINING-DEVELOPMENT-PLAN-2026-04-30.md)。当前建议按 Phase 顺序推进：

1. `Phase 4.1` MCP 质量治理 tools 兼容层：旧 tools 保持兼容，v2 tools 返回统一 envelope。
2. `Phase 4.2` MCP lifecycle tools：workspace/source/build/archive tools 支撑外部 Harness 管理独立知识库。
3. `Phase 4.3` build operation queue：同 workspace 串行排队，支持 cancel、blocked、failed/retryable 和 `server_interrupted` 恢复。
4. `Phase 4.4` 外部 Harness MCP 验收：已跑通 create -> import -> build -> poll -> query_v2 -> feedback_v2 -> rules_v2 -> review_v2 -> correction_plan_v2 -> archive。
5. `Phase 5.1` GraphRAG 图谱质量面板：已完成第一版。Graph snapshot 返回 `quality_diagnostics`，`/knowledge` 展示 top communities、弱主题、低价值 entity、孤立节点或低关系节点，并能一键带入质量反馈。
6. `Phase 5.2` Workspace & Source Manager：当前推进。补工作区创建/选择、目录绑定、导入式 source、source 台账、失败原因和低信号状态。
7. `Phase 5.3` Refresh Operation UI：接入异步 build queue，展示首次刷新/增量刷新、阶段进度、取消、重试和失败诊断。
8. `Phase 5.4` Source Distill Trace：按 source 展示原始文件、distill units、LLMWiki 页面和 GraphRAG 节点/社区的可追溯流水线。

### 已完成：Phase 3 收口

Phase 2 已于 2026-04-29 完成阶段性验收，验收记录见 [PHASE-2-ACCEPTANCE-REPORT.md](./PHASE-2-ACCEPTANCE-REPORT.md)。后续 `distill` 工作转为质量观察与低信号 source 覆盖率优化，不再阻塞 Phase 3。

### 已完成：Phase 2 收尾

1. 在第二轮产品/机构/赛事、工具/语言/公司类标题收缩基础上，继续做 `title-only / low-content source` 的实体归并
2. 收紧标题到主题的细粒度映射
3. 继续补强 `provenance / source profile` 的解释性

验收重点：

- 同一主题下不再轻易裂成多个弱实体
- 低正文 source 不再被过早打上 broad bucket 主题
- 高权重 unit 都能解释来源和保留原因

完整验收标准：

1. `distill` 已成为稳定中间契约层
2. title-only / low-content source 不再大面积退化为 `0 unit` 或误产强 `conclusion`
3. 主题映射不过早泛化到 broad bucket
4. CLI / API 调试与解释性够用
5. `llmwiki` 与 `graphrag` 稳定消费同一套中间层 contract
6. 基于 `row/deepseek_split` 的端到端验证稳定

2026-04-29 验收结果：

- `53 passed`
- 86 sources / 248 distilled units
- `title_derived_conclusion_count`: 0
- `zero_unit_count`: 8 / 86，作为后续质量观察项
- GraphRAG 查询 `VSCode` 命中核心实体，payload source 为 `app.graphrag.bridge`
- LLMWiki 页面检索链路可用，但页面标题自然度继续放入 LLMWiki 质量提升

### 已完成：Phase 3 收口

1. 固定 graph engine owner
2. 保持 `data_service` 只做 ingest 编排、contract staging 与统一查询入口
3. 保持 `knowledge/query|graph` 的公共结构稳定

验收重点：

- `data_service` 不再继续膨胀为第二套 GraphRAG
- `app.graphrag` 成为 graph query / community / materialization 的最终 owner

完整验收标准：

1. graph engine owner 固定到 `app.graphrag`
2. `data_service` 回到编排边界
3. `knowledge/query|graph` 的 graph query model 对外稳定
4. compat 逻辑收薄，不再散落在 `data_service`
5. `/knowledge`、CLI、HTTP、MCP 在 owner 固定后行为稳定
6. 基于 `row/deepseek_split` 的端到端验证稳定，图谱质量不明显倒退

2026-04-29 验收结果：

- `53 passed`
- 默认 `data_service ingest` 使用 `app.graphrag` owner
- 真实知识库端到端：86 sources / 248 distilled units / `llmwiki: success` / `graphrag: indexed`
- compat state：85 entities / 76 themes / 131 relationships
- boundary audit：`graph_index_execution=current_owner app.graphrag / status done`
- GraphRAG 查询 `VSCode` 命中核心实体，payload source 为 `app.graphrag.bridge`

### 当前推进：LLMWiki 质量与知识产品化

### 第三优先级：LLMWiki 质量提升

1. 提升 topic 聚合质量
2. 提升 source/topic 标题自然度
3. 让 `distill` 质量改进稳定传导到页面内容

验收重点：

- 页面标题不再大量停留在 `conversation id`
- topic 更接近真实主题，而不是文件名或泛标签

## Phase 2：正式化中间层

### 目标

把 `distill` 从内部产物变成正式中间层。

### 任务 2.1：目录与文件契约

输出物：

- `workspace/distill/` 的正式布局

建议内容：

- `sources/`
- `units/`
- `manifest.json`
- `schema.json`

验收标准：

- 不看代码也能理解 distill 产物结构

### 任务 2.2：增加调试和预览能力

当前状态：基础完成

输出物：

- distill 预览 API
- distill CLI

建议接口：

- `POST /api/v1/knowledge/distill`
- `python -m data_service distill --workspace ...`

验收标准：

- 可以直接查看某个 source 被提炼成了哪些 units

### 任务 2.3：输入边界固定

当前状态：基础完成

输出物：

- `llmwiki` 输入规范
- `graphrag` 输入规范

验收标准：

- 两个引擎不再偷偷依赖对方私有产物

## Phase 3：GraphRAG 职责收口

### 目标

把图算法从 `data_service` 中逐步剥离，回归 `graphrag` 专职负责。

### 任务 3.1：盘点两套 GraphRAG 能力

当前状态：基础完成（已可通过 boundary audit 查看当前重叠能力和迁移表）

输出物：

- `backend/data_service` 图能力清单
- `backend/app/graphrag` 能力清单
- 重叠与缺口表

验收标准：

- 明确哪些保留，哪些迁移，哪些废弃

### 任务 3.2：迁移或适配图索引逻辑

当前状态：推进中（已支持 owner 选择、runtime 落盘和真实 runner 接入；graph snapshot / query 已默认经 `app.graphrag.service` bridge 返回；默认 graph state 物化也已通过 `app.graphrag.service`）

输出物：

- 更明确的 Graph adapter 层

方案候选：

- 方案 A：把轻量图算法迁回 `app/graphrag`
- 方案 B：保留 `data_service` 轻图索引，但 `app/graphrag` 变成更明确的下游执行器

验收标准：

- `data_service` 不再长期承载核心图算法细节

### 任务 3.3：统一 graph query model

当前状态：基础完成（`DataService` snapshot / query 默认返回 `app.graphrag.bridge` payload）

输出物：

- 节点、边、社区、查询命中结构统一

验收标准：

- 前端和 MCP 不需要知道底层图实现差异

## Phase 4：MCP / Agent 化

### 目标

让知识底座可以被本地 Agent 与外部 Harness 工程稳定调用。当前 Phase 4 已通过外部 HarnessOS 真实 stdio MCP 验收，MCP provider 契约进入回归维护；开发主线转入 Phase 5 的 `/knowledge` 图谱质量产品化。

### 任务 4.1：精细化 MCP tools

当前状态：兼容层已完成

输出物：

- `knowledge_query`
- `knowledge_quality_summary`
- `knowledge_correction_plan`
- `knowledge_quality_feedback`
- `knowledge_correction_rules`
- `knowledge_review_correction_rule`
- `knowledge_ingest_v2`
- `knowledge_query_v2`
- `knowledge_quality_summary_v2`
- `knowledge_correction_plan_v2`
- `knowledge_quality_feedback_v2`
- `knowledge_correction_rules_v2`
- `knowledge_review_correction_rule_v2`

验收标准：

- Agent 可读取质量计划与 action impact
- Agent 可提交受控 feedback
- Agent 可按 enum 状态审核 correction rule
- Agent 可读取 LLMWiki 质量计划与影响范围，默认通过读时治理消费
- 旧 tools 响应格式保持兼容
- v2 tools 返回统一 envelope：`workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data`
- archived workspace 写类 v2 tools 返回 `blocked`

### 任务 4.2：路由策略沉淀

输出物：

- 查询路由规则
- agent 使用建议

验收标准：

- 阅读类问题优先走 `llmwiki`
- 关系类问题优先走 `graphrag`

### 任务 4.3：MCP 化知识库生命周期管理

当前状态：第一版已完成，进入契约固化

目标：

- 让外部 Harness 开发工程通过当前服务的 MCP server 创建和管理知识库
- 对齐 `../harnessOS/docs/architecture/data-service-mcp-codex-handoff.md`
- 已支撑 HarnessOS `data_service_mcp` connector ref 与 tool contract；真实 MCP client execution 已通过持久化 stdio session 完成验收
- 避免外部工程直接写本项目的 `workspace/row / llmwiki / graphrag / quality` 目录
- 把长任务从同步 tool call 拆成 `operation_id + status polling`

统一返回 envelope：

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

输出物：

- `knowledge_workspace_create`
  - input：`name / root / owner / tags`
  - 默认在 `DATA_SERVICE_WORKSPACE_ROOT` 下创建；显式 `root` 必须通过 allowlist 校验；返回 `workspace_path` 与 capabilities
- `knowledge_workspace_list`
  - input：`owner / tag / limit`
  - 只列 `DATA_SERVICE_WORKSPACE_ROOT` 下 workspace；`limit` 有上限
- `knowledge_workspace_describe`
  - input：`workspace_id` 或 `workspace`
  - 返回 layout、summary、engine status、latest build、quality status
- `knowledge_workspace_archive`
  - input：`workspace_id / reason`
  - 标记 read-only / archived，不物理删除数据
- `knowledge_source_import`
  - input：`workspace_id / paths / texts / metadata`
  - 校验 allowlist、realpath、symlink escape、file size、text length；计算 `sha256`；重复导入幂等
- `knowledge_source_list`
  - input：`workspace_id / status / limit`
  - 返回 `source_id / sha256 / title / status / low_signal / ingest_status`
- `knowledge_source_remove`
  - input：`workspace_id / source_id / reason`
  - 软删除或停用 source，不删除历史 build artifacts
- `knowledge_build_start`
  - input：`workspace_id / mode`
  - mode：`full / incremental / graph_only / llmwiki_only`
  - 立即返回 `operation_id`，记录 operation state，并进入 workspace 级 build queue，不长时间阻塞 MCP host
- `knowledge_build_status`
  - input：`workspace_id / operation_id`
  - 返回 `mode / stage / progress / error / retryable / artifacts`
- `knowledge_build_cancel`
  - input：`workspace_id / operation_id / reason`
  - 已完成则返回 completed + warning；可取消则进入 `cancelled`

operation stages：

- `source_import`
- `distill`
- `llmwiki`
- `graphrag`
- `quality_plan`
- `completed`
- `failed`
- `cancelled`

### 任务 4.4：Build operation queue

当前状态：第一版已完成

目标：

- 同一 workspace 的 build 串行排队，避免并发写 `llmwiki / graphrag / quality` 产物目录
- queued operation 可取消
- running operation 在阶段边界响应 cancel
- MCP server 中断遗留的 running operation 标记为 `failed / retryable / server_interrupted`

验收标准：

- 连续启动多个 build 时，operation 均返回 `queued`，并按创建顺序进入 running / terminal 状态
- `knowledge_build_status` 能返回 `queued / running / completed / failed / blocked / cancelled`
- `knowledge_build_cancel` 对 completed operation 返回 completed + warning
- unknown operation 返回 `blocked` envelope

### 任务 4.5：外部 Harness MCP 验收

当前状态：已通过外部 HarnessOS 真实 stdio MCP 调用验收

验收链路：

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

2026-05-02 真实验收结果：

- 外部 HarnessOS 通过持久化 `McpStdioSession` 在同一 MCP stdio 会话内完成完整链路
- `workspace_id`: `harnessosrealdataserviceacceptance4`
- `operation_id`: `op_fb639a7aee3c`
- final `status`: `ok`
- `warnings`: `[]`
- 实际覆盖链路：`create -> import -> build_start -> build_status(completed) -> query_v2 -> feedback_v2 -> correction_rules_v2 -> review_correction_rule_v2 -> correction_plan_v2 -> archive`
- 调用方仅依赖 opaque `workspace_id` 和 MCP tools，未直接读写内部 workspace
- 验收前需要确保 data_service venv 已完整安装 `backend/requirements.txt`，否则 build 阶段可能因 GraphRAG 依赖缺失失败

通过标准：

- 全链路只依赖 opaque `workspace_id`
- 不直接读写本项目内部 workspace 目录
- 业务可预期失败使用 `blocked` envelope
- 旧 tools 兼容测试继续通过
- 外部 HarnessOS 真实链路已通过，后续作为 Phase 4 回归验收保留

安全与兼容要求：

- workspace access 限制在 `DATA_SERVICE_WORKSPACE_ROOT` 或既有 explicit allowlist
- 每次 MCP call 独立校验 workspace，不隐式修改全局 workspace state
- source import 必须拒绝 path traversal 与 symlink escape
- 对 `limit / top_k / file count / text length / file size` 设置 bounded limit
- `knowledge_correction_plan` 读取不隐式写入，除非显式 `rebuild=true`
- 不移除、不重命名既有 MCP tools；保留 per-call `workspace` 支持
- v2 tools 新增统一 envelope，但不强制旧 tools 改格式

验收标准：

- 外部 Harness 工程可通过 MCP 完成“创建 workspace -> 导入 source -> 启动构建 -> 查询状态 -> 查询知识 -> 提交质量反馈 -> 审核规则 -> 读取 correction plan impact”
- 每个 lifecycle tool 返回统一 envelope：`workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data`
- v2 tools 返回统一 envelope，旧 tools 保持兼容
- workspace 与 source path 继续执行 allowlist、大小上限、去重和 symlink 防绕过校验
- 构建失败能定位到 `source_import / distill / llmwiki / graphrag / quality_plan` 阶段
- 同 workspace build 串行排队
- archived workspace 写操作返回 `blocked`
- server 中断遗留 running operation 返回 `failed / retryable / server_interrupted`
- 现有 `knowledge_ingest / knowledge_query / quality tools` 保持兼容
- 现有 `knowledge_query / quality` tools 已支持 `workspace_id`，外部 Harness 可用 opaque workspace id 完成查询、反馈、规则审核和读取 correction plan impact
- 当前验证：`python3.12 -m pytest backend/tests/test_data_service_mcp.py -q` 为 `14 passed`
- Data Service/API/MCP 回归：`74 passed, 14 skipped`
- LLMWiki 回归：`34 passed`
- 外部 HarnessOS fake MCP workflow：`1 passed`
- Pack/connector fake MCP：`14 passed`
- gateway/stdio 相关：`4 passed`
- 真实 data_service MCP E2E：最终 `status=ok`
- 混合类问题走 `data_service`

## Phase 5：知识产品化

### 目标

把 `/knowledge` 从调试工作台推进成真正顺手的个人知识库管理产品。当前 Phase 5 是主推进项；Phase 4 的 MCP lifecycle、v2 envelope、build queue、blocked / archived contract 与外部 Harness 链路作为回归基线保留。

Phase 5 的产品目标：

- 支持“目录即知识库”和“导入式知识库”
- 前端可创建/选择 workspace、绑定目录、导入文件、查看 source 台账
- 首次刷新和增量刷新走异步 operation，前端展示阶段、进度、错误、取消和重试
- source 详情能展示 `原始文件 -> distill units -> LLMWiki 页面 -> GraphRAG 节点/社区`
- 后续支持目录监听和待刷新队列

### 任务 5.1：GraphRAG 图谱质量面板

当前状态：✅ 第一版完成

输出物：

- top communities、弱主题、低价值 entity、孤立节点、低关系节点列表
- 每个图谱问题可一键带入 `mark_noise / merge_suggest / rename_suggest`
- approved 规则生成后，Graph snapshot/query 展示 filtered / rewritten / merged 影响计数
- GraphRAG native CLI preflight 继续保持 `healthy=true`

验收标准：

- `/knowledge` 能直接发现并审核图谱质量问题
- 图谱问题能进入 `feedback -> correction_rules -> review -> correction_plan -> read-time governance` 闭环
- 真实知识库复跑后，top communities 不出现明显长标题、废弃主题或重复实体

完成记录：

- Graph snapshot 新增 `quality_diagnostics.schema_version=1.0`
- 诊断类型覆盖 `top_communities / weak_communities / isolated_nodes / low_value_nodes`
- 诊断项包含 `feedback_target`，可直接进入 `needs_review / mark_noise / merge_suggest / rename_suggest`
- `/knowledge` 新增 GraphRAG diagnostics 面板，支持点击诊断项定位图节点或社区
- 自动化验证：图谱诊断定向 Data Service/API 测试 `3 passed`；Data Service/API 回归 `75 passed`；前端 `npm run build` 通过

### 任务 5.2：Workspace & Source Manager

当前状态：当前推进

输出物：

- 工作区创建/选择/最近使用入口
- 目录绑定入口，支持“目录即知识库”
- 文件导入入口，支持“导入式知识库”
- source 文件台账：`source_id / title / original_path / sha256 / ingest_status / low_signal / last_build_status`
- source 操作：停用、重新收录、查看失败原因、查看蒸馏详情
- HTTP API 对齐 MCP lifecycle 的 workspace/source tools

验收标准：

- 用户能在前端创建或选择一个知识库，不需要手动理解内部 workspace 目录
- 用户能绑定本地目录，并看到扫描文件数、可收录文件数、已收录文件数
- 用户能导入文件，并在 source 列表看到 pending/indexed/failed/disabled/low_signal
- 目录绑定模式不修改原始文件；导入式模式复制到 managed source area
- source list/remove/import 行为与 MCP lifecycle 保持一致

### 任务 5.3：Refresh Operation UI

当前状态：待开发

输出物：

- 首次刷新、增量刷新、只刷新 LLMWiki、只刷新 GraphRAG
- `operation_id / status / stage / progress / error / retryable` 状态卡
- 阶段展示：`source_import / distill / llmwiki / graphrag / quality_plan / completed`
- 操作：取消、重试、刷新状态、查看日志摘要
- HTTP API 对齐 MCP `knowledge_build_start/status/cancel`

验收标准：

- 点击刷新后页面不阻塞，立即进入 queued/running 状态
- 前端能轮询到 completed/failed/cancelled
- 同 workspace build 串行执行，不并发写产物目录
- failed/retryable 给出明确重试入口
- archived workspace 写操作返回 blocked

### 任务 5.4：Source Distill Trace

当前状态：待开发

输出物：

- source 详情流水线：原始文件、标题/正文抽取、distill units、LLMWiki 页面、GraphRAG 节点/社区
- 每个阶段展示状态、产物数量、低信号诊断、失败原因和跳转入口
- LLMWiki 页面和 GraphRAG 节点可反向跳回 source
- `profile_debug / title_normalization / low_signal reasons / unit_kind_counts` 转成产品化展示

验收标准：

- 任意 source 能看到 distill units 和 unit kind counts
- source 能跳转到对应 LLMWiki 页面
- source 能看到关联 GraphRAG 节点或社区
- 用户能判断该 source 是否被正确蒸馏，而不需要直接读 JSON

### 任务 5.5：Directory Watcher

当前状态：后续开发

输出物：

- 目录监听开关：开启、暂停、关闭
- 待刷新队列：新增、修改、删除、无法读取
- 变更摘要：影响 source 数、建议刷新模式、上次扫描时间
- 自动刷新开关作为后续增强项，默认关闭

验收标准：

- 绑定目录新增/修改/删除文件后，前端能展示待刷新变更
- 未经确认不自动改写知识产物
- 用户可从待刷新队列触发增量刷新

### 任务 5.6：知识质量面板

当前状态：第一版完成（`summary.json.quality.manual_feedback` 已展示人工反馈总量、action 分布、target type 分布；`summary.json.quality.correction_rules` 已展示规则总量、状态分布、规则类型分布）

输出物：

- source 覆盖率
- unverified 比例
- top topics
- top communities
- low-quality entities

### 任务 5.7：低信号 source 回归抽查

当前状态：低信号观测与保守补强第一版完成，当前真实知识库临时验收为 `zero_unit_count=0 / 86`、`title_derived_conclusion_count=0`。

输出物：

- title-only / low-content source 抽查记录
- LLMWiki topic/source 页面可读性抽查
- GraphRAG top communities 噪音回归记录

验收标准：

- `summary.json.quality.distill.zero_unit_count == 0`
- `title_derived_conclusion_count == 0`
- 低信号 source 的 topic 页收缩到核心主题，原始长标题只保留在 source 页用于追溯
- 抽查页面不出现“标题被当成事实/结论”的内容

### 任务 5.8：人工校正入口

当前状态：第一版完成（反馈先落盘，并可生成、审核校正规则；仍不直接改写知识产物）

输出物：

- 标题修正
- topic 合并
- 噪音实体屏蔽

第一版已完成：

- `POST /api/v1/knowledge/quality/feedback`
- `POST /api/v1/knowledge/quality/feedback/list`
- `/knowledge` 反馈面板
- `workspace/quality/feedback.jsonl`
- `workspace/quality/correction_rules.json`
- `POST /api/v1/knowledge/quality/corrections`
- `POST /api/v1/knowledge/quality/corrections/build`
- `POST /api/v1/knowledge/quality/corrections/review`

下一步：

- 继续观察 approved 规则在 LLMWiki topic 合并和 GraphRAG 噪音屏蔽中的实际影响
- 继续把 GraphRAG snapshot/query 的治理适配从 `data_service` 读时层下沉到 `app.graphrag.service`

## 依赖关系

必须遵守的依赖顺序：

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5

其中最关键的强依赖是：

- 没有稳定 `distill schema`，就不要急着做更复杂的 GraphRAG
- 没有收口 Graph 职责边界，就不要把更多功能堆进 `data_service`
- 没有统一 query model，就不要继续膨胀前端图交互逻辑

## 近期建议执行顺序

后续按这个顺序推进，不再漂移：

1. Phase 5.2 Workspace & Source Manager
- 工作区创建/选择
- 目录绑定与导入式 source 管理
- source 文件台账、状态、失败原因和低信号标记

2. Phase 5.3 Refresh Operation UI
- 首次刷新、增量刷新、取消、重试
- 前端接入 operation queue 和阶段进度

3. Phase 5.4 Source Distill Trace
- source 级蒸馏流水线
- source 与 LLMWiki 页面、GraphRAG 节点/社区互相追溯

4. Phase 5.5 Directory Watcher
- 监听绑定目录变化
- 展示待刷新队列

5. `LLMWiki` 质量提升与低信号回归
- topic/page 可读性继续抽查
- `distill` 质量向页面层传导

6. Phase 4 MCP 回归维护
- 外部 Harness 真实 MCP 链路可复跑
- lifecycle / v2 envelope / build queue / blocked contract 不退化
- MCP / Agent tools 第一版已完成，后续按真实使用反馈收紧契约

每次较大开发进展完成后，统一执行：

- 回归测试：`pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`
- 真实知识库端到端验证：`/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split`
- 同步更新 `PROJECT-BASELINE.md`、`ACCEPTANCE-PLAN.md`、`CURRENT-STATUS.md`、`current-vs-target-gap.md`、`2026-04-26-data-service-execution-roadmap.md`、`current_vs_target_flow.drawio`
- 如果架构边界发生变化，再同步 `01_current_architecture.drawio`、`02_target_architecture.drawio`

## 对应文档

- Data Service 文档入口：[README.md](./README.md)
- 项目最新基线：[PROJECT-BASELINE.md](./PROJECT-BASELINE.md)
- 验收计划：[ACCEPTANCE-PLAN.md](./ACCEPTANCE-PLAN.md)
- 当前状态：[CURRENT-STATUS.md](./CURRENT-STATUS.md)
- 差距分析：[current-vs-target-gap.md](./current-vs-target-gap.md)
- 当前架构图：[diagrams/01_current_architecture.drawio](./diagrams/01_current_architecture.drawio)
- 目标架构图：[diagrams/02_target_architecture.drawio](./diagrams/02_target_architecture.drawio)
- 历史总计划：[history/data-service-evolution-plan.md](./history/data-service-evolution-plan.md)
