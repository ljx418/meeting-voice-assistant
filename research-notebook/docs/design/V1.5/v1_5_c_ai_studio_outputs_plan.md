# ResearchNotebook V1.5-C AI Studio Outputs Plan

日期：2026-05-27

## 阶段目标

用真实 AI 生成 PRD Phase 1 Studio 轻量输出：

- Notes
- Study Guide
- Briefing Doc
- FAQ

## Entry Gate

- V1.5-A provider PASS。
- V1.5-B 至少完成 Guide evidence context 验证。
- 当前 Notebook 至少存在可引用 evidence_refs。

## 计划实现

- 扩展 `/studio/artifacts`，支持 AI generation mode。
- 每类输出要求结构化 JSON。
- 每类输出保留 evidence_refs。
- 无 evidence 时拒绝生成。
- provider 失败只显示局部错误。
- 前端继续复用 Studio 面板。

## 验收标准

- Notes 可生成并带引用。
- Study Guide 有结构化大纲、重点、建议追问。
- Briefing Doc 适合复述 / 汇报。
- FAQ 每条答案带引用或明确未覆盖。
- Studio citation 可定位 source / unit / span。
- 无证据时不生成无来源输出。
- `npm run check` PASS。

## PRD 规格检视

该阶段对应 PRD Studio 轻量输出。不得把 Audio / PPT / 思维导图 / 文档对比纳入 V1.5。

## 风险评估

- 规格漂移风险：MEDIUM。
- 虚假验收风险：HIGH，若输出仍为模板或无 citation。

## 审计意见

等待 V1.5-A 和 V1.5-B 至少完成证据上下文后进入。

