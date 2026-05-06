# Data Service 当前架构与目标架构差异

配套 draw.io：

- [01_current_architecture.drawio](./diagrams/01_current_architecture.drawio)
- [02_target_architecture.drawio](./diagrams/02_target_architecture.drawio)
- [current_vs_target_flow.drawio](./current_vs_target_flow.drawio)
- [PERSONAL-KNOWLEDGE-PRODUCT-GAP-2026-05-06.md](./PERSONAL-KNOWLEDGE-PRODUCT-GAP-2026-05-06.md)

## 1. 总体差异

当前项目已经形成一个可用的双引擎体系：

- `data_service` 已是统一入口
- `llmwiki` 已负责知识编译与阅读
- `graphrag` 当前已具备轻量图索引与社区图展示能力
- `/knowledge` 已是可用的双引擎工作台

但新的产品目标已经不只是“能展示双引擎产物”，而是要做成一个顺手的个人知识库管理产品。目标用户不应该理解内部 `workspace/summary/llmwiki/graphrag/distill` 目录，也不应该手动判断哪些文件已经收录、哪些构建失败、哪些产物来自哪个 source。

目标产品形态固定为：

- 同时支持“目录即知识库”和“导入式知识库”
- 首次刷新和增量刷新先以手动确认为主，再提供目录监听和待刷新队列
- 前端展示工作区、source 文件、构建任务、LLMWiki 摘要、GraphRAG 图谱和 source 级蒸馏流水线
- 原始绑定目录只读，导入式 source area 由系统管理

架构上仍然不能继续把能力堆进 `data_service`，而是要形成清晰边界：

- `data_service`：稳定的上游编排与服务边界
- `distill`：正式中间契约层
- `llmwiki`：知识编译层
- `graphrag`：图谱引擎层
- `/knowledge`：个人知识库管理产品入口

## 2. 分层差异

| 层级 | 当前状态 | 目标状态 | 关键差距 |
| --- | --- | --- | --- |
| 用户入口 | `/knowledge`、CLI、HTTP、MCP 均可用；前端有 workspace 路径输入和 ingest 按钮 | 用户在网页完成工作区创建/选择、目录绑定、文件导入、首次刷新、增量刷新、结果浏览 | 入口已通，但还像工程控制台；缺工作区向导、最近工作区、source 管理和刷新任务体验 |
| 上游编排 | `data_service` 已具备 workspace、summary、distill、graph/page/query API，并已补 workspace/source allowlist；MCP lifecycle 已有 workspace/source/build tools | `data_service` 只做上游编排、layout、summary、API、MCP，并向前端提供等价 lifecycle HTTP API | MCP lifecycle 已成熟，但浏览器侧 HTTP/API 和 UI 尚未完整承接 |
| 中间层 | 已有 `distill`、source profile、weight、theme/entity 候选 | 版本化 `distill schema` 和目录契约 | 当前仍偏内部实现细节 |
| 知识编译 | `llmwiki` 已可输出 source/topic/conversation 页面，读时消费 approved quality plan；默认 ingest 不再自动改写 markdown | `llmwiki` 只负责编译、页面、检索、provenance | 后续仅在明确产品需求下设计可回滚 materialize 流程 |
| 图谱引擎 | graph snapshot/query 已由 `app.graphrag.service` bridge 提供，data_service 只做读时 quality plan 展示适配 | `graphrag` 负责图算法、社区、关系、查询 | quality plan 的 graph 适配仍需继续沉入 GraphRAG owner |
| 产品层 | `/knowledge` 已可作为工作台使用，能展示 summary、query、LLMWiki、GraphRAG 和质量反馈 | `/knowledge` 升级为个人知识库管理产品 | 当前仍偏调试与巡检；缺 source 文件台账、构建任务台账、source 级蒸馏流水线和目录监听 |

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
- native CLI preflight：`graphrag --help` 健康检查，区分 CLI 缺失、preflight 失败与 native index 阶段失败
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

### 3.3 个人知识库管理产品缺口

当前 `/knowledge` 已具备：

- summary 预览
- page 预览
- graph 图
- 三种 query
- distill source/unit 预览
- 质量反馈、规则审核、消费计划和 GraphRAG diagnostics

但距离“顺手的个人知识库管理产品”仍有以下真实 gap：

#### Gap A：Workspace 选择、创建和最近使用

当前：

- 前端支持手动输入 workspace 绝对路径
- 后端 HTTP 接口按 workspace path 工作
- MCP lifecycle 已支持 `knowledge_workspace_create/list/describe/archive`

目标：

