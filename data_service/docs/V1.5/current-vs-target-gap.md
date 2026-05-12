# Local Knowledge Governance Service 当前实现与剩余收敛项

更新时间：2026-05-12

## 总体结论

当前仓库已经具备独立本地知识治理服务的主体能力：MCP、CLI、HTTP、workspace/source/build lifecycle、distill、LLMWiki、GraphRAG、Source Trace、Quality Governance 和目录扫描。PhaseG31 已完成 V1.5 closure acceptance，V1.5 收口状态为 accepted。

V1.0 中记录的主要偏差大多已经闭环：MCP handler 模块化、GraphRAG service 边界、MCP/HTTP contract hardening、typed distill units、docx/yaml 格式扩展、服务治理控制台、前端 GraphRAG 可见性和 PhaseG1-G13 接口语义收敛均已完成并通过出门验证。

当前文档不再把这些已完成项视为开放 gap。剩余收敛项主要是兼容窗口和后续演进：

- 代码包名仍保留 `data_service`，作为当前实现承载层和兼容入口。
- HTTP / CLI 仍保留 `/api/v1/knowledge/*` 和 `data_service` 兼容语义，部分入口仍允许 `workspace` path；PhaseG30 已开放首批目标 HTTP `/api/workspaces/{workspace_id}/...`，但旧入口仍处于兼容窗口。
- 目标 CLI `knowledge *` 仍有 advanced graph / session 子命令未开放；PhaseG28/G29 已开放 MCP distill preview 与 source trace，后续不得把其它 planned 能力误认为已开放。
- Low Signal Audit 已在 PhaseG7 抽成 shared contract helper；Quality Summary / Correction Plan 已在 PhaseG8 固化当前 MCP contract 与漂移护栏；Quality Feedback / Rules / Review 已在 PhaseG9 固化当前 MCP contract 与漂移护栏，并在 PhaseG10/G11 将现有 HTTP quality 兼容入口迁移到 shared helper。PhaseG12 已固化 Quality CLI planned 迁移窗口，PhaseG13 已开放 `data_service quality` 只读 preview，PhaseG14 已开放写入型治理命令，PhaseG15 已提供 `knowledge quality` entrypoint-ready alias，PhaseG18 已开放 `knowledge query` 最小 alias，PhaseG19 已开放 `knowledge workspace list/describe` 只读 alias，PhaseG20 已开放 `knowledge source list` 只读 alias，PhaseG21 已开放 `knowledge build status` 只读 alias，PhaseG22 已开放 `knowledge graph snapshot` 只读 alias，PhaseG23 已开放 `knowledge trace source` 只读 alias，PhaseG25 已开放 `knowledge workspace create/archive` 写入型 alias，PhaseG26 已开放 `knowledge source import/remove` 写入型 alias，PhaseG27 已开放 `knowledge build start/cancel` 写入型 alias，PhaseG28 已开放 MCP `knowledge_distill_preview`，PhaseG29 已开放 MCP `knowledge_source_trace`，PhaseG30 已开放首批目标 HTTP query / distill / source trace，PhaseG31 已完成 V1.5 收口验收。
- 目标 workspace layout 仅作为内部演进方向，外部 contract 仍只依赖 MCP / CLI / HTTP 的稳定字段。

## Draw.io 文档职责与冻结规则

- `docs/V1.5/data-service-v1.5-roadmap.drawio` 是 V1.5 主路线图（canonical master），负责完整表达 V1.0 固化基线、V1.5 目标架构、详细开发计划和验收里程碑。
- `docs/V1.5/current-vs-target-gap.drawio` 是唯一维护的 Current vs Target / Gap 摘要图，只承载当前状态、目标架构、阶段摘要和验收摘要。
- V1.5 已在 PhaseG31 accepted 后冻结。`data-service-v1.5-roadmap.drawio`、`current-vs-target-gap.drawio` 和本文档必须保持 PhaseG31 accepted 状态一致。
- 如这些文件出现不一致，只允许做勘误修正，不在 V1.5 文档中新增 V1.6 能力描述。

## V1.5 收口进度

当前已把 2026-05-07 的差距作为 V1.0 基线冻结，V1.5 开始按 MCP-first、最小粒度和微服务化方向收口。

