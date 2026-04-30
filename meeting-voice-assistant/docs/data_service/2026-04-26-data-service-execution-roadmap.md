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
- `app.graphrag` runner preflight 增强：native CLI 不再只看 `which graphrag`，而是执行 `graphrag --version`；当前本机能明确诊断 `/usr/local/bin/graphrag` shim 指向已不存在的 `/tmp/graphrag_patched.py`
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
- `GraphRAG` CLI preflight 补强：真实知识库 ingest 当前返回 `reason=graphrag_cli_broken`、`cli_health.path=/usr/local/bin/graphrag`、`returncode=2`，并继续由 compat materializer 产出 `85 entities / 76 themes / 131 relationships`
- `LLMWiki` topic 质量第一轮：topic slug 与 title 共用产品/工具/专有名词优先的 anchor，拒绝动作词、数值残片和英文句子脚手架；真实知识库端到端验证 `bad_topic_titles=0`
- `LLMWiki` 页面结构第一轮：topic 页面改为 `Overview / Source Signals / Evidence Notes`，title-only source 不再重复写成 `Facts`；真实知识库验证 `topic_source_signal_pages=79`、`topic_facts_pages=0`
- `LLMWiki` source 页面结构第一轮：source 页面改为用 `Source Signals` 承载标题级材料，title-only source 不再重复写成 `Core Conclusion / Evidence`；真实知识库验证 `source_signal_pages=86`、`source_evidence_pages=0`
- `/knowledge` 质量反馈与人工校正入口第一版：workspace 新增 `quality/feedback.jsonl`，HTTP 新增 feedback submit/list，summary 质量字段新增 `manual_feedback`，前端可从页面、图节点、distill source、当前查询快速带入反馈对象
- 质量反馈到 draft 校正规则第一版：workspace 新增 `quality/correction_rules.json`，`rename_suggest / merge_suggest / mark_noise / needs_review` 可生成待审核规则，HTTP 新增 corrections list/build，前端可查看规则队列

当前下一步：

- `Phase 2` 与 `Phase 3` 已完成阶段性验收，后续不再把新能力继续堆进 `data_service`
- `distill` 调试与筛选能力已基本够用，下一步更应转向蒸馏质量与 source 内容理解质量
- 在蒸馏质量侧继续提升“标题型 source”和“低正文 source”的语义理解，当前弱语义标题的 `question/topic/entity/note/fact/risk` 已完成第一轮补齐，title-only 主题映射也完成第一轮去泛化，实体归并第二轮已覆盖产品/机构/赛事、工具/语言/公司类标题，`title_normalization` 已补解释链路；下一步继续扩展实体归并与标题到主题的细粒度映射
- topic 合并策略继续优化，draft 校正规则下一步补审核动作并接入规则消费
- 继续压弱实体与专有名词归并，重点处理 `日历`、`股市S1含义`、`日历App跨端协作技术专利方案`

## 接下来的开发计划

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

让知识底座可以被本地 Agent 稳定调用。

### 任务 4.1：精细化 MCP tools

输出物：

- `knowledge_query_llmwiki`
- `knowledge_query_graphrag`
- `knowledge_query_hybrid`
- `knowledge_summary`
- `knowledge_graph`

验收标准：

- 工具边界清晰，不再让 agent 猜 mode

### 任务 4.2：路由策略沉淀

输出物：

- 查询路由规则
- agent 使用建议

验收标准：

- 阅读类问题优先走 `llmwiki`
- 关系类问题优先走 `graphrag`
- 混合类问题走 `data_service`

## Phase 5：知识产品化

### 目标

把 `/knowledge` 从调试工作台推进成真正的知识工作台。

### 任务 5.1：图谱可视化升级

输出物：

- 更强的 community graph
- 更好的缩放、定位、聚类展示
- 更清晰的选中反馈

### 任务 5.2：知识质量面板

当前状态：第一版完成（`summary.json.quality.manual_feedback` 已展示人工反馈总量、action 分布、target type 分布；`summary.json.quality.correction_rules` 已展示 draft 规则总量、状态分布、规则类型分布）

输出物：

- source 覆盖率
- unverified 比例
- top topics
- top communities
- low-quality entities

### 任务 5.3：人工校正入口

当前状态：第一版完成（反馈先落盘，并可生成 draft 校正规则；仍不直接改写知识产物）

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

下一步：

- 增加 approve / reject / archive 审核动作
- 将 approved 规则接入 LLMWiki topic 合并和 GraphRAG 噪音屏蔽

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

1. `LLMWiki` 质量提升
- topic 聚合
- source/topic 标题自然度
- `distill` 质量向页面层传导

2. `distill` 质量观察
- 低信号 source 覆盖率
- 弱实体和专有名词归并
- 保持 title-only source 不误产强结论

3. `/knowledge` 产品化
- 图谱质量面板
- 人工校正入口
- MCP / Agent tools 精细化

每次较大开发进展完成后，统一执行：

- 回归测试：`pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q`
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
