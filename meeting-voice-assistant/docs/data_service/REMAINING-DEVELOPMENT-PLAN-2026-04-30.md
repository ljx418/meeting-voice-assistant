# 剩余开发计划

日期：2026-05-06

## 总目标

当前项目已经从“本地知识库双引擎工作台”推进到 Phase 5 知识产品化阶段。Phase 4 MCP / Agent 化收口已经通过外部 HarnessOS 真实 stdio MCP 验收，并作为后续回归基线保留。剩余开发的目标不是继续堆入口，而是把质量治理从读时展示继续固化为可观察、可回滚、可被 Agent 使用的知识运营能力。

## 剩余阶段 1：query hit 级影响记录

状态：✅ 第一版已完成

开发目的：

- 让 GraphRAG / hybrid 查询结果明确展示哪些 hit 被 approved 规则过滤、哪些 hit 被 rename / merge 改写
- 避免只知道“规则生效了”，但不知道具体影响了哪些查询结果
- 给后续 `/knowledge` 质量运营面板和 Agent tools 提供可解释 payload

验收标准：

- GraphRAG query payload 中包含 `quality_plan.query_hit_impact`
- `suppressed_hits` 记录被 suppress 规则过滤的 hit
- `rewritten_hits` 记录 title / snippet 被 rename / merge 改写的 hit
- `/knowledge` 查询区域能显示本次查询的 filtered / rewritten 数量

完成记录：

- GraphRAG query payload 已返回 `quality_plan.query_hit_impact`
- `/knowledge` 查询卡片已展示 filtered / rewritten / actions
- 自动化验证：`61 passed`

## 剩余阶段 2：LLMWiki 读时治理消费

状态：✅ 第一版已完成

开发目的：

- 当前 LLMWiki read page / query 已经能读时应用 `correction_plan.json`
- 默认保持 ingest/compile 产物可回滚，不自动改写 markdown
- 减少 revoke 后无法恢复原始生成产物的风险

验收标准：

- LLMWiki read page / query 可读取 `correction_plan.json`
- source/topic/page 展示中应用 rename / merge 展示名
- suppress 不删除页面，只在展示层过滤或标记
- 撤回规则后，重新读取即可回到未治理展示

完成记录：

- LLMWiki ingest/compile 默认不自动改写生成 markdown
- rename / merge / suppress 通过 read page / query 读时消费
- MCP 不再暴露 LLMWiki markdown 落盘改写工具
- 自动化验证：`63 passed`

## 剩余阶段 3：质量规则回滚与重新编辑

状态：✅ 第一版已完成

开发目的：

- 人工审核不可避免会有误判
- 需要把 approved 规则从“单向进入消费计划”升级为“可撤回、可重新置 draft、可归档”
- 避免错误规则长期影响查询和页面

验收标准：

- 支持 `approved -> draft` 或 `revoked`
- `correction_plan.json` 重新生成后不再包含 revoked 规则
- `/knowledge` 可对 approved 规则执行撤回
- summary 中能区分 approved / revoked / archived

完成记录：

- 规则状态新增 `revoked`
- approved 规则可撤回，撤回后会立即重建 `correction_plan.json`
- 非 approved 规则可重新置为 `draft`
- `/knowledge` 已提供“撤回”和“重新置草稿”操作
- 自动化验证：`64 passed`

## 剩余阶段 4：topic 合并策略固化

状态：✅ 第一版已完成

开发目的：

- 把 `merge_suggest` 从展示层治理推进到 topic 聚合质量治理
- 减少同义 topic、弱实体 topic、长标题 topic
- 让 LLMWiki topic 与 GraphRAG entity/community 的合并逻辑趋于一致

验收标准：

- approved merge 规则能影响 topic anchor / topic slug 选择
- topic 页面不会重复生成明显同义页面
- GraphRAG query 与 LLMWiki topic 页面对 canonical 名称一致

完成记录：

- approved merge 命中旧 topic/page markdown 时，会写入 `quality_merged_into`
- 如果 canonical topic/page markdown 已存在，会追加 `Merged Topic Signals`
- 旧页面不删除，避免破坏已有链接；canonical 页面获得可读的合并来源信号
- 自动化验证：`65 passed`

