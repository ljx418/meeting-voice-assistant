# 项目验收计划

更新时间：2026-05-06

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
- 当前本机 `/usr/local/bin/graphrag` 已恢复为 `graphrag.cli.main:app` 真实入口；GraphRAG 3.0.8 不支持全局 `--version`，preflight 使用 `graphrag --help`，当前可返回 `healthy=true`

当前 `/knowledge` 质量反馈入口结论：

- 2026-04-30 已完成质量反馈与人工校正入口第一版，记录见 [KNOWLEDGE-QUALITY-FEEDBACK-REPORT-2026-04-30.md](./KNOWLEDGE-QUALITY-FEEDBACK-REPORT-2026-04-30.md)
- 2026-04-30 已完成质量反馈到 draft 校正规则第一版，记录见 [QUALITY-CORRECTION-RULES-REPORT-2026-04-30.md](./QUALITY-CORRECTION-RULES-REPORT-2026-04-30.md)
- 2026-04-30 已完成质量规则审核第一版，记录见 [QUALITY-RULE-REVIEW-REPORT-2026-04-30.md](./QUALITY-RULE-REVIEW-REPORT-2026-04-30.md)
- 2026-04-30 已完成 approved 校正规则消费第一版，记录见 [QUALITY-CORRECTION-PLAN-REPORT-2026-04-30.md](./QUALITY-CORRECTION-PLAN-REPORT-2026-04-30.md)
- 人工反馈落盘到 `workspace/quality/feedback.jsonl`
- draft 校正规则落盘到 `workspace/quality/correction_rules.json`
- approved 消费计划落盘到 `workspace/quality/correction_plan.json`
- `summary.json.quality.manual_feedback` 可展示反馈总量、action 分布和 target type 分布
- `summary.json.quality.correction_rules` 可展示规则总量、状态分布和规则类型分布
- `summary.json.quality.correction_plan` 可展示 action 总量、action 分布和 target engine 分布
- `quality/corrections/review` 可把规则置为 `approved / rejected / archived`
- `quality/corrections/plan` 可把 approved 规则转换为消费计划
- Graph 快照、GraphRAG query、LLMWiki read page 均会读取 `correction_plan.json` 并应用展示治理
- `correction_plan.json.actions[].impact` 可展示 Graph nodes、Graph edges、LLMWiki pages 影响范围
- GraphRAG query payload 中的 `quality_plan.query_hit_impact` 可展示 filtered / rewritten hit 数量和样例
- LLMWiki ingest/compile 默认不改写生成 markdown；read page / query 读取时应用 approved rename / merge / suppress 展示治理
- approved 规则可置为 `revoked`，撤回后 `correction_plan.json` 不再包含该规则
- rejected / archived / revoked 规则可重新置为 `draft`
- approved merge 命中旧 topic/page markdown 时会写入 `quality_merged_into`，canonical 页面会追加 `Merged Topic Signals`
- MCP stdio server 已开放质量治理 tools：`knowledge_quality_summary / knowledge_correction_plan / knowledge_quality_feedback / knowledge_correction_rules / knowledge_review_correction_rule`
- Agent 可读取质量计划与影响范围、提交受控 feedback、执行受控审核；MCP 读取 correction plan 不隐式写 workspace
- `/knowledge` 可从当前页面、图节点、distill source、当前查询快速带入反馈对象
- MCP 化知识库生命周期管理已通过外部 HarnessOS 真实 stdio MCP 验收：外部 Harness 工程已通过 MCP 创建 workspace、导入 source、启动构建、查询状态、查询知识并执行质量治理
- 剩余开发计划见 [REMAINING-DEVELOPMENT-PLAN-2026-04-30.md](./REMAINING-DEVELOPMENT-PLAN-2026-04-30.md)

## 必跑自动化验收