- PhaseA1 已完成 Session MCP handler 模块化：`knowledge_session_*`、session graph、community、actor summary 从 `mcp_stdio.py` 拆到独立 handler；出门验证覆盖 session 创建、turns ingest、同步 build、graph snapshot、actor summary、session query 和 delete。
- PhaseA2 已完成 Quality MCP handler 模块化：`knowledge_quality_summary`、`knowledge_correction_plan`、`knowledge_quality_feedback`、`knowledge_correction_rules`、`knowledge_review_correction_rule` 从 `mcp_stdio.py` 拆到独立 handler；出门验证覆盖质量反馈、规则生成、审核、纠正计划、质量汇总和 V2 envelope。
- PhaseA3 已完成 Core MCP handler 模块化：`knowledge_ingest`、`knowledge_query` 从 `mcp_stdio.py` 拆到独立 handler；出门验证覆盖 ingest、hybrid query 和 V2 query envelope。
- PhaseA4.1 已完成 Workspace MCP handler 模块化：`knowledge_workspace_create`、`knowledge_workspace_list`、`knowledge_workspace_describe`、`knowledge_workspace_archive` 从 `mcp_stdio.py` 拆到独立 handler；出门验证覆盖 create、describe、owner/tag list、archive 和归档后 describe。
- PhaseA4.2 已完成 Source MCP handler 模块化：`knowledge_source_import`、`knowledge_source_list`、`knowledge_source_remove` 从 `mcp_stdio.py` 拆到独立 handler；出门验证覆盖文本导入、重复导入、列表、软删除、removed 过滤和归档 workspace 写保护。
- PhaseA4.3 已完成 Build MCP handler 模块化：`knowledge_build_start`、`knowledge_build_status`、`knowledge_build_cancel` 从 `mcp_stdio.py` 拆到独立 handler；出门验证覆盖 source 导入后 build start/status 到完成、终态 cancel warning 和归档 workspace build 阻断。
- PhaseA5.1 已完成 MCP common helpers 模块化：`now`、`bounded_int`、`slug`、`read_json`、`write_json`、`envelope`、`blocked` 从 `mcp_stdio.py` 拆到 `mcp_common.py`；出门验证覆盖 workspace/source/build 完成链路和 archived workspace blocked envelope。
- PhaseA5.2 已完成 MCP workspace runtime 模块化：workspace root/meta/path resolve/layout helper 从 `mcp_stdio.py` 拆到 `mcp_workspace_runtime.py`；出门验证覆盖 workspace create/describe、source import、build completed、archive 和 archived build blocked。
- 本阶段同步修复异步 build/status 并发 JSON 读写的瞬态误判：MCP 与 session operation 写入改为原子替换，避免轮询读到半截 JSON 后误判为 blocked。
- PhaseA5.3 已完成 MCP build runtime 模块化：operation envelope、source ingest status、operation update、取消检查、interrupted running operation 标记、单 workspace build queue 和 worker lifecycle 从 `mcp_stdio.py` 拆到 `mcp_build_runtime.py`；出门验证覆盖同一 workspace 两个 queued build 依次 completed、source built 和 archived build blocked。
- PhaseA5.4 已完成 MCP registry / resource / dispatch 模块化：tool registry 拆到 `mcp_tool_registry.py`，resource specs/reader 拆到 `mcp_resources.py`，tool dispatch 拆到 `mcp_dispatcher.py`；出门验证覆盖 38 tools、resources、build completed、query_v2、legacy resource URI 兼容和 archived V2 blocked。
- MCP resource URI 已规范化为 `data-service://summary`、`data-service://layout`；reader 继续兼容旧 `data_service://summary`、`data_service://layout` 输入。
- PhaseA5.5 已完成 MCP contract tests：补齐 tool registry、resource URI/canonicalization、resource reader、direct dispatcher archived V2 blocked 和 unknown tool error contract；MCP 专项回归提升为 19 passed，组合回归提升为 97 passed。
- PhaseB1 已完成 Session GraphRAG service 边界抽取：新增 `backend/app/graphrag/service/session_graph_service.py`，承载 session graph build、snapshot、neighbors、community summary、session query 和 actor summary；`backend/data_service/session_service.py` 继续只负责 session lifecycle、ingest、operation 和持久化编排。
- PhaseB1 出门验证已完成：MCP 专项回归 20 passed；Data Service/API/MCP 组合回归 98 passed；覆盖 3 speaker / 10 turn session E2E、A/B session 隔离、actor summary source_refs 保留和 GraphRAG service 边界 contract。
- PhaseB2 已完成 Session relation extractor 边界抽取：新增 `backend/app/graphrag/service/session_relation_extractor.py`，承载 session unit classification、topic/entity extraction、actor relation、source relation 和 co-occurrence relation；`SessionKnowledgeService` 只读取 session source payload 并委托 extractor。
- `mcp_stdio.py` 当前约 84 行，基本只承载 MCP SDK server 绑定与 stdio 入口。PhaseB 核心服务边界已收敛，下一阶段进入 PhaseC Contract Hardening。
- PhaseB2 出门验证已完成：MCP 专项回归 21 passed；Data Service/API/MCP 组合回归 99 passed；覆盖 relation extractor boundary contract、3 speaker / 10 turn session E2E、A/B session 隔离、actor summary source_refs 保留。
- PhaseC1 已完成 MCP external payload hardening：`mcp_common.envelope` 统一清洗外部响应，将 public `path` / `workspace_path` / `artifacts` 等字段收敛为 `artifact_ref` 与 `debug_paths`；内部 manifest、operation 和 workspace layout 持久化不变。
- PhaseC1 出门验证已完成：MCP 专项回归 22 passed；Data Service/API/MCP 组合回归 100 passed；新增 no-internal-path contract 覆盖 workspace create、source import、build start/status 和 workspace describe。
- PhaseC2 已完成 MCP error code contract hardening：`mcp_common` 新增统一 error normalization，blocked/failed/disposed 响应稳定携带 `data.error.code/message/retryable`；operation error 的 `type` 出站归一为 `code`。
- PhaseC2 出门验证已完成：MCP 专项回归 22 passed；Data Service/API/MCP 组合回归 100 passed；覆盖 unknown source、unknown operation、server interrupted failed operation 和 disposed session graph 的 error code contract。
- PhaseC3 已完成 HTTP envelope contract convergence：`backend/app/api/v1/data_service.py` 的 lifecycle HTTP envelope/blocked 响应复用 `data_service.mcp_common` 的 sanitizer 和 error normalization；HTTP 与 MCP 的 public payload 对 `path/workspace_path/original_path/bound_paths/roots/files/artifacts` 保持同一 debug 分层。
- PhaseC3 出门验证已完成：API 专项回归 10 passed；Data Service/API/MCP 组合回归 100 passed；覆盖 workspace create/list、source import/list/remove、directory scan、build start/status 和 unknown operation 的 HTTP no-internal-path / error code contract。
- PhaseD1 已完成 typed distill units v1.2 兼容映射：`DataService.DISTILL_SCHEMA_VERSION` 升级到 `1.2`，每个 distill unit、engine handoff、distill bundle 和 source profile 均携带 `typed_unit` / `typed_unit_type_counts`；旧 `kind` 与旧 GraphRAG/LLMWiki 消费路径保持兼容。
- PhaseD1 出门验证已完成：Data Service 专项回归 68 passed；Data Service/API/MCP 组合回归 100 passed；覆盖 schema 1.2、legacy kind -> typed type mapping、manifest/source/profile/provenance typed counts、engine handoff typed contract。
- PhaseD2 已完成 typed unit consumer hardening：`read_distill_bundle` 增加 `typed_unit_type` 过滤，HTTP 增加 `typed_unit_type` 请求字段，CLI 增加 `--typed-type`；boundary audit 与 quality summary 显式展示 typed unit contract 和 typed unit type 分布。
- PhaseD2 出门验证已完成：Data Service 专项回归 68 passed；API 专项回归 10 passed；Data Service/API/MCP 组合回归 100 passed；覆盖 CLI/HTTP typed filter、boundary typed contract、quality typed diagnostics。
- PhaseD3 已完成 typed fixture coverage：新增会议 turns fixture 覆盖 `meeting_summary/risk/claim/entity_evidence`，新增代码分析 JSON fixture 覆盖 `architecture_note/code_symbol/code_dependency/code_call_edge`；代码分析 JSON 继续用旧 `note/entity_candidate/relation_candidate` 兼容 kind 出站。
- PhaseD3 出门验证已完成：新增 fixture 2 passed；Data Service 专项回归 70 passed；Data Service/API/MCP 组合回归 102 passed；覆盖会议与代码上层适配输入在 typed unit contract 下的端到端生成和过滤。
- PhaseE1 已完成多格式扩展首段：新增 `DocxExtractor` 与 `YamlExtractor`，`DataService.SUPPORTED_SOURCE_SUFFIXES`、LLMWiki source type detection 和 distill excerpt 路径均支持 `docx/yaml/yml`；出门验证覆盖 docx/yaml 同时进入 distill、LLMWiki 和 GraphRAG。
- PhaseE1 出门验证已完成：新增 extractor + pipeline E2E 2 passed；本阶段后按要求进入代码检视与全量测试，重点观察外部开放能力是否仅新增格式支持而无隐藏性语义变更。
- PhaseE2 已完成格式治理诊断：distill source record、manifest quality、distill source profile 和 summary quality 均展示 `source_format`、`extractor_name`、`extractor_available`、`format_counts`、`extractor_counts` 与 `format_issue_sources`。
- PhaseE2 出门验证已完成：PhaseE docx/yaml pipeline E2E 1 passed；Data Service/API/MCP 组合回归 103 passed；drawio XML 校验通过。
- PhaseF1 已完成控制台 format diagnostics 可视化：`/knowledge` Overview 指标栏、Source 台账、当前 Source 工作流、Distill Detail 和 Distill Quality 面板均展示格式 / extractor 状态。
- PhaseF1 出门验证已完成：frontend `npm run build` 通过并生成静态产物；Data Service/API/MCP 组合回归 103 passed。
- PhaseF2 已完成控制台异常队列 drilldown：Overview 新增 failed source、unreadable file、low-signal sample、format issue 四类治理队列，并提供跳转到 Source Trace / Quality 的操作。
- PhaseF2 出门验证已完成：frontend `npm run build` 通过并生成静态产物；Data Service/API/MCP 组合回归 103 passed；backend 全量测试 138 passed；drawio XML 校验通过。
- PhaseF2 停点代码检视已完成：入口扫描覆盖 HTTP route、MCP stdio、CLI parser，本阶段未新增 MCP tool / HTTP route / CLI 参数，未发现隐藏性对外能力变更。
- PhaseF3 已完成控制台 MCP contract 可视化：`/knowledge` 新增 MCP 工作台页签，展示 38 tools、2 canonical resources、legacy resource URI 兼容入口和 V2 envelope alias 映射。
- PhaseF3 出门验证已完成：frontend `npm run build` 通过并生成静态产物；MCP 专项回归 23 passed；Data Service/API/MCP 组合回归 104 passed；新增控制台 contract 快照与后端 registry 一致性测试。
- PhaseF3 对外能力检查已完成：未新增 MCP tool / HTTP route / CLI 参数，本阶段只新增前端静态 contract 可视化与测试保护。
- PhaseF4 已完成控制台 MCP Debugger 本地预检：MCP 工作台新增 payload 预检面板，支持按 tool 生成示例 payload、required field 校验、JSON object 校验和 envelope 预览。
- PhaseF4 出门验证已完成：frontend `npm run build` 通过并生成静态产物；MCP 专项回归 23 passed；Data Service/API/MCP 组合回归 104 passed。
- PhaseF4 对外能力检查已完成：未新增 MCP tool / HTTP route / CLI 参数，Debugger 当前仅做前端本地预检与 envelope 预览，不执行真实 MCP call。
- PhaseF5 已完成前端社区图恢复与 Explore 工作台可读性优化：GraphRAG 入口显式打开 Explore 并定位社区图区块，社区图移动到 Explore 首屏，新增刷新、加载、空态和错误反馈。
- PhaseF5 出门验证已完成：frontend `npm run build` 通过并生成静态产物；MCP 专项回归 23 passed；Data Service/API/MCP 组合回归 104 passed。
- PhaseF5 已新增前端验收阶段：使用 Playwright 截图验证桌面视口和移动 `#graph-panel` 视口，截图归档到 `docs/V1.5/frontend-acceptance/`。
- PhaseF5 对外能力检查已完成：未新增 MCP tool / HTTP route / CLI 参数，本阶段只调整前端交互、布局和视觉可读性。
- PhaseF6 已完成 Source Trace 前端审计与修复：`GraphRAG 社区 暂无匹配社区` 被定位为 source 级直接匹配社区为空，不是主社区图缺失；前端已增加 direct match + global fallback、明确空态文案和自动补拉全局 `/graph`。
- PhaseF6 出门验证已完成：frontend `npm run build` 通过并生成静态产物；MCP 专项回归 23 passed；Data Service/API/MCP 组合回归 104 passed；Playwright 图谱截图验收已归档。
- PhaseF6 对外能力检查已完成：未新增 MCP tool / HTTP route / CLI 参数，本阶段只复用既有 `/graph` 与 `/source/trace` 响应修复前端体验。
- PhaseF7 已完成社区图不可见根因修复：`loadDistill()` 初始化不再自动触发 source 选择链路，避免 `?view=graph` 进入 Explore 后被隐式切回 Sources；GraphRAG 入口、`#graph-panel` 与 active workbench watch 均会补拉图谱。
- PhaseF7 已新增图谱可见性兜底：`GraphCommunityView` 接收 communities 并在画布内展示社区概览层，确保 147 nodes / 366 edges / 49 communities 的真实图谱在前端可见。
- PhaseF7 出门验证已完成：frontend `npm run build` 通过并生成静态产物；MCP 专项回归 23 passed；Data Service/API/MCP 组合回归 104 passed；Playwright 可见性截图归档到 `docs/V1.5/frontend-acceptance/data_service_phasef7_graph_visible_fixed.png`。
- PhaseF7 对外能力检查已完成：未新增 MCP tool / HTTP route / CLI 参数，本阶段只修复前端状态流、图谱加载兜底和社区视觉层。
- PhaseF8 已完成 GraphRAG 页面可读性优化：社区 chips 从画布内浮层移到画布上方，图谱质量诊断改为折叠治理面板，右侧信息优先展示选中社区/节点详情。
- PhaseF8 已完成移动端遮挡优化：移动端图谱高度区间收紧，画布内操作提示隐藏，成功 toast 缩短到 1.6 秒，避免遮挡主内容。
- PhaseF8 出门验证已完成：frontend `npm run build` 通过；MCP 专项回归 23 passed；Data Service/API/MCP 组合回归 104 passed；桌面与移动截图归档到 `docs/V1.5/frontend-acceptance/`。
- PhaseF8 对外能力检查已完成：未新增 MCP tool / HTTP route / CLI 参数，本阶段只修改前端布局、视觉层级和 toast 行为。
- PhaseF9 已完成 Explore 工作台规则网格重生成：`page-stack--explore` 改为 12 列 grid，GraphRAG 主图占满首行，Query 与 LLMWiki Summary 等高并排，Wiki Pages 独占下一行。
- PhaseF9 已收敛板块随机感：header 与主内容统一 1480px 宽度，GraphRAG 侧栏 detail / queue / diagnostics 使用统一 surface、border 和 8px radius。
- PhaseF9 出门验证已完成：frontend `npm run build` 通过；MCP 专项回归 23 passed；Data Service/API/MCP 组合回归 104 passed；桌面与移动截图归档到 `docs/V1.5/frontend-acceptance/`。
- PhaseF9 对外能力检查已完成：未新增 MCP tool / HTTP route / CLI 参数，本阶段只修改前端布局 CSS 和静态构建产物。
- PhaseF10 已完成 MCP Debugger response / error envelope 预览：控制台本地展示 success response、error envelope 和 compat/stable diff，并支持 `?view=mcp` 深链进入 MCP 工作台。
- PhaseF10 出门验证已完成：frontend `npm run build` 通过；MCP 专项回归 23 passed；Data Service/API/MCP 组合回归 104 passed；桌面与移动截图归档到 `docs/V1.5/frontend-acceptance/`。
- PhaseF10 对外能力检查已完成：未新增 MCP tool / HTTP route / CLI 参数，Debugger 仍只做本地预览，不执行真实 MCP call。
- PhaseG1 已完成接口语义统一基线：新增 `docs/V1.5/interface-convergence-matrix.md`，控制台 MCP Contract 展示 MCP / HTTP / CLI 三入口矩阵，并增加 contract drift 测试护栏。
- PhaseG1 当前约束：不新增 MCP tool / HTTP route / CLI command，不修改现有响应形态；`data_service` CLI 和 `/api/v1/knowledge/*` 继续作为兼容入口。
- PhaseG1 出门验证已完成：frontend `npm run build` 通过；MCP 专项回归 `24 passed`；Data Service/API/MCP 组合回归 `105 passed`；Interface Matrix 桌面与移动端截图已归档；drawio XML 校验通过。
- PhaseG1 对外能力检查已完成：未新增公开 MCP tool、HTTP route 或 CLI command；修复 `knowledge_build_cancel` 运行中取消的即时返回和后台 worker 覆盖竞态，使取消请求稳定返回 `cancelled`，避免隐藏性暴露 `running` 或被后续完成态覆盖。
- PhaseG2 已完成 query 最小能力组语义收敛：新增 `backend/data_service/query_contract.py`，MCP `knowledge_query`、HTTP `/api/v1/knowledge/query` 和 CLI `data_service query` 共享同一个 query payload serializer。
- PhaseG2 当前约束：不新增 MCP tool / HTTP route / CLI command，不改变 query 响应字段集合；新增三入口端到端 contract 测试防止后续漂移。
- PhaseG2 出门验证已完成：frontend `npm run build` 通过；MCP 专项回归 `25 passed`；Data Service/API/MCP 组合回归 `106 passed`；drawio XML 校验通过。
- PhaseG2 对外能力检查已完成：未新增公开 MCP tool、HTTP route 或 CLI command；query 响应字段集合保持 `mode / query / answer / hits / engine_payloads`。
- PhaseG3 已完成 distill preview 最小能力组语义收敛：新增 `backend/data_service/distill_contract.py`，HTTP `/api/v1/knowledge/distill` 和 CLI `data_service distill` 共享同一个 distill preview payload contract。
- PhaseG3 当时约束：不新增 `knowledge_distill_preview` MCP tool，不新增 HTTP route 或 CLI command，不改变 distill preview 响应字段集合；新增 HTTP / CLI 端到端 contract 测试防止后续漂移。
- PhaseG3 出门验证已完成：frontend `npm run build` 通过；新增 distill HTTP / CLI contract 测试 `1 passed`；MCP 专项回归 `25 passed`；Data Service/API/MCP 组合回归 `107 passed`；drawio XML 校验通过。
- PhaseG3 对外能力检查已完成：未新增公开 MCP tool、HTTP route 或 CLI command；distill preview 响应字段集合保持不变，MCP distill tool 仍为 planned。
- PhaseG4 已完成 Source Trace 目标 contract 设计：新增 `docs/V1.5/source-trace-contract.md`，固化当前 HTTP `/api/v1/knowledge/source/trace` 请求/响应字段，明确 MCP `knowledge_source_trace` 和 CLI `knowledge trace source` 仍为 planned。
- PhaseG4 当前约束：不新增 MCP tool / HTTP route / CLI command，不改变 Source Trace 响应字段集合；新增漂移测试防止 planned 入口提前落地或 HTTP trace 形态漂移。
- PhaseG4 出门验证已完成：frontend `npm run build` 通过；新增 Source Trace target contract 测试 `2 passed`；MCP 专项回归 `25 passed`；Data Service/API/MCP 组合回归 `109 passed`；drawio XML 校验通过。
- PhaseG4 对外能力检查已完成：未新增 `knowledge_source_trace` MCP tool、未新增 `knowledge trace source` CLI command、未新增 HTTP route；`/api/v1/knowledge/source/trace` 响应字段集合保持不变。
- PhaseG5 已完成 Source Trace shared contract helper：新增 `backend/data_service/source_trace_contract.py`，当前 HTTP `/api/v1/knowledge/source/trace` 已复用 `source_trace_payload`，API 层不再持有 trace payload 组装逻辑。
- PhaseG5 当前约束：不新增 MCP tool / HTTP route / CLI command，不改变 Source Trace 响应字段集合；新增 HTTP response 与 shared helper 完全一致的 contract 测试。
- PhaseG5 出门验证已完成：frontend `npm run build` 通过；新增 Source Trace shared contract 测试 `2 passed`；MCP 专项回归 `25 passed`；Data Service/API/MCP 组合回归 `110 passed`；drawio XML 校验通过。
- PhaseG5 对外能力检查已完成：未新增 `knowledge_source_trace` MCP tool、未新增 `knowledge trace source` CLI command、未新增 HTTP route；`/api/v1/knowledge/source/trace` 响应字段集合保持不变。
- PhaseG6 已完成 Source Trace schema 示例与迁移窗口文档化：`docs/V1.5/source-trace-contract.md` 已补 HTTP request、目标 MCP request、目标 CLI 参数、response schema 示例和 Stage 1-4 迁移说明。
- PhaseG6 当前约束：不新增 MCP tool / HTTP route / CLI command，不改变 Source Trace 响应字段集合；新增 drift test 防止文档中的 schema、`limit` contract 和 `source_trace_payload` 复用规则漂移。
- PhaseG6 出门验证已完成：frontend `npm run build` 通过；新增 Source Trace schema drift 测试 `1 passed`；MCP 专项回归 `25 passed`；Data Service/API/MCP 组合回归 `111 passed`；drawio XML 校验通过。
- PhaseG6 对外能力检查已完成：未新增 `knowledge_source_trace` MCP tool、未新增 `knowledge trace source` CLI command、未新增 HTTP route；`/api/v1/knowledge/source/trace` 响应字段集合保持不变。
- PhaseG7 已完成 Low Signal Audit shared contract helper：新增 `backend/data_service/quality_contract.py`，当前 HTTP `/api/v1/knowledge/quality/low-signal-audit` 已复用 `low_signal_audit_payload`，API 层不再持有 low-signal audit payload 组装逻辑。
- PhaseG7 当前约束：不新增 MCP tool / HTTP route / CLI command，不改变 Low Signal Audit 响应字段集合；新增 HTTP response 与 shared helper 完全一致的 contract 测试。
- PhaseG7 出门验证已完成：frontend `npm run build` 通过；新增 Low Signal Audit shared contract 测试 `1 passed`；MCP 专项回归 `25 passed`；Data Service/API/MCP 组合回归 `112 passed`；drawio XML 校验通过。
- PhaseG7 对外能力检查已完成：未新增 MCP tool、未新增 CLI `quality` command、未新增 HTTP route；`/api/v1/knowledge/quality/low-signal-audit` 响应字段集合保持不变。
- PhaseG8 已完成 Quality Summary / Correction Plan contract 固化：新增 `docs/V1.5/quality-contract.md`，明确 `knowledge_quality_summary` 与 `knowledge_correction_plan` 的 request / response 稳定字段、当前 HTTP 兼容入口和 planned CLI 状态。
- PhaseG8 当前约束：不新增 MCP tool / HTTP route / CLI command；不提前开放 `/api/v1/knowledge/quality/summary`；不新增 CLI `quality` command；新增 drift tests 防止 registry schema、HTTP route、CLI parser 和 E2E response shape 漂移。
- PhaseG8 出门验证已完成：frontend `npm run build` 通过；MCP 专项回归 `27 passed`；Data Service/API/MCP 组合回归 `114 passed`；drawio XML 校验通过。
- PhaseG8 对外能力检查已完成：未新增 MCP tool、未新增 HTTP route、未新增 CLI command；Quality Summary / Correction Plan 稳定字段集合保持不变。
- PhaseG9 已完成 Quality Feedback / Rules / Review contract 固化：扩展 `docs/V1.5/quality-contract.md`，明确 `knowledge_quality_feedback`、`knowledge_correction_rules`、`knowledge_review_correction_rule` 的 request / response 稳定字段、当前 HTTP 兼容入口和 planned CLI 状态。
- PhaseG9 当前约束：不新增 MCP tool / HTTP route / CLI command；不新增 CLI `quality` command；现有 `/api/v1/knowledge/quality/feedback`、`/feedback/list`、`/corrections`、`/corrections/build`、`/corrections/review` 兼容入口保持不变；Review 保持 non-destructive governance 语义。
- PhaseG9 出门验证已完成：frontend `npm run build` 通过；MCP 专项回归 `29 passed`；Data Service/API/MCP 组合回归 `116 passed`；drawio XML 校验通过。
- PhaseG9 对外能力检查已完成：未新增 MCP tool、未新增 HTTP route、未新增 CLI command；Quality Feedback / Rules / Review 稳定字段集合保持不变。
- PhaseG10 已完成 Quality HTTP shared helper 迁移：扩展 `backend/data_service/quality_contract.py`，新增 feedback / feedback list / correction rules / rules build / rule review payload helper，当前 HTTP quality 兼容入口已复用这些 helper。
- PhaseG10 当前约束：不新增 MCP tool / HTTP route / CLI command；不改变 Quality HTTP feedback / rules / review 响应字段集合；API 层只保留 request parsing、workspace resolve 和 HTTP error mapping。
- PhaseG10 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `17 passed`；MCP 专项回归 `29 passed`；Data Service/API/MCP 组合回归 `117 passed`；drawio XML 校验通过。
- PhaseG10 对外能力检查已完成：未新增 MCP tool、未新增 HTTP route、未新增 CLI command；Quality HTTP feedback / rules / review 兼容入口路径和响应字段保持不变。
- PhaseG11 已完成 Quality Correction Plan HTTP helper 迁移：扩展 `backend/data_service/quality_contract.py`，新增 `quality_correction_plan_payload`，当前 HTTP `/api/v1/knowledge/quality/corrections/plan` 已复用该 helper。
- PhaseG11 当前约束：不新增 MCP tool / HTTP route / CLI command；不改变 HTTP correction plan 响应字段集合；`quality_correction_plan_payload` 保持既有 HTTP build 语义，不新增 `rebuild` 请求字段。
- PhaseG11 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `18 passed`；MCP 专项回归 `29 passed`；Data Service/API/MCP 组合回归 `118 passed`；drawio XML 校验通过。
- PhaseG11 对外能力检查已完成：未新增 MCP tool、未新增 HTTP route、未新增 CLI command；HTTP correction plan 兼容入口路径和响应字段保持不变。
- PhaseG12 已完成 Quality CLI planned 迁移窗口固化：扩展 `docs/V1.5/quality-contract.md`，明确目标 `data_service quality ...` 命令形态、Stage 1-4 迁移窗口和未来 CLI 必须复用 shared helper / MCP handler 的约束。
- PhaseG12 当时约束：不新增 MCP tool / HTTP route / CLI command；当时 `data_service` CLI 已开放命令集合保持 `ingest / summary / distill / boundary / graphrag-execute / query`；`quality` 子命令未开放。
- PhaseG12 出门验证已完成：frontend `npm run build` 通过；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `119 passed`；drawio XML 校验通过。
- PhaseG12 对外能力检查已完成：未新增 MCP tool、未新增 HTTP route、未新增 CLI command；仅新增迁移窗口文档和 drift test。
- PhaseG13 已完成 Quality CLI 只读 preview 最小实现：`data_service quality summary / correction-plan / feedback-list / rules` 已开放，并全部复用 `data_service.quality_contract` helper。
- PhaseG13 当前约束：不新增 MCP tool / HTTP route；不开放写入型 CLI `feedback / rules-build / review`；`--workspace-id` 当前作为 `--workspace` 兼容别名解析为本地 workspace directory。
- PhaseG13 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `19 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `120 passed`；drawio XML 校验通过。
- PhaseG13 对外能力检查已完成：仅新增只读 CLI preview；MCP registry 与 HTTP route 集合保持不变；Quality HTTP 兼容入口响应字段保持不变。
- PhaseG14 已完成 Quality CLI 写入型治理命令：`data_service quality feedback / rules-build / review` 已开放，并全部复用 `data_service.quality_contract` helper。
- PhaseG14 当前约束：不新增 MCP tool / HTTP route；写入动作仍是 non-destructive governance，只记录 feedback、生成/审核 correction rules、刷新 approved correction plan，不直接改写 source。
- PhaseG14 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `20 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `121 passed`；drawio XML 校验通过。
- PhaseG14 对外能力检查已完成：仅新增 CLI 写入型治理命令；MCP registry 与 HTTP route 集合保持不变；Quality HTTP 兼容入口响应字段保持不变。
- PhaseG15 已完成 `knowledge quality ...` entrypoint-ready alias：新增 `knowledge_main`，复用 `data_service` CLI parser、quality 子命令和 `data_service.quality_contract` helper。
- PhaseG15 当前约束：不新增 MCP tool / HTTP route；不新增打包配置；不假设系统已安装独立 `knowledge` 命令；`data_service quality ...` 继续作为兼容入口。
- PhaseG15 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `21 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `122 passed`；drawio XML 校验通过。
- PhaseG15 对外能力检查已完成：仅新增 entrypoint-ready alias 函数；MCP registry、HTTP route 集合和 Quality HTTP 响应字段保持不变。
- PhaseG16 已完成 packaging / console script 最小配置：新增 `backend/pyproject.toml`，声明 `data-service = data_service.__main__:main` 和 `knowledge = data_service.__main__:knowledge_main`。
- PhaseG16 当前约束：不新增 MCP tool / HTTP route；不新增运行时依赖；`data_service quality ...` 继续作为兼容入口。
- PhaseG16 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `22 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `123 passed`；drawio XML 校验通过。
- PhaseG16 对外能力检查已完成：仅新增 packaging 元数据和 console script 声明；MCP registry、HTTP route 集合和 Quality HTTP 响应字段保持不变。
- PhaseG17 已完成 `knowledge` alias 公开面护栏：新增 `_build_knowledge_parser`，当前 `knowledge` 顶层命令严格限制为 `quality`，避免隐式开放 `knowledge ingest/query/distill/...`。
- PhaseG17 当时约束：不新增 MCP tool / HTTP route；不新增完整 `knowledge` alias 面；`data_service` 兼容 CLI 保持不变。
- PhaseG17 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `23 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `124 passed`；drawio XML 校验通过。
- PhaseG17 对外能力检查已完成：仅收窄 `knowledge` console script parser 到 `quality` 能力组；未扩大公开面。
- PhaseG18 已完成 `knowledge query` 最小 alias：`_add_query_parser` 被抽成共享 parser，`data_service query` 与 `knowledge query` 共用同一参数定义，并复用 `run_query_contract`。
- PhaseG18 当前约束：不新增 MCP tool / HTTP route；不新增 `knowledge workspace/source/build/distill/graph/trace` alias；`knowledge` 顶层仅允许 `quality` 和 `query` 两个能力组。
- PhaseG18 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `24 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `125 passed`；drawio XML 校验通过。
- PhaseG18 对外能力检查已完成：仅新增 `knowledge query` CLI alias；MCP registry、HTTP route 集合和 query 响应字段保持不变。
- PhaseG19 已完成 `knowledge workspace` 只读 alias：当前只开放 `list` 和 `describe`，并转调现有 `knowledge_workspace_list` / `knowledge_workspace_describe` MCP handler。
- PhaseG19 当时约束：不新增 MCP tool / HTTP route；不开放 `knowledge workspace create/archive`；不新增后续能力组 alias；`knowledge` 顶层仅允许 `quality`、`query` 和只读 `workspace`。
- PhaseG19 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `25 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `126 passed`；drawio XML 校验通过。
- PhaseG19 对外能力检查已完成：仅新增 `knowledge workspace list/describe` CLI alias；MCP registry、HTTP route 集合和 workspace envelope 字段保持不变。
- PhaseG20 已完成 `knowledge source list` 只读 alias：当前只开放 `list`，并转调现有 `knowledge_source_list` MCP handler。
- PhaseG20 当时约束：不新增 MCP tool / HTTP route；不开放 `knowledge source import/remove`；不新增后续能力组 alias；`knowledge` 顶层仅允许 `quality`、`query`、只读 `workspace` 和只读 `source`。
- PhaseG20 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `26 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `127 passed`；drawio XML 校验通过。
- PhaseG20 对外能力检查已完成：仅新增 `knowledge source list` CLI alias；MCP registry、HTTP route 集合和 source envelope 字段保持不变。
- PhaseG21 已完成 `knowledge build status` 只读 alias：当前只开放 `status`，并转调现有 `knowledge_build_status` MCP handler。
- PhaseG21 当前约束：不新增 MCP tool / HTTP route；不开放 `knowledge build start/cancel`；不新增 `knowledge distill/graph/trace` alias；`knowledge` 顶层仅允许 `quality`、`query`、只读 `workspace`、只读 `source` 和只读 `build`。
- PhaseG21 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `27 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `128 passed`；drawio XML 校验通过。
- PhaseG21 对外能力检查已完成：仅新增 `knowledge build status` CLI alias；MCP registry、HTTP route 集合和 build operation envelope 字段保持不变。
- PhaseG22 已完成 `knowledge graph snapshot` 只读 alias：当前只开放 `snapshot`，并转调现有 session MCP handler 的 `knowledge_graph_snapshot` 分支，固定 workspace scope。
- PhaseG22 当前约束：不新增 MCP tool / HTTP route；不开放 `knowledge graph neighbors/community/query/session`；不新增 `knowledge distill/trace` alias；当时 `knowledge` 顶层仅允许 `quality`、`query`、只读 `workspace`、只读 `source`、只读 `build` 和只读 `graph`。
- PhaseG22 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `28 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `129 passed`；drawio XML 校验通过。
- PhaseG22 对外能力检查已完成：仅新增 `knowledge graph snapshot` CLI alias；MCP registry、HTTP route 集合和 graph snapshot envelope 字段保持不变。
- PhaseG23 已完成 `knowledge trace source` 只读 alias：当前只开放 `source`，并复用 `source_trace_payload` shared serializer，输出字段与 HTTP `/api/v1/knowledge/source/trace` 保持一致。
- PhaseG23 当前约束：不新增 MCP tool / HTTP route；不开放 `knowledge_source_trace` MCP tool；不新增 `data_service trace` 兼容 CLI；`knowledge` 顶层仅允许 `quality`、`query`、只读 `workspace`、只读 `source`、只读 `build`、只读 `graph` 和只读 `trace`。
- PhaseG23 出门验证已完成：frontend `npm run build` 通过；API 专项回归 `29 passed`；MCP 专项回归 `30 passed`；Data Service/API/MCP 组合回归 `130 passed`；drawio XML 校验通过。
- PhaseG23 对外能力检查已完成：仅新增 `knowledge trace source` CLI alias；MCP registry、HTTP route 集合和 Source Trace 响应字段保持不变。

