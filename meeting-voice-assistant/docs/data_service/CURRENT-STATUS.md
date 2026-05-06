# Data Service 架构文档

## 一、当前项目状态（双引擎知识工作台已可运行）

更新时间：2026-05-06

当前 `meeting-voice-assistant` 在原有会议语音助手能力之外，已经形成一条可运行的本地知识双引擎链路。项目现在不是只有 `llmwiki`，也不是只有 `graphrag`，而是已经具备：

- `backend/data_service`：统一的数据编排与对外服务边界
- `backend/app/llmwiki`：本地知识编译与阅读层
- `backend/app/graphrag`：图谱方向独立代码库
- `/api/v1/knowledge/*`：统一知识接口
- `/knowledge`：双引擎知识工作台

当前这条链路已经可以对 `row/deepseek_split` 目录做递归 ingest，在 `workspace/` 下产出：

- `summary/`
- `llmwiki/`
- `graphrag/`

并支持：

- `llmwiki`
- `graphrag`
- `hybrid`

三种查询模式。

### 1.1 当前实现的目录结构

```text
meeting-voice-assistant/
├── backend/
│   ├── data_service/                  # ✅ 统一编排层
│   │   ├── __init__.py
│   │   ├── __main__.py               # CLI: ingest/query/summary
│   │   ├── adapters.py               # 下游适配器契约
│   │   ├── default_adapters.py       # LLMWiki / GraphRAG 默认实现
│   │   ├── mcp_stdio.py              # ✅ MCP stdio server
│   │   ├── models.py                 # IngestPlan / QueryResponse / DistilledUnit
│   │   └── service.py                # ✅ workspace / distill / graph / summary
│   │
│   └── app/
│       ├── api/
│       │   └── v1/
│       │       ├── data_service.py   # ✅ /api/v1/knowledge/*
│       │       ├── wiki.py           # ⚠️ 历史 wiki / GraphRAG 路线仍保留
│       │       └── ...
│       │
│       ├── llmwiki/                  # ✅ 本地知识编译层
│       │   ├── compiler/
│       │   ├── extractors/
│       │   ├── search/
│       │   ├── cli.py
│       │   ├── mcp_stdio.py
│       │   └── engine.py
│       │
│       └── graphrag/                 # ⚠️ 独立 GraphRAG 代码库仍在
│
├── frontend/
│   └── src/
│       ├── api/dataService.ts        # ✅ data_service 前端 API 封装
│       ├── components/
│       │   └── GraphCommunityView.vue
│       └── pages/
│           └── KnowledgePage.vue     # ✅ 双引擎工作台
│
└── docs/
    └── data_service/
        ├── README.md
        ├── PROJECT-BASELINE.md
        ├── ACCEPTANCE-PLAN.md
        ├── CURRENT-STATUS.md
        ├── current-vs-target-gap.md
        ├── current_vs_target_flow.drawio
        ├── 2026-04-26-data-service-execution-roadmap.md
        └── diagrams/
            ├── 01_current_architecture.drawio
            └── 02_target_architecture.drawio
```

### 1.2 当前实现的组件