- 前端提供工作区创建/选择向导
- 用户可以选择“绑定本地目录”或“导入文件到系统管理区”
- 展示最近工作区、工作区路径、source 数、最近刷新时间、构建状态和健康状态
- 用户无需理解内部 workspace 目录结构

差距：

- HTTP API 还没有等价 MCP lifecycle 的 workspace create/list/describe/archive 能力
- `/knowledge` 没有最近工作区、工作区向导、绑定目录说明和工作区健康摘要

#### Gap B：Source 文件管理台账

当前：

- `ingest` 支持目录递归展开
- MCP source lifecycle 已支持 import/list/remove
- summary 能展示部分统计

目标：

- 前端展示 source 文件列表
- 每个 source 显示 `pending / indexed / failed / disabled / low_signal`
- 展示原始路径、导入方式、sha256、重复状态、文件大小、最后修改时间、最近构建结果
- 支持停用 source、重新收录 source、查看失败原因

差距：

- HTTP 和 `/knowledge` 尚未完整展示 source manifest
- 目录扫描与导入式 source area 没有统一出现在前端
- 用户无法从 UI 判断哪些文件已被收录、哪些文件失败或被跳过

#### Gap C：首次刷新、增量刷新和异步任务

当前：

- 前端有同步 `ingest` 按钮
- MCP 已有 `knowledge_build_start/status/cancel` 和 workspace 级 queue
- build operation 可返回 `queued / running / completed / failed / blocked / cancelled`

目标：

- 前端支持首次刷新、增量刷新、只刷新 LLMWiki、只刷新 GraphRAG
- 刷新动作立即返回 operation id，页面轮询阶段进度
- 展示 `source_import / distill / llmwiki / graphrag / quality_plan / completed`
- 支持取消、重试、失败诊断和安全提示

差距：

- 浏览器侧尚未接入 MCP build queue
- HTTP API 缺少 lifecycle build start/status/cancel 等价接口
- 现在的同步 ingest 不适合长任务，也不适合作为产品化首次刷新体验

#### Gap D：Source 级蒸馏流水线

当前：

- distill 预览能查看 source、units、profile_debug、low_signal
- LLMWiki 页面和 GraphRAG 图谱可以分别查看

目标：

- 用户点击一个 source 后看到完整流水线：
  `原始文件 -> 抽取/标题识别 -> distill units -> LLMWiki 页面 -> GraphRAG entity/theme/community`
- 每个阶段显示状态、产物数量、关键诊断和跳转入口
- 从 LLMWiki 页面或 GraphRAG 节点可以反向跳回 source

差距：

- 当前 distill 视图偏调试字段，不是 source 级过程图
- source 与 LLMWiki page、GraphRAG node/community 的关联还没有产品化展示
- 用户难以理解“这篇文档如何变成摘要、页面和图谱节点”

#### Gap E：目录监听和待刷新队列

当前：

- 项目有历史 file watcher 能力，但 Data Service `/knowledge` 产品链路没有目录监听状态
- 用户需要手动刷新

目标：

- 绑定目录后可开启监听
- 前端展示新增、修改、删除的待刷新文件
- 默认不自动重建，先提示用户确认刷新；后续可开启自动刷新

差距：

- 缺少 Data Service 侧 watcher 状态、变更队列和前端展示
- 缺少“监听中 / 暂停 / 有 N 个变更待刷新”的产品状态

#### Gap F：空状态、错误状态和上手引导

当前：

- API key 缺失或无 workspace 数据时会进入空数据状态
- 页面上已有很多能力块，但初次使用路径不够明确

目标：

- 首次打开时明确引导：创建/选择工作区 -> 绑定目录或导入文件 -> 首次刷新 -> 浏览摘要/图谱/蒸馏过程
- 错误状态给出配置、权限、路径、API key、构建失败的可操作说明

差距：

- 缺少面向普通用户的空状态和故障恢复路径
- 当前信息架构更适合开发者巡检，不适合第一次使用的个人知识库用户

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

- topic/page 可读性持续抽查
- 页面结构持续观察
- `/knowledge` 图谱质量面板第一版已完成，知识运营体验仍需真实数据打磨
- quality plan 的 graph 适配继续向 GraphRAG owner 下沉

## 4. 建议推进顺序

1. 保持 Phase 4 MCP lifecycle / v2 envelope / build queue / blocked contract 作为回归基线
2. Phase 5.2-5.5 第一版已完成，继续把 `/knowledge` 从工程工作台打磨为顺手的个人知识库管理产品
3. 继续真实数据回归 Workspace & Source Manager、Refresh Operation UI、Source Distill Trace 和 Directory Watcher
4. 补强目录 watcher 增强项：后台常驻监听、暂停/恢复、自动刷新开关和删除 source 后续处理向导
5. 持续把 quality plan 的 graph 适配从 `data_service` 读时适配收回到 `app.graphrag` owner 边界