## 剩余阶段 5：MCP / Agent tools 精细化

状态：✅ 第一版已完成

开发目的：

- 让本地 Agent 不只会查知识，还能参与质量运营
- 把反馈、规则、审核、消费计划、影响范围做成稳定工具能力

验收标准：

- Agent tool 可读取 summary / graph / page / correction plan
- Agent tool 可提交 feedback
- Agent tool 可列出 draft rules 和 approved impacts
- Agent tool 可执行受控审核动作

完成记录：

- `data_service` MCP stdio server 新增质量治理 tools：
  - `knowledge_quality_summary`
  - `knowledge_correction_plan`
  - `knowledge_quality_feedback`
  - `knowledge_correction_rules`
  - `knowledge_review_correction_rule`
- Agent 可读取 `summary.json.quality`、近期 feedback、correction rules、approved correction plan 与 action impact
- Agent 可提交受控 feedback，并通过 status enum 执行 `draft / approved / rejected / archived / revoked` 审核动作
- Agent 可读取 LLMWiki approved quality plan 的影响范围，默认通过读时治理消费
- 自动化验证：`65 passed, 3 skipped`

## 剩余阶段 6：低信号 source 质量观察

状态：✅ 观测与保守补强第一版已完成

开发目的：

- Phase 2 验收中曾剩余 `zero unit = 8 / 86`
- 当前保守补强后已降到 `zero_unit_count=0 / 86`
- 后续要在不误产强 conclusion 的前提下保持覆盖率，并抽查页面和图谱噪音

验收标准：

- title-only / low-content source 仍不误写强 conclusion
- 能补充保守的 question / note / fact_candidate / risk
- zero unit 数量下降，且人工抽查无明显幻觉型结论

完成记录：

- `distill/sources/*.json.profile.low_signal` 新增低信号诊断
- `distill/sources/*.json.profile.zero_unit` 标记该 source 是否完全没有 unit
- `profile_debug.low_signal.reasons` 记录 zero-unit 原因，例如 `no_entity_candidates / no_theme_labels / no_safe_title_fallback / no_content_sentences / low_density_source`
- `distill/manifest.json.quality` 新增 `zero_unit_count / zero_unit_sources / low_signal_reason_counts / title_fallback_source_counts`
- `summary.json.quality.distill` 同步暴露 zero-unit 与 title fallback 覆盖统计
- `/knowledge` Distill Quality 面板已展示 Zero Unit、Low Signal Reasons、Title Fallback 和 Zero Unit Sources
- Source 级蒸馏详情已展示当前 source 的 low-signal reasons 与 title fallback 类型
- 已验证 title-only source 仍不产出强 `conclusion`
- 基于真实知识库 low-signal reasons 补充保守标题规则，覆盖退休资金、管培生案例、端午注意事项、云南菜评价、车企相关、智能卡片专利、creample 术语、香农极限应用
- LLMWiki topic anchor 已同步覆盖上述低信号标题；真实知识库复跑后 topic 页收缩为 `退休资金 / 管培生 / 端午节 / 云南菜 / 车企 / 智能卡片 / 香农极限 / creample` 等核心主题，原始长标题保留在 source 页
- 真实知识库临时验收：86 sources / 293 units / `zero_unit_count=0` / `title_derived_conclusion_count=0` / LLMWiki success / GraphRAG indexed
- 自动化验证：`backend/tests/test_llmwiki.py` 为 `34 passed`；`backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py` 为 `74 passed, 4 skipped`；`npx vite build` 通过

## 下一阶段开发计划：Phase 5 产品化优先

当前剩余阶段 1-6 均已完成第一版。`Phase 4：MCP / Agent 化收口` 已通过外部 HarnessOS 真实 stdio MCP 验收，外部 Harness 工程已可稳定调用当前知识底座。`Phase 5.1：GraphRAG 图谱质量面板` 第一版也已完成。

下一阶段的产品目标已经明确为：把 `/knowledge` 做成一个顺手的个人知识库管理产品，而不只是双引擎调试工作台。产品形态固定为：