| 组件 | 状态 | 说明 |
|------|------|------|
| Data Service CLI | ✅ 完成 | `python -m data_service ingest/query/summary` |
| Data Service HTTP API | ✅ 完成 | `/api/v1/knowledge/*` |
| Data Service MCP | ✅ Phase 4 外部验收通过 | 本地 stdio MCP server 已有 lifecycle tools、v2 envelope tools、workspace 级 build queue 与 blocked 错误契约；外部 HarnessOS 已通过持久化 MCP stdio session 完成真实端到端验收；旧 tools 保持兼容 |
| 目录递归 ingest | ✅ 完成 | 后端 ingest 支持目录路径自动展开 |
| workspace reset | ✅ 完成 | 只清中间产物，不碰 `row` |
| distill | ✅ 可用 | 已有高信息单元、权重、标题清洗、主题/实体候选 |
| LLMWiki compile | ✅ 可用 | source/topic/conversation 页面、本地检索、MiniMax 编译 |
| GraphRAG 轻索引链 | ✅ 可用 | theme/entity/relationship/community |
| `/knowledge` 页面 | ✅ 已完成统一版 | 已改为对齐首页的深色渐变视觉语言，并收成按组件宽度自动换行的流式卡片布局：GraphRAG 保持大卡，其余状态、查询、LLMWiki、Distill 按内容宽度自然排布 |
| Graph 图交互 | ✅ 可用 | 缩放、拖拽、适应、定位、社区选中联动 |
| `backend/app/graphrag` 收口 | ✅ Phase 3 阶段验收通过 | 默认 graph execution owner 已固定为 `app.graphrag`；graph snapshot / query 默认通过 `app.graphrag.service` bridge 返回；`DataService` 内部重复 graph helper、直接 compat snapshot/query 路径、默认适配器直连 materializer 路径已删除 |
| distill 正式 schema | ✅ 已完成 `v1.1` | 已有 `schema_version`、`sources/`、`units/`、`manifest.json`、`schema.json`，并新增 `profile / unit_kind_counts` |
| distill 预览能力 | ✅ 已完成增强版 | 已有 `POST /api/v1/knowledge/distill` 和 `python -m data_service distill`，manifest 缺失时可从 `distill/sources` 自恢复，并支持按 `kind / min_importance / llm_enriched_only / authority / min_source_weight / min_source_density` 筛选；source 级预览已补 `profile_debug / provenance_summary / units_by_kind / top_units`，并新增 `title_only_excerpt / entity_candidates / theme_labels / title_normalization` 解释字段，`schema.json` 已声明 `profile_debug`，已使用 `知识库/row/deepseek_split` 做端到端验证 |
| distill 标题理解 | ✅ 已完成第三版 | source 标题现在优先读取 JSON/Markdown 内部真实标题；对正文近乎为空但标题有语义的 source，会补保守型 `title-derived question`，并优先从标题抽核心实体，避免 `0 unit`、碎标签或把标题误写成 `conclusion`；低正文标题还会按语义补 `note / fact_candidate / risk` |
| distill 低信号观测 | ✅ 观测与保守补强第一版完成 | source profile 新增 `zero_unit / low_signal`，manifest 与 summary 新增 `zero_unit_count / zero_unit_sources / low_signal_reason_counts / title_fallback_source_counts`；`/knowledge` 已展示 zero-unit、原因分布、title fallback 覆盖和 source 级诊断；真实知识库临时验收已从 `zero_unit_count=8` 降到 `0`，并保持 `title_derived_conclusion_count=0` |
| distill 实体归并 | ✅ Phase 2 阶段验收通过 | 第一轮已验证 `日历App跨端协作技术专利方案 -> 日历`、`股市S1含义解析 -> 股市S1`；第二轮已补产品/机构/赛事、工具/语言/公司类标题收缩，真实知识库已验证 `小米SU7玻璃防晒性能解析 -> 小米SU7`、`中国民营航天公司上市进展及股东情况 -> 中国民营航天公司`、`美加墨世界杯小组赛时间 -> 美加墨世界杯`、`已安装VSCode选项验证 -> VSCode`、`TypeScript中的多态与复态解析 -> TypeScript`、`鸿蒙手机Python自动化测试代码示例 -> Python / 鸿蒙手机`、`超聚变公司股权结构及背景介绍 -> 超聚变公司`；2026-04-29 验收为 `title_derived_conclusion_count=0`、`zero_unit_count=8/86` |
| engine 输入边界 | ✅ 已完成第一版 | `distill -> llmwiki/graphrag` 已有显式 handoff contract 和 `input_contract.json` |
| 边界盘点能力 | ✅ 已完成第一版 | 已有 `POST /api/v1/knowledge/boundary` 和 `python -m data_service boundary` |
| 能力迁移表 | ✅ 已完成第一版 | boundary audit 已返回 capability / current_owner / target_owner / action / impact_scope |
| graph query model | ✅ 已完成共用版 | graph / query 已统一返回 `graph_model_version`、`nodes / edges / communities / stats / hits`，且标准快照/查询构建已抽入 `app.graphrag.service.data_service_query_model`；`DataService` 的 snapshot / query 默认经 `app.graphrag.service` bridge 取数 |
| graph execution owner | ✅ Phase 3 阶段验收通过 | 默认 owner 已切换为 `app.graphrag`；workspace 落盘 `execution_owner.json / execution_request.json`；GraphRAG CLI 不可用或失败时由 `app.graphrag` runner 走 compat materializer 完成本地图谱 state |
| app.graphrag runner 接入 | ✅ 已完成增强版 | 已有自动尝试执行与显式入口：`python -m data_service graphrag-execute`、`POST /api/v1/knowledge/graphrag/execute`；native CLI preflight 已改为 `graphrag --help` 健康检查，可区分 CLI 不存在、preflight 失败、index 阶段失败 |
| GraphRAG native CLI 健康 | ✅ 本机入口已恢复 | `/usr/local/bin/graphrag` 已从临时 `/tmp/graphrag_patched.py` wrapper 恢复为 `graphrag.cli.main:app` 真实入口；GraphRAG 3.0.8 不支持全局 `--version`，preflight 已改为 `graphrag --help`；当前 healthcheck 返回 `healthy=true`，native index 若因配置或输入失败则进入 `app_graphrag_compat_after_cli_failure` |
| app.graphrag bridge 接管 | ✅ 已完成第二版 | `data_service` 已默认通过 `app.graphrag.service` 提供 graph snapshot / query，bridge 承担 community / materialization 入口；CLI/API 返回的 graph payload source 已固定为 `app.graphrag.bridge` |
| compat materializer 迁移 | ✅ 已完成 | 兼容 graph DB 的写库逻辑本体已迁入 `app.graphrag.service.data_service_materializer`，`data_service` 默认 GraphRAG 适配器已改为调用 `app.graphrag.service.materialize_workspace_graph_state`，不再直接导入 materializer；`data_service` 侧只保留 ingest 编排与 contract staging |
| summary 质量观测 | ✅ 已完成第一版 | `summary.json` 已包含 `distill / llmwiki / graphrag` 质量字段，`distill` 已增加 `unit_kind_counts` |
| 图谱质量治理 | ✅ Phase 5.1 第一版完成，持续推进 | 已完成第五轮噪音清理，并继续随 `distill` 实体归并收紧图谱输入。以 `知识库/row/deepseek_split` 的 86 条真实 source 端到端重建后，本轮验证为 `85 entities / 76 themes / 131 relationships`，`小米SU7 / 中国民营航天公司 / 美加墨世界杯 / VSCode / TypeScript / Python / 超聚变公司` 已稳定落图且不再出现裸 `SU7`、`已安装VSCode选项验证`、`中的多态与复态`、`鸿蒙手机Python自动化测试代码示例`、`背景介绍` 这类长串或功能尾缀节点；Graph snapshot 已新增 `quality_diagnostics`，`/knowledge` 已展示 top communities、弱社区、孤立节点和低价值节点，并可一键带入质量反馈；当前剩余问题主要是低信号 source 回归抽查、少量弱实体归并和 GraphRAG owner 边界继续下沉 |
| LLMWiki 标题治理 | ✅ 标题第一轮完成 | 2026-04-29 已完成标题质量阶段验收：聊天 JSON 可从 user question 派生标题，普通 JSON `title` 字段使用字段值，中文短标题不再误判；真实知识库验证 `bad_source_titles=0`、`bad_page_titles=0` |
| LLMWiki topic 治理 | ✅ topic 第一轮完成 | topic anchor 已优先识别产品/工具/专有名词，并拒绝动作词、数值残片和英文句子脚手架；真实知识库验证 `VSCode / 小米SU7 / 股市S1 / 税前工资 / creample / 等额本息月供` 收缩通过，`bad_topic_titles=0`。页面内容结构仍继续优化 |
| LLMWiki 页面结构 | ✅ topic 结构第一轮完成 | topic 页面已区分 `Overview / Source Signals / Evidence Notes`；title-only source 不再重复写成 `Facts`，真实知识库验证 `topic_source_signal_pages=79`、`topic_facts_pages=0` |
| LLMWiki source 页面结构 | ✅ source 结构第一轮完成 | title-only source 页不再把来源标题重复写成 `Core Conclusion / Evidence`，而是进入 `Source Signals`；真实知识库验证 `source_signal_pages=86`、`source_evidence_pages=0` |
| `/knowledge` 质量反馈入口 | ✅ 第一版完成 | workspace 新增 `quality/feedback.jsonl`；HTTP 新增 `quality/feedback` submit/list；`summary.json.quality.manual_feedback` 可统计反馈数量、action 和 target type；前端可从页面、图节点、distill source、当前查询快速带入反馈对象 |
| 质量校正规则队列 | ✅ 第一版完成 | workspace 新增 `quality/correction_rules.json`；`rename_suggest / merge_suggest / mark_noise / needs_review` 可生成 `draft` 规则；HTTP 新增 correction rules list/build；前端可查看待审核规则 |
| 质量规则审核 | ✅ 第一版完成 | HTTP 新增 `quality/corrections/review`；规则可进入 `approved / rejected / archived`；重新 build 会保留既有审核状态；前端已提供批准、拒绝、归档按钮 |
| approved 规则消费 | ✅ 第一版完成 | workspace 新增 `quality/correction_plan.json`；HTTP 新增 `quality/corrections/plan`；Graph 快照、GraphRAG query、LLMWiki read page 读取时会应用 approved suppress / rename / merge 展示治理；action 已记录 Graph nodes / Graph edges / LLMWiki pages 影响范围；GraphRAG query 已返回 `quality_plan.query_hit_impact`；前端已提供“生成消费计划”、影响范围展示和查询治理计数 |
| LLMWiki 治理消费 | ✅ 读时治理模式 | 默认 ingest/compile 不自动改写生成 markdown；read page / query 读时消费 approved plan，MCP 不再暴露落盘改写工具，避免 revoke 后无法回滚 |
| 质量规则回滚 | ✅ 第一版完成 | 规则状态新增 `revoked`；approved 规则可撤回并立即重建消费计划；rejected / archived / revoked 可重新置为 draft；前端已提供撤回和重新置草稿操作 |
| topic 合并策略 | ✅ 第一版完成 | approved merge 命中旧 topic/page markdown 时写入 `quality_merged_into`；canonical 页面追加 `Merged Topic Signals`；旧页面不删除，避免破坏已有链接 |
| MCP / Agent 质量治理 tools | ✅ 安全收紧版 | `data_service` MCP stdio server 已新增质量治理 tools；tool call 每次独立校验 workspace/source allowlist；query/list 参数有上限；读取 correction plan 不再隐式写入 workspace |
| MCP lifecycle / v2 contract | ✅ 外部 HarnessOS 验收通过 | 已新增 `knowledge_workspace_* / knowledge_source_* / knowledge_build_*`；已新增 `knowledge_ingest_v2 / knowledge_query_v2 / knowledge_quality_*_v2 / knowledge_correction_*_v2` envelope tools；build 已改为 workspace 级队列，支持排队、取消、状态轮询和 `server_interrupted` retryable 恢复；外部验收 `workspace_id=harnessosrealdataserviceacceptance4`、`operation_id=op_fb639a7aee3c`、最终 `status=ok`、`warnings=[]` |
| 安全与回归修复 | ✅ 2026-04-30 完成 | `.env` 和 `.DS_Store` 已从 git 跟踪移除，新增 `.env.example`；knowledge API 默认要求 API key 或 dev bypass；workspace/source allowlist 与目录 symlink 防绕过已补；CORS 默认收紧；前端 Markdown 预览禁用 raw HTML 并净化输出；LLMWiki query、community policy、Graph merge 去重和 summary 读路径已回归修复 |