从项目根目录运行：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
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
- source 级记录包含 `profile / profile_debug / unit_kind_counts`，并包含 `profile.zero_unit / profile.low_signal / profile_debug.low_signal`
- unit 级记录包含 `kind / authority / source_weight / source_density_score / provenance`
- manifest 与 summary 可展示 `zero_unit_count / zero_unit_sources / low_signal_reason_counts / title_fallback_source_counts`
- CLI / API 预览能展示 `profile_debug / provenance_summary / units_by_kind / top_units`
- `/knowledge` Distill Quality 面板能展示 zero-unit 数量、原因分布、title fallback 覆盖和 zero-unit source 列表
- title-only / low-content source 不再大面积退化为 `0 unit`，且不再产出 title-derived 强 `conclusion`
- 当前真实知识库临时验收：`zero_unit_count=0 / 86`，`title_derived_conclusion_count=0`
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
- GraphRAG native CLI preflight: `healthy=true` on current machine
- 如果 native index 因配置或输入失败，execution result reason 应为 `graphrag_index_failed`，并进入 `app_graphrag_compat_after_cli_failure`

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

- `graphrag --help` 返回 0
- `python3 -m data_service ingest ...` 的 graph execution 不再返回 `graphrag_cli_not_found` 或 `graphrag_cli_broken`
- 如果 native index 失败，返回中必须包含 `cli_health` 与 `cli_error`，能定位是 preflight 失败还是 index 阶段失败

当前本机状态：

- `/usr/local/bin/graphrag` 存在
- 入口已恢复为 `graphrag.cli.main:app`
- `graphrag --help` 返回 0
- preflight 可返回 `healthy=true`

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
- 对 draft 规则执行“批准 / 拒绝 / 归档”后，状态分布更新
- 再次“生成规则”不会把已审核规则重置回 draft
- 页面无明显遮挡、错位、空白卡片或异常报错

## Phase 4：MCP / Agent 化收口验收

目标是确认另一个 Harness 开发工程可以把当前服务当作知识库 MCP 后端使用，而不是直接读写本项目内部目录。

当前状态：本项目侧已完成 lifecycle tools、v2 envelope tools、workspace 级 build queue 与 blocked 错误契约第一版；外部 HarnessOS 已通过持久化 MCP stdio session 完成真实 data_service MCP 端到端验收。

需求来源：

- `../harnessOS/docs/architecture/data-service-mcp-codex-handoff.md`
- harnessOS 侧已完成 `data_service_mcp` lifecycle/v2/legacy tool 注册，并修正相对命令健康检查
- 当前项目提供真实 `data_service.mcp_stdio` lifecycle tools；HarnessOS 已通过真实 MCP client execution 验证 provider 契约

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

已通过验收链路：

1. 外部 Harness 工程通过 MCP stdio 启动当前服务的 `data_service.mcp_stdio`
2. 调用 `knowledge_workspace_create` 创建独立测试知识库
3. 调用 `knowledge_source_import` 导入一个小型 fixture source
4. 调用 `knowledge_build_start` 启动 `full` 构建，并用 `knowledge_build_status` 轮询到终态
5. 调用 `knowledge_query_v2` 查询导入内容
6. 调用 `knowledge_quality_feedback_v2` 提交质量反馈
7. 调用 `knowledge_correction_rules_v2` 和 `knowledge_review_correction_rule_v2` 完成规则审核
8. 调用 `knowledge_correction_plan_v2` 读取 approved impact
9. 调用 `knowledge_workspace_archive` 归档测试知识库

2026-05-02 外部 HarnessOS 验收记录：