- 同时支持“目录即知识库”和“导入式知识库”
- 手动首次刷新/增量刷新优先，后续补目录监听和待刷新队列
- 按 source 展示 `原始文件 -> distill units -> LLMWiki 页面 -> GraphRAG 节点/社区` 的可追溯流水线

因此下一阶段主线改为 `Phase 5.2 Workspace & Source Manager`、`Phase 5.3 Refresh Operation UI`、`Phase 5.4 Source Distill Trace`、`Phase 5.5 Directory Watcher`；data_service venv 依赖与外部调用文档作为 Phase 4 回归链路继续固化。

### 总体目标

1. Phase 5：把工作区创建、目录绑定、导入文件、最近工作区和健康状态做成网页主流程
2. Phase 5：把 source 文件台账、收录状态、失败原因、低信号诊断和停用/重收录做成可管理对象
3. Phase 5：把同步 ingest 升级为前端可见的异步刷新任务，支持首次刷新、增量刷新、取消、重试和失败诊断
4. Phase 5：按 source 展示蒸馏流水线，串起 distill、LLMWiki 页面和 GraphRAG 节点/社区
5. Phase 5：后续补目录监听和待刷新队列
6. Phase 5：继续保留图谱质量反馈闭环，并把 GraphRAG quality plan 适配向 `app.graphrag.service` owner 边界下沉
7. Phase 4 回归：保持 MCP lifecycle tools、v2 envelope tools、build operation queue、blocked error contract、archived read-only 语义和外部 Harness 调用链路稳定

### Phase 5.1：GraphRAG 图谱质量面板

状态：✅ 第一版已完成

开发目的：

- 让 `/knowledge` 不只展示图谱，还能直接发现图谱质量问题
- 把 top communities、弱主题、孤立节点、低关系节点变成可审核的质量对象
- 让人工质量反馈能从图谱问题直接进入 `feedback -> correction_rules -> correction_plan -> read-time governance` 闭环

验收标准：

- `/knowledge` 能展示 top communities、弱主题、低价值 entity、孤立节点或低关系节点
- 每个图谱问题能一键带入质量反馈，例如 `mark_noise / merge_suggest / rename_suggest`
- approved 规则生成后，Graph snapshot/query 中能看到 filtered / rewritten / merged 的影响计数
- 真实知识库复跑后，明显长标题、废弃主题、重复实体不进入 top communities
- GraphRAG native CLI preflight 返回 `healthy=true`；如 native index 因配置或输入失败，runner 只能进入 `app_graphrag_compat_after_cli_failure`，不能再出现 `/tmp/graphrag_patched.py` 这类 wrapper 故障

完成记录：

- Graph snapshot 已新增 `quality_diagnostics`，schema version 为 `1.0`
- 诊断类型已覆盖 `top_communities / weak_communities / isolated_nodes / low_value_nodes`
- 每个诊断项已包含 `feedback_target`，可直接带入 `needs_review / mark_noise / merge_suggest / rename_suggest`
- `/knowledge` 已新增 GraphRAG diagnostics 面板，并可从诊断项定位图节点或社区
- 自动化验证：定向 Data Service/API 测试 `3 passed`；Data Service/API 回归 `75 passed`；前端 `npm run build` 通过

### Phase 5.2：Workspace & Source Manager

状态：✅ 第一版完成

开发目的：

- 让用户在网页上完成个人知识库工作区的创建、选择、目录绑定和文件导入
- 把 source 文件变成可管理对象，而不是只靠手动输入 ingest 路径
- 同时支持“目录即知识库”和“导入式知识库”

输出物：

- `/knowledge` 工作区向导：创建/选择 workspace、最近工作区、当前工作区健康状态
- 目录绑定入口：展示绑定目录、只读说明、扫描到的文件数和可收录文件数
- 导入式 source 入口：复用 managed source area，把导入文件纳入 source manifest
- source 列表：展示 `source_id / title / original_path / sha256 / ingest_status / low_signal / last_build_status`
- source 操作：停用、重新收录、查看失败原因、查看蒸馏详情
- HTTP API 对齐 MCP lifecycle 的 workspace/source 能力，浏览器不直接依赖 MCP stdio