### 1.3 当前架构图（现状）

当前架构图见：

- [01_current_architecture.drawio](./diagrams/01_current_architecture.drawio)

当前差距总览图见：

- [current_vs_target_flow.drawio](./current_vs_target_flow.drawio)

剩余开发计划见：

- [REMAINING-DEVELOPMENT-PLAN-2026-04-30.md](./REMAINING-DEVELOPMENT-PLAN-2026-04-30.md)

### 1.4 下一阶段开发目标

当前项目已经完成 Phase 1-3，`Phase 4：MCP / Agent 化收口` 已通过外部 HarnessOS 真实 stdio MCP 验收，并作为后续回归链路保留。当前开发主线处于 `Phase 5：知识产品化`；`Phase 5.1 GraphRAG 图谱质量面板`、`Phase 5.2 Workspace & Source Manager`、`Phase 5.3 Refresh Operation UI`、`Phase 5.4 Source Distill Trace`、`Phase 5.5 Directory Watcher` 和 `Phase 5.6 Low Signal Audit` 第一版已完成。接下来继续推进 GraphRAG quality owner 边界下沉、真实知识库体验打磨和目录 watcher 增强。

Phase 4 已完成并通过验收的五件事：

1. 固化 MCP lifecycle tools：workspace、source、build、archive
2. 固化 v2 envelope tools：query、quality summary、feedback、rules、review、correction plan
3. 保持旧 MCP tools 兼容，避免破坏已有调用方
4. 稳定 build operation queue：排队、取消、状态轮询、失败恢复
5. 完成外部 Harness MCP 验收链路：create -> import -> build -> poll -> query_v2 -> feedback_v2 -> rules_v2 -> review_v2 -> correction_plan_v2 -> archive

