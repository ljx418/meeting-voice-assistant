# Data Service 当前架构与目标架构差异

配套 draw.io：

- [01_current_architecture.drawio](./diagrams/01_current_architecture.drawio)
- [02_target_architecture.drawio](./diagrams/02_target_architecture.drawio)
- [current_vs_target_flow.drawio](./current_vs_target_flow.drawio)

## 1. 总体差异

当前项目已经形成一个可用的双引擎体系：

- `data_service` 已是统一入口
- `llmwiki` 已负责知识编译与阅读
- `graphrag` 当前已具备轻量图索引与社区图展示能力
- `/knowledge` 已是可用的双引擎工作台

但目标架构不是继续把能力堆进 `data_service`，而是要形成清晰边界：

- `data_service`：稳定的上游编排与服务边界
- `distill`：正式中间契约层
- `llmwiki`：知识编译层
- `graphrag`：图谱引擎层

## 2. 分层差异

| 层级 | 当前状态 | 目标状态 | 关键差距 |
| --- | --- | --- | --- |
| 用户入口 | `/knowledge`、CLI、HTTP、MCP 均可用 | 用户、前端、Agent 统一走 knowledge API / MCP | 入口已通，但路由与产品体验还未固化 |
| 上游编排 | `data_service` 已具备 workspace、summary、distill、graph/page/query API | `data_service` 只做上游编排、layout、summary、API、MCP | 当前仍承载部分 Graph 构建逻辑 |
| 中间层 | 已有 `distill`、source profile、weight、theme/entity 候选 | 版本化 `distill schema` 和目录契约 | 当前仍偏内部实现细节 |
| 知识编译 | `llmwiki` 已可输出 source/topic/conversation 页面，标题质量、topic anchor、topic/source 页面结构第一轮已完成 | `llmwiki` 只负责编译、页面、检索、provenance | 还需继续提升 topic 合并策略 |
| 图谱引擎 | `data_service` 侧轻量图索引链可用，`app/graphrag` 独立代码库仍在 | `graphrag` 负责图算法、社区、关系、查询 | 两套 Graph 路线尚未收口 |
| 产品层 | `/knowledge` 已可作为工作台使用 | `/knowledge` 升级为知识运营台 | 当前仍偏调试与巡检 |

## 3. 最重要的架构缺口

### 3.1 `distill` 缺口

当前 `distill` 已承担：

- 去噪
- source density 计算
- title flags
- entity/theme 候选
- source weight
- 高信息单元生成

但它仍缺：

- 更细粒度的调试与筛选能力

当前已完成：

- `schema_version`
- `workspace/distill/sources/`
- `workspace/distill/units/`
- `manifest.json`
- `schema.json`
- `POST /api/v1/knowledge/distill`
- `python -m data_service distill`
- `distill -> llmwiki/graphrag` 显式 handoff contract
- `workspace/llmwiki/state/input_contract.json`
- `workspace/graphrag/cache/input_contract.json`
- `POST /api/v1/knowledge/boundary`
- `python -m data_service boundary`
- capability migration table
- `graph_model_version`
- 统一的 `nodes / edges / communities / stats / hits` graph query model
- `graphrag_execution_owner`
- `workspace/graphrag/cache/execution_owner.json`
- `workspace/graphrag/cache/execution_request.json`
- `python -m data_service graphrag-execute`
- `POST /api/v1/knowledge/graphrag/execute`
- `app.graphrag.service.data_service_runner`
- native CLI preflight：`graphrag --version` 健康检查，区分 `graphrag_cli_not_found` 与 `graphrag_cli_broken`
- `app.graphrag.service.data_service_bridge`
- bridge 已承担 `DataService` 默认 graph snapshot / query 路径，并承接 community / materialization 入口
- `app.graphrag.service.data_service_materializer`
- `data_service` 默认 GraphRAG 适配器已改为调用 `app.graphrag.service.materialize_workspace_graph_state`，不再直接导入 materializer