验收标准：

- 用户无需理解内部 workspace 目录，也能创建或选择一个知识库
- 用户能绑定本地目录，并看到扫描文件数、可收录文件数和已收录文件数
- 用户能导入文件，并在 source 列表中看到 `pending / indexed / failed / disabled / low_signal`
- source import/list/remove 与 MCP lifecycle 行为一致
- 目录绑定模式下不修改原始目录；导入式模式下由系统管理 copied source

完成记录：

- HTTP 已新增 `/knowledge/workspaces/create|list|describe`
- HTTP 已新增 `/knowledge/sources/import|list|remove`
- `/knowledge` 已新增知识库管理区，支持创建/绑定、最近工作区、Source 导入、Source 台账、停用和蒸馏详情入口
- Source 台账已合并导入式 manifest 与既有 distill 产物，现有目录 ingest workspace 能直接看到 indexed source
- 自动化验证：`backend/tests/test_data_service_api.py` 为 `9 passed`；前端 `npm run build` 通过

### Phase 5.3：Refresh Operation UI

状态：✅ 第一版完成

开发目的：

- 把当前前端同步 `ingest` 升级为产品化刷新流程
- 让首次刷新和增量刷新可以长时间运行、可取消、可重试、可定位失败阶段
- 复用已有 MCP build queue 语义，并补 HTTP/API 与前端轮询

输出物：

- 前端刷新动作：首次刷新、增量刷新、只刷新 LLMWiki、只刷新 GraphRAG
- operation 状态面板：`operation_id / status / stage / progress / started_at / completed_at / error / retryable`
- 阶段展示：`source_import / distill / llmwiki / graphrag / quality_plan / completed`
- 操作：取消、重试、刷新状态、查看日志摘要
- HTTP API 对齐 `knowledge_build_start/status/cancel`

验收标准：

- 点击首次刷新后页面不阻塞，立即展示 operation id 和 queued/running 状态
- 构建过程中可以看到当前阶段和最近错误
- 同一 workspace 连续刷新不会并发写产物目录
- failed/retryable 状态给出明确重试入口
- archived workspace 写操作返回 blocked，不允许刷新

完成记录：

- HTTP 已新增 `/knowledge/build/start|status|cancel`，返回统一 lifecycle envelope
- FastAPI 进程内复用 workspace operation JSON 协议，支持 queued/running/completed/failed/cancelled/blocked
- operation data 已包含 `mode / stage / progress / started_at / completed_at / error / retryable / artifacts / results`
- `/knowledge` 已新增刷新任务面板，支持全量、增量、LLMWiki-only、GraphRAG-only、状态轮询、取消和重试
- 旧的“运行 ingest”已改为启动异步 full refresh operation，不再阻塞浏览器等待长任务
- 自动化验证：`backend/tests/test_data_service_api.py` 为 `9 passed`；前端 `npm run build` 通过

### Phase 5.4：Source Distill Trace

状态：✅ 第一版完成

开发目的：

- 让“知识蒸馏过程”从调试字段变成用户可理解的 source 级流水线
- 用户可以看清一篇文档如何变成 distill units、LLMWiki 页面和 GraphRAG 节点/社区

输出物：

- source 详情页或侧栏流水线：
  `原始文件 -> 标题/正文抽取 -> distill units -> LLMWiki 页面 -> GraphRAG entity/theme/community`
- 每个阶段展示状态、产物数量、低信号诊断、失败原因和跳转入口
- LLMWiki 页面可反向跳回 source
- GraphRAG 节点/社区可反向展示关联 source
- 保留 `profile_debug / title_normalization / low_signal reasons / unit_kind_counts`，但以产品化文案展示

验收标准：

- 任意 source 能看到 distill units、unit kind counts、low-signal reasons
- source 能跳转到对应 LLMWiki 页面
- source 能看到关联 GraphRAG 节点或社区
- 从 LLMWiki 页面和 GraphRAG 节点能反向定位 source
- 用户能判断该 source 是否被正确蒸馏，而不需要直接读 JSON