外部 HarnessOS 真实验收记录：

- `workspace_id`: `harnessosrealdataserviceacceptance4`
- `operation_id`: `op_fb639a7aee3c`
- final `status`: `ok`
- `warnings`: `[]`
- 调用方仅依赖 opaque `workspace_id` 与 MCP tools，未直接读写内部 workspace
- 真实验收前需要确保 data_service venv 已完整安装 `backend/requirements.txt`，否则 build 阶段可能因 GraphRAG 依赖缺失失败

开发重点：

- 保留 `knowledge_ingest / knowledge_query / quality tools` 的旧响应格式
- 新增并稳定 `knowledge_ingest_v2 / knowledge_query_v2 / knowledge_quality_*_v2 / knowledge_correction_*_v2`
- lifecycle tools 和 v2 tools 返回统一 envelope：`workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data`
- 业务可预期失败返回 `blocked` envelope；未知工具、严重 schema 错误仍走 MCP error
- 同一 workspace 的 build 串行排队，避免并发写产物目录
- archived workspace 写操作返回 `blocked`
- server 重启或 worker 中断后的 running operation 标记为 `failed / retryable / server_interrupted`
- harnessOS 已补持久化 `McpStdioSession` 并可真实调用当前 stdio MCP provider；当前项目侧继续保持 provider 契约稳定
- Phase 5.1 已让 `/knowledge` 展示 top communities、弱主题、低价值 entity、孤立节点或低关系节点
- Phase 5.1 已让图谱质量问题一键带入 `needs_review / mark_noise / merge_suggest / rename_suggest`
- 继续保持 title-only / low-content source 不误产强 `conclusion`
- 继续提升 topic 聚合质量与页面可读性，让低信号 topic 收缩到核心主题
- 收紧 `data_service` 与 `graphrag` 的边界
- 继续把剩余 community 组装、quality plan 适配与 compat 细节从兼容层收回 `app.graphrag`

