import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const outRoot = process.cwd();

const projects = [
  {
    slug: "01-codexPat-agent-desktop-pet",
    name: "codexPat / Agent Desktop Pet",
    shortName: "codexPat",
    tagline: "把本地 Agent 工作状态转成可见、可互动、可审计的桌面工作猫。",
    status: "V10.11 product experience rebaseline passed-scoped, 2026-06-05",
    audience: ["本地开发者", "Codex/Agent 工作流用户", "需要低干扰状态反馈的人"],
    experience: [
      "桌面 work-cat-v1 通过 idle / thinking / running / success / warning / error / need_input / sleeping 表达状态。",
      "Manager/Settings 可预览动作、恢复默认 pack，并通过真实桌面截图留证。",
      "V10 明确 2D-first，不把 provider、3D、签名发布或跨平台能力提前宣称为 ready。"
    ],
    journey: ["启动桌面应用", "进入设置与 work-cat 引导", "本地事件进入状态机", "播放对应动画与微交互", "预览或恢复默认素材", "查看截图与验收证据"],
    future: [
      "继续打磨三分钟本地上手路径和 settings/onboarding 文案。",
      "扩展 2D action pack 与视觉 QA，但保持 renderer 安全边界。",
      "3D、photo-to-3D、provider、marketplace、release signing 必须等待真实证据门禁。"
    ],
    reminders: [
      "可宣讲已通过的范围：tested local bundled work-cat-v1 的产品级 2D 动画体验。",
      "不要把 V8/V9 provider 或 3D 实验包装成 V10 已交付能力。"
    ],
    sources: [
      "../codexPat/docs/V10.x/v10_11-product-experience-rebaseline.md",
      "../codexPat/docs/V10.x/v10_x-target-architecture.md",
      "../codexPat/docs/V10.x/v10_x-product-grade-final-acceptance-report.md",
      "../codexPat/docs/active/agent_desktop_pet_prd_v8.md"
    ],
    theme: ["#1F2937", "#F59E0B", "#10B981", "#F8FAFC", "#E5E7EB"]
  },
  {
    slug: "02-data-service-architecture-intelligence",
    name: "data_service / Architecture Intelligence",
    shortName: "data_service",
    tagline: "面向知识库、代码资产与外部 Agent 的证据化架构审查服务层。",
    status: "V2.9 documentation-only planning; V2.8 accepted with caveats",
    audience: ["Tech Lead", "架构审查者", "外部 Coding Agent", "文档/审计 Agent"],
    experience: [
      "把大型项目的代码与文档转为 public surface evidence、关系路径、ranking、human review report 和 context pack。",
      "通过 HTTP / MCP / CLI 暴露同一批架构资产，便于人和 Agent 同时消费。",
      "明确区分 deterministic evidence、heuristic needs_review、ranking priority 与 acceptance status。"
    ],
    journey: ["选择 workspace/codebase", "构建 public surface evidence", "生成 shallow relationships", "校准 ranking/review queue", "渲染 human review report", "输出 context pack 给 Agent"],
    future: [
      "推进 V2.9 Phase 63-68：line-level evidence、relationship v2、ranking calibration、人类可读报告、context pack v3。",
      "完成 data_service 与 HarnessOS 双 real-repo E2E、HTTP/MCP/CLI parity、redaction 与 false-green scan。",
      "把架构审查从文档规划推进到可运行的证据硬化实现。"
    ],
    reminders: [
      "V2.9 当前是文档开发规划线，业务代码实现需要从 Phase 63 pre-implementation audit 后开始。",
      "宣讲时可把 V2.8 当作已验收基线，把 V2.9 当作下一阶段证据硬化目标。"
    ],
    sources: [
      "../data_service/docs/active/README.md",
      "../data_service/docs/V2.x/V2_9_TARGET_PRD.md",
      "../data_service/docs/V2.x/V2_9_TARGET_ARCHITECTURE.md",
      "../data_service/docs/V2.x/V2_9_PHASE_68_CLOSURE_PACKAGE.md"
    ],
    theme: ["#0F172A", "#2563EB", "#14B8A6", "#F8FAFC", "#CBD5E1"]
  },
  {
    slug: "03-harnessOS-controlled-agent-workflow",
    name: "harnessOS / Controlled Agent Workflow OS",
    shortName: "harnessOS",
    tagline: "让 Agent 在可审计、可回滚、可人工接管的边界内执行和协作。",
    status: "V9 planning baseline after V8 station-agent workflow pilot",
    audience: ["工作流编排者", "AI 工程团队", "需要证据链和高风险门禁的团队"],
    experience: [
      "用户目标进入 Mission TUI / Workflow Studio，系统生成工作流、Agent 分工、diff 和执行计划。",
      "高风险动作通过 approval、policy、capability、rollback、kill switch 和 evidence chain 受控执行。",
      "Studio 展示 workflow graph、station inspector、Agent profile、产物、diff、rerun 和 review console。"
    ],
    journey: ["输入目标", "生成 workflow 与 Agent 分工", "形成执行计划", "人工确认高风险动作", "受控 executor 执行", "多 Agent 协作与测试审查", "Studio 查看产物与证据"],
    future: [
      "V9-1/2：Agent executor safety gate 与 controlled executor runtime。",
      "V9-3/4/5：多 Agent 编排、自主编码试点、受限 terminal worker。",
      "V9-6/7/8：Workflow Studio 产品化、生产治理门禁、最终验收。"
    ],
    reminders: [
      "V9 不能宣称 production ready、unrestricted executor 或 terminal automation ready。",
      "可以讲清楚它是在 V7/V8 已验收试点上设计高风险执行基线。"
    ],
    sources: [
      "../harnessOS/docs/design/V9.x/00_README.md",
      "../harnessOS/docs/design/V9.x/v9_target_prd.md",
      "../harnessOS/docs/design/V9.x/v9_target_architecture.md",
      "../harnessOS/docs/design/V9.x/v9_milestone_roadmap.md"
    ],
    theme: ["#111827", "#7C3AED", "#F97316", "#F9FAFB", "#D1D5DB"]
  },
  {
    slug: "04-research-notebook-source-grounded-workbench",
    name: "ResearchNotebook / Source-grounded Workbench",
    shortName: "ResearchNotebook",
    tagline: "把多来源资料变成可信引用问答、Studio 输出和补源研究报告的笔记工作台。",
    status: "V2.x PRD expanded RC ready with limitations, 2026-06-02",
    audience: ["知识工作者", "研究者", "需要带来源证据输出的人"],
    experience: [
      "三列 Notebook 体验：Sources、Chat、Studio，围绕导入、导读、问答和输出组织。",
      "回答、Studio artifact 和 Research report 都必须绑定 evidence_refs，资料不足时拒答并建议补源。",
      "OCR、Audio、PPT、Mindmap、Document comparison 默认保持 provider/decision gate，不能伪装成已 ready。"
    ],
    journey: ["创建 Notebook", "批量导入 PDF/TXT/Markdown 与 approved URL", "生成 Notebook Guide", "点击 Suggested Question 问答", "citation 跳转证据片段", "生成 Notes/Study Guide/FAQ", "补源后输出 Research report"],
    future: [
      "继续提升 P0/P1 sources 稳定性、URL 安全抽取和多数据集 AI 质量人工验收。",
      "为 OCR、Audio、PPT、Mindmap、Compare 分别建立 provider、schema、preview、export、manual review 门禁。",
      "后续可开 V3 或 V2.x 子计划推进高风险后置能力。"
    ],
    reminders: [
      "根 README 与最新 V2.x 文档口径存在版本差异，宣讲时以 V2.8/V2.x 最新扩展 RC 报告为准。",
      "重点说明 ready with limitations，避免声明 all-source-type、full AI quality 或 cloud collaboration。"
    ],
    sources: [
      "../research-notebook/docs/design/V2/v2_prd.md",
      "../research-notebook/docs/design/V2/v2_target_architecture.md",
      "../research-notebook/docs/design/V2.8/v2_8_final_prd_expanded_rc_report.md",
      "../research-notebook/docs/design/V2.8/v2_8_final_prd_expanded_rc_plan.md"
    ],
    theme: ["#1F2937", "#059669", "#D97706", "#FFFBEB", "#D6D3D1"]
  },
  {
    slug: "05-meeting-voice-assistant-session-knowledge",
    name: "Meeting Voice Assistant / Session Knowledge",
    shortName: "Meeting Voice",
    tagline: "从实时会议转写走向会话型知识图谱与 Data Service 消费端。",
    status: "Meeting capability retained; Data Service session GraphRAG integration is current direction",
    audience: ["会议记录用户", "团队知识沉淀用户", "未来面试/访谈/支持场景用户"],
    experience: [
      "前端采集音频，后端通过 ASR adapter 支持 DashScope、FunASR 和 mock，输出转写与语义结构。",
      "会议应用不再内置知识双引擎，而是通过 Data Service MCP 处理知识固化、GraphRAG、LLMWiki、source trace。",
      "会议 transcript 归一成 workspace/session/source/actor/unit/relation 的通用会话知识模型。"
    ],
    journey: ["录音或上传音频", "WebSocket/文件 ASR 转写", "语义解析 speaker/topic/chapter", "创建 Data Service session", "ingest turns", "build graph/community", "前端展示会话图谱与发言摘要"],
    future: [
      "V2 roadmap：JWT 认证、多用户数据模型、会议/面试双场景。",
      "面试助手：进度管理、模拟面试、实时答案提示、复盘与学习计划。",
      "增强跨会议知识关联、GraphRAG 检索、团队协作与移动端。"
    ],
    reminders: [
      "docs/README 指向的部分 Data Service 文件在该仓库中可能缺失，宣讲时应以架构 overview、roadmap 与 session GraphRAG requirements 交叉说明。",
      "当前最好讲成“会议应用作为 Data Service 的首个会话型消费场景”。"
    ],
    sources: [
      "../meeting-voice-assistant/docs/README.md",
      "../meeting-voice-assistant/docs/architecture/overview.md",
      "../meeting-voice-assistant/docs/history/roadmap/2026-04-16-v2.0-product-roadmap.md",
      "../meeting-voice-assistant/docs/data_service/2026-05-08-session-graphrag-mcp-development-requirements.md"
    ],
    theme: ["#0F172A", "#0EA5E9", "#A855F7", "#F8FAFC", "#CBD5E1"]
  },
  {
    slug: "06-foodMap-local-food-journal-map",
    name: "FoodMap / Local Food Journal Map",
    shortName: "FoodMap",
    tagline: "一张带照片、评分和回忆的本地私人美食地图。",
    status: "V1.0 accepted; V1.2 recommendation layer implemented, 2026-06-04",
    audience: ["美食记录用户", "旅行规划用户", "朋友分享用户", "本地收藏用户"],
    experience: [
      "首屏就是地图，用户通过图钉、照片、评分、到访时间、标签和图层管理私人美食记忆。",
      "纯前端 local-first：IndexedDB、hash route、AMap key path 与 Leaflet fallback、.foodmap.json 导入导出。",
      "V1.2 增加高德扫街榜推荐层，推荐点保存后才成为个人 FoodPlace。"
    ],
    journey: ["打开 #/map", "搜索或地图点击新增地点", "填写评分/图层/笔记/照片", "按城市/标签/评分筛选", "切换图层或查看详情", "生成只读分享快照", "导出或导入 .foodmap.json"],
    future: [
      "用 AMap Open Platform key 获取更精确 POI 坐标。",
      "如果公共页面稳定，扩展更完整的扫街榜提取管线和推荐点图例。",
      "如需账号、同步、协作或公网分享，应作为 V2 另起后端范围。"
    ],
    reminders: [
      "active README 仍保留早期“无源码”表述，但最新实现/验收报告已证明 V1.0/V1.2 有完成项。",
      "V1.0 的核心不是社交榜单，而是本地优先、低干扰的私人地图手账。"
    ],
    sources: [
      "../foodMap/docs/active/product-requirements-document.md",
      "../foodMap/docs/active/target-architecture.md",
      "../foodMap/docs/active/final-acceptance-report.md",
      "../foodMap/docs/active/v1.2-implementation-report.md"
    ],
    theme: ["#3B2B1F", "#C76A32", "#6F7F47", "#FFF8EA", "#D8C5A5"]
  },
  {
    slug: "07-navia-page-companion-agent",
    name: "Navia / Page Companion Agent",
    shortName: "Navia",
    tagline: "常驻网页边缘的本地伴随式 AI 助手与 Headless AgentCore。",
    status: "V1.2 readiness/stage-gate line; mock-first development after audit and gates",
    audience: ["网页阅读者", "资料整理用户", "需要页面内摘要/追问/导图的人", "后续模块化开发团队"],
    experience: [
      "Chrome 页面内悬浮球作为入口，hover 小长条，点击展开双轨聊天面板，并支持挤压/覆盖/收起。",
      "当前网页上下文进入 Local Runtime，提供摘要、问答、Mermaid mindmap、session restore 和 trace。",
      "V1.2 将 ChatBox 拆成 A Page Perception、B Renderer、C Mindmap、D CoreProvider/Adapter、E Integration。"
    ],
    journey: ["安装插件并打开网页", "悬浮球 hover/点击展开", "抽取 PageContext/StructuredPageContext", "通过 /v1/chat/stream 发起 turn", "D 模块编排工具与治理", "B/C 渲染文本和 mindmap artifact", "Trace/SourceMap 回看证据"],
    future: [
      "按 V1.2-A/B/C/D/E 分模块 mock-first、fixture-first 开发和真实 Chrome E2E。",
      "真实 piAgentProvider 需先完成依赖锁定、license、runtime 与工具调用模型审计。",
      "长期记忆、RAG、多 Agent、浏览器自动操作、OCR/视频/直播理解留待后续版本。"
    ],
    reminders: [
      "V1.2 文档强调 Go for audit，不等同于真实 piAgentProvider ready。",
      "宣讲重点应是 Headless runtime + 页面内 Companion 体验，而不是把它讲成通用浏览器自动化 Agent。"
    ],
    sources: [
      "../navia/docs/navia_v1_project_docs/01-prd.md",
      "../navia/docs/navia_v1_project_docs/02-architecture.md",
      "../navia/docs/navia_v1_project_docs/design/v1.2-ai-reading-modular-architecture.md",
      "../navia/docs/navia_v1_project_docs/design/v1.2-readiness-closure-audit.md"
    ],
    theme: ["#172554", "#38BDF8", "#FACC15", "#F8FAFC", "#BFDBFE"]
  }
];

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function wrapText(text, maxChars) {
  const raw = String(text);
  const words = raw.includes(" ") ? raw.split(/\s+/) : Array.from(raw);
  const lines = [];
  let line = "";
  for (const word of words) {
    const sep = raw.includes(" ") && line ? " " : "";
    const next = line + sep + word;
    if ([...next].length > maxChars && line) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function textBlock(text, x, y, maxChars, lineHeight, options = {}) {
  const {
    size = 28,
    weight = 500,
    fill = "#111827",
    maxLines = 8,
    anchor = "start"
  } = options;
  const lines = wrapText(text, maxChars).slice(0, maxLines);
  return lines
    .map((line, i) => `<text x="${x}" y="${y + i * lineHeight}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}">${esc(line)}</text>`)
    .join("\n");
}

function listBlock(items, x, y, maxChars, lineHeight, options = {}) {
  return items
    .map((item, i) => textBlock(`• ${item}`, x, y + i * lineHeight * 2.1, maxChars, lineHeight, options))
    .join("\n");
}

function baseSvg(project, title, subtitle, body) {
  const [ink, accent, accent2, bg, line] = project.theme;
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-label="${esc(title)}">
  <rect width="1600" height="900" fill="${bg}"/>
  <rect x="48" y="44" width="1504" height="812" rx="28" fill="#FFFFFF" stroke="${line}" stroke-width="3"/>
  <rect x="48" y="44" width="1504" height="116" rx="28" fill="${ink}"/>
  <text x="92" y="104" font-size="40" font-weight="800" fill="#FFFFFF">${esc(title)}</text>
  <text x="92" y="140" font-size="22" font-weight="500" fill="#E5E7EB">${esc(subtitle)}</text>
  <circle cx="1478" cy="98" r="26" fill="${accent}"/>
  <circle cx="1414" cy="98" r="18" fill="${accent2}"/>
  ${body}
</svg>`;
}

function experienceSvg(project) {
  const [ink, accent, accent2, , line] = project.theme;
  const body = `
  <text x="92" y="216" font-size="34" font-weight="800" fill="${ink}">体验呈现</text>
  <text x="92" y="254" font-size="22" fill="#4B5563">${esc(project.tagline)}</text>

  <rect x="92" y="305" width="500" height="390" rx="22" fill="#F9FAFB" stroke="${line}" stroke-width="2"/>
  <rect x="126" y="340" width="432" height="210" rx="18" fill="${ink}" opacity="0.92"/>
  <rect x="154" y="370" width="150" height="26" rx="13" fill="${accent}"/>
  <rect x="154" y="414" width="350" height="16" rx="8" fill="#E5E7EB"/>
  <rect x="154" y="446" width="290" height="16" rx="8" fill="#E5E7EB"/>
  <circle cx="480" cy="472" r="44" fill="${accent2}"/>
  <rect x="126" y="585" width="180" height="44" rx="10" fill="${accent}"/>
  <rect x="326" y="585" width="132" height="44" rx="10" fill="#FFFFFF" stroke="${line}"/>
  <text x="126" y="665" font-size="24" font-weight="800" fill="${ink}">用户第一眼看到什么</text>
  ${textBlock(project.experience[0], 126, 700, 25, 28, { size: 21, fill: "#374151", maxLines: 3 })}

  <rect x="632" y="305" width="394" height="390" rx="22" fill="#FFFFFF" stroke="${line}" stroke-width="2"/>
  <text x="668" y="360" font-size="28" font-weight="800" fill="${ink}">核心价值</text>
  ${listBlock(project.experience.slice(0, 3), 668, 412, 25, 25, { size: 21, fill: "#374151", maxLines: 3 })}

  <rect x="1066" y="305" width="402" height="390" rx="22" fill="#FFFFFF" stroke="${line}" stroke-width="2"/>
  <text x="1102" y="360" font-size="28" font-weight="800" fill="${ink}">当前阶段</text>
  ${textBlock(project.status, 1102, 410, 24, 29, { size: 22, fill: "#374151", maxLines: 4 })}
  <text x="1102" y="560" font-size="24" font-weight="800" fill="${ink}">面向谁讲</text>
  ${listBlock(project.audience, 1102, 604, 22, 23, { size: 20, fill: "#374151", maxLines: 2 })}

  <rect x="92" y="742" width="1376" height="72" rx="16" fill="${accent}" opacity="0.12"/>
  <text x="126" y="788" font-size="25" font-weight="800" fill="${ink}">宣讲主句：</text>
  ${textBlock(project.tagline, 270, 788, 55, 28, { size: 24, fill: ink, maxLines: 1 })}
  `;
  return baseSvg(project, `${project.shortName} · 体验呈现`, project.status, body);
}

function journeySvg(project) {
  const [ink, accent, accent2, , line] = project.theme;
  const stepWidth = 205;
  const startX = 118;
  const y = 325;
  const steps = project.journey.slice(0, 7);
  const cards = steps.map((step, i) => {
    const x = startX + i * stepWidth;
    const arrow = i < steps.length - 1 ? `<path d="M${x + 158} ${y + 88} L${x + 190} ${y + 88}" stroke="${accent}" stroke-width="5" stroke-linecap="round"/><path d="M${x + 184} ${y + 78} L${x + 198} ${y + 88} L${x + 184} ${y + 98}" fill="none" stroke="${accent}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>` : "";
    return `
      <rect x="${x}" y="${y}" width="160" height="176" rx="18" fill="#FFFFFF" stroke="${line}" stroke-width="2"/>
      <circle cx="${x + 40}" cy="${y + 42}" r="24" fill="${i % 2 ? accent2 : accent}"/>
      <text x="${x + 40}" y="${y + 51}" font-size="24" font-weight="900" fill="#FFFFFF" text-anchor="middle">${i + 1}</text>
      ${textBlock(step, x + 20, y + 96, 8, 26, { size: 22, weight: 800, fill: ink, maxLines: 3 })}
      ${arrow}
    `;
  }).join("\n");
  const body = `
  <text x="92" y="216" font-size="34" font-weight="800" fill="${ink}">用户交互路径</text>
  <text x="92" y="254" font-size="22" fill="#4B5563">按 PPT 讲解时，可把这张图作为“用户怎么走完核心闭环”的主图。</text>
  ${cards}
  <rect x="112" y="602" width="1328" height="148" rx="22" fill="#F9FAFB" stroke="${line}" stroke-width="2"/>
  <text x="148" y="656" font-size="28" font-weight="800" fill="${ink}">路径讲解要点</text>
  ${listBlock(project.experience, 148, 704, 58, 25, { size: 21, fill: "#374151", maxLines: 2 })}
  `;
  return baseSvg(project, `${project.shortName} · 用户交互路径`, project.tagline, body);
}