## 4.1 整体开发计划

| 阶段 | 目标 | 当前状态 | 下一步验收重点 |
| --- | --- | --- | --- |
| Phase 1 稳定双引擎工作流 | 固化当前可用版，降低图谱噪音，提升页面质量 | 已完成基础收口 | `distill v1.1` 已补 `risk/example/fact_candidate` 与低信号过滤；剩余是页面质量与聚合细节 |
| Phase 2 正式化中间层 | 让 `distill` 变成 first-class 中间层 | ✅ 2026-04-29 已完成阶段性验收 | `distill v1.1`、预览筛选、source profile 解释性、真实知识库端到端验收已通过；低信号 `0 unit` source 转为后续质量观察 |
| Phase 3 收口 GraphRAG | 明确谁负责图算法，减少 `data_service` 图逻辑 | ✅ 2026-04-29 已完成阶段性验收 | 默认 graph execution owner 已固定为 `app.graphrag`；graph query model、community assembly、materialization 均归 `app.graphrag.service`；`data_service` 保留编排和统一入口 |
| Phase 4 MCP / Agent 化 | 让本地 agent 和外部 Harness 工程稳定消费 knowledge capability | ✅ 外部 HarnessOS 真实 stdio MCP 验收已通过 | lifecycle tools、v2 envelope tools、workspace build queue、blocked / archived / server_interrupted contract 已完成第一版；后续作为回归链路保留 |
| Phase 5 知识产品化 | 把 `/knowledge` 从工作台推进为个人知识库管理产品 | 🔄 Phase 5.1 第一版完成，Phase 5.2 当前推进 | Workspace & Source Manager、异步刷新任务、source 级蒸馏流水线、目录监听、质量运营体验 |

## 4.2 下一阶段开发计划