验收条件：

- `row/deepseek_split` 全量 ingest 稳定
- `summary / llmwiki / graphrag` 产物稳定可读
- `summary.json.quality.distill.zero_unit_count == 0`
- `title_derived_conclusion_count == 0`
- 低信号 source 的 topic 页收缩到核心主题，原始长标题只保留在 source 页用于追溯
- MCP tools 输出字段稳定，参数有上限和 allowlist 校验
- 外部 Harness 工程能通过 MCP 完成独立知识库的创建、source 导入、构建、查询和质量治理
- v2 tools 全部返回统一 envelope，旧 tools 保持兼容
- 同一 workspace 的 build 不并发写产物目录
- lifecycle 业务错误返回 `blocked` envelope
- `/knowledge` 能完成反馈、规则生成、审核、消费计划、撤回闭环
- top communities 没有明显噪音主题、长标题主题或废弃主题（Phase 5 验收重点）
- GraphRAG native CLI preflight 返回 `healthy=true`；不能再出现 `/tmp/graphrag_patched.py` wrapper 故障

#### 接下来的开发计划

接下来按 Phase 5 推进，Phase 4 作为回归基线保留：

1. `Phase 5.1` GraphRAG 图谱质量面板
- 状态：✅ 第一版完成
- Graph snapshot 已返回 `quality_diagnostics.schema_version=1.0`
- 展示 top communities、弱主题、低价值 entity、孤立节点或低关系节点
- 每个图谱问题可一键带入质量反馈
- approved 规则生成后，Graph snapshot/query 继续展示 filtered / rewritten / merged 影响计数

