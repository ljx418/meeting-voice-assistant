# ResearchNotebook V1.6-C OCR / Scanned PDF Contract Plan Audit

日期：2026-05-28

## 审计结论

Conditional Go。

允许进入 V1.6-C 合同发现和 disabled / unsupported 状态实现。不得接入 OCR provider，不得声明 OCR ready。

## 审计意见

| 编号 | 意见 | 风险 | 处理 |
| --- | --- | --- | --- |
| C1 | 可抽取 PDF 通过不能代表扫描 PDF ready。 | HIGH | 阶段计划明确只做 OCR required / unsupported 状态。 |
| C2 | capability manifest 增加 OCR 字段可能被误解为 ready。 | MEDIUM | 字段必须默认 false。 |
| C3 | UI 不能把 OCR 缺失显示成普通崩溃。 | MEDIUM | 显示局部 unavailable / OCR required。 |
| C4 | 无 OCR provider 不得做质量声明。 | HIGH | 完成声明限定 CONTRACT_DISCOVERY。 |

## 风险评估

开发计划漂移风险：LOW。

虚假验收风险：MEDIUM。

是否存在 HIGH 风险：NO，前提是只做合同发现并保持 OCR ready false。

## Go / No-Go

Go for V1.6-C contract discovery。

完成后只能声明：

ResearchNotebook V1.6-C OCR / scanned PDF contract discovery is documented, with unsupported states ready.

不能声明：

- OCR ready。
- scanned PDF extraction ready。
- image source ready。