## 当前实际架构

```text
MCP / CLI / HTTP / Console
  -> backend/data_service
  -> distill
  -> backend/app/llmwiki
  -> backend/app/graphrag
  -> summary / trace / quality
```

当前定位：

- `backend/data_service` 是 Knowledge Governance Service 当前实现承载层。
- `backend/app/llmwiki` 是可读 Wiki 固化引擎。
- `backend/app/graphrag` 是内置 GraphRAG 执行与图谱查询服务。
- `/knowledge` 是服务治理控制台，而不是用户知识消费 App。
- `backend/data_service/mcp_stdio.py` 基本只承载 MCP SDK server 绑定与 stdio 入口；workspace/source/build/core/quality/session handlers、runtime、registry、resources 和 dispatcher 已拆分。
- PhaseG2/G3/G5/G7/G10/G11/G13/G14/G15/G16/G17/G18/G19/G20/G21/G22/G23 已分别为 query、distill preview、Source Trace、Low Signal Audit、Quality HTTP feedback/rules/review/plan、Quality CLI read-only preview、Quality CLI write commands、knowledge quality alias、packaging console script、alias surface guard、knowledge query alias、workspace read-only alias、source read-only alias、build status read-only alias、graph snapshot read-only alias 和 trace source read-only alias 抽出、复用或声明 shared contract helper；PhaseG8/G9 已固化 quality summary/plan/feedback/rules/review 当前 contract。后续 MCP / CLI / HTTP 新入口必须复用既有 handler 或 shared helper，不重新组装 payload。

