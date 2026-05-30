# ResearchNotebook V1.5 Development Plan

日期：2026-05-26

## 总目标

把 V1.4 的 PASS_LIMITED 主路径推进为真实 AI 质量可验收路径。

V1.5 不追求新增 Phase 2/3 功能，只做 PRD Phase 1 的质量闭环。

## 子阶段

### V1.5-0 Plan / Audit Gate

目标：

- 建立 V1.5 规格门禁。
- 明确真实数据。
- 明确端到端验收。
- 审计下一阶段是否允许进入实质开发。

验收：

- V1.5 文档存在。
- 明确 HIGH 风险退出规则。
- 明确当前是否具备真实 LLM 开发条件。

### V1.5-A AI Provider Contract Enablement

目标：

- 冻结真实 LLM provider 合同。
- 明确模型、认证、超时、错误、成本、脱敏和日志规则。
- 后端提供 Notebook Guide / Studio generation 的 AI provider adapter。

准入：

- 必须存在可用 LLM provider 配置。
- 必须能在本地 smoke 中真实调用模型。
- 必须明确禁止把 deterministic fallback 当成 AI quality pass。

验收：

- provider health probe PASS。
- model metadata 可记录。
- 认证失败有稳定错误。
- 超时有稳定错误。
- 不把 API key 写入日志、fixtures、docs。
- 不调用外部互联网搜索来回答 Notebook 内问题。

### V1.5-B AI Notebook Guide Quality

目标：

- 使用真实 LLM 生成 Overview / Key Topics / Suggested Questions。
- 输出必须带 evidence_refs。
- 无 evidence 时不能伪造 Guide。

验收：

- 导入数字人 Markdown / PDF 后生成 Guide。
- Guide 内容不是模板化占位。
- 每个关键主题至少有 evidence_refs。
- Suggested Questions 与资料内容相关。
- 点击 Suggested Questions 进入引用问答。

### V1.5-C AI Studio Lightweight Outputs

目标：

- 使用真实 LLM 生成 Notes / Study Guide / Briefing Doc / FAQ。
- 输出必须带 evidence_refs。

验收：

- 四类输出均能生成。
- 每类输出至少包含一个 citation。
- FAQ 每条答案必须带引用或明确未覆盖。
- Study Guide 包含结构化大纲和建议追问。
- Briefing Doc 面向复述 / 汇报。

### V1.5-D Source-grounded QA Quality

目标：

- 真实 AI 问答遵守 source-grounded 策略。
- 资料不足时拒答并补源。
- 区分来源结论和推断 / 解释。

验收：

- 数字人资料覆盖问题：回答带 citation。
- 数字人资料未覆盖问题：拒答。
- 推断性问题：明确标注“基于来源的推断”。
- citation 点击可定位。

### V1.5-E ChromeCLI / Manual E2E Acceptance

目标：

- 像普通用户一样完整操作一次。
- 使用真实数据，不用 mock。

验收：

- 创建 Notebook。
- 上传数字人 Markdown / PDF。
- 等待解析。
- 查看 AI Guide。
- 点击建议问题。
- 执行引用问答。
- 生成 Studio 输出。
- 点击 citation 定位。
- 触发资料不足拒答。
- 点击添加来源。

### V1.5-RC Quality Release Handoff

目标：

- 汇总质量验收。
- 更新 PRD coverage matrix。
- 明确 PASS / PASS_LIMITED / NOT_READY。

验收：

- `npm run check` PASS。
- 后端 AI focused tests PASS。
- ChromeCLI E2E PASS。
- 人工审查报告 PASS 或明确 BLOCKED。

## 阶段推进规则

每个阶段结束后必须记录：

- 完成内容。
- 端到端验收结果。
- PRD 规格检视。
- 规格漂移风险。
- 虚假验收风险。
- 下一阶段审计意见。

如果规格漂移或虚假验收风险为 HIGH，停止自动推进。

