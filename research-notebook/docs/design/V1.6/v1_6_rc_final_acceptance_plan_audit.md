# ResearchNotebook V1.6-RC Final Acceptance Plan Audit

日期：2026-05-28

## 审计结论

STOP FOR HUMAN ACCEPTANCE。

V1.6-RC 不是纯自动化开发阶段，必须由用户进行人工质量验收后才能继续声明 V1.6 完成。

## 审计意见

| 编号 | 意见 | 风险 | 处理 |
| --- | --- | --- | --- |
| RC1 | V1.6-B 自动候选评估不能替代人工质量评分。 | HIGH | 使用人工评分模板验收后再升级状态。 |
| RC2 | Studio 导出文件未在真实浏览器中人工打开检查。 | MEDIUM | RC 手动下载并检查 Markdown / JSON。 |
| RC3 | Research 质量不能只靠 contract smoke。 | HIGH | 人工检查结论、推断、缺口和冲突。 |
| RC4 | ChromeCLI / 浏览器路径不能证明内容质量。 | MEDIUM | 自动路径和人工质量评分同时通过。 |
| RC5 | Phase 2/3 disabled shell 不能被误判为输出能力 ready。 | HIGH | 人工确认 Audio / PPT / Mindmap / Compare 不生成输出、不发起后端生成请求。 |
| RC6 | 人工验收失败时不能进入 final sync。 | HIGH | report 必须记录 FAIL / NOT_READY / DEGRADED_ACCEPTED，并保持 final decision 不变。 |
| RC7 | 人工验收未完成前不能降低规格漂移和虚假验收风险。 | HIGH | 风险保持 HIGH，V1.6 保持 PENDING_HUMAN_ACCEPTANCE。 |

## 风险评估

开发计划漂移风险：HIGH。

虚假验收风险：HIGH。

## 计划调整复核

已要求 RC plan 补充：

- 环境记录字段。
- 浏览器主路径的 Markdown / PDF / Studio / Research / cleanup 全链路。
- Studio Markdown / JSON 导出人工检查细项。
- 多数据集人工质量评分阈值。
- Research 人工质量检查细项。
- Phase 2/3 disabled 检查细项。
- 任一失败时不改 final decision、不进入 final sync 的处理规则。

## 结论

必须停止自动推进。用户完成人工验收并给出结论后，才能继续进入 V1.6-RC report / final sync。