## 目标架构

```text
External Apps / Agents / CLI / Console
  -> MCP / HTTP / CLI
  -> Knowledge Governance Service
  -> Workspace & Tenant Manager
  -> Source Registry
  -> Multi-format Parser
  -> Normalize Pipeline
  -> Distill Engine
  -> Entity & Relation Extractor
  -> LLMWiki Builder
  -> GraphRAG Service
  -> Retrieval Service
  -> Source Trace Service
  -> Quality Governance Service
  -> Artifact Store
  -> Local Workspace Store
```

## 收敛项 1：命名和文档边界

当前：

- 代码包名仍是 `data_service`，这是当前实现承载层和兼容入口，不再视为必须立即重命名的架构偏差。
- 新增 V1.5 文档、drawio 和阶段报告已经统一使用 Local Knowledge Governance Service / Knowledge Governance Service。
- `/knowledge` 已重新定位为服务治理控制台，而不是终端用户知识消费 App。
- 历史文档中仍可能保留个人知识库产品、会议应用上下文或旧 `/knowledge` 叙述；这些属于归档语境，不作为当前设计依据。

剩余约束：

- 不做大规模破坏性重命名，直到 MCP / CLI / HTTP 新入口有迁移计划和兼容 shim。
- 新增文档必须继续以 Knowledge Governance Service 为主叙事，并明确 `data_service` 是当前实现层。