### 3.2 GraphRAG 边界缺口

当前 graph 构建相关逻辑主要在 `backend/data_service`，这有两个问题：

- `data_service` 容易继续膨胀
- `backend/app/graphrag` 与 `data_service` 的图能力长期并存

目标应该是：

- `data_service` 负责上游组织
- `graphrag` 负责图引擎

### 3.3 产品层缺口

当前 `/knowledge` 已具备：

- summary 预览
- page 预览
- graph 图
- 三种 query

但还缺：

- 数据质量面板
- 更强的 graph 结构表达
- source/topic/community 的人工校正能力
- 更成熟的状态反馈与运营视角

### 3.4 LLMWiki 质量进展

已完成标题质量第一轮：

- 聊天 JSON 无显式标题时，可从首条 user question 派生可读标题
- mapping readable Markdown 不再把 UUID 写成 H1
- 普通 JSON 顶层 `title` 字段会使用字段值，不再把字段名 `title` 当成标题
- 两个汉字的中文短标题可作为有效 source/page 标题
- 真实知识库验证结果：`bad_source_titles = 0`、`bad_page_titles = 0`

已完成 topic 质量第一轮：

- topic anchor 优先识别产品、工具、代码语言、专有名词和计算主题
- topic slug 与 topic title 共用 anchor 判断
- `已安装 / 免费 / User seeks clarification / 税后 万` 等残片不再成为稳定 topic 标题
- 真实知识库验证结果：`bad_topic_titles = 0`

已完成页面结构第一轮：

- topic 页面使用 `Overview / Source Signals / Evidence Notes`
- title-only source 不再重复写成 `Facts`
- 真实知识库验证结果：`topic_source_signal_pages = 79`、`topic_facts_pages = 0`

已完成 source 页面结构第一轮：

- source 页面使用 `Source Signals` 承载标题级材料
- title-only source 不再重复写成 `Core Conclusion / Evidence`
- 真实知识库验证结果：`source_signal_pages = 86`、`source_evidence_pages = 0`

剩余差距转为：

- topic 合并策略
- 页面结构持续观察
- `/knowledge` 质量反馈和人工校正入口

## 4. 建议推进顺序

1. 基于 capability migration table 收口 `backend/data_service` 与 `backend/app/graphrag` 的职责边界
2. 基于已接入的 runner / bridge / materializer，以及已默认经 bridge 返回的 graph snapshot / query，继续把 graph execution owner 固定到 `app.graphrag`
3. 再继续做 `/knowledge` 的产品化升级

## 4.1 整体开发计划

| 阶段 | 目标 | 当前状态 | 下一步验收重点 |
| --- | --- | --- | --- |
| Phase 1 稳定双引擎工作流 | 固化当前可用版，降低图谱噪音，提升页面质量 | 已完成基础收口 | `distill v1.1` 已补 `risk/example/fact_candidate` 与低信号过滤；剩余是页面质量与聚合细节 |
| Phase 2 正式化中间层 | 让 `distill` 变成 first-class 中间层 | ✅ 2026-04-29 已完成阶段性验收 | `distill v1.1`、预览筛选、source profile 解释性、真实知识库端到端验收已通过；低信号 `0 unit` source 转为后续质量观察 |
| Phase 3 收口 GraphRAG | 明确谁负责图算法，减少 `data_service` 图逻辑 | ✅ 2026-04-29 已完成阶段性验收 | 默认 graph execution owner 已固定为 `app.graphrag`；graph query model、community assembly、materialization 均归 `app.graphrag.service`；`data_service` 保留编排和统一入口 |
| Phase 4 MCP / Agent 化 | 让本地 agent 稳定消费 knowledge capability | 部分完成；LLMWiki 标题质量切片已完成 | 精细化 MCP tools、固化路由策略，继续推进 topic 聚合质量 |
| Phase 5 知识产品化 | 把 `/knowledge` 从工作台推进为知识运营界面 | 质量反馈入口与 draft 校正规则第一版完成 | 图谱可视化、校正规则审核、规则消费 |