function roadmapSvg(project) {
  const [ink, accent, accent2, , line] = project.theme;
  const columns = [
    ["当前可讲", [project.status, project.reminders[0] || "以最新验收文档为准。"]],
    ["下一阶段", project.future.slice(0, 2)],
    ["发展边界", [project.future[2] || project.reminders[1] || "新增能力需要独立门禁。", project.reminders[1] || "避免扩大声明范围。"]]
  ];
  const cards = columns.map((col, i) => {
    const x = 112 + i * 456;
    const color = i === 0 ? accent : i === 1 ? accent2 : ink;
    return `
      <rect x="${x}" y="306" width="400" height="386" rx="22" fill="#FFFFFF" stroke="${line}" stroke-width="2"/>
      <rect x="${x}" y="306" width="400" height="68" rx="22" fill="${color}"/>
      <text x="${x + 28}" y="350" font-size="27" font-weight="900" fill="#FFFFFF">${esc(col[0])}</text>
      ${listBlock(col[1], x + 30, 430, 28, 26, { size: 21, fill: "#374151", maxLines: 4 })}
    `;
  }).join("\n");
  const body = `
  <text x="92" y="216" font-size="34" font-weight="800" fill="${ink}">后续可能的发展</text>
  <text x="92" y="254" font-size="22" fill="#4B5563">这张图适合放在每个项目介绍的结尾：先讲现状，再讲下一步，最后讲不该过度承诺的边界。</text>
  ${cards}
  <rect x="112" y="744" width="1328" height="72" rx="16" fill="${accent}" opacity="0.12"/>
  <text x="148" y="789" font-size="24" font-weight="900" fill="${ink}">建议结尾：</text>
  ${textBlock(project.future[0], 282, 789, 53, 27, { size: 23, fill: ink, maxLines: 1 })}
  `;
  return baseSvg(project, `${project.shortName} · 发展路线`, project.status, body);
}