## 收敛项 2：Workspace / Tenant Contract

当前：

- 已有 `workspace_id`、workspace path、bound paths、source manifest 和 lifecycle operations。
- MCP workspace/source/build lifecycle 已以 `workspace_id` 为主语义。
- MCP 和 HTTP lifecycle public payload 已完成 `artifact_ref` / `debug_paths` 分层，外部响应不再把内部 path 当作稳定字段。
- HTTP / CLI 兼容入口仍允许直接传 `workspace` path，用于现有控制台和旧脚本。

剩余收敛：

- `workspace_id` 继续作为稳定外部 ID。
- `root_path` / bound paths 只作为控制台和 debug 语境，不进入稳定公共 contract。
- 后续 HTTP / CLI 新入口逐步收敛到 workspace-scoped 语义；旧 `workspace` path 入口保留兼容窗口。

## 收敛项 3：服务治理控制台

当前：

- `/knowledge` 已能展示 summary、query、LLMWiki、GraphRAG、distill、Source Trace 和 quality。
- 历史定位偏终端用户知识消费产品。
- PhaseF1 已将 PhaseE2 的 format diagnostics 显示到控制台：Overview 显示格式数量，Sources 显示每个 source 的 format / extractor，Quality 显示 format_counts / extractor_counts / format_issue_sources。
- PhaseF2 已将 failed/unreadable/low-signal/format issues 合并到 Overview 的异常队列，支持直接定位 Source Trace 或 Quality 工作流。
- PhaseF3 已新增 MCP 工作台，把 MCP tool/resource contract、V2 alias 和兼容入口放到控制台可观察面，同时用测试防止前端 contract 快照偏离后端 registry。
- PhaseF4 已把 MCP 工作台推进到本地 Debugger：可选 tool、生成示例 payload、校验 required fields，并预览调用 envelope；执行面仍未打开，避免引入隐藏性公共能力变化。
- PhaseF5 已恢复 GraphRAG 社区图作为 Explore 工作台首屏主体，并新增前端截图验收阶段；后续真实大图谱密度仍需要在有数据 workspace 下补充视觉验收。
- PhaseF6 已修复 Source Trace 社区空态误导：当 source 级社区没有直接匹配时，控制台展示相关全局社区或全局候选，并说明 direct / visible community 数量差异。
- PhaseF7 已修复 GraphRAG 入口不可见问题：`?view=graph` 保持 Explore，初始化 distill 不再隐式切换到 Sources，图谱画布内增加社区概览兜底。
- PhaseF8 已优化 GraphRAG 页面信息层级：图谱画布不再被社区 chips 遮挡，社区详情优先于队列和质量诊断，移动端减少浮层遮挡。
- PhaseF9 已重生成 Explore 规则工作台：桌面端以 12 列 grid 固化主图、查询、摘要和 Wiki 区块位置，降低板块大小不一的视觉问题。
- PhaseF10 已补齐 MCP Debugger response / error envelope 预览：控制台能在不执行真实 MCP call 的前提下展示 payload、success、error 和 compat diff。
- PhaseG1 已固化接口矩阵与迁移护栏：MCP 为 primary contract，HTTP / CLI 保持 compat。
- PhaseG2 已对 query 引入目标语义 shim：三入口共享内部 query contract helper。
- PhaseG3 已对 distill preview 引入目标语义 shim：HTTP / CLI 共享内部 distill contract helper，MCP distill tool 仍保持 planned。
- PhaseG4 已固化 Source Trace 目标 contract：当前只保留 HTTP 兼容入口，MCP / CLI trace 入口继续 planned。
- PhaseG5 已抽取 Source Trace shared contract helper：`source_trace_payload` 作为当前 HTTP 与未来 MCP / CLI trace 的唯一 payload serializer。
- PhaseG6 已补齐 Source Trace schema 示例与迁移窗口：后续开放 MCP / CLI trace 必须复用 `source_trace_payload`，HTTP 兼容入口不得删除现有字段。
- PhaseG7 已抽取 Low Signal Audit shared contract helper：`low_signal_audit_payload` 作为当前 HTTP low-signal audit 与未来 quality CLI/HTTP 迁移的 payload serializer。
- PhaseG8 已固化 Quality Summary / Correction Plan contract：`knowledge_quality_summary` 与 `knowledge_correction_plan` 的 request / response 形态已文档化并加入 drift tests，`/api/v1/knowledge/quality/summary` 仍不开放。
- PhaseG9 已固化 Quality Feedback / Rules / Review contract：`knowledge_quality_feedback`、`knowledge_correction_rules`、`knowledge_review_correction_rule` 的 request / response 形态已文档化并加入 drift tests。
- PhaseG10 已迁移 Quality HTTP shared helper：`/quality/feedback`、`/feedback/list`、`/corrections`、`/corrections/build`、`/corrections/review` 复用 `data_service.quality_contract`，响应字段保持不变。
- PhaseG11 已迁移 Quality Correction Plan HTTP helper：`/quality/corrections/plan` 复用 `data_service.quality_contract`，响应字段保持不变。
- PhaseG12 已固化 Quality CLI planned 迁移窗口；PhaseG13 已开放 `data_service quality summary / correction-plan / feedback-list / rules` 只读 preview；PhaseG14 已开放 `feedback / rules-build / review` 写入型治理命令；PhaseG15 已提供 `knowledge quality ...` entrypoint-ready alias；PhaseG18 已开放 `knowledge query` 最小 alias；PhaseG19 已开放 `knowledge workspace list/describe` 只读 alias；PhaseG20 已开放 `knowledge source list` 只读 alias；PhaseG21 已开放 `knowledge build status` 只读 alias；PhaseG22 已开放 `knowledge graph snapshot` 只读 alias；PhaseG23 已开放 `knowledge trace source` 只读 alias；PhaseG25 已开放 `knowledge workspace create/archive` 写入型 alias；PhaseG26 已开放 `knowledge source import/remove` 写入型 alias；PhaseG27 已开放 `knowledge build start/cancel` 写入型 alias。

