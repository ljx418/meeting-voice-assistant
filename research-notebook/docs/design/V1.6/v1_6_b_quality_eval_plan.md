# ResearchNotebook V1.6-B Multi-dataset Quality Evaluation Plan

日期：2026-05-28

## 阶段目标

V1.6-B 用至少 3 个真实主题数据集评估 Guide、QA、Studio、拒答和 citation 质量。该阶段不是新增产品功能，而是把 V1.5 的数字人单数据集质量 smoke 扩展为多主题质量评估。

## 推荐真实数据集

| 数据集 | 路径 | 主要来源类型 | 目的 |
| --- | --- | --- | --- |
| 数字人 | `Desktop/技术分享/11-数字人` | Markdown + PDF | 延续 V1.5 P0 数据集，验证数字人资料。 |
| Claude Code 技术分享 | `Desktop/技术分享/02-claudecode技术分享` | Markdown | 验证开发工具类资料。 |
| AI 视频工作流 | `Desktop/技术分享/08-AITextToVideoWorkflow` | Markdown | 验证工作流 / 创作类资料。 |

## 必须验收

每个数据集都必须完成：

- 创建 workspace。
- 导入至少 1 个真实 source。
- build 完成。
- 生成 Guide。
- 执行至少 2 个覆盖型 QA。
- 执行至少 1 个资料外拒答 QA。
- 生成至少 1 类 Studio 输出。
- 验证 citation 可定位 source / unit / EvidenceSpan。
- 保存候选输出 fixtures。

## 质量评分维度

每个数据集必须有评分表：

| 维度 | PASS 标准 |
| --- | --- |
| 资料相关性 | 输出明显来自当前资料，不是泛泛常识。 |
| 覆盖完整性 | Guide 覆盖资料核心主题，QA 回答覆盖问题重点。 |
| citation 正确性 | citation 指向的片段能支持对应结论。 |
| 拒答正确性 | 资料外问题明确拒答并引导补源。 |
| 中文表达 | 可读、准确、适合 Notebook 首屏或 Studio 输出。 |
| 幻觉风险 | 不出现资料中没有的硬结论、公司、政策或数据。 |

建议阈值：

- Guide 可用性 >= 4/5。
- QA citation 正确率 >= 80%。
- 拒答正确率 >= 80%。
- citation 可定位率 >= 90%。
- 高危幻觉 = 0。

## 自动化和人工边界

自动化 smoke 可以证明：

- API 路径可走。
- AI 输出 schema 成立。
- evidence_refs 存在。
- citation route 可解析。
- 拒答字段或文本存在。

自动化 smoke 不能单独证明：

- citation 内容真的支持结论。
- 输出没有细微幻觉。
- 中文表达质量足够。
- 多主题质量达到 PRD 可验收水平。

因此 V1.6-B 若缺少人工质量评分，只能输出 `CANDIDATE_READY_FOR_MANUAL_REVIEW`，不得声明 PASS。

## 风险评估

开发计划漂移风险：MEDIUM。

原因：多数据集评估可能被误写成全行业 ready。

虚假验收风险：HIGH，除非人工质量评分完成。

原因：自动化只能验证结构和 citation 可解析，不能验证语义质量。

## Go / No-Go

当前只允许实现评估 harness、fixtures 和评分表模板。

不得声明 V1.6-B PASS，除非人工质量评分完成且达到阈值。