详细剩余开发计划见 [REMAINING-DEVELOPMENT-PLAN-2026-04-30.md](./REMAINING-DEVELOPMENT-PLAN-2026-04-30.md)。

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
27. `GraphRAG` native CLI preflight：runner 已从单纯 `which graphrag` 升级为执行真实 CLI 健康检查；本机 `/usr/local/bin/graphrag` 已从临时 `/tmp/graphrag_patched.py` wrapper 恢复为 `graphrag.cli.main:app` 真实入口；GraphRAG 3.0.8 不支持全局 `--version`，preflight 已改为 `graphrag --help`，当前 healthcheck 可返回 `healthy=true`
28. `LLMWiki` topic 质量第一轮：topic anchor 优先识别产品/工具/专有名词，拒绝动作词、数值残片和英文句子脚手架；真实知识库端到端验证 `bad_topic_titles=0`，样例 `VSCode / 小米SU7 / 股市S1 / 税前工资 / creample / 等额本息月供` 收缩通过
29. `LLMWiki` 页面结构第一轮：topic 页面区分 `Overview / Source Signals / Evidence Notes`，title-only source 不再重复写成 `Facts`；真实知识库验证 `topic_source_signal_pages=79`、`topic_facts_pages=0`
30. `LLMWiki` source 页面结构第一轮：source 页面使用 `Source Signals` 承载标题级材料，title-only source 不再重复写成 `Core Conclusion / Evidence`；真实知识库验证 `source_signal_pages=86`、`source_evidence_pages=0`
31. `/knowledge` 质量反馈与人工校正入口第一版：workspace 新增 `quality/feedback.jsonl`，API 新增 feedback submit/list，summary 质量字段新增 `manual_feedback`，前端可从页面、图节点、distill source、当前查询快速带入反馈对象
32. 质量反馈到 draft 校正规则第一版：workspace 新增 `quality/correction_rules.json`，`rename_suggest / merge_suggest / mark_noise / needs_review` 可生成待审核规则，前端可查看规则队列
33. 质量规则审核第一版：HTTP 新增 `quality/corrections/review`，draft 规则可进入 `approved / rejected / archived`，重新 build 会保留既有审核状态
34. approved 校正规则消费第一版：workspace 新增 `quality/correction_plan.json`，HTTP 新增 `quality/corrections/plan`，Graph 快照、GraphRAG query、LLMWiki read page 读取时会应用 suppress / rename / merge 展示治理；action impact 已记录 Graph nodes / Graph edges / LLMWiki pages 并在 `/knowledge` 展示；GraphRAG query 已返回 `quality_plan.query_hit_impact` 并在查询卡片展示 filtered / rewritten 计数
35. LLMWiki 读时消费第一版：LLMWiki ingest/compile 默认不改写生成 markdown；read page / query 读取时应用 quality plan；rename / merge 改写展示文本；suppress 在展示层过滤但不删除页面
36. 质量规则回滚第一版：规则状态新增 `revoked`，approved 规则可撤回并立即从 `correction_plan.json` 移除，非 approved 规则可重新置为 draft
37. topic 合并策略第一版：approved merge 命中旧 topic/page markdown 时写入 `quality_merged_into`，canonical 页面追加 `Merged Topic Signals`，旧页面不删除以保护既有链接
38. MCP / Agent 质量治理 tools 安全收紧版：MCP stdio server 新增 `knowledge_quality_summary / knowledge_correction_plan / knowledge_quality_feedback / knowledge_correction_rules / knowledge_review_correction_rule`，Agent 可读取质量计划与影响范围、提交受控反馈、审核规则；读取 correction plan 不再隐式写 workspace，query/list 参数有上限
39. distill 低信号 source 观测与保守补强第一版：source profile 新增 `zero_unit / low_signal`，manifest、summary 与 `/knowledge` 新增 `zero_unit_count / zero_unit_sources / low_signal_reason_counts / title_fallback_source_counts` 展示；基于真实 reasons 补充保守标题规则后，临时验收 `zero_unit_count=0 / 86` 且 `title_derived_conclusion_count=0`
40. 安全与质量回归修复：`backend/app/.env` 和 `.DS_Store` 已从 git 跟踪移除并新增 `.env.example`；knowledge API 默认要求 API key 或 dev bypass；workspace/source allowlist 与目录 symlink 防绕过已补；MCP 增加参数上限；CORS 默认收紧；前端 Markdown 预览禁用 raw HTML 并净化输出；LLMWiki query 读时消费 approved quality plan；Graph community policy、merge 去重、stats 语义与 `/summary` 读路径副作用已修复。回归：`73 passed, 3 skipped`，`npx vite build` 通过
41. 外部 HarnessOS MCP 真实验收通过：HarnessOS 通过持久化 stdio MCP session 调用 `data_service.mcp_stdio`，完成 `knowledge_workspace_create -> knowledge_source_import -> knowledge_build_start -> knowledge_build_status -> knowledge_query_v2 -> knowledge_quality_feedback_v2 -> knowledge_correction_rules_v2 -> knowledge_review_correction_rule_v2 -> knowledge_correction_plan_v2 -> knowledge_workspace_archive`；验收 `workspace_id=harnessosrealdataserviceacceptance4`、`operation_id=op_fb639a7aee3c`、最终 `status=ok`、`warnings=[]`

下一阶段按个人知识库管理产品化推进，Phase 4 外部 MCP 验收链路保留为回归基线：

1. `Phase 5.1` GraphRAG 图谱质量面板：✅ 第一版完成。Graph snapshot 已返回 `quality_diagnostics`，`/knowledge` 已展示 top communities、弱主题、低价值 entity、孤立节点或低关系节点，并能一键带入质量反馈。
2. `Phase 5.2` Workspace & Source Manager：✅ 第一版完成。已补工作区创建/选择、目录绑定、导入式 source、source 台账、低信号状态、停用和蒸馏详情入口。
3. `Phase 5.3` Refresh Operation UI：✅ 第一版完成。HTTP 已接入异步 build queue，前端已展示首次刷新/增量刷新、阶段进度、取消、重试和失败诊断。
4. `Phase 5.4` Source Distill Trace：✅ 第一版完成。已按 source 展示原始文件、distill units、LLMWiki 页面和 GraphRAG 节点/社区的可追溯流水线。
5. `Phase 5.5` Directory Watcher：✅ 第一版完成。已新增 `/knowledge/directories/scan`，对绑定目录展示新增、修改、删除、无法读取的待刷新队列；扫描快照持久化到 `workspace/lifecycle/directory_scan.json`；默认手动确认刷新，新增/修改文件可进入 `incremental` refresh，删除文件先提示停用或重建。
6. `Phase 5.6` Low Signal Audit：✅ 审计面板第一版完成。已新增 `/knowledge/quality/low-signal-audit`，把 `zero_unit_count`、`title_derived_conclusion_count`、标题派生强语义 unit、LLMWiki 长标题泄漏和 GraphRAG top community 长标题泄漏纳入可视化回归；前端已展示检查项、状态和风险样本。真实知识库当前暴露 `disallowed_title_derived_count=33`，集中在标题派生 `topic_candidate`，这是下一步质量治理的真实缺口。
7. `Phase 4 回归`：继续复跑 create -> import -> build -> poll -> query_v2 -> feedback_v2 -> rules_v2 -> review_v2 -> correction_plan_v2 -> archive，确保外部 Harness 调用契约不退化。