## 4.2 下一阶段开发计划

当前 `Phase 1` 已完成：

1. `distill schema version`
2. `workspace/distill/` 正式目录布局
3. 第二轮 Graphrag 噪音清理
4. LLMWiki 标题与 topic 质量提升
5. `summary.json` 质量指标补全
6. distill 预览 API / CLI
7. `distill -> llmwiki/graphrag` 输入边界固定
8. boundary audit 与 capability migration table
9. graph query model 第一版统一
10. graph execution owner 第一版收口（owner 选择 + runtime 落盘）
11. `app.graphrag` runner 第一版接入（自动尝试执行 + 显式 CLI/API）
12. `app.graphrag` bridge 第一版接管（app owner 模式下的 graph snapshot / query / community / materialization 入口）
13. `app.graphrag` materializer 迁入并完成 direct hookup（compat graph DB 写库逻辑本体）
14. `distill v1.1` 质量增强（`risk / example / fact_candidate`、低信号聊天过滤、`unit_kind_counts`）
15. `distill` 调试能力继续增强：预览接口与 CLI 已支持按 `kind / min_importance / llm_enriched_only / authority / source_weight / density` 筛选，并新增 `profile_debug / provenance_summary / units_by_kind / top_units`
16. `distill` 标题理解增强：source 标题优先读取内部真实标题；标题型空壳 source 已能保守地产出 `title-derived question`
17. `distill` 标题理解第二轮增强：title-only source 已不再把标题误写成 `conclusion`，并优先从标题抽核心实体；真实知识库已验证 `米醋/白醋`、`四代住宅`、`腱鞘炎`、`中国高层住宅`、`武汉` 这类标题实体可以稳定落到 `entity/topic/question`
18. `distill` 标题理解第三轮增强：title-only / low-content source 已能按标题语义补保守的 `note / fact_candidate / risk`；真实知识库已验证 `武汉周末小众游推荐`、`中国核电建设及并网时间数据`、`Bose耳机配对问题排查指南` 三类标题都能落到合适的 unit 类型
19. `distill` title-only 主题映射第一轮收口：低正文 source 已优先保留贴近标题本身的主题，不再提前注入 broad bucket 主题；真实知识库已验证 `中国核电建设及并网时间数据` 不再额外带 `投资`
20. 第四轮 GraphRAG 噪音治理：`unit.tags -> entity/theme` 回流已切断，混合说明型候选不再轻易回灌进图
21. 第五轮 GraphRAG 噪音治理：数值驱动标题与残片已进入专门清洗规则，年龄/金额/续航类长尾碎片不再轻易进入主题
22. `distill` 实体归并第一轮：title-only / low-content source 的标题实体已开始收缩到核心实体；真实知识库已验证 `日历App跨端协作技术专利方案 -> 日历`、`股市S1含义解析 -> 股市S1`
23. `distill` 实体归并第二轮启动：产品/机构/赛事类标题继续收缩到核心实体；真实知识库已验证 `小米SU7玻璃防晒性能解析 -> 小米SU7`、`中国民营航天公司上市进展及股东情况 -> 中国民营航天公司`、`美加墨世界杯小组赛时间 -> 美加墨世界杯`，并压掉裸 `SU7` 重复节点；`profile_debug` 已补 `title_only_excerpt / entity_candidates / theme_labels` 解释字段
24. `distill` 标题到主题细粒度映射继续收紧：工具/语言/公司类 title-only source 不再把安装状态、代码示例、背景介绍、`中的...` 说明片段落成主题或实体；真实知识库已验证 `已安装VSCode选项验证 -> VSCode`、`TypeScript中的多态与复态解析 -> TypeScript`、`鸿蒙手机Python自动化测试代码示例 -> Python / 鸿蒙手机`、`超聚变公司股权结构及背景介绍 -> 超聚变公司`
25. `distill` source profile 解释性增强：`profile_debug.title_normalization` 已能解释 title-only 标题收缩过程，包含 `raw_title / normalized_entities / normalized_themes / dropped_fragments / rules_applied`；`schema.json` 已把 `profile_debug` 纳入 source record 字段
26. `LLMWiki` 标题质量第一轮：聊天 JSON / mapping readable Markdown / 普通 JSON `title` 字段 / 中文短标题均已补标题派生与清洗回归；真实知识库端到端验证 `bad_source_titles=0`、`bad_page_titles=0`
27. `GraphRAG` native CLI preflight：runner 已从单纯 `which graphrag` 升级为执行 `graphrag --version`；当前本机明确诊断为 `graphrag_cli_broken`，原因是 `/usr/local/bin/graphrag` 指向已不存在的 `/tmp/graphrag_patched.py`，compat state 仍稳定 indexed
28. `LLMWiki` topic 质量第一轮：topic anchor 优先识别产品/工具/专有名词，拒绝动作词、数值残片和英文句子脚手架；真实知识库端到端验证 `bad_topic_titles=0`，样例 `VSCode / 小米SU7 / 股市S1 / 税前工资 / creample / 等额本息月供` 收缩通过
29. `LLMWiki` 页面结构第一轮：topic 页面区分 `Overview / Source Signals / Evidence Notes`，title-only source 不再重复写成 `Facts`；真实知识库验证 `topic_source_signal_pages=79`、`topic_facts_pages=0`
30. `LLMWiki` source 页面结构第一轮：source 页面使用 `Source Signals` 承载标题级材料，title-only source 不再重复写成 `Core Conclusion / Evidence`；真实知识库验证 `source_signal_pages=86`、`source_evidence_pages=0`
31. `/knowledge` 质量反馈与人工校正入口第一版：workspace 新增 `quality/feedback.jsonl`，API 新增 feedback submit/list，summary 质量字段新增 `manual_feedback`，前端可从页面、图节点、distill source、当前查询快速带入反馈对象
32. 质量反馈到 draft 校正规则第一版：workspace 新增 `quality/correction_rules.json`，`rename_suggest / merge_suggest / mark_noise / needs_review` 可生成待审核规则，前端可查看规则队列