2. `Phase 5.2` Workspace & Source Manager
- 状态：✅ 第一版完成
- 已支持创建/选择 workspace、目录绑定和导入式 source 管理
- 前端已展示 source 文件台账、收录状态、低信号标记，并可停用 source 或进入蒸馏详情
- HTTP API 已对齐 MCP lifecycle 的 workspace/source tools

3. `Phase 5.3` Refresh Operation UI
- 状态：✅ 第一版完成
- 首次刷新和增量刷新已改为前端可见的异步 operation
- 已展示 `queued / running / completed / failed / cancelled / blocked`
- 已展示 `source_import / distill / llmwiki / graphrag / quality_plan / completed` 阶段、进度、错误、retryable 和时间戳
- 已支持取消、重试和失败诊断；旧“运行 ingest”已转为启动异步 full refresh

4. `Phase 5.4` Source Distill Trace
- 状态：✅ 第一版完成
- 已按 source 展示 `原始文件 -> distill units -> LLMWiki 页面 -> GraphRAG 节点/社区`
- 已支持从 Source Trace 面板跳转 LLMWiki 页面、定位 GraphRAG 节点和社区

5. `Phase 5.5` Directory Watcher
- 状态：✅ 第一版完成
- 已新增 `/knowledge/directories/scan`，对绑定目录生成 `new / modified / deleted / unreadable / unchanged` 扫描结果
- 扫描快照已持久化到 `workspace/lifecycle/directory_scan.json`
- `/knowledge` 已展示目录变更摘要和待刷新队列
- 默认不自动重建，用户确认后才把新增/修改文件送入 `incremental` refresh；删除文件先提示后续停用或重建
- 第一版为手动扫描式 watcher，后台常驻监听和自动刷新仍是后续增强

6. `Phase 5.6` Low Signal Audit / GraphRAG quality owner 边界下沉
- 状态：✅ 低信号审计面板第一版完成，边界下沉持续推进
- 已新增 `/knowledge/quality/low-signal-audit`
- 已检查 `zero_unit_count`、`title_derived_conclusion_count`、标题派生强语义 unit、LLMWiki 长标题泄漏和 GraphRAG 头部社区长标题泄漏
- `/knowledge` 已在 Distill Quality 面板展示低信号审计状态、检查项和风险样本
- 真实知识库当前审计暴露真实缺口：`disallowed_title_derived_count=33`，样本集中在标题派生 `topic_candidate`；`zero_unit_count=0`、`title_derived_conclusion_count=0` 和 LLMWiki/GraphRAG 长标题泄漏为 0
- 继续把 Graph snapshot/query 的治理适配从 `data_service` 读时层收回到 `app.graphrag.service`
- 保持 `data_service` 只负责编排、contract staging、统一入口和 MCP/API 边界

4. `Phase 4 回归链路`
- 继续保持旧 MCP tools 兼容
- lifecycle 与 v2 tools 继续返回统一 envelope
- 同 workspace build 继续串行排队
- archived workspace 写操作继续返回 `blocked`
- 外部 Harness 链路继续可复跑：create -> import -> build -> poll -> query_v2 -> feedback_v2 -> rules_v2 -> review_v2 -> correction_plan_v2 -> archive

当前验证：Phase 5.6 后 `python3 -m pytest backend/tests/test_data_service_api.py -q` 为 `10 passed`；前端 `npm run build` 通过。Phase 5.1 相关历史回归 `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q` 为 `75 passed`；针对图谱诊断的定向 Data Service/API 测试为 `3 passed`。历史 MCP 回归：`python3.12 -m pytest backend/tests/test_data_service_mcp.py -q` 为 `14 passed`；外部 HarnessOS fake MCP workflow 为 `1 passed`，Pack/connector fake MCP 为 `14 passed`，gateway/stdio 相关为 `4 passed`，真实 data_service MCP E2E 最终 `status=ok`。

每次较大开发进展完成后，统一执行：