下一阶段统一验收重点：

- `row/deepseek_split` 全量 ingest 稳定
- LLMWiki success，GraphRAG indexed
- `summary.json.quality.distill.zero_unit_count == 0`
- `title_derived_conclusion_count == 0`
- top communities 没有明显噪音主题、长标题主题或废弃主题
- `/knowledge` 能完成反馈、规则生成、审核、消费计划、撤回闭环
- 外部 Harness 工程已通过 MCP 完成独立测试知识库的创建、source 导入、构建状态轮询、查询和质量治理；后续回归继续保持该链路可复跑
- lifecycle tools 返回 `workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data` envelope
- v2 tools 返回同一 envelope，旧 `knowledge_query / quality` tools 保持兼容并继续支持 `workspace_id`
- lifecycle 业务错误返回 `blocked` envelope
- 同 workspace build 串行排队，不并发写产物目录
- archived workspace 写操作返回 `blocked`
- 当前本项目侧 MCP 自动化验收：`14 passed`
- Phase 5.6 定向 HTTP/API 回归：`backend/tests/test_data_service_api.py` 为 `10 passed`
- Data Service/API/MCP 历史回归：`74 passed, 14 skipped`
- LLMWiki 回归：`34 passed`
- GraphRAG native CLI preflight 返回 `healthy=true`
- data_service venv 完整安装 `backend/requirements.txt`，避免真实 MCP build 因 GraphRAG 依赖缺失失败

建议按这个顺序执行：

1. Phase 5 `/knowledge` 产品化
- GraphRAG 图谱质量面板第一版已完成，后续按真实数据继续校准诊断排序和反馈闭环
- 低信号 source 内容级人工抽查
- topic 聚合与页面可读性继续提升

2. 并行观察 `distill` 低信号 source
- 保持 title-only source 不误产强 `conclusion`
- 保持当前 `zero_unit_count=0 / 86`
- 抽查新增保守 unit 是否没有把标题误写成事实或结论

3. 保持 Phase 4 MCP 回归
- 旧 tools 兼容
- v2 envelope
- lifecycle tools
- build queue
- 外部 Harness 验收链路继续可复跑

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

- `Phase 5`：Phase 5.1-5.6 第一版已完成，当前推进低信号 source 内容级抽查、GraphRAG quality owner 边界下沉和真实知识库体验打磨
- `LLMWiki`：topic/page 可读性抽查、`distill` 质量向页面层传导
- `distill`：保持 `zero_unit_count=0 / 86` 与 `title_derived_conclusion_count=0`

#### 统一验收规则 / Acceptance Rules

- 必须跑回归测试：`pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`
- 必须用 `/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split` 做真实知识库端到端验证
- 每次较大进展后必须同步更新 `PROJECT-BASELINE.md`、`ACCEPTANCE-PLAN.md`、`CURRENT-STATUS.md`、`current-vs-target-gap.md`、`2026-04-26-data-service-execution-roadmap.md`、`current_vs_target_flow.drawio`
- 如果架构边界发生变化，再同步 `01_current_architecture.drawio` 与 `02_target_architecture.drawio`

## 5. 当前架构图与目标架构图差异

| 主题 | 当前架构图应表达 | 目标架构图应表达 | 差距 |
| --- | --- | --- | --- |
| data_service | 编排 + distill + summary + API / CLI / MCP + quality 读时适配 | 稳定的上游编排层 | graph quality plan 适配继续下沉到 GraphRAG owner |
| distill | `v1.1` 已契约化，低信号保守补强后 `zero_unit_count=0` | 明确 schema、manifest、目录布局并保持可解释 | 需要持续抽查低信号 title fallback 质量 |
| llmwiki | 已可读、可检索、可追溯，读时消费 approved plan | 只专注知识编译与阅读 | topic/page 可读性继续观察 |
| graphrag | execution owner、runner、bridge、materializer 已收口到 `app.graphrag`，graph snapshot 已有 `quality_diagnostics` | 正式图引擎层 | 治理 owner 边界继续增强，quality plan 适配继续下沉 |
| knowledge UI | 已是工作台并具备质量反馈闭环第一版，已新增 GraphRAG diagnostics 面板 | 升级为知识运营台 | 需要真实知识库回归抽查和质量运营体验打磨 |
