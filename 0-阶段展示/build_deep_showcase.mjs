import { mkdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const generatedAt = "2026-06-05";

const stages = {
  accepted: { label: "已验收", tone: "accepted" },
  limited: { label: "受限完成", tone: "limited" },
  planning: { label: "规划/门禁", tone: "planning" }
};

const projects = [
  {
    slug: "01-codexPat-agent-desktop-pet",
    name: "codexPat / Agent Desktop Pet",
    short: "codexPat",
    label: "本地桌面工作猫",
    stage: "accepted",
    status: "V10.16 selected UX benchmark passed, 2026-06-05",
    type: "桌面 Agent 伴随反馈",
    summary: "把本地 Agent 工作状态压缩成可见、低打扰、可审计的桌面工作猫。",
    why: "它解决的是长时间本地 Agent 工作不可见的问题：开发者不必反复切回终端，就能知道任务在运行、卡住、成功、告警还是需要输入。",
    audience: ["本地开发者", "Codex/Agent 工作流用户", "需要低打扰状态反馈的人"],
    done: [
      "V10.16 通过 selected open-source UX benchmark 的本地 macOS 视觉质量与首跑引导场景验收。",
      "内置 premium bundled cats，核心动作覆盖 idle、thinking、running、success、warning、error、need_input、sleeping。",
      "Manager / Settings 支持预览、默认素材恢复、截图证据和普通用户首跑路径。"
    ],
    planned: [
      "继续打磨三分钟上手、Manager 解释和证据报告的一致性。",
      "扩展 2D action pack 与视觉 QA，但新增能力必须单独过证据门禁。",
      "provider、marketplace、release signing、跨平台与 3D 都进入后续独立阶段。"
    ],
    goals: [
      "让 Agent 后台任务状态在桌面层面稳定可见。",
      "保持 renderer 安全边界，不让桌宠接触 raw payload、token、shell command 或完整本地路径。",
      "把工程验收口径转成普通用户能理解的本地产品体验。"
    ],
    applications: [
      "开发者本地状态仪表：配合代码生成、测试、长任务执行。",
      "Agent 可视化外壳：未来可接不同本地 Agent，但必须通过安全事件协议。",
      "个性化桌面陪伴：以本地素材包和可审计状态机形成轻量情绪反馈。"
    ],
    journey: ["启动桌面应用", "首跑选择本地猫包", "本地事件进入状态机", "播放动作与微交互", "Manager 预览/恢复", "截图与验收报告留证"],
    boundary: [
      "允许声明：V10.16 selected open-source UX benchmark exceeded for tested local macOS visual quality and first-run onboarding scenarios.",
      "不能声明：Petdex parity achieved、3D ready、automatic photo-to-3D ready、provider integration verified、asset marketplace ready、production signed release ready、cross-platform ready、Windows ready。"
    ],
    sources: [
      ["V10.16 Final Acceptance Report", "../codexPat/docs/V10.x/v10_16-final-acceptance-report.md"],
      ["V10.x Target Architecture", "../codexPat/docs/V10.x/v10_x-target-architecture.md"],
      ["V10 Acceptance Evidence", "../codexPat/docs/V10.x/evidence/v10_acceptance_showcase_2026-06-05.png"]
    ],
    visuals: [
      ["拟真概念图", "assets/generated-prd-visuals/codexpat.png", "PRD-grounded desktop companion concept", "基于 V10.16 / V10.x PRD 生成的拟真产品图，非真实截图。"],
      ["真实截图", "assets/project-evidence/codexpat/v10-16-runtime-desktop.png", "V10.16 runtime desktop screenshot", "真实桌面运行证据，作为参考证据。"],
      ["真实证据", "assets/project-evidence/codexpat/work-cat-contact-sheet.png", "work-cat-v1 contact sheet", "核心动作覆盖的本地素材证据。"],
      ["验收报告", "assets/project-evidence/codexpat/v10-acceptance-showcase.png", "V10 acceptance showcase", "验收结论与禁止声明说明。"],
      ["PRD概念图", "01-codexPat-agent-desktop-pet/deep-images/deep-03-future-scenario.png", "后续本地伴随场景", "基于 V10.x 路线生成的未来场景图，非截图。"]
    ],
    accent: "#d97706"
  },
  {
    slug: "02-data-service-architecture-intelligence",
    name: "data_service / Architecture Intelligence",
    short: "data_service",
    label: "证据化架构服务",
    stage: "planning",
    status: "V2.10 target PRD: Generic Architecture Pattern Evidence Adapters",
    type: "架构证据与 Context Pack",
    summary: "为大型代码库、知识库和外部 Agent 提供可回溯的架构证据、报告和上下文包。",
    why: "V2.9 能识别 false acceptance，但在 registry、decorator、TUI command table、workflow manifest 等架构模式上会缺少 deterministic line ranges。V2.10 用通用模式适配器补齐这层能力。",
    audience: ["Tech Lead", "架构审查者", "外部 Coding Agent", "文档/审计 Agent"],
    done: [
      "已有控制台、GraphRAG community preview、统一查询、LLMWiki summary 等前端验收图。",
      "V2.8/V2.9 建立 public surface evidence、relationship、ranking、review report、context pack 的证据硬化方向。",
      "V2.10 PRD 明确 pattern adapter registry、AST binding、definition lookup、manifest resolver 和 runtime introspection candidate。"
    ],
    planned: [
      "实现 generic architecture pattern adapter registry。",
      "用 Python AST 绑定 registry assignment、decorator、class inheritance、factory call、manifest reference 到 line ranges。",
      "在 HarnessOS 和至少一个额外真实项目或真实项目式 fixture 上跑 E2E。"
    ],
    goals: [
      "把“代码看懂了”改成可采样、可回溯的 source file + line range 证据。",
      "让 HTTP / MCP / CLI 消费同一批架构资产。",
      "让 coding agent 获取压缩但不丢证据的 context pack。"
    ],
    applications: [
      "大仓库 onboarding：快速理解 public surfaces、模块边界和风险点。",
      "架构治理：持续发现文档漂移、缺证据声明和 unsupported patterns。",
      "Agent 任务规划：为自动修复、审查、文档更新提供证据约束。"
    ],
    journey: ["选择 codebase", "尝试 pattern adapters", "AST/definition lookup 绑定", "生成 accepted evidence 或 blocker", "输出 HTML/JSON/context pack", "人类审查与 Agent 消费"],
    boundary: [
      "V2.10 是目标 PRD 与架构线，不能把规划目标说成已实现。",
      "不能声明 full call graph、runtime topology inference、data-flow/control-flow/type inference、automatic architecture refactoring 或 HarnessOS-only hardcoded support。"
    ],
    sources: [
      ["V2.10 Target PRD", "../data_service/docs/V2.x/V2_10_TARGET_PRD.md"],
      ["V2.10 Target Architecture", "../data_service/docs/V2.x/V2_10_TARGET_ARCHITECTURE.md"],
      ["Frontend Acceptance Evidence", "../data_service/docs/V1.5/frontend-acceptance/data_service_phaseg31_default.png"]
    ],
    visuals: [
      ["拟真概念图", "assets/generated-prd-visuals/data-service.png", "PRD-grounded pattern evidence concept", "基于 V2.10 PRD 生成的拟真架构证据图，非真实截图。"],
      ["真实截图", "assets/project-evidence/data-service/console-default.png", "V1.5 knowledge console", "既有控制台体验证据，不等同于 V2.10 已完成。"],
      ["真实截图", "assets/project-evidence/data-service/console-graph.png", "Graph preview panel", "既有图谱/查询区域验收截图。"],
      ["PRD概念图", "02-data-service-architecture-intelligence/deep-images/deep-02-capability-map.png", "V2.10 pattern adapter map", "基于 V2.10 PRD 的能力图，非截图。"],
      ["PRD概念图", "02-data-service-architecture-intelligence/deep-images/deep-03-future-scenario.png", "Architecture review future", "基于应用前景的概念图。"]
    ],
    accent: "#2563eb"
  },
  {
    slug: "03-harnessOS-controlled-agent-workflow",
    name: "harnessOS / Controlled Agent Workflow OS",
    short: "harnessOS",
    label: "受控 Agent 工作流",
    stage: "planning",
    status: "V9 target PRD / high-risk baseline",
    type: "Agent 执行与 Workflow Studio",
    summary: "让 Agent 在可审计、可回滚、可人工接管的边界内执行、协作、审查和产出。",
    why: "harnessOS 的核心不是让 Agent 拥有无限 shell，而是把高风险执行拆成 policy、approval、capability、rollback、kill switch 和 evidence chain。",
    audience: ["AI 工程团队", "工作流编排者", "需要高风险门禁的组织"],
    done: [
      "已有 Workflow Studio 视觉验收图，覆盖工作流图、Agent 建议、产物、质量报告和治理证据。",
      "V8 已证明 station-agent workflow pilot ready for review。",
      "V9 PRD 完整定义 Agent Executor、多 Agent 编排、自主编码试点、Workflow Studio 产品化与受限 terminal worker。"
    ],
    planned: [
      "V9-1/2：Agent executor safety gate 与 controlled executor runtime。",
      "V9-3/4/5：多 Agent 编排、自主编码试点、受限 terminal worker。",
      "V9-6/7/8：Workflow Studio 产品化、生产治理门禁、最终验收。"
    ],
    goals: [
      "把 Agent 从建议推进到可审计执行，但不开放无限制 shell。",
      "让工作流、产物、diff、测试、review、rerun 和 evidence chain 可解释。",
      "让人工确认成为 durable mutation 和高风险自动化的硬边界。"
    ],
    applications: [
      "内部 AI 工程平台：需求拆分、实现、测试、review、修复的闭环。",
      "复杂业务自动化：需要审批、审计、回滚的多步骤流程。",
      "Workflow Studio：给非底层工程师配置、运行和审查 Agent 工作流。"
    ],
    journey: ["用户提出目标", "生成 workflow 与 Agent 分工", "形成执行计划", "高风险动作人工确认", "受控 executor 执行", "测试/Review Agent 审查", "Studio 展示产物与证据"],
    boundary: [
      "允许声明：V9 complete 后最多是 high-risk Agent execution and workflow productization baseline ready for review。",
      "不能声明：production ready、Agent executor ready、controlled executor ready、full multi-Agent orchestration ready、autonomous coding workflow ready、complete Workflow Studio ready、unrestricted terminal worker ready、production terminal automation ready。"
    ],
    sources: [
      ["V9 Target PRD", "../harnessOS/docs/design/V9.x/v9_target_prd.md"],
      ["V9 Target Architecture", "../harnessOS/docs/design/V9.x/v9_target_architecture.md"],
      ["Workflow Console Visual Evidence", "../harnessOS/apps/workflow-console/docs/visual-acceptance/workflow-studio-overview.png"]
    ],
    visuals: [
      ["拟真概念图", "assets/generated-prd-visuals/harnessos.png", "PRD-grounded controlled workflow concept", "基于 V9 PRD 生成的拟真工作流图，非真实截图。"],
      ["真实截图", "assets/project-evidence/harnessos/workflow-studio-overview.png", "Workflow Studio overview", "工作流图与画布助手真实视觉验收图。"],
      ["真实截图", "assets/project-evidence/harnessos/running-board.png", "Run board", "运行面板与状态展示。"],
      ["真实截图", "assets/project-evidence/harnessos/governance-evidence.png", "Governance evidence", "治理证据区域截图。"],
      ["PRD概念图", "03-harnessOS-controlled-agent-workflow/deep-images/deep-03-future-scenario.png", "V9 future scenario", "基于 V9 PRD 的未来场景图，非截图。"]
    ],
    accent: "#7c3aed"
  },
  {
    slug: "04-research-notebook-source-grounded-workbench",
    name: "ResearchNotebook / Source-grounded Workbench",
    short: "ResearchNotebook",
    label: "可信引用研究笔记",
    stage: "limited",
    status: "V2.x PRD expanded RC ready with limitations, 2026-06-02",
    type: "来源约束研究工作台",
    summary: "把多来源资料转成可信引用问答、Studio 输出和补源研究报告。",
    why: "ResearchNotebook 的价值不是回答更多，而是所有 Guide、QA、Studio artifact 和 Research report 都能回到 evidence_refs，并在资料不足时拒答。",
    audience: ["知识工作者", "研究者", "需要证据定位输出的人"],
    done: [
      "V2.8 报告显示 V2.x PRD expanded RC completed，出门状态为 ready with accepted limitations。",
      "Validated PDF / TXT / Markdown sources、approved public URL 前端验证、Sources 搜索、Notes 管理、Studio artifact 管理、AI quality fallback UI 已进入受限口径。",
      "OCR、Audio、PPT、Mindmap、Document Comparison 已记录决策或 NOT_READY，不伪装成完成。"
    ],
    planned: [
      "继续提升 P0/P1 source 稳定性、URL 安全抽取和多数据集人工质量验收。",
      "为 OCR、Audio、PPT、Mindmap、Compare 分别建立 provider、schema、preview、export、manual review 门禁。",
      "后续如果做协作、云同步或全来源类型，需要新阶段而不是扩大 V2 声明。"
    ],
    goals: [
      "降低从资料到可信输出的摩擦。",
      "让每个 AI 输出保留 evidence_refs 与 generation metadata。",
      "用 disabled / decision gate 明确高风险后置能力，避免 false ready。"
    ],
    applications: [
      "个人研究工作台：论文、报告、网页资料的导读、问答和学习材料生成。",
      "团队知识消化：项目资料整理成 briefing、FAQ、study guide。",
      "审计型 AI 输出：适合需要证据定位和拒答边界的场景。"
    ],
    journey: ["创建 Notebook", "导入 PDF/TXT/Markdown/approved URL", "查看 per-file 状态", "生成 Guide", "基于 Suggested Question 问答", "citation 定位证据", "补源后生成 Research report"],
    boundary: [
      "完成声明必须带 with accepted limitations。",
      "不能声明 all websites URL ready、all-source-type ready、full AI quality ready、OCR/Audio/PPT/Mindmap/Compare ready、cloud sync / collaboration ready。"
    ],
    sources: [
      ["V2 PRD", "../research-notebook/docs/design/V2/v2_prd.md"],
      ["V2.8 Final RC Report", "../research-notebook/docs/design/V2.8/v2_8_final_prd_expanded_rc_report.md"],
      ["V2 Target Architecture", "../research-notebook/docs/design/V2/v2_target_architecture.md"]
    ],
    visuals: [
      ["拟真概念图", "assets/generated-prd-visuals/research-notebook.png", "PRD-grounded source workbench concept", "基于 V2 PRD 主路径生成的拟真工作台图，非真实截图。"],
      ["真实截图", "assets/project-evidence/research-notebook/live-workbench.png", "Local frontend first screen", "本地 Vite 前端首屏截图；只证明界面可打开，不代表完整工作流。"],
      ["PRD概念图", "04-research-notebook-source-grounded-workbench/deep-images/deep-01-experience.png", "Source-grounded workbench", "基于 V2 PRD 主路径生成的体验图。"],
      ["PRD概念图", "04-research-notebook-source-grounded-workbench/deep-images/deep-02-capability-map.png", "Evidence capability map", "基于 citation / refusal / Studio / Research 口径生成。"],
      ["PRD概念图", "04-research-notebook-source-grounded-workbench/deep-images/deep-03-future-scenario.png", "Bounded research future", "基于后续 provider gate 生成，非截图。"]
    ],
    accent: "#059669"
  },
  {
    slug: "05-meeting-voice-assistant-session-knowledge",
    name: "Meeting Voice Assistant / Session Knowledge",
    short: "Meeting Voice",
    label: "会议与会话知识",
    stage: "limited",
    status: "Meeting capability retained; Data Service session GraphRAG direction",
    type: "语音转写与会话知识",
    summary: "从实时会议转写助手演进为会议/面试双场景和 Data Service 会话知识消费端。",
    why: "会议助手不再把知识双引擎塞进自身，而是把 transcript 作为 session material 交给独立 Data Service 处理 GraphRAG、LLMWiki、source trace 和质量治理。",
    audience: ["会议记录用户", "团队知识沉淀用户", "面试/访谈/支持场景用户"],
    done: [
      "V1.x 已有实时语音转文本、文件批量识别、LLM 会议分析、说话人分离、章节时间戳等成熟或基础能力。",
      "架构 overview 明确 ASR adapter：DashScope / FunASR / Mock。",
      "外部知识服务边界明确：会议应用通过 Data Service MCP 创建 session、ingest turns、build graph/community。"
    ],
    planned: [
      "V2 Now：JWT 认证、多用户数据模型、会议/面试会话模型。",
      "V2 Next：面试进度管理、模拟面试、实时答案提示、面试复盘、学习计划。",
      "V2 Later：团队协作、会议分享、评论标注、移动端 PWA。"
    ],
    goals: [
      "让会议内容从一次性 transcript 变成可检索、可关联、可复用的团队知识。",
      "把会议、面试、访谈、支持工单统一到 session-oriented knowledge 模型。",
      "把 ASR、语义解析、知识图谱、摘要和质量治理拆到清晰边界。"
    ],
    applications: [
      "企业会议助手：实时转写、会后纪要、行动项和跨会议知识沉淀。",
      "个人面试助手：面试前模拟、面试中提示、面试后复盘。",
      "会话分析平台：销售发现、客服复盘、事故复盘等时间序列记录。"
    ],
    journey: ["录音或上传音频", "WebSocket/文件 ASR 转写", "speaker/topic/chapter 语义解析", "创建 Data Service session", "ingest turns", "build graph/community", "查看会话图谱与发言摘要"],
    boundary: [
      "当前最好宣讲为会议应用 + Data Service 会话消费方向。",
      "不要把 V2 面试助手、认证、协作、移动端和跨会议知识增强讲成当前已完成平台能力。"
    ],
    sources: [
      ["Architecture Overview", "../meeting-voice-assistant/docs/architecture/overview.md"],
      ["V2 Product Roadmap", "../meeting-voice-assistant/docs/history/roadmap/2026-04-16-v2.0-product-roadmap.md"],
      ["Architecture Diagram", "../meeting-voice-assistant/docs/architecture.png"]
    ],
    visuals: [
      ["拟真概念图", "assets/generated-prd-visuals/meeting.png", "PRD-grounded session knowledge concept", "基于会议 roadmap 与 Data Service session 边界生成，非真实截图。"],
      ["架构图", "assets/project-evidence/meeting/architecture.png", "Meeting architecture overview", "本地 docs 架构图。"],
      ["PRD概念图", "05-meeting-voice-assistant-session-knowledge/deep-images/deep-01-experience.png", "Session knowledge experience", "基于 roadmap 与 architecture overview 生成。"],
      ["PRD概念图", "05-meeting-voice-assistant-session-knowledge/deep-images/deep-02-capability-map.png", "ASR to Data Service flow", "基于 session GraphRAG 边界生成。"],
      ["PRD概念图", "05-meeting-voice-assistant-session-knowledge/deep-images/deep-03-future-scenario.png", "Interview assistant future", "基于 V2 roadmap 生成，非当前完成截图。"]
    ],
    accent: "#0ea5e9"
  },
  {
    slug: "06-foodMap-local-food-journal-map",
    name: "FoodMap / Local Food Journal Map",
    short: "FoodMap",
    label: "本地美食手账地图",
    stage: "accepted",
    status: "V1.0 accepted; V1.2 recommendation layer implemented, 2026-06-04",
    type: "本地优先地图工具",
    summary: "一张带照片、评分、回忆和扫街榜推荐层的本地私人美食地图。",
    why: "FoodMap 不是大众点评式社区，也不是商家榜单；它是地图优先、暖色纸感、本地优先、低干扰的个人记录工具。",
    audience: ["美食记录用户", "旅行规划用户", "朋友分享用户", "本地收藏用户"],
    done: [
      "V1.0 支持个人工作台、本地持久化、地图点位、图层管理、搜索筛选、照片、分享快照、导入导出。",
      "V1.2 增加独立高德扫街榜推荐层、武汉推荐数据、推荐 marker、推荐面板和收藏为个人记录。",
      "推荐点与个人 FoodPlace 分层，保存后才进入用户正常数据模型。"
    ],
    planned: [
      "接入 AMap Open Platform key path，提高 POI 坐标精度。",
      "如果公共页面稳定，扩展更完整的扫街榜采集管线和推荐图例。",
      "账号、同步、协作、公网分享应作为 V2 后端范围另起。"
    ],
    goals: [
      "让吃过、想去、推荐、避雷地点从聊天收藏和地图收藏夹中独立出来。",
      "保持地图第一、本地隐私和导入导出可控。",
      "区分推荐候选与我的个人记录，避免数据混淆。"
    ],
    applications: [
      "个人旅行美食手账：城市旅行前后整理想去、已去、推荐和避雷地点。",
      "朋友分享：用只读快照和 .foodmap.json 传递本地地图包。",
      "轻量 POI 资料整理：不需要后端但需要地图管理的个人工具。"
    ],
    journey: ["打开 #/map", "搜索或地图点击新增", "填写评分/图层/笔记/照片", "按城市/标签/评分筛选", "加载扫街榜", "收藏推荐为个人记录", "生成只读快照或导入导出"],
    boundary: [
      "V1.0/V1.2 不做账号、后端同步、多人协作、服务端照片存储、公网永久分享或公开榜单。",
      "扫街榜当前数据不伪造 APP-only 条目，近似坐标需要收藏后手动校准。"
    ],
    sources: [
      ["V1.0 PRD", "../foodMap/docs/active/product-requirements-document.md"],
      ["V1.2 Implementation Report", "../foodMap/docs/active/v1.2-implementation-report.md"],
      ["Target Architecture", "../foodMap/docs/active/target-architecture.md"]
    ],
    visuals: [
      ["拟真概念图", "assets/generated-prd-visuals/foodmap.png", "PRD-grounded local food map concept", "基于 FoodMap V1.0/V1.2 PRD 生成的拟真地图图，非真实截图。"],
      ["真实截图", "assets/project-evidence/foodmap/live-map.png", "Local FoodMap #/map screenshot", "本地 Vite 真实地图工作台截图，作为参考证据。"],
      ["PRD概念图", "06-foodMap-local-food-journal-map/deep-images/deep-01-experience.png", "Travel journal map", "基于 PRD 旅行手账风生成。"],
      ["PRD概念图", "06-foodMap-local-food-journal-map/deep-images/deep-02-capability-map.png", "Local-first data flow", "基于 local-first / import-export / recommendation layer 生成。"],
      ["PRD概念图", "06-foodMap-local-food-journal-map/deep-images/deep-03-future-scenario.png", "Trip planning future", "基于后续 AMap key path 和推荐图层生成。"]
    ],
    accent: "#c76a32"
  },
  {
    slug: "07-navia-page-companion-agent",
    name: "Navia / Page Companion Agent",
    short: "Navia",
    label: "网页伴读 Agent",
    stage: "limited",
    status: "V1.1 frontend fidelity ready; V1.2 AI reading modular architecture line",
    type: "Chrome 页面内伴随式 AI",
    summary: "常驻网页边缘的本地伴随式 AI 助手，把当前页面上下文转成摘要、问答和导图工作流。",
    why: "Navia 解决复制粘贴式 Chatbot 无法理解当前页面的问题；它把网页内 Companion UI 和可复用、可观测、可监督的 Headless Runtime 分开。",
    audience: ["网页阅读者", "资料整理用户", "Chrome 插件用户", "后续模块化开发团队"],
    done: [
      "V1.1 出门评审允许声明 frontend fidelity ready。",
      "真实 Chrome MV3 unpacked extension 的 in-page E2E 和 visual E2E 通过，截图覆盖 floating、hover、440px push、50vw push、overlay、mobile、runtime offline。",
      "V1.2 文档冻结 A Page Perception、B Renderer、C Mindmap、D CoreProvider/Adapter、E Integration 的模块边界。"
    ],
    planned: [
      "按 V1.2 A/B/C/D/E 模块 mock-first、fixture-first 开发，再接真实 Chrome E2E。",
      "真实 piAgentProvider 需先锁定仓库、版本、license、runtime 与工具调用模型。",
      "长期记忆、RAG、多 Agent、浏览器自动操作、OCR/视频/直播理解留到后续版本。"
    ],
    goals: [
      "让用户不用复制粘贴，就能围绕当前网页总结、追问和生成 mindmap source artifact。",
      "让 UI 只是壳，Runtime 才是可复用、可观测、可监督的核心。",
      "用 Adapter Layer 控制 MCP / Skill / API 接入，避免前端绕过治理。"
    ],
    applications: [
      "网页伴读：技术文档、文章、报告和产品页面的即时摘要与追问。",
      "个人知识入口：后续可沉淀到本地知识库，但当前不做长期记忆。",
      "多端伴随式 AI 底座：Chrome 插件先行，未来扩展 Web/App/桌面形态。"
    ],
    journey: ["打开网页", "悬浮球 hover/点击", "展开 440px push 面板", "读取 PageContext", "通过 Runtime stream 生成回答", "展示 artifact/source map", "收起恢复页面"],
    boundary: [
      "V1.1 可讲 frontend fidelity ready；V1.2 是模块架构与开发线。",
      "不能声明真实 piAgentProvider ready、RAG ready、多 Agent ready、浏览器自动操作 ready、通用深度研究 ready 或 Mindmap visual high-fidelity complete。"
    ],
    sources: [
      ["V1 PRD", "../navia/docs/navia_v1_project_docs/01-prd.md"],
      ["V1.1 Exit Review", "../navia/docs/navia_v1_project_docs/stage-gates/v1.1-e-exit-review.md"],
      ["V1.2 Modular Architecture", "../navia/docs/navia_v1_project_docs/design/v1.2-ai-reading-modular-architecture.md"]
    ],
    visuals: [
      ["拟真概念图", "assets/generated-prd-visuals/navia.png", "PRD-grounded page companion concept", "基于 Navia V1/V1.2 PRD 生成的拟真页面伴读图，非真实截图。"],
      ["真实截图", "assets/project-evidence/navia/floating-default.png", "Floating default", "真实 E2E 截图。"],
      ["真实截图", "assets/project-evidence/navia/panel-440-push.png", "440px push panel", "真实 E2E 截图，展示页面内聊天面板。"],
      ["真实截图", "assets/project-evidence/navia/mobile-overlay.png", "Mobile overlay", "真实 E2E 移动视口截图。"],
      ["PRD概念图", "07-navia-page-companion-agent/deep-images/deep-03-future-scenario.png", "Companion future", "基于 V1.2 后续路线生成，非当前能力截图。"]
    ],
    accent: "#38bdf8"
  }
];

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function stage(project) {
  return stages[project.stage] ?? stages.planning;
}

function visualPath(project, visual, fromDetail = false) {
  const file = visual[1];
  const resolved = path.join(root, file);
  const fallback = `${project.slug}/images/01-experience.svg`;
  const chosen = existsSync(resolved) ? file : fallback;
  return `${fromDetail ? "../" : "./"}${chosen}`;
}

function sourceHref(sourcePath, fromDetail = false) {
  return `${fromDetail ? "../" : ""}${sourcePath}`;
}

function list(items) {
  return `<ul>${items.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>`;
}

function visualCard(project, visual, fromDetail = false) {
  const [kind, file, title, note] = visual;
  const evidence = kind === "真实截图" || kind === "真实证据" || kind === "验收报告" || kind === "架构图";
  return `<article class="visual-card ${evidence ? "evidence" : "concept"}">
    <div class="visual-frame"><img src="${visualPath(project, visual, fromDetail)}" alt="${esc(title)}"></div>
    <div class="visual-copy">
      <span class="asset-kind">${esc(kind)}</span>
      <strong>${esc(title)}</strong>
      <p>${esc(note)}</p>
    </div>
  </article>`;
}

function sourceLinks(project, fromDetail = false) {
  return project.sources
    .map(([label, href]) => `<a href="${sourceHref(href, fromDetail)}">${esc(label)}</a>`)
    .join("");
}

const css = `
:root{--bg:#eef2f6;--paper:#fff;--ink:#152033;--muted:#667085;--line:#d7dee9;--soft:#f6f8fb;--dark:#121a29;--shadow:0 18px 46px rgba(17,24,39,.09);--radius:10px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.56}a{color:inherit;text-decoration:none}img{display:block;max-width:100%;cursor:zoom-in}.layout{display:grid;grid-template-columns:286px minmax(0,1fr);min-height:100vh}.side{position:sticky;top:0;height:100vh;padding:26px 20px;background:#111827;color:#fff}.brand{font-size:19px;font-weight:900;letter-spacing:0}.brand span{display:block;margin-top:6px;color:#cbd5e1;font-size:12px;font-weight:600}.nav{display:grid;gap:7px;margin-top:28px}.nav a{padding:9px 10px;border-radius:8px;color:#d1d5db;font-size:14px}.nav a:hover{background:rgba(255,255,255,.08);color:#fff}.side-note{margin-top:28px;padding:14px;border:1px solid rgba(255,255,255,.14);border-radius:8px;background:rgba(255,255,255,.05);color:#d1d5db;font-size:13px}.main{padding:30px}.portal-hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(360px,.95fr);gap:20px;align-items:stretch}.hero-copy{min-height:520px;padding:40px;border-radius:14px;background:#0f172a;color:#fff;box-shadow:0 22px 65px rgba(15,23,42,.24);display:flex;flex-direction:column;justify-content:space-between}.kicker{display:inline-flex;width:max-content;border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:5px 10px;color:#dbeafe;background:rgba(255,255,255,.08);font-size:13px;font-weight:800}.hero-copy h1{font-size:48px;line-height:1.08;margin:22px 0 12px;letter-spacing:0}.hero-copy p{margin:0;color:#dbe4f0;font-size:18px;max-width:780px}.hero-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}.hero-actions a{border-radius:8px;padding:10px 14px;background:#fff;color:#111827;font-weight:900}.hero-actions a.secondary{background:rgba(255,255,255,.08);color:#fff;border:1px solid rgba(255,255,255,.2)}.hero-metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:28px}.metric{border:1px solid rgba(255,255,255,.14);border-radius:8px;padding:12px;background:rgba(255,255,255,.07)}.metric b{display:block;font-size:25px}.metric span{font-size:12px;color:#cbd5e1}.mosaic{display:grid;grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(2,1fr);gap:12px}.mosaic figure{margin:0;position:relative;overflow:hidden;border-radius:12px;background:#f8fafc;box-shadow:var(--shadow);border:1px solid var(--line)}.mosaic img{width:100%;height:100%;object-fit:contain;background:#f8fafc}.mosaic figcaption{position:absolute;left:12px;right:12px;bottom:12px;padding:8px 10px;border-radius:8px;background:rgba(15,23,42,.76);color:#fff;font-size:12px;font-weight:800;backdrop-filter:blur(10px)}.section{margin-top:32px}.section-head{display:flex;justify-content:space-between;align-items:end;gap:16px;margin-bottom:14px}.section h2{font-size:24px;margin:0}.section-head p{margin:5px 0 0;color:var(--muted)}.filters{display:flex;gap:8px;flex-wrap:wrap}.filters button{border:1px solid var(--line);border-radius:999px;background:#fff;padding:7px 11px;color:#334155;font-weight:800;cursor:pointer}.filters button.active{background:#111827;color:#fff;border-color:#111827}.project-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.project-card{display:grid;grid-template-columns:220px minmax(0,1fr);gap:0;overflow:hidden;border:1px solid var(--line);border-radius:12px;background:#fff;box-shadow:var(--shadow)}.project-card .thumb{height:100%;min-height:250px;background:#f8fafc;border-right:1px solid var(--line)}.project-card .thumb img{width:100%;height:100%;object-fit:contain;background:#f8fafc}.project-body{padding:18px}.tag{display:inline-flex;align-items:center;border-radius:999px;padding:4px 9px;color:#fff;font-size:12px;font-weight:900}.tag.accepted{background:#0f9f6e}.tag.limited{background:#b7791f}.tag.planning{background:#2563eb}.project-card h3{margin:10px 0 7px;font-size:20px}.project-card p{margin:0;color:var(--muted)}.mini-meta{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.mini-meta span{border:1px solid var(--line);border-radius:999px;background:#f8fafc;padding:4px 8px;color:#475467;font-size:12px;font-weight:800}.link-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.link-row a,.source-row a{border:1px solid var(--line);border-radius:8px;background:#f8fafc;padding:7px 10px;font-weight:800;font-size:13px}.evidence-wall{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.evidence-tile{overflow:hidden;border-radius:10px;background:#fff;border:1px solid var(--line);box-shadow:var(--shadow)}.evidence-tile img{width:100%;aspect-ratio:16/10;object-fit:contain;background:#f8fafc}.evidence-tile div{padding:12px}.evidence-tile strong{display:block}.evidence-tile span{display:block;color:var(--muted);font-size:12px;margin-top:3px}.timeline{display:grid;gap:10px}.event{display:grid;grid-template-columns:125px 1fr;gap:16px;border:1px solid var(--line);border-radius:10px;background:#fff;padding:15px;box-shadow:var(--shadow)}.event time{font-weight:900;color:#2563eb}.event p{margin:4px 0 0;color:var(--muted)}.detail-hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(420px,.9fr);gap:18px}.detail-intro{padding:30px;border-radius:14px;background:#fff;border:1px solid var(--line);box-shadow:var(--shadow)}.detail-intro h1{font-size:42px;line-height:1.08;margin:12px 0}.detail-intro p{color:var(--muted);font-size:17px}.hero-shot{border-radius:14px;overflow:hidden;background:#f8fafc;box-shadow:var(--shadow);border:1px solid var(--line);min-height:360px;display:grid;place-items:center}.hero-shot img{width:100%;height:100%;object-fit:contain;background:#f8fafc}.detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.panel{border:1px solid var(--line);border-radius:12px;background:#fff;padding:20px;box-shadow:var(--shadow)}.panel h2{margin:0 0 10px;font-size:20px}.panel p{color:var(--muted)}.panel ul{margin:0;padding-left:20px}.panel li{margin:8px 0}.wide{grid-column:1/-1}.journey{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px;counter-reset:step}.step{position:relative;padding:14px 10px;border:1px solid var(--line);border-radius:10px;background:#fff;box-shadow:var(--shadow);min-height:96px}.step:before{counter-increment:step;content:counter(step);display:inline-grid;place-items:center;width:24px;height:24px;border-radius:999px;background:var(--accent);color:#fff;font-weight:900;font-size:12px;margin-bottom:8px}.step span{display:block;font-weight:800;font-size:13px}.visual-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.visual-card{overflow:hidden;border:1px solid var(--line);border-radius:12px;background:#fff;box-shadow:var(--shadow)}.visual-frame{background:#f8fafc}.visual-card img{width:100%;aspect-ratio:16/9;object-fit:contain;background:#f8fafc}.visual-copy{padding:14px}.asset-kind{display:inline-flex;margin-bottom:7px;border-radius:999px;padding:3px 8px;font-size:12px;font-weight:900;color:#fff;background:#64748b}.visual-card.evidence .asset-kind{background:#0f9f6e}.visual-card.concept .asset-kind{background:#7c3aed}.visual-copy strong{display:block}.visual-copy p{margin:5px 0 0;color:var(--muted);font-size:13px}.source-row{display:flex;gap:8px;flex-wrap:wrap}.boundary{border-left:5px solid var(--accent)}.footer{margin:34px 0 0;color:var(--muted);font-size:13px}.empty{display:none!important}.image-viewer{position:fixed;inset:0;z-index:1000;background:rgba(8,13,24,.94);display:none;overflow:hidden}.image-viewer.open{display:block}.viewer-stage{position:absolute;inset:0;cursor:grab;touch-action:none}.viewer-stage.dragging{cursor:grabbing}.viewer-stage img{position:absolute;left:50%;top:50%;max-width:none;max-height:none;transform-origin:center center;user-select:none;cursor:grab;box-shadow:0 26px 90px rgba(0,0,0,.46);background:#f8fafc}.viewer-toolbar{position:absolute;z-index:2;top:18px;left:50%;transform:translateX(-50%);display:flex;gap:8px;padding:8px;border:1px solid rgba(255,255,255,.18);border-radius:12px;background:rgba(15,23,42,.72);backdrop-filter:blur(14px)}.viewer-toolbar button{min-width:42px;height:36px;border:1px solid rgba(255,255,255,.18);border-radius:8px;background:rgba(255,255,255,.1);color:#fff;font-size:15px;font-weight:900;cursor:pointer}.viewer-caption{position:absolute;left:18px;right:18px;bottom:18px;z-index:2;color:#e5e7eb;font-size:13px;text-align:center;text-shadow:0 1px 8px rgba(0,0,0,.8);pointer-events:none}
@media(max-width:1180px){.layout{grid-template-columns:1fr}.side{position:static;height:auto}.portal-hero,.detail-hero,.project-grid,.detail-grid,.visual-grid{grid-template-columns:1fr}.project-card{grid-template-columns:1fr}.hero-metrics,.evidence-wall{grid-template-columns:repeat(2,1fr)}.journey{grid-template-columns:repeat(3,1fr)}}
@media(max-width:720px){.main{padding:20px}.hero-copy{min-height:auto;padding:28px}.hero-copy h1{font-size:34px}.mosaic{grid-template-columns:1fr}.hero-metrics,.evidence-wall,.journey{grid-template-columns:1fr}.event{grid-template-columns:1fr}.detail-intro h1{font-size:32px}}
`;

function overview() {
  const cards = projects.map((project) => {
    const firstVisual = project.visuals[0];
    return `<article class="project-card" data-stage="${project.stage}">
      <div class="thumb"><img src="${visualPath(project, firstVisual)}" alt="${esc(project.name)}"></div>
      <div class="project-body">
        <span class="tag ${stage(project).tone}">${stage(project).label}</span>
        <h3>${esc(project.name)}</h3>
        <p>${esc(project.summary)}</p>
        <div class="mini-meta"><span>${esc(project.type)}</span><span>${esc(project.status)}</span></div>
        <div class="link-row"><a href="./${project.slug}/深度介绍.html">进入详情</a><a href="./${project.slug}/项目介绍.md">旧版介绍</a><a href="${sourceHref(project.sources[0][1])}">最新来源</a></div>
      </div>
    </article>`;
  }).join("");

  const evidenceTiles = projects.flatMap((project) => project.visuals.slice(0, 1).map((visual) => ({ project, visual }))).map(({ project, visual }) => `
    <article class="evidence-tile">
      <img src="${visualPath(project, visual)}" alt="${esc(visual[2])}">
      <div><strong>${esc(project.short)}</strong><span>${esc(visual[0])} · ${esc(visual[2])}</span></div>
    </article>`).join("");

  const mosaic = [
    [projects[5], projects[5].visuals[0]],
    [projects[6], projects[6].visuals[0]],
    [projects[2], projects[2].visuals[0]],
    [projects[0], projects[0].visuals[0]]
  ].map(([project, visual]) => `<figure><img src="${visualPath(project, visual)}" alt="${esc(visual[2])}"><figcaption>${esc(project.short)} · ${esc(visual[0])}</figcaption></figure>`).join("");

  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>项目群入口 · 阶段展示</title><style>${css}</style></head><body><div class="layout"><aside class="side"><div class="brand">项目群入口<span>阶段展示 / 证据化宣讲资料</span></div><nav class="nav"><a href="#overview">入口总览</a><a href="#projects">项目入口</a><a href="#evidence">拟真主图</a><a href="#timeline">进展日志</a><a href="./项目宣讲资料总览.md">资料总览</a><a href="./组图预览.html">旧版组图</a></nav><div class="side-note">主图优先使用 PRD 依据的拟真概念图，以减少事实截图误导；真实截图保留在详情页作为证据或参考。</div></aside><main class="main"><header id="overview" class="portal-hero"><section class="hero-copy"><div><span class="kicker">Docs-grounded project portal</span><h1>面向宣讲的项目群入口</h1><p>基于本地最新 docs、PRD 和验收报告重整 7 个项目：每个项目都有状态口径、可完成功能、规划路线、开发目标、应用前景和 PRD 拟真主图。</p><div class="hero-actions"><a href="#projects">浏览项目入口</a><a class="secondary" href="#evidence">查看拟真主图</a></div></div><div class="hero-metrics"><div class="metric"><b>7</b><span>项目详情页</span></div><div class="metric"><b>拟真</b><span>主图优先</span></div><div class="metric"><b>PRD</b><span>配图依据</span></div><div class="metric"><b>边界</b><span>禁止声明</span></div></div></section><section class="mosaic">${mosaic}</section></header><section id="projects" class="section"><div class="section-head"><div><h2>项目入口</h2><p>按当前状态筛选，每张卡片进入该项目的详细宣讲页。</p></div><div class="filters"><button class="active" data-filter="all">全部</button><button data-filter="accepted">已验收</button><button data-filter="limited">受限完成</button><button data-filter="planning">规划/门禁</button></div></div><div class="project-grid">${cards}</div></section><section id="evidence" class="section"><div class="section-head"><div><h2>PRD 拟真主图</h2><p>这些图片用于宣讲视觉呈现，均为 PRD-grounded realistic concept，不作为真实截图证据。</p></div></div><div class="evidence-wall">${evidenceTiles}</div></section><section id="timeline" class="section"><div class="section-head"><div><h2>进展日志</h2><p>本页后续继续记录资料、截图和配图更新。</p></div></div><div class="timeline"><article class="event"><time>2026-06-05</time><div><strong>升级为项目群入口</strong><p>重写总入口与 7 个详情页，加入 PRD 来源、真实截图参考和禁止声明边界。</p></div></article><article class="event"><time>2026-06-05</time><div><strong>补充本地界面截图</strong><p>使用 Playwright 抓取 FoodMap 和 ResearchNotebook 本地前端首屏，放入详情页作为参考。</p></div></article><article class="event"><time>2026-06-05</time><div><strong>切换为拟真主图优先</strong><p>生成 7 张 PRD-grounded realistic concept PNG，替代容易误导的事实截图作为主视觉。</p></div></article></div></section><footer class="footer">生成时间：${generatedAt}。项目状态以本地 docs 和验收报告为准；拟真概念图只用于解释应用前景。</footer></main></div><script>const buttons=[...document.querySelectorAll("[data-filter]")];const cards=[...document.querySelectorAll("[data-stage]")];buttons.forEach((button)=>button.addEventListener("click",()=>{buttons.forEach((b)=>b.classList.remove("active"));button.classList.add("active");const filter=button.dataset.filter;cards.forEach((card)=>card.classList.toggle("empty",filter!=="all"&&card.dataset.stage!==filter));}));</script>${viewerScript}</body></html>`;
}

function detail(project) {
  const heroVisual = project.visuals[0];
  const steps = project.journey.map((step) => `<div class="step"><span>${esc(step)}</span></div>`).join("");
  const visuals = project.visuals.map((visual) => visualCard(project, visual, true)).join("");
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(project.name)} · 项目详情</title><style>${css}:root{--accent:${project.accent}}</style></head><body><div class="layout"><aside class="side"><div class="brand">${esc(project.label)}<span>${esc(project.status)}</span></div><nav class="nav"><a href="../进展展示.html">返回入口</a><a href="#position">项目定位</a><a href="#capability">功能与规划</a><a href="#journey">交互路径</a><a href="#visuals">图片组</a><a href="#sources">PRD 来源</a><a href="./项目介绍.md">旧版介绍</a></nav><div class="side-note">本页用于对外宣讲。真实截图和 PRD 概念图已分开标注；概念图不能作为验收证据。</div></aside><main class="main"><section id="position" class="detail-hero"><article class="detail-intro"><span class="tag ${stage(project).tone}">${stage(project).label}</span><h1>${esc(project.name)}</h1><p>${esc(project.summary)}</p><p>${esc(project.why)}</p><div class="mini-meta">${project.audience.map((item) => `<span>${esc(item)}</span>`).join("")}</div></article><div class="hero-shot"><img src="${visualPath(project, heroVisual, true)}" alt="${esc(heroVisual[2])}"></div></section><section id="capability" class="section"><div class="detail-grid"><article class="panel"><h2>当前可完成功能</h2>${list(project.done)}</article><article class="panel"><h2>规划项目</h2>${list(project.planned)}</article><article class="panel"><h2>开发目标</h2>${list(project.goals)}</article><article class="panel"><h2>应用前景</h2>${list(project.applications)}</article><article class="panel wide boundary"><h2>宣讲边界</h2>${list(project.boundary)}</article></div></section><section id="journey" class="section"><div class="section-head"><div><h2>用户交互路径</h2><p>用于转成 PPT 时可直接拆成流程页。</p></div></div><div class="journey">${steps}</div></section><section id="visuals" class="section"><div class="section-head"><div><h2>图片组</h2><p>真实证据优先；PRD 概念图用于补充体验、架构和后续发展表达。</p></div></div><div class="visual-grid">${visuals}</div></section><section id="sources" class="section"><article class="panel"><h2>PRD / Docs 来源</h2><p>下列来源决定本页口径。若项目文档与截图不一致，以最新 PRD、验收报告和边界说明为准。</p><div class="source-row">${sourceLinks(project, true)}</div></article></section><footer class="footer">生成时间：${generatedAt}。本详情页不扩大项目完成声明。</footer></main></div>${viewerScript}</body></html>`;
}

function promptFile(project) {
  return `# GPT Image 2 PRD-grounded prompts: ${project.name}

Use these only for PRD concept images. Do not present generated images as real product screenshots.

## Project basis

- Current status: ${project.status}
- Product summary: ${project.summary}
- Key PRD boundary: ${project.boundary.join(" ")}

## Experience concept

Wide 16:9 product presentation image based strictly on the PRD for ${project.name}. Show the user-facing experience described here: ${project.journey.join(" -> ")}. Make it polished and rich, but avoid inventing features outside the listed PRD scope. No brand logos, no readable claims, no fake metrics.

## Capability / architecture concept

Wide 16:9 technical visual based strictly on the PRD/docs for ${project.name}. Visualize these capabilities: ${project.done.concat(project.planned).slice(0, 7).join("; ")}. Use abstract panels, evidence paths, source labels, and system boundaries. Do not imply forbidden capabilities.

## Future application concept

Wide 16:9 future scenario image based on the project's stated roadmap only: ${project.applications.join("; ")}. Clearly feel like a conceptual roadmap image, not an actual screenshot. No fake customer logos, no invented integrations, no readable product claims.
`;
}

const viewerScript = `<script>
(() => {
  const images = [...document.querySelectorAll("img")].filter((img) => !img.closest(".image-viewer"));
  if (!images.length) return;
  const viewer = document.createElement("div");
  viewer.className = "image-viewer";
  viewer.innerHTML = '<div class="viewer-stage"><img alt=""></div><div class="viewer-toolbar"><button data-action="out">-</button><button data-action="in">+</button><button data-action="reset">1:1</button><button data-action="close">×</button></div><div class="viewer-caption"></div>';
  document.body.appendChild(viewer);
  const stage = viewer.querySelector(".viewer-stage");
  const image = stage.querySelector("img");
  const caption = viewer.querySelector(".viewer-caption");
  let scale = 1;
  let x = 0;
  let y = 0;
  let startX = 0;
  let startY = 0;
  let baseX = 0;
  let baseY = 0;
  let dragging = false;

  function apply() {
    image.style.transform = "translate(calc(-50% + " + x + "px), calc(-50% + " + y + "px)) scale(" + scale + ")";
  }

  function fit() {
    const naturalW = image.naturalWidth || 1600;
    const naturalH = image.naturalHeight || 900;
    const fitScale = Math.min((window.innerWidth * 0.9) / naturalW, (window.innerHeight * 0.82) / naturalH, 1);
    image.style.width = naturalW + "px";
    image.style.height = naturalH + "px";
    scale = Math.max(0.12, fitScale);
    x = 0;
    y = 0;
    apply();
  }

  function open(img) {
    image.src = img.currentSrc || img.src;
    image.alt = img.alt || "";
    caption.textContent = img.alt || "图片预览";
    viewer.classList.add("open");
    document.body.style.overflow = "hidden";
    if (image.complete) fit();
    else image.onload = fit;
  }

  function close() {
    viewer.classList.remove("open");
    document.body.style.overflow = "";
    image.removeAttribute("src");
  }

  images.forEach((img) => img.addEventListener("click", () => open(img)));
  viewer.addEventListener("click", (event) => {
    const action = event.target.dataset.action;
    if (!action) return;
    event.stopPropagation();
    if (action === "close") close();
    if (action === "in") {
      scale = Math.min(8, scale * 1.22);
      apply();
    }
    if (action === "out") {
      scale = Math.max(0.08, scale / 1.22);
      apply();
    }
    if (action === "reset") fit();
  });
  viewer.addEventListener("click", (event) => {
    if (event.target === viewer) close();
  });
  stage.addEventListener("wheel", (event) => {
    if (!viewer.classList.contains("open")) return;
    event.preventDefault();
    const next = event.deltaY < 0 ? scale * 1.12 : scale / 1.12;
    scale = Math.min(8, Math.max(0.08, next));
    apply();
  }, { passive: false });
  stage.addEventListener("pointerdown", (event) => {
    if (!viewer.classList.contains("open")) return;
    dragging = true;
    startX = event.clientX;
    startY = event.clientY;
    baseX = x;
    baseY = y;
    stage.classList.add("dragging");
    stage.setPointerCapture(event.pointerId);
  });
  stage.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    x = baseX + event.clientX - startX;
    y = baseY + event.clientY - startY;
    apply();
  });
  stage.addEventListener("pointerup", (event) => {
    dragging = false;
    stage.classList.remove("dragging");
    stage.releasePointerCapture(event.pointerId);
  });
  stage.addEventListener("dblclick", fit);
  window.addEventListener("keydown", (event) => {
    if (!viewer.classList.contains("open")) return;
    if (event.key === "Escape") close();
    if (event.key === "+" || event.key === "=") {
      scale = Math.min(8, scale * 1.22);
      apply();
    }
    if (event.key === "-") {
      scale = Math.max(0.08, scale / 1.22);
      apply();
    }
    if (event.key === "0") fit();
  });
  window.addEventListener("resize", () => {
    if (viewer.classList.contains("open")) fit();
  });
})();
</script>`;

function markdownIndex() {
  return `# 项目宣讲资料总览

本目录已升级为项目群展示入口，面向后续对外宣讲和 PPT 拆分。

## 入口网页

- [进展展示.html](./进展展示.html)：项目群入口，含状态筛选、PRD 拟真主图和详情页入口。
- [组图预览.html](./组图预览.html)：旧版 SVG 组图预览。

## 项目详情

${projects.map((project) => `- [${project.name}](./${project.slug}/深度介绍.html)：${project.status}`).join("\n")}

## 口径规则

- 真实截图、验收报告、架构图可以作为证据图。
- PRD 概念图只用于解释体验、架构和未来场景，不能作为真实产品截图。
- 所有项目必须讲清楚已完成范围、规划范围和禁止声明。
`;
}

await mkdir(path.join(root, "garden-gpt-image-2", "prompt"), { recursive: true });

await writeFile(path.join(root, "进展展示.html"), overview(), "utf8");
await writeFile(path.join(root, "项目宣讲资料总览.md"), markdownIndex(), "utf8");

for (const project of projects) {
  await mkdir(path.join(root, project.slug), { recursive: true });
  await writeFile(path.join(root, project.slug, "深度介绍.html"), detail(project), "utf8");
  await writeFile(path.join(root, "garden-gpt-image-2", "prompt", `${project.slug}-prd-grounded-visuals-${generatedAt.replaceAll("-", "")}.md`), promptFile(project), "utf8");
}

console.log(`Generated project portal for ${projects.length} projects`);