function docFor(project) {
  const slideOutline = [
    "项目一句话定位",
    "目标用户与核心场景",
    "当前体验呈现",
    "核心交互闭环",
    "技术/架构支撑",
    "当前验收状态与证据",
    "后续发展方向",
    "宣讲边界与 Q&A"
  ];
  return `# ${project.name} 宣讲介绍

## 一句话定位

${project.tagline}

## 当前状态

${project.status}

## 目标用户

${project.audience.map((item) => `- ${item}`).join("\n")}

## 核心体验

${project.experience.map((item) => `- ${item}`).join("\n")}

## 用户交互路径

${project.journey.map((item, i) => `${i + 1}. ${item}`).join("\n")}

## 后续可能发展

${project.future.map((item) => `- ${item}`).join("\n")}

## 宣讲提醒

${project.reminders.map((item) => `- ${item}`).join("\n")}

## PPT 页纲建议

${slideOutline.map((item, i) => `${i + 1}. ${item}`).join("\n")}

## 组图

- [01-experience.svg](./images/01-experience.svg)：体验呈现
- [02-user-journey.svg](./images/02-user-journey.svg)：用户交互路径
- [03-roadmap.svg](./images/03-roadmap.svg)：后续可能的发展

## 主要参考文档

${project.sources.map((item) => `- \`${item}\``).join("\n")}
`;
}

function rootIndex() {
  return `# 项目宣讲资料总览