完成记录：

- HTTP 已新增 `/knowledge/source/trace`
- trace payload 已串起 `source / distill units / LLMWiki pages / GraphRAG nodes / edges / communities / trace_summary`
- `/knowledge` 已新增 Source Trace 面板，展示原始文件、unit 数、LLMWiki page 数、GraphRAG node/community 数
- Source Trace 面板已支持跳转 LLMWiki 页面、定位 GraphRAG 节点和社区
- 自动化验证：`backend/tests/test_data_service_api.py` 为 `9 passed`；前端 `npm run build` 通过

### Phase 5.5：Directory Watcher

状态：✅ 第一版完成

开发目的：

- 对绑定目录提供文件变化感知
- 默认不自动重建，先把变化进入待刷新队列，让用户确认

输出物：

- 目录监听开关：开启、暂停、关闭
- 待刷新队列：新增、修改、删除、无法读取
- 变更摘要：影响 source 数、建议刷新模式、上次扫描时间
- 自动刷新开关作为后续增强项，默认关闭

验收标准：

- 绑定目录新增文件后，前端能看到待收录变更
- 修改文件后，前端能看到待增量刷新变更
- 删除文件后，前端提示 source 可能需要停用或重新构建
- 未经确认不自动改写知识产物

完成记录：

- HTTP 已新增 `/knowledge/directories/scan`
- 后端已对绑定目录做受控扫描，按 `new / modified / deleted / unreadable / unchanged` 生成变更摘要
- 扫描快照已持久化到 `workspace/lifecycle/directory_scan.json`，用于下一次扫描比较
- 已复用 workspace/source allowlist、realpath 和 symlink 防绕过校验；扫描只读取支持的 source 后缀
- `/knowledge` 已新增 Directory Watcher 面板，展示文件总数、新增、修改、删除、无法读取和待刷新队列
- 用户确认后可把新增/修改文件作为 `incremental` refresh 输入；删除文件先提示后续停用或重建，不自动改写知识产物
- 第一版是“手动扫描 + 待刷新队列”，后台常驻 watcher、暂停/恢复开关和自动刷新保持为后续增强
- 自动化验证：`backend/tests/test_data_service_api.py` 为 `10 passed`；前端 `npm run build` 通过

### Phase 5.6：低信号 source 回归抽查

状态：✅ 审计面板第一版完成，持续真实数据回归

开发目的：

- 确认 `zero_unit_count=0` 不是靠制造弱结论换来的
- 保持 title-only / low-content source 只落到保守的 `question / note / fact_candidate / risk`
- 让 distill 的低信号治理稳定传导到 LLMWiki topic 页面和 GraphRAG 输入

验收标准：

- `row/deepseek_split` 全量 ingest 稳定通过
- `summary.json.quality.distill.zero_unit_count == 0`
- `title_derived_conclusion_count == 0`
- 低信号 source 的 topic 页收缩到核心主题，原始长标题只保留在 source 页用于追溯
- 抽查页面不出现“标题被当成事实/结论”的内容
- GraphRAG top communities 中不出现新增 title fallback 引入的明显长标题或功能尾缀主题

完成记录：

- HTTP 已新增 `/knowledge/quality/low-signal-audit`
- 审计 payload 已聚合 `zero_unit_count`、`title_derived_conclusion_count`、标题派生强语义 unit、LLMWiki 长标题泄漏、GraphRAG top community 长标题泄漏
- 标题派生安全白名单固定为 `question / note / fact_candidate / risk`
- `/knowledge` 的 Distill Quality 面板已新增 Low Signal Audit 区块，展示 passed / warning / failed 检查项、关键指标和风险样本
- 自动化验证：`backend/tests/test_data_service_api.py` 为 `10 passed`；前端 `npm run build` 通过
- 真实知识库 `/Users/Zhuanz/Desktop/workspace/知识库/workspace` 审计结果：`zero_unit_count=0`、`title_derived_conclusion_count=0`、LLMWiki/GraphRAG 长标题泄漏为 0，但 `disallowed_title_derived_count=33`，主要是标题派生 `topic_candidate`；这是下一步质量治理的真实缺口
- 后续仍需用 `row/deepseek_split` 定期复跑，抽查 topic/page 内容是否真的没有把标题当成强事实