当前状态：

- `/knowledge` 已定义为 Knowledge Service Console。
- 控制台已覆盖 Overview、Sources、Distill、Wiki、GraphRAG、Trace、Quality、MCP Contract / Debugger 等治理视图。
- 前端社区图不可见、Source Trace 社区空态、板块大小不一和 MCP Debugger 预览均已完成阶段性修复与截图验收。

剩余收敛：

- 继续按真实大 workspace 做视觉回归，防止 GraphRAG 大图谱密度、移动端遮挡和空态文案回退。
- MCP Debugger 仍是本地预览，不执行真实 MCP call；如后续开放执行能力，需要单独评审权限和安全边界。

## 收敛项 4：多格式解析

当前已支持：

- `json`
- `txt`
- `md`
- `html`
- `csv`
- `pdf`
- `ppt`
- `pptx`
- `docx`
- `yaml` / `yml`

PhaseE1 已补齐 `docx` 与 `yaml/yml` 的基础抽取和端到端入库链路。PhaseE2 已补齐格式治理诊断：source profile、manifest quality 和 summary quality 可观察格式分布、extractor 分布和 extractor 缺失问题。PhaseF1/F2 已把这些诊断展示到控制台与异常队列。

复杂多模态输入由外部适配器处理后传入本服务，例如 OCR 文本、视频转写、代码分析产物和结构化 JSON。