- `workspace_id`: `harnessosrealdataserviceacceptance4`
- `operation_id`: `op_fb639a7aee3c`
- final `status`: `ok`
- `warnings`: `[]`
- 实际覆盖链路：`create -> import -> build_start -> build_status(completed) -> query_v2 -> feedback_v2 -> correction_rules_v2 -> review_correction_rule_v2 -> correction_plan_v2 -> archive`
- HarnessOS 侧通过持久化 `McpStdioSession` 保持同一 stdio MCP 会话，避免 build queue 状态在一次性 MCP 进程退出后丢失
- feedback action 使用 `needs_review`，可生成 draft correction rule，并实际调用 `knowledge_review_correction_rule_v2`
- 调用方仅依赖 opaque `workspace_id` 与 MCP tools，未直接读写内部 workspace
- 真实验收前必须确保 data_service venv 已完整安装 `backend/requirements.txt`，否则 build 阶段可能因 GraphRAG 依赖缺失失败

通过标准：

- 所有 lifecycle tools 返回统一 envelope，包含 `workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data`
- v2 tools 返回同一 envelope；旧 `knowledge_ingest / knowledge_query / quality tools` 保持兼容，不强制改响应格式
- 长任务返回 `operation_id`，构建状态能定位 `source_import / distill / llmwiki / graphrag / quality_plan / completed / failed / cancelled` 阶段
- 同一 workspace build 串行排队，不并发写 `llmwiki / graphrag / quality` 产物目录
- queued build 可取消；running build 在阶段边界响应 cancel；已完成 build cancel 返回当前终态并附 warning
- server 中断遗留的 running operation 会进入 `failed`，并返回 `retryable=true` 与 `server_interrupted`
- workspace/source path 继续执行 allowlist、realpath、大小上限、去重和 symlink 防绕过校验
- 重复导入同一 source 幂等，不产生重复页面、重复 entity 或重复 source 记录
- archived workspace 可读但不可写，写类 tool 返回 `blocked`
- lifecycle 业务可预期失败返回 `blocked` envelope；未知工具或严重 schema 错误仍走 MCP error
- 读取 correction plan 不隐式写入，除非显式 `rebuild=true`
- 外部 HarnessOS 验收通过：fake MCP workflow `1 passed`，Pack/connector fake MCP `14 passed`，gateway/stdio 相关 `4 passed`，真实 data_service MCP E2E 最终 `status=ok`
- 现有 `knowledge_ingest / knowledge_query / quality tools` 保持兼容
- `knowledge_query / quality` tools 支持 `workspace_id`，外部 Harness 不需要使用 workspace path 即可完成验收链路

最小自动化测试：

- `list_tools` 包含全部 lifecycle tools
- `list_tools` 包含 `knowledge_ingest_v2 / knowledge_query_v2 / knowledge_quality_*_v2 / knowledge_correction_*_v2`
- workspace create/list/describe 在临时 `DATA_SERVICE_WORKSPACE_ROOT` 下可用
- source import from file 返回 `source_id` 和 `sha256`
- duplicate import 幂等，不创建重复 source records
- source import 对 allowlist 外路径返回 `blocked`
- source import 对 symlink escape 返回 `blocked`
- build start 返回 `operation_id` 和 queued/running status，且不阻塞
- 同一 workspace 连续启动多个 build 时按队列串行执行
- build status 返回 stage、progress、artifacts、retryable error payload
- build cancel 返回 cancelled 或 completed-with-warning
- unknown source / operation 返回 `blocked`
- running operation 遗留后标记为 `failed / retryable / server_interrupted`
- workspace archive 标记 archived 并保留数据
- archived workspace 写类 v2 tools 返回 `blocked`
- multi-workspace calls 保持隔离
- existing quality tools 继续通过

当前验证结果：

- `python3.12 -m pytest backend/tests/test_data_service_mcp.py -q`：`14 passed`
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：`74 passed, 14 skipped`
- `python3 -m pytest backend/tests/test_llmwiki.py -q`：`34 passed`

## Phase 5：知识产品化验收

当前状态：Phase 5 是当前主推进项；`Phase 5.1` GraphRAG 图谱质量面板第一版已完成，下一阶段目标是把 `/knowledge` 做成一个顺手的个人知识库管理产品。Phase 4 MCP / Agent 化链路作为回归基线保留。

