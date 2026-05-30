# ResearchNotebook V1.5-D Source-grounded QA Quality Plan

日期：2026-05-27

## 阶段目标

验证真实 AI 问答符合 PRD 的可信研究机制：

- 默认只基于当前 Notebook sources 回答。
- 每个关键断言带 citation。
- 资料不足时拒答。
- 推断 / 解释必须标注。

## Entry Gate

- V1.5-A provider PASS。
- 数字人资料已导入。
- DocumentUnit / EvidenceSpan 可定位。

## 验收问题

覆盖型问题：

1. 数字人产业链包括哪些环节？
2. 数字人企业应用有哪些典型场景？
3. 当前数字人技术趋势是什么？
4. 资料中提到的风险和政策问题有哪些？

资料外问题：

1. 资料是否覆盖某个未出现公司？
2. 资料是否覆盖无关行业结论？

推断型问题：

1. 基于资料，数字人未来商业化可能面临什么挑战？

## 验收标准

- 覆盖型问题回答必须带 citation。
- 资料外问题必须拒答。
- 推断型问题必须标注“基于来源的推断”。
- citation 可定位。
- answer failure 不清空 Guide / Studio。
- `npm run check` PASS。

## PRD 规格检视

该阶段对应 PRD “可信研究”和“未覆盖知识处理”。

## 风险评估

- 规格漂移风险：MEDIUM。
- 虚假验收风险：HIGH，若 AI 回答无 citation 或硬答资料外问题。