当前状态：

- 多格式解析不再是主要开放 gap。
- 后续新增格式必须遵循 extractor + source profile + manifest quality + summary quality + 控制台展示 + 端到端出门验证的同一模式。

## 收敛项 5：typed distill units

当前：

- `DistilledUnitKind` 包含 `fact_candidate / question / conclusion / step / example / note / risk / entity_candidate / relation_candidate / topic_candidate`。
- PhaseD1 已增加 typed unit 兼容层：`topic_candidate -> concept`、`conclusion -> claim`、`step -> workflow`、`note -> meeting_summary`、`fact_candidate -> fact`、`entity_candidate -> entity_evidence`、`relation_candidate -> relation_evidence` 等映射随 unit 出站。
- PhaseD2 已将 typed unit type 接入服务消费侧：CLI / HTTP / distill preview 可以按 typed type 过滤，boundary / quality 能展示 typed contract 与分布。
- PhaseD3 已补会议 turns 与代码分析 JSON fixture：代码结构化输入会额外生成 `architecture_note/code_symbol/code_dependency/code_call_edge` typed units，同时不破坏旧 `kind`。

当前状态：

- distill schema 已从通用 unit 进入 typed distill units v1.2 兼容阶段；旧 `kind` 在迁移窗口内保留。
- 目标类型包括 `definition / concept / claim / decision / task / workflow / constraint / risk / example / misconception / entity_evidence / relation_evidence / meeting_summary / code_symbol / code_dependency / code_call_edge / architecture_note`。
- typed units 是支撑会议、学习、面试和代码理解四类上层应用的关键。

