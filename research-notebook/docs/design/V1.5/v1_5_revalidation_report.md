# ResearchNotebook V1.5 Revalidation Report

日期：2026-05-28

## 结论

PASS_LIMITED。

本轮按收紧后的 V1.5 审计口径重新复验：先验证真实 LLM provider，再验证数字人 P0 数据集上的 Guide、Studio、Source-grounded QA 和 ChromeCLI / Manual E2E。复验未发现 HIGH 规格漂移或 HIGH 虚假验收风险。

## 审计背景

外部审计意见指出：

- 若 V1.5-A AI Provider Contract 仍为 BLOCKED，则 V1.5-B/C/D/E/RC 必须 NO-GO。
- deterministic fallback 可作为 UX fallback，但不能作为 AI quality pass。
- V1.4-C Sources P0，尤其 PDF 导入 / 抽取 / citation，必须先确认不再 BLOCKED。

本地当前事实：

- MiniMax OpenAI-compatible provider 已配置。
- 数字人 Markdown / PDF 验收材料存在。
- V1.5 smoke 脚本和 fixtures 已存在。

## 复验结果

| 阶段 | 命令 | 结果 | 说明 |
| --- | --- | --- | --- |
| V1.5-A Provider | `npm run smoke:v1.5-a-provider` | PASS | 真实 MiniMax 调用成功，schema 和脱敏通过。 |
| V1.5-B Guide | `npm run smoke:v1.5-b-guide` | PASS | Markdown/PDF 导入、build、AI Guide evidence/metadata 验证通过。 |
| V1.5-C Studio | `npm run smoke:v1.5-c-studio` | PASS | Notes / Study Guide / Briefing Doc / FAQ 均通过 AI output/citation/metadata 验证。 |
| V1.5-D QA | `npm run smoke:v1.5-d-qa` | PASS | 覆盖型问题、资料外拒答、推断标注均通过。 |
| V1.5-E Browser E2E | `npm run smoke:v1.5-e-e2e` | PASS | Guide、QA citation、高亮、Studio 四类输出、拒答和 cleanup 通过。 |

## V1.4-C Sources P0 回归判断

V1.5-B/C/D/E 复验均重新导入数字人 Markdown 和可抽取文本 PDF，并完成 workspace build、source preview / DocumentUnit / EvidenceSpan 相关路径验证。因此本轮确认：

- Markdown import：PASS。
- PDF import：PASS。
- 可抽取文本 PDF build：PASS。
- citation / EvidenceSpan 路径：PASS_LIMITED。

仍不声明：

- OCR / 扫描 PDF ready。
- Word / PPT / audio / video 原生摄入 ready。
- all-source-type ready。

## 质量和风险

| 项目 | 评估 |
| --- | --- |
| 规格漂移风险 | LOW |
| 虚假验收风险 | MEDIUM |
| 是否出现 HIGH 风险 | NO |

虚假验收风险保持 MEDIUM 的原因：

- 验收数据仍限定为数字人 P0 数据集。
- ChromeCLI 路径证明用户主流程可走，但内容质量仍建议继续扩大数据集人工评分。
- 本轮不代表所有 source type、所有行业或所有输出场景 ready。

## 声明边界

可声明：

ResearchNotebook V1.5 AI Guide, source-grounded QA, and Studio lightweight outputs are quality-smoke-ready for the AI digital human P0 dataset.

仍不能声明：

- all-source-type ready。
- OCR ready。
- Word / PPT / audio / video ready。
- arbitrary Agent ready。
- Audio Overview ready。
- PPT generation ready。
- mindmap ready。
- document comparison ready。

范围剔除：

- 云同步 / 协作已从 V1.x 剩余闭环范围剔除。