### Phase 4.1：Agent / MCP 真实使用收紧

开发目的：

- 让 Agent 能稳定读取质量状态、提交受控反馈、查看 approved impact
- 避免 MCP tool 输出膨胀、参数失控或跨 workspace 误读
- 固化质量治理 tool 的最小可用契约

验收标准：

- MCP tools 输出字段稳定，参数有上限和 allowlist 校验
- Agent 可读取 quality summary、correction plan、draft rules、approved impacts
- Agent 可提交 feedback，但审核动作仍是受控 enum：`draft / approved / rejected / archived / revoked`
- 多 workspace 场景下不会串 workspace 或读取未允许路径
- 读取 correction plan 不隐式写 workspace

### Phase 4.2：MCP 化知识库创建与管理

当前状态：Phase 4 优先项第一版已完成并通过外部 HarnessOS 真实验收。`data_service.mcp_stdio` 已提供 workspace/source/build lifecycle tools；已新增 v2 envelope tools；build start 已进入 workspace 级 operation queue，status 可轮询到终态；外部 HarnessOS 已通过持久化 MCP stdio session 跑通 create/import/build/poll/query/feedback/rules/review/plan/archive。

需求来源：

- 新要求来自 `../harnessOS/docs/architecture/data-service-mcp-codex-handoff.md`
- harnessOS 侧 Phase 5-A 只声明 `data_service_mcp` connector ref 与 tool contract，并实现 Connector Stub
- harnessOS 侧已完成真实 MCP client execution 验收，并补持久化 `McpStdioSession` 避免 build queue 状态随一次性 MCP 进程退出而丢失
- 当前项目侧需要把 `data_service.mcp_stdio` 扩展为真实 MCP lifecycle tools provider

开发目的：

- 让另一个 Harness 开发工程可以通过当前服务的 MCP server 创建、导入、构建、查询和治理知识库
- 把当前 `knowledge_ingest / knowledge_query / quality tools` 从“单 workspace 调用”扩展为“受控 workspace 生命周期管理”
- 保留旧 MCP tools 兼容性，同时提供 `knowledge_ingest_v2 / knowledge_query_v2 / knowledge_quality_*_v2 / knowledge_correction_*_v2` 统一 envelope tools
- 让外部工程不需要理解本项目内部目录结构，也不直接写 `workspace/row / llmwiki / graphrag / quality` 产物

统一返回 envelope：

所有新增 lifecycle tools 必须返回 JSON object：

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

约束：

- workspace-scoped call 必须返回 `workspace_id`
- 长构建操作必须返回 `operation_id`
- `warnings` 是可读字符串数组
- `artifact_refs` 是稳定 workspace artifact 或 source record 引用
- `next_actions` 告诉 Agent 下一步可执行动作
- `data` 承载 tool-specific payload
- lifecycle tools 与 v2 tools 返回 envelope；旧 tools 不强制改响应格式
- 业务可预期失败返回 `blocked` envelope；未知工具或严重 schema 错误仍走 MCP error

建议工具分层：

- `knowledge_workspace_create`
  - input：`name / root / owner / tags`
  - behavior：默认在 `DATA_SERVICE_WORKSPACE_ROOT` 下创建 workspace；如果提供 `root`，必须通过 allowlist 校验；初始化标准 Data Service workspace layout
  - output data：`workspace_path` 与 `capabilities.ingest/query/quality_feedback/build`
- `knowledge_workspace_list`
  - input：`owner / tag / limit`
  - behavior：只列出 `DATA_SERVICE_WORKSPACE_ROOT` 下允许访问的 workspace；`limit` 有上限
  - output data：`items[].workspace_id/name/workspace_path/status/updated_at/tags`
- `knowledge_workspace_describe`
  - input：`workspace_id` 或显式 `workspace`
  - behavior：每次独立校验 workspace；返回 layout、summary、engine、latest build、quality 状态
