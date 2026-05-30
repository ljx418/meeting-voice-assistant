# ResearchNotebook V1.4 Release Acceptance Checklist

日期：2026-05-26

状态值：

- PASS
- PASS_LIMITED
- NOT_READY
- BLOCKED

## PRD Phase 1 验收

| 验收项 | 状态 | 说明 |
| --- | --- | --- |
| 三列布局 | PASS_LIMITED | Sources / Chat / Studio 骨架已落地；Guide 已接入，Studio 真实输出仍未接入。 |
| Notebook 生命周期 | PASS_LIMITED | 创建、列表、重命名、归档、最近打开可用；物理删除和跨设备最近打开不声明 ready。 |
| P0 Sources | PASS_LIMITED | Markdown/TXT/可抽取文本 PDF 已用数字人资料包通过浏览器式上传和后端 smoke；扫描版 PDF/OCR 不声明 ready。 |
| Notebook Guide | PASS_LIMITED | `/guide` 返回 Overview / Key Topics / Suggested Questions；Suggested Question 可直接进入带证据问答。当前是确定性导读，不声明完整 AI Guide 质量 ready。 |
| Source-grounded Chat | PASS_LIMITED | workspace query 已支持引用问答、资料不足拒答、补源建议和轻量推断提示；不声明完整 Research / session query ready。 |
| 资料不足补源入口 | PASS_LIMITED | 拒答状态提供“添加来源”入口并聚焦来源导入表单；不声明联网搜索或 Research ready。 |
| Studio Notes | PASS_LIMITED | 可生成带 evidence_refs 的确定性 Notes；不声明高质量 AI 写作 ready。 |
| Study Guide | PASS_LIMITED | 可生成带 evidence_refs 的确定性 Study Guide；不声明高质量 AI 写作 ready。 |
| Briefing Doc | PASS_LIMITED | 可生成带 evidence_refs 的确定性 Briefing Doc；不声明高质量 AI 写作 ready。 |
| FAQ | PASS_LIMITED | 可生成带 evidence_refs 的确定性 FAQ；不声明高质量 AI 写作 ready。 |
| Citation jump | PASS_LIMITED | Chat / Studio citation 在 text/markdown/json/可抽取文本 PDF 受限路径可用；PDF 原版页面渲染、OCR 和 all-source-type precise backjump 不声明 ready。 |
| V1.4-RC 自动化集中验收 | PASS_LIMITED | 后端 focused tests、前端 focused tests、npm run check、sources P0 smoke 均通过。 |
| 人工体验验收 | NOT_READY | 未在本轮执行 ChromeCLI / 人工完整体验验收，建议 V1.5-A 执行。 |
| AI 输出质量验收 | NOT_READY | 当前 Guide / Studio 是确定性输出，不声明 Claude / LLM 高质量 ready。 |

## V1.3 后移验收

| 验收项 | 状态 | 说明 |
| --- | --- | --- |
| Agent folder summary browser path | DEFERRED_TO_V1_4_RC | 不再单独提前验收。 |
| Summary quality review | DEFERRED_TO_V1_4_RC | 与 PRD Studio 输出一起验收。 |
| Edge case manual tests | DEFERRED_TO_V1_4_RC | 空目录、大文件、权限失败等统一验收。 |