下一阶段优先继续做：

1. 继续优化 topic 合并策略，并为 draft 校正规则补 approve / reject / archive 审核动作
2. 继续观察低信号 `0 unit` source，在不误产强 `conclusion` 的前提下提高覆盖率
3. 继续压弱实体与专有名词归并，如 `日历`、`股市S1含义`、`日历App跨端协作技术专利方案`

建议按这个顺序执行：

1. 回到 `llmwiki` 页面质量
- 提升 topic 聚合质量
- 提升 source/topic 标题自然度
- 让 `distill` 改善稳定传导到页面可读性

2. 并行观察 `distill` 低信号 source
- 保持 title-only source 不误产强 `conclusion`
- 对阶段验收中剩余的 8 个 `0 unit` source 逐步补足保守 unit

### Phase 2 验收标准

当前状态：✅ 2026-04-29 已完成阶段性验收，记录见 [PHASE-2-ACCEPTANCE-REPORT.md](./PHASE-2-ACCEPTANCE-REPORT.md)。

1. `distill` 已成为稳定中间契约层
- 目录、schema、manifest、source/unit 文件结构固定
- 不看代码也能理解中间层产物

2. title-only / low-content source 不再大面积退化
- 不再频繁产出 `0 unit`
- 不再误产强 `conclusion`
- 能稳定落到保守的 `question / entity / topic / note / fact_candidate / risk`

3. 主题映射不过早泛化
- 低正文 source 不再过早落到 `投资 / 宏观政策 / 软件开发 / AI学习`
- 主题优先贴 source 自身语义

4. 调试与解释性够用
- CLI / API 支持精细筛选
- `profile_debug / provenance_summary / units_by_kind / top_units` 能解释产物来源

