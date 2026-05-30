# ResearchNotebook V1.6-B Manual Quality Review Template

日期：2026-05-28

用途：V1.6-B 自动评估只能产出候选结果。最终 PASS 必须由人工按本模板审查。

## 数据集评分表

| 数据集 | Guide 可用性 1-5 | 资料相关性 1-5 | 覆盖完整性 1-5 | citation 正确率 | citation 可定位率 | 拒答正确率 | 中文表达 1-5 | 高危幻觉数 | 结论 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 数字人 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 |
| Claude Code 技术分享 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 |
| AI 视频工作流 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 | 待评 |

## PASS 阈值

- Guide 可用性 >= 4/5。
- 资料相关性 >= 4/5。
- 覆盖完整性 >= 4/5。
- citation 正确率 >= 80%。
- citation 可定位率 >= 90%。
- 拒答正确率 >= 80%。
- 中文表达 >= 4/5。
- 高危幻觉数 = 0。

## 人工审查说明

自动评估已经检查：

- Guide / QA / Studio schema。
- evidence_refs 是否存在。
- citation route 是否可解析。
- provider fallback 是否被误用。
- raw path 是否泄漏。

人工必须补充检查：

- citation 片段是否真的支持输出结论。
- 输出是否遗漏资料中的关键主题。
- 资料外问题是否真的应该拒答。
- 是否存在资料中没有的公司、政策、数字、结论。
- 中文表达是否适合真实用户使用。

## 最终声明规则

人工评分未完成前，只能声明：

V1.6-B automatic quality evaluation candidates are ready for manual review.

不能声明：

- V1.6-B PASS。
- multi-dataset quality ready。
- all-domain ready。
- all-source-type ready。
