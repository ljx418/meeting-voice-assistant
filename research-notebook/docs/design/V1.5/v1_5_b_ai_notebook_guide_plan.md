# ResearchNotebook V1.5-B AI Notebook Guide Plan

日期：2026-05-27

## 阶段目标

用真实 AI 基于当前 Notebook sources 生成 Notebook Guide：

- Overview
- Key Topics
- Suggested Questions
- evidence_refs

## Entry Gate

- V1.5-A provider health probe PASS。
- 真实模型调用 smoke PASS。
- 数字人真实数据可导入。
- V1.4 deterministic Guide 仍可作为 fallback，但不可声明 AI quality。

## 计划实现

- 扩展或新增 Guide generation route。
- 使用 DocumentUnit / EvidenceSpan 作为输入上下文。
- 让 AI 输出结构化 JSON。
- 后端校验 AI 输出 schema。
- 后端补齐 evidence_refs 映射。
- 前端展示 AI Guide 状态：
  - generating
  - ready
  - provider unavailable
  - insufficient evidence
  - deterministic fallback

## 验收标准

- 使用 `Desktop/技术分享/11-数字人` 导入 Markdown 和 PDF。
- Guide 内容不是固定模板。
- Overview 能概括数字人资料。
- Key Topics 至少 3 个。
- Suggested Questions 至少 3 个。
- Guide 至少 1 条 evidence_ref。
- evidence_ref 可定位来源片段。
- provider 失败时不伪装为 AI Guide ready。
- `npm run check` PASS。

## PRD 规格检视

该阶段对应 PRD 的 Guide-first 中间区域交互。必须保证“自动生成 Notebook Guide”不是模板占位。

## 风险评估

- 规格漂移风险：MEDIUM，原因是 AI Guide 质量标准需要人工判断。
- 虚假验收风险：HIGH，若没有 V1.5-A provider smoke 或没有真实数据。

## 审计意见

等待 V1.5-A PASS 后才能进入实质开发。