- 回归测试：`python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`
- LLMWiki 回归：`python3 -m pytest backend/tests/test_llmwiki.py -q`
- 前端打包：`npx vite build`
- 真实知识库端到端验证：`/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split`
- 同步更新 `PROJECT-BASELINE.md`、`ACCEPTANCE-PLAN.md`、`CURRENT-STATUS.md`、`current-vs-target-gap.md`、`2026-04-26-data-service-execution-roadmap.md`、`current_vs_target_flow.drawio`
- 如果架构边界发生变化，再同步 `01_current_architecture.drawio`、`02_target_architecture.drawio`

#### Phase 2 验收标准

`Phase 2：正式化中间层` 完成时，需要同时满足：

当前状态：✅ 2026-04-29 已完成阶段性验收，详见 [PHASE-2-ACCEPTANCE-REPORT.md](./PHASE-2-ACCEPTANCE-REPORT.md)。

1. `distill` 作为正式中间层可独立阅读
- `workspace/distill/` 目录稳定存在
- `schema.json / manifest.json / sources/ / units/` 结构固定
- 不看代码也能理解 source 与 unit 产物

2. title-only / low-content source 不再大面积退化
- 不再频繁出现 `0 unit`
- 不再把纯标题误蒸馏成强 `conclusion`
- 能稳定落到保守的 `question / entity / topic / note / fact_candidate / risk`

3. 标题到主题映射收紧
- 低正文 source 不再过早打上 `投资 / 宏观政策 / 软件开发 / AI学习` 这类 broad bucket 主题
- 主题优先贴近 source 自身语义

4. `distill` 调试与解释性够用
- CLI / API 能按 `kind / importance / authority / source_weight / density` 直接筛选
- `profile_debug / provenance_summary / units_by_kind / top_units` 能解释“为什么产出这些 unit”

5. `llmwiki` 与 `graphrag` 稳定消费同一套中间层
- `input_contract.json` 持续有效
- 改 `distill` 时不会出现一边正常、一边悄悄失效的情况

6. 真实知识库端到端验证稳定
- 基于 `/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split`
- ingest 稳定跑通
- `distill` 产物在真实样本上可读、可追溯、可解释

#### Phase 3 验收标准

`Phase 3：GraphRAG 职责收口` 完成时，需要同时满足：

当前状态：✅ 2026-04-29 已完成阶段性验收，详见 [PHASE-3-ACCEPTANCE-REPORT.md](./PHASE-3-ACCEPTANCE-REPORT.md)。

1. graph engine owner 固定
- `app.graphrag` 成为 graph build / query / community / materialization 的最终 owner
- `data_service` 不再长期承载核心 graph 组装逻辑

2. `data_service` 收回到编排边界
- 只负责 ingest / layout / summary / API / MCP / owner routing / contract
- 不再继续膨胀成第二套 GraphRAG

3. graph query model 对外稳定
- `knowledge/query|graph` 持续输出统一结构
- 至少保持 `graph_model_version / nodes / edges / communities / stats / hits`
- 前端、CLI、MCP、Agent 不需要理解两套 graph 输出

4. 残余 compat 逻辑收薄
- `community assembly / compat materialization` 不再散落在 `data_service`
- fallback 只保留最薄兼容层

5. owner 切换不影响上层调用
- `knowledge/query`
- `knowledge/graph`
- `/knowledge`
- MCP / CLI
  这些入口在 owner 固定后保持行为稳定

6. 真实知识库端到端验证稳定
- 基于 `/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split`
- `llmwiki: success`
- `graphrag: indexed` 或等价完成态
- 头部社区和图谱规模收敛方向稳定，不因 owner 收口而明显退化

### 1.5 当前剩余缺口