- `knowledge_source_import`
  - input：`workspace_id / paths / texts / metadata`
  - behavior：导入外部 Harness 提供的文件路径或 text payload；对 path 做 allowlist、realpath、symlink escape、文件大小校验；对 text 做长度上限；计算 `sha256` 并幂等处理重复导入；不得写入 generated LLMWiki / GraphRAG 输出目录
  - output data：`sources[].source_id/sha256/title/status/path`
- `knowledge_source_list`
  - input：`workspace_id / status / limit`
  - output data：`items[].source_id/sha256/title/status/low_signal/ingest_status`
- `knowledge_source_remove`
  - input：`workspace_id / source_id / reason`
  - behavior：软删除或停用 source，不物理删除历史 build artifacts，返回更新后的 source state
- `knowledge_build_start`
  - input：`workspace_id / mode`
  - mode：`full / incremental / graph_only / llmwiki_only`
  - behavior：不得长时间阻塞 MCP host；立即返回 `operation_id`；在 workspace 内记录 operation state，并进入 workspace 级 queue
  - stages：`source_import / distill / llmwiki / graphrag / quality_plan`
  - output data：`mode / stage / progress`
- `knowledge_build_status`
  - input：`workspace_id / operation_id`
  - output data：`mode / stage / progress / error / retryable / artifacts`
- `knowledge_build_cancel`
  - input：`workspace_id / operation_id / reason`
  - behavior：已完成则返回 completed state 并追加 warning；可取消则置为 `cancelled`；不得留下半写坏 workspace
- `knowledge_workspace_archive`
  - input：`workspace_id / reason`
  - behavior：标记 workspace read-only / archived，不物理删除数据

传输与集成策略：

- 第一阶段使用 stdio MCP：外部 Harness 工程以 MCP client 启动 `python -m data_service.mcp_stdio`，通过 `DATA_SERVICE_WORKSPACE_ROOT` 或显式 workspace 参数访问允许目录
- 第二阶段按需要补 streamable HTTP MCP bridge：复用同一套 tool schema，HTTP 层使用 API key / dev bypass / workspace allowlist，不重新实现业务逻辑
- MCP tool 只调用 `DataService` / HTTP API 的稳定边界，不绕过现有安全校验，不直接操作底层文件

安全与兼容要求：

- workspace access 限制在 `DATA_SERVICE_WORKSPACE_ROOT` 或既有 explicit allowlist
- source import 继续使用 source-path allowlist validation
- 所有路径先解析 realpath，再拒绝 symlink escape 和 path traversal
- 对 `limit / top_k / file count / text length / file size` 做 bounded limit
- 任何 MCP call 不得隐式修改全局 workspace state
- 每次 call 独立校验 workspace，不复用上一次 call 的隐式上下文
- 读取 correction plan 不隐式写 workspace，除非显式 `rebuild=true`
- 现有 quality governance 语义保持 read-time、reversible
- 不删除、不重命名既有 MCP tools，并保留 existing tools 的 per-call `workspace` 支持
- archived workspace 读操作可用，写操作返回 `blocked`
- 同一 workspace 的 build 串行排队，避免并发写产物目录
- server 中断遗留 running operation 标记为 `failed / retryable / server_interrupted`

验收标准：

- 外部 Harness 工程能通过 MCP 完成“创建 workspace -> 导入 source -> 启动构建 -> 查询状态 -> 查询知识 -> 提交质量反馈 -> 审核规则 -> 读取影响范围”
- 每个 lifecycle tool 返回统一 envelope，包含 `workspace_id / operation_id / status / warnings / artifact_refs / next_actions / data`
- v2 tools 返回统一 envelope，旧 tools 保持兼容
- workspace 与 source path 必须经过 allowlist 与 symlink 防绕过校验，不能访问未授权目录
- 重复导入同一 source 能幂等处理，不产生重复页面、重复 entity 或重复 source 记录
- 构建任务失败时返回可诊断阶段：`source_import / distill / llmwiki / graphrag / quality_plan`
- 长任务不阻塞 MCP host：`knowledge_build_start` 返回 operation id，`knowledge_build_status` 轮询状态
- 同 workspace build 串行排队
- queued build 可取消；running build 在阶段边界响应 cancel
- lifecycle 业务错误返回 `blocked`
- 保留现有 `knowledge_ingest / knowledge_query / quality tools` 兼容性；生命周期 tools 作为新层，不破坏当前 Agent 使用方式
- 现有 `knowledge_query / quality` tools 支持 `workspace_id`，外部 Harness 可用 opaque workspace id 完成查询、反馈、规则审核和读取 correction plan impact