本目录为多个开发项目生成了单独的宣讲资料包。每个项目目录都包含：

- \`项目介绍.md\`：中文宣讲介绍、PPT 页纲、版本提醒、参考文档。
- \`images/01-experience.svg\`：项目体验呈现。
- \`images/02-user-journey.svg\`：用户交互路径。
- \`images/03-roadmap.svg\`：后续可能的发展。

## 项目列表

${projects.map((p) => `- [${p.name}](./${p.slug}/项目介绍.md)`).join("\n")}

## 宣讲顺序建议

1. 先讲已验收、最容易被听众理解的产品体验：FoodMap、codexPat、ResearchNotebook。
2. 再讲平台/底座型项目：meeting-voice-assistant、data_service。
3. 最后讲高风险执行与未来空间：Navia、harnessOS。

## 口径提醒

- 对已验收项目，直接讲“已通过的受限范围”和用户闭环。
- 对规划线项目，讲“目标架构、门禁、下一步证据”，不要把规划当成交付。
- 多个项目都有明确 forbidden claims，PPT 中建议用“当前可讲 / 不能过度承诺 / 下一步”三段式收口。
`;
}

function galleryHtml() {
  const cards = projects.flatMap((p) => [
    [p, "01-experience.svg", "体验呈现"],
    [p, "02-user-journey.svg", "用户交互路径"],
    [p, "03-roadmap.svg", "后续发展"]
  ]);
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>项目宣讲组图预览</title>
  <style>
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f3f4f6; color: #111827; }
    header { padding: 28px 36px; background: #111827; color: white; }
    main { padding: 28px; display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 22px; }
    article { background: white; border: 1px solid #d1d5db; border-radius: 12px; padding: 14px; }
    h2 { font-size: 18px; margin: 0 0 12px; }
    img { width: 100%; height: auto; border: 1px solid #e5e7eb; border-radius: 8px; background: white; }
  </style>
</head>
<body>
  <header>
    <h1>项目宣讲组图预览</h1>
    <p>所有图片均为 SVG，可直接放入 PPT 或浏览器打开。</p>
  </header>
  <main>
    ${cards.map(([p, file, label]) => `<article><h2>${esc(p.shortName)} · ${esc(label)}</h2><img src="./${p.slug}/images/${file}" alt="${esc(p.shortName)} ${esc(label)}"></article>`).join("\n")}
  </main>
</body>
</html>`;
}

await writeFile(path.join(outRoot, "项目宣讲资料总览.md"), rootIndex(), "utf8");
await writeFile(path.join(outRoot, "组图预览.html"), galleryHtml(), "utf8");

for (const project of projects) {
  const dir = path.join(outRoot, project.slug);
  const imgDir = path.join(dir, "images");
  await mkdir(imgDir, { recursive: true });
  await writeFile(path.join(dir, "项目介绍.md"), docFor(project), "utf8");
  await writeFile(path.join(imgDir, "01-experience.svg"), experienceSvg(project), "utf8");
  await writeFile(path.join(imgDir, "02-user-journey.svg"), journeySvg(project), "utf8");
  await writeFile(path.join(imgDir, "03-roadmap.svg"), roadmapSvg(project), "utf8");
}

console.log(`Generated ${projects.length} project presentation packs in ${outRoot}`);