- `distill` 已完成 `v1.1` 版本化和增强预览能力，新增 `risk / example / fact_candidate` 蒸馏、低信号聊天过滤、`unit_kind_counts`，支持按 `kind / min_importance / llm_enriched_only / authority / source_weight / density` 筛选，并已补 `profile_debug / provenance_summary / units_by_kind / top_units`
- `profile_debug.title_normalization` 已能解释 title-only source 的标题收缩过程，包括原始标题、保留的实体/主题、丢弃的标题功能片段和触发规则；CLI/API 预览可直接看到 `install_status_removed / functional_suffix_removed / latin_prefix_kept / title_contracted_to_core_entity / theme_aligned_to_entity`
- source 标题理解已收口到第三版：优先读取内部真实标题；标题型空壳 source 现在会保守地产出 `title-derived question`，并优先抽核心标题实体；同时会按标题语义补低风险的 `note / fact_candidate / risk`。真实知识库中的 `武汉周末小众游推荐`、`中国核电建设及并网时间数据`、`Bose耳机配对问题排查指南` 已验证会分别补出 `note / fact_candidate / risk`，且不误产 `conclusion`
- title-only source 的主题映射已收口第一版：对低正文 source 优先保留贴近标题本身的主题，不提前注入 `投资 / 宏观政策 / 软件开发 / AI学习` 这类泛主题。真实知识库中的 `中国核电建设及并网时间数据` 已验证只保留 `中国核电`，不再额外带 `投资`
- `data_service` 当前仍承载编排和薄兼容入口，但 graph snapshot / query 默认已通过 `app.graphrag.service` bridge 返回，标准 graph query model 构建、community assembly、compat materialization 与重复 graph helper 已收回 `app.graphrag.service`
- `backend/app/graphrag` 与 `backend/data_service` 图能力已按 Phase 3 完成职责收口：`app.graphrag` 负责 graph execution / query model / community assembly / materialization，`data_service` 保留编排、contract staging 和统一入口
- `app.graphrag` 真实执行器已接入，compat materializer 本体也已迁入 `app.graphrag.service`，`bridge` 已直接调用该 materializer，且 `data_service` 默认适配器也不再直接导入 materializer
- graph snapshot / query 的标准 payload 已统一由 `app.graphrag.service.data_service_query_model` 生成，并经 `app.graphrag.service` bridge 作为 `DataService` 默认路径返回；execution owner 已固定到 `app.graphrag`
- 图谱质量已明显收紧，数值驱动长尾碎片已基本压下；剩余主要是少量弱实体与专有名词归并问题，例如 `日历`、`股市S1含义`、`日历App跨端协作技术专利方案`
- `distill` 已进入质量收尾阶段，当前主要缺口已从“能否产出 unit”切到“实体归并、标题到主题映射、弱语义 source 的解释性”
- `distill` 实体归并已进入第二轮：真实知识库中的 `日历App跨端协作技术专利方案` 已收成 `日历`，`股市S1含义解析` 已收成 `股市S1`，`小米SU7玻璃防晒性能解析` 已收成 `小米SU7`，`中国民营航天公司上市进展及股东情况` 已收成 `中国民营航天公司`，`美加墨世界杯小组赛时间` 已收成 `美加墨世界杯`，`已安装VSCode选项验证` 已收成 `VSCode`，`TypeScript中的多态与复态解析` 已收成 `TypeScript`，`超聚变公司股权结构及背景介绍` 已收成 `超聚变公司`；但跨 source 的更广义实体归并仍未完成
- `/knowledge` 已完成一轮首页风格统一，并改成按组件宽度自动换行的流式卡片布局；旧的多分栏和叠加样式已清理，后续重点转为内容密度、滚动体验和运营化能力

---

## 二、目标架构（Phase 1-5）

### 2.1 目标架构 - 五层结构

```text
L1 用户入口层
  前端 / CLI / Agent / MCP Host

L2 上游编排层
  data_service
  - ingest / layout / summary / API / MCP

L3 正式中间层
  distill contract
  - schema / manifest / source summary / units / provenance

L4 下游引擎层
  llmwiki
  graphrag

L5 产品与调用层
  /knowledge
  MCP tools
  Agent routing
```

### 2.2 目标架构说明

目标不是让 `data_service` 继续承载越来越多图算法，而是形成稳定的双引擎边界：

- `data_service`：只负责上游编排与服务边界
- `distill`：正式中间契约层
- `llmwiki`：知识编译与阅读层
- `graphrag`：图谱引擎层

目标架构图见：

- [02_target_architecture.drawio](./diagrams/02_target_architecture.drawio)

当前与目标差距总览图见：

- [current_vs_target_flow.drawio](./current_vs_target_flow.drawio)