外部 HarnessOS 真实验收记录：

- `workspace_id`: `harnessosrealdataserviceacceptance4`
- `operation_id`: `op_fb639a7aee3c`
- final `status`: `ok`
- `warnings`: `[]`
- 实际覆盖链路：`knowledge_workspace_create -> knowledge_source_import -> knowledge_build_start -> knowledge_build_status(completed) -> knowledge_query_v2 -> knowledge_quality_feedback_v2 -> knowledge_correction_rules_v2 -> knowledge_review_correction_rule_v2 -> knowledge_correction_plan_v2 -> knowledge_workspace_archive`
- 真实验收前需要确保 data_service venv 已完整安装 `backend/requirements.txt`，否则 build 阶段可能因 GraphRAG 依赖缺失失败

最小测试要求：

- `list_tools` 包含全部 lifecycle tools
- `list_tools` 包含全部 v2 envelope tools
- 临时 `DATA_SERVICE_WORKSPACE_ROOT` 下 workspace create/list/describe 可用
- source import from file 返回 `source_id` 和 `sha256`
- duplicate import 幂等，不创建重复 source records
- source import 对 allowlist 外路径返回 `blocked`
- source import 对 symlink escape 返回 `blocked`
- build start 返回 `operation_id` 和 queued/running status，且不阻塞
- 同 workspace 连续启动多个 build 时按队列串行执行
- build status 返回 stage、progress、artifacts、retryable error payload
- build cancel 返回 cancelled 或 completed-with-warning
- unknown source / operation 返回 `blocked`
- archived workspace 写类 v2 tools 返回 `blocked`
- running operation 遗留后标记为 `failed / retryable / server_interrupted`
- workspace archive 标记 archived 并保留数据
- multi-workspace calls 保持隔离
- existing quality tools 继续通过

当前验证：

- `python3.12 -m pytest backend/tests/test_data_service_mcp.py -q`：`14 passed`
- `python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q`：`74 passed, 14 skipped`
- `python3 -m pytest backend/tests/test_llmwiki.py -q`：`34 passed`

### 统一验收流程

每个开发包完成后执行：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
python3 -m pytest backend/tests/test_llmwiki.py -q
npx vite build
```

真实知识库端到端验收：

- 输入目录：`/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split`
- LLMWiki success
- GraphRAG indexed
- distill units 可读、可追溯
- `zero_unit_count=0`
- `title_derived_conclusion_count=0`
- top communities 没有明显噪音主题
- `/knowledge` 能完成反馈、规则生成、审核、消费计划、撤回闭环
- 外部 Harness 工程能通过 MCP 生命周期 tools 创建并管理一个独立测试知识库
- 外部 HarnessOS 真实 MCP E2E 已通过，后续回归需确保最终 `status=ok`、`warnings=[]`

## 建议执行顺序

1. 保持 Phase 4：依赖环境固化、外部调用文档和 MCP 验收链路回归
2. 保持外部 Harness 工程真实调用结果继续反压 v2 envelope、blocked error 与 operation queue schema
3. Phase 5.2-5.5 第一版已完成，继续用真实知识库回归 `/knowledge` 产品主流程
4. 补强 Directory Watcher 后续增强：后台常驻监听、暂停/恢复、自动刷新开关和删除 source 后续处理向导
5. 持续推进 Phase 5.6 后续：低信号 source 内容级人工抽查、LLMWiki topic/page 可读性观察和 GraphRAG owner 边界下沉
