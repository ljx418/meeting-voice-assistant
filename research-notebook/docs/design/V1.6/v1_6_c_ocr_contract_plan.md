# ResearchNotebook V1.6-C OCR / Scanned PDF Contract Plan

日期：2026-05-28

## 阶段目标

V1.6-C 只做 OCR / 扫描 PDF 合同发现和 disabled / unsupported 状态。没有 OCR provider 前，不实现 OCR，不声明 OCR ready。

目标是让扫描 PDF 和图片型 PDF 失败得更清楚：它们不是普通 PDF 解析失败，而是 `ocr_required` 或 `unsupported_ocr`。

## 允许范围

- capability manifest 增加 OCR 相关字段，默认 false。
- 可抽取文本 PDF 仍保持 PASS_LIMITED。
- 扫描 PDF / 图片 PDF 返回稳定 unsupported 状态。
- UI 显示“需要 OCR 合同 / 当前不可用”。
- 文档和 fixtures 记录 OCR 未就绪。

## 禁止范围

- 不接 OCR provider。
- 不做图像文字识别。
- 不声明 scanned PDF ready。
- 不把可抽取文本 PDF 的通过结论套到扫描 PDF。
- 不声明 Word / PPT / 图片 / 音视频 ready。

## 验收标准

- capability manifest 明确 OCR disabled。
- 文本 PDF smoke 不回退。
- 扫描 PDF 返回 `ocr_required` 或 `unsupported_ocr`。
- Preview / DocumentUnit 对扫描 PDF 显示局部 unavailable。
- response 不含 raw path、cache path、artifact physical path、stack trace。
- `npm run check` PASS。

## 风险评估

开发计划漂移风险：LOW。

虚假验收风险：MEDIUM。

原因：OCR 合同发现容易被误读为 OCR 可用。

收敛措施：所有状态使用 CONTRACT_DISCOVERY / NOT_READY，不使用 PASS。
