# ResearchNotebook V1.5 PRD Quality Gate

日期：2026-05-26

## PRD 基线

V1.5 继续围绕用户提供的《AI Notebook 产品 PRD v0.2》执行。PRD Phase 1 MVP 主任务是：

```text
导入资料 -> 自动生成 Notebook Guide -> 基于来源的引用问答 -> Studio 轻量输出
```

V1.4 已完成受限合同和 UI 主路径，但 Guide / Studio 仍是确定性输出。因此 V1.5 的核心目标不是扩大功能范围，而是验证真实 AI 输出质量。

## V1.5 必须满足的 PRD 规格

1. 默认只基于当前 Notebook sources 回答。
2. Notebook Guide 必须包含 Overview / Key Topics / Suggested Questions。
3. AI 回答的关键断言必须带引用。
4. 资料不足时必须明确拒答并引导补源。
5. Studio Notes / Study Guide / Briefing Doc / FAQ 必须带引用。
6. 引用必须能跳转到来源片段。
7. 必须区分来源明确支持的结论和推断 / 解释。
8. MVP P0 来源仍限定为 PDF / TXT / Markdown。

## V1.5 不允许声明

- 不声明通用互联网问答 ready。
- 不声明无来源百科式回答 ready。
- 不声明扫描版 PDF / OCR ready。
- 不声明 Word / PPT / 音视频 / YouTube ready。
- 不声明 Audio Overview / PPT / 思维导图 / 文档对比 ready。
- 不声明跨 Notebook 全局知识库 ready。
- 不声明云同步 / 协作 / 权限 ready。
- 不声明 Agent 自由执行任意工具 ready。

## 真实验收数据

P0 验收目录：

```text
Desktop/技术分享/11-数字人
```

可用文件：

- `AI数字人产业发展报告_2026-05-26.pdf`
- `AI数字人资料包/README.md`
- `AI数字人资料包/01_industry_overview.md`
- `AI数字人资料包/02_technology_trends.md`
- `AI数字人资料包/03_business_applications.md`
- `AI数字人资料包/04_company_products.md`
- `AI数字人资料包/05_policy_and_risks.md`
- `AI数字人资料包/06_future_trends.md`
- `AI数字人资料包/sources_index.md`

## 虚假验收禁止项

以下情况必须判定为虚假验收风险 HIGH：

1. 用确定性模板冒充真实 AI 输出。
2. 无 LLM provider / API key / model contract，却声明 AI quality ready。
3. 没有真实数据导入，只用 mock fixture 声明通过。
4. AI 输出没有 citation，却声明 source-grounded。
5. citation 不能定位到 source/unit/span，却声明引用跳转通过。
6. 对资料不足问题硬答，却声明拒答策略通过。

