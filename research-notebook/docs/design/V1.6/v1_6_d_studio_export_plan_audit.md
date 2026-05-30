# ResearchNotebook V1.6-D Studio Export / Download Plan Audit

日期：2026-05-28

## 审计结论

Go。

V1.6-D 可以进入实质开发。该阶段只实现 Studio 轻量输出导出，不新增 Phase 2/3 输出能力。

## 审计意见

| 编号 | 意见 | 风险 | 处理 |
| --- | --- | --- | --- |
| D1 | 导出必须保留 citation metadata。 | MEDIUM | JSON 和 Markdown 均必须包含 evidence refs。 |
| D2 | 导出文件不能泄漏本地路径。 | MEDIUM | 使用 safe slug，数据来自 normalized artifact。 |
| D3 | 不能把导出写成 PPT/Audio ready。 | LOW | 阶段限定 Studio 轻量输出。 |

## 风险评估

开发计划漂移风险：LOW。

虚假验收风险：LOW。

是否存在 HIGH 风险：NO。