5. 双引擎消费同一套中间层
- `llmwiki` 与 `graphrag` 都稳定消费同一套 contract
- 修改 `distill` 不会破坏任一引擎的输入边界

6. 真实知识库验证稳定
- 用 `row/deepseek_split` 端到端验证
- `distill` 产物可读、可追溯、可解释

### Phase 3 验收标准

当前状态：✅ 2026-04-29 已完成阶段性验收，记录见 [PHASE-3-ACCEPTANCE-REPORT.md](./PHASE-3-ACCEPTANCE-REPORT.md)。

1. graph owner 固定
- `app.graphrag` 成为 graph build / query / community / materialization 的最终 owner

2. `data_service` 回到编排边界
- 只保留 ingest / layout / summary / API / MCP / owner routing / contract
- 不再维护第二套 graph 核心实现

3. graph query model 对外稳定
- `knowledge/query|graph` 继续使用统一结构
- `nodes / edges / communities / stats / hits` 不发生无控制漂移

4. compat 逻辑收薄
- `community assembly / compat materialization` 已收回 `app.graphrag.service`
- fallback 仅保留最薄兼容层

5. 上层入口保持稳定
- `/knowledge`、CLI、HTTP、MCP 在 owner 固定后行为不退化

6. 真实知识库验证稳定
- 用 `row/deepseek_split` 端到端验证
- 图谱质量、头部社区、整体收敛方向不明显倒退

验收标准：

- `row/deepseek_split` 全量 ingest 稳定
- `summary / llmwiki / graphrag` 产物稳定可读
- `废弃于` 不再进入主题和实体
- 头部社区能稳定出现 `AI学习`、`投资`、`宏观政策`
- 页面标题不再大量停留在 `conversation id`
- `distill` 产物具备稳定目录与基础契约

### Roadmap Acceptance Matrix

#### 已完成 / Done

- `Phase 1` 基础收口已完成
- `Phase 2` distill 正式中间层已完成阶段性验收
- `Phase 3` GraphRAG 职责收口已完成阶段性验收
- `distill schema / preview / contract / boundary audit / graph query model / runner / bridge / materializer` 已接通
- `app.graphrag` 已接入 graph execution owner、runner、bridge、direct materializer hookup

#### 已完成 MVP / Done MVP

- `distill v1.1`
- title-only source 三轮质量增强
- title-only 主题去泛化第一轮
- title-only 实体归并第一轮

#### 当前推进 / In Progress

- `LLMWiki`：topic 聚合、source/topic 标题自然度、`distill` 质量向页面层传导
- `distill`：继续观察低信号 `0 unit` source，不作为 Phase 3 阻塞项

#### 统一验收规则 / Acceptance Rules

- 必须跑回归测试：`pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q`
- 必须用 `/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split` 做真实知识库端到端验证
- 每次较大进展后必须同步更新 `PROJECT-BASELINE.md`、`ACCEPTANCE-PLAN.md`、`CURRENT-STATUS.md`、`current-vs-target-gap.md`、`2026-04-26-data-service-execution-roadmap.md`、`current_vs_target_flow.drawio`
- 如果架构边界发生变化，再同步 `01_current_architecture.drawio` 与 `02_target_architecture.drawio`

## 5. 当前架构图与目标架构图差异

| 主题 | 当前架构图应表达 | 目标架构图应表达 | 差距 |
| --- | --- | --- | --- |
| data_service | 编排 + distill + summary + 部分 graph 构建 | 稳定的上游编排层 | 需要减轻图算法负担 |
| distill | 已有高信息单元但未正式契约化 | 明确 schema、manifest、目录布局 | 需要版本化 |
| llmwiki | 已可读、可检索、可追溯 | 只专注知识编译与阅读 | 页面质量还需提升 |
| graphrag | 当前以轻量图索引链为主 | 收口为正式图引擎层 | 需要统一双路线 |
| knowledge UI | 已是工作台 | 升级为知识运营台 | 需要更强的数据质量反馈 |