剩余收敛：

- 如继续扩展 typed units，应保持旧 `kind` 兼容、typed filter、boundary / quality diagnostics 和 fixture 覆盖同步推进。

## 收敛项 6：目标 workspace layout

当前：

- 已有 `distill/`、`llmwiki/`、`graphrag/`、`summary/`、`quality/`、`lifecycle/`。

目标：

```text
workspace/
├── manifest.json
├── sources/
├── normalized/
├── distill/
├── graph/
├── graphrag/
├── wiki/
├── retrieval/
├── trace/
└── quality/
```

目标布局仅作为内部演进方向。外部调用方只能依赖 MCP / CLI / HTTP。

当前状态：

- workspace layout 不是稳定外部 API。
- PhaseC 已通过 `artifact_ref` / `debug_paths` 分层防止内部路径外泄为稳定 contract。
- 目标布局可以继续内部演进，但不得要求外部应用读取 workspace 内部文件。

## 收敛项 7：接口语义统一

当前：

- MCP lifecycle/v2 tools 已成熟。
- Session、Quality、Core、Workspace、Source 与 Build MCP handler 已完成 V1.5 PhaseA1/PhaseA2/PhaseA3/PhaseA4.1/PhaseA4.2/PhaseA4.3 模块化，旧 tool name、payload 和 V2 envelope 兼容路径保持稳定。
- CLI 和 HTTP 仍保留当前 `data_service` / `/api/v1/knowledge/*` 兼容语义；HTTP lifecycle envelope 已开始复用 MCP sanitizer 和 error normalization。
- common envelope/error/json helper 已拆到 `mcp_common.py`，workspace runtime/helper 已拆到 `mcp_workspace_runtime.py`，build queue/runtime 已拆到 `mcp_build_runtime.py`，tool registry 已拆到 `mcp_tool_registry.py`，resource reader 已拆到 `mcp_resources.py`，tool dispatch 已拆到 `mcp_dispatcher.py`；`mcp_stdio.py` 基本只承担 MCP SDK server 绑定与 stdio 入口。
- PhaseG1 已固化 MCP / HTTP / CLI 接口矩阵与迁移护栏。
- PhaseG2 已统一 query 的 MCP / HTTP / CLI payload serializer。
- PhaseG3 已统一 distill preview 的 HTTP / CLI payload serializer，MCP distill tool 仍 planned。
- PhaseG4-G6 已固化 Source Trace 目标 contract、shared serializer、schema 示例和迁移窗口；MCP / CLI trace 入口仍 planned。
- PhaseG7 已统一 Low Signal Audit HTTP response 与 shared contract helper。
- PhaseG8 已固化 Quality Summary / Correction Plan 当前 contract 与 drift tests；`/api/v1/knowledge/quality/summary` 仍 planned / 未开放。
- PhaseG9 已固化 Quality Feedback / Rules / Review 当前 contract 与 drift tests。
- PhaseG10 已迁移现有 Quality HTTP feedback / rules / review 兼容入口到 shared helper。
- PhaseG11 已迁移现有 Quality HTTP correction plan 兼容入口到 shared helper。
- PhaseG12 已固化 Quality CLI planned 迁移窗口；PhaseG13 已开放 `data_service quality` 只读 preview；PhaseG14 已开放写入型 quality CLI；PhaseG15 已提供 `knowledge quality ...` entrypoint-ready alias；PhaseG18 已开放 `knowledge query` alias；PhaseG19 已开放 `knowledge workspace list/describe` 只读 alias；PhaseG20 已开放 `knowledge source list` 只读 alias；PhaseG21 已开放 `knowledge build status` 只读 alias；PhaseG22 已开放 `knowledge graph snapshot` 只读 alias；PhaseG23 已开放 `knowledge trace source` 只读 alias；PhaseG25 已开放 `knowledge workspace create/archive` 写入型 alias；PhaseG26 已开放 `knowledge source import/remove` 写入型 alias；PhaseG27 已开放 `knowledge build start/cancel` 写入型 alias。

当前状态：

- MCP 是默认主入口，CLI 和 HTTP 与 MCP 共享语义。
- 兼容入口保留到迁移窗口结束。
- 已完成 query、distill、trace、low-signal audit、quality summary / correction plan、quality feedback / rules / review 等最小能力组的内部 contract 收敛、目标 contract 固化或 HTTP shared helper 迁移。

剩余收敛：

- PhaseG24 已固化 `knowledge graph` advanced 子命令迁移窗口；`knowledge graph neighbors/community/query/session` 仍处于 planned。PhaseG25 已开放 `knowledge workspace create/archive` 写入型治理 alias。PhaseG26 已开放 `knowledge source import/remove` 写入型治理 alias。PhaseG27 已开放 `knowledge build start/cancel` 写入型治理 alias。PhaseG28 已开放 MCP `knowledge_distill_preview`。PhaseG29 已开放 MCP `knowledge_source_trace`；`knowledge` 当前顶层公开面只允许 `quality`、`query`、`workspace(create/list/describe/archive)`、`source(import/list/remove)`、`build(start/status/cancel)`、只读 `graph snapshot` 和只读 `trace source`。
- 后续 planned MCP / CLI / HTTP 新入口必须复用已抽出的 shared helper 或既有 handler 后才能开放。
- PhaseG30 已开放首批目标 HTTP route：`/api/workspaces/{workspace_id}/query`、`/api/workspaces/{workspace_id}/distill`、`/api/workspaces/{workspace_id}/sources/{source_id}/trace`；旧 `/api/v1/knowledge/*` 兼容入口不废弃。

## V1.5 剩余开发计划

详细计划见 `docs/V1.5/PHASE-G24-G31-REMAINING-DEVELOPMENT-PLAN-2026-05-12.md`。

- PhaseG24：Graph advanced CLI 迁移窗口已完成，已固化 `knowledge graph neighbors/community/query/session` planned contract，当前仍不开放 advanced 子命令。
- PhaseG25：Workspace write CLI contract 已完成，已开放 `knowledge workspace create/archive`，只复用现有 workspace MCP handler。
- PhaseG26：Source write CLI contract 已完成，已开放 `knowledge source import/remove`，只复用现有 source MCP handler。
- PhaseG27：Build write CLI contract 已完成，已开放 `knowledge build start/cancel`，只复用现有 build MCP handler。
- PhaseG28：MCP distill preview 已完成，已开放 `knowledge_distill_preview`，并复用 `run_distill_contract`。
- PhaseG29：MCP source trace 已完成，已开放 `knowledge_source_trace`，并复用 `source_trace_payload`。
- PhaseG30：目标 HTTP route 已完成，已开放 query / distill / source trace 首批 route，旧 `/api/v1/knowledge/*` 保留兼容窗口。
- PhaseG31：V1.5 收口验收已完成，closure status accepted；全量回归、公开面扫描、前端验收和 drawio/md 一致性检查通过。

V1.5 已完成收口。后续进入 V1.6 planning；V1.6 候选能力仅记录，不在 V1.5/PhaseG31 实现。

## 硬规则

1. 不依赖会议项目模块。可以接收会议转写文本，但不能 import meeting app 的代码。
2. 不依赖上层应用状态。面试、学习、代码助手都只能传入数据或查询请求。
3. 不暴露内部文件布局为稳定 API。workspace 内部存储可以演进；外部只认 MCP / CLI / HTTP contract。
