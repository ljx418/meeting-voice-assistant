# V1.3 PRD 对齐改造计划

日期：2026-05-26

## 依据和限制

本计划基于 Stitch 可读取的项目元数据、screen 列表、design theme，以及本地 `v1_3_prd_coverage_analysis.md`。PRD Markdown 原文当前只能读取到文件元数据，下载超时，因此本计划不是 PRD 原文逐条审计。

如果后续拿到 PRD 原文，必须先执行二次审计，再调整本计划。

## 改造目标

把当前偏工程化的 ResearchNotebook 体验改造成更接近 `Productivity Intelligence` 风格的中文 AI 研究工作台：

- 页面优先服务用户任务，而不是展示版本阶段。
- Agent 入口以“文件夹总结工作流”为核心，让用户从目标输入、草案确认、运行状态到总结证据回跳形成闭环。
- 来源预览、文档单元和证据高亮保持现有合同，不扩大 ready 声明。
- 保持 md/txt、本地授权、已注册工作流模板等边界。

## 执行阶段

| 阶段 | 目标 | 状态 |
| --- | --- | --- |
| PRD-A | 建立 PRD 对齐计划和门禁 | PASS |
| PRD-B | 清理用户可见开发态文案 | PASS |
| PRD-C | 对齐低噪音研究工作台视觉和信息架构 | PASS_LIMITED |
| PRD-D | 强化 Agent 文件夹总结工作流体验 | PASS_LIMITED |
| PRD-E | 强化 summary citation、来源预览和证据阅读体验 | PASS_LIMITED |
| PRD-F | 记录 PRD 对齐验收和剩余风险 | PASS_LIMITED |

## 保持不变的边界

- 不声明任意 Agent 工具调用 ready。
- 不声明 PDF/PPTX/DOCX/video/audio/image 原生正文摄入 ready。
- 不声明 all-source-type precise backjump ready。
- 不声明 Assessment、Governance、Graph editing、Cloud collaboration ready。
- 不把 `relative_path_only` 证据伪装成可精确定位证据。

## 风险评估

| 风险 | 等级 | 收敛措施 |
| --- | --- | --- |
| PRD 原文不可读导致规格遗漏 | HIGH_KNOWN_LIMITATION | 文档明确基于快照；拿到原文后必须二次审计。 |
| Agent 入口被误读为自由 Agent | MEDIUM | UI 使用“文件夹总结工作流”和“受限可用”，不写自由 Agent ready。 |
| Summary citation 被误读为全格式 ready | MEDIUM | UI 区分“可打开原文定位”和“仅显示文件路径”。 |
| 视觉对齐不足 | MEDIUM | 本轮只做产品层级和低噪音布局，像素级 parity 另开设计审计。 |