### 个人知识库管理产品验收

目标体验：

- 用户能在网页上创建或选择个人知识库工作区
- 用户能选择“目录即知识库”或“导入式知识库”
- 用户能看到知识库收录了多少文件、哪些文件待处理、哪些文件失败、哪些文件低信号
- 用户能点击首次刷新或增量刷新，并看到异步构建进度
- 用户能预览 LLMWiki 摘要和页面
- 用户能查看 GraphRAG 社区实体图
- 用户能按 source 查看知识蒸馏流水线

通过标准：

- 首次打开 `/knowledge` 时，空状态能引导用户完成：创建/选择工作区 -> 绑定目录或导入文件 -> 首次刷新
- 工作区页显示 workspace 名称、路径、source 总数、最近刷新时间、最近 build 状态和健康提示
- 目录绑定模式下，系统不修改原始目录；导入式模式下，系统复制文件到 managed source area
- source 列表显示 `source_id / title / path / ingest_status / low_signal / last_build_status`
- source 支持停用、重新收录、查看失败原因和查看蒸馏详情
- 刷新任务使用 operation 状态展示 `queued / running / completed / failed / cancelled / blocked`
- 刷新任务显示阶段：`source_import / distill / llmwiki / graphrag / quality_plan / completed`
- 失败时页面显示失败阶段、错误摘要、retryable 标记和重试入口
- source 详情能展示 distill units、unit kind counts、low-signal reasons、对应 LLMWiki 页面和关联 GraphRAG 节点/社区
- LLMWiki 页面和 GraphRAG 节点能反向定位关联 source
- 目录监听开启后，新增/修改/删除文件能进入待刷新队列；默认不自动重建，需用户确认

### GraphRAG 图谱质量面板

当前状态：✅ 第一版完成

通过标准：

- `/knowledge` 能展示 top communities、弱主题、低价值 entity、孤立节点或低关系节点
- 每个图谱问题能一键带入质量反馈，例如 `mark_noise / merge_suggest / rename_suggest`
- approved 规则生成后，Graph snapshot/query 中能看到 filtered / rewritten / merged 的影响计数
- 真实知识库复跑后，明显长标题、废弃主题、重复实体不进入 top communities
- GraphRAG native CLI preflight 返回 `healthy=true`

当前已完成：

- Graph snapshot payload 包含 `quality_diagnostics.schema_version=1.0`
- `quality_diagnostics` 包含 `top_communities / weak_communities / isolated_nodes / low_value_nodes / summary`
- 诊断项包含 `feedback_target`，可带入 `needs_review / mark_noise / merge_suggest / rename_suggest`
- `/knowledge` 已展示 GraphRAG diagnostics 面板，并支持诊断项定位图节点或社区
- 定向 Data Service/API 验证为 `3 passed`；Data Service/API 回归为 `75 passed`；前端 `npm run build` 通过

### 低信号 source 回归抽查

当前状态：🔄 当前推进

通过标准：

- `row/deepseek_split` 全量 ingest 稳定通过
- `summary.json.quality.distill.zero_unit_count == 0`
- `title_derived_conclusion_count == 0`
- 低信号 source 的 topic 页收缩到核心主题，原始长标题只保留在 source 页用于追溯
- 抽查页面不出现“标题被当成事实/结论”的内容
- GraphRAG top communities 中不出现新增 title fallback 引入的明显长标题或功能尾缀主题

### Phase 4 回归

通过标准：

- lifecycle tools 和 v2 tools 继续返回统一 envelope
- 旧 `knowledge_ingest / knowledge_query / quality tools` 保持兼容
- 外部 Harness 链路继续可复跑：create -> import -> build -> poll -> query_v2 -> feedback_v2 -> rules_v2 -> review_v2 -> correction_plan_v2 -> archive
- archived workspace 写操作继续返回 `blocked`

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
