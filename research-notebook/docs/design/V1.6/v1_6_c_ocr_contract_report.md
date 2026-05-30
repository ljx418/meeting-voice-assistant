# ResearchNotebook V1.6-C OCR / Scanned PDF Contract Report

日期：2026-05-28

## 结论

V1.6-C OCR / 扫描 PDF 合同发现已完成，状态为 CONTRACT_DISCOVERY_READY。

本阶段没有接入 OCR provider，没有做扫描 PDF OCR，也没有声明 OCR ready。

## 实现内容

- capability manifest 增加：
  - `ocr=false`
  - `scanned_pdf_ocr=false`
- 扫描或不可抽取文本 PDF 的 preview unsupported reason 归一为 `ocr_required`。
- DocumentUnit 对扫描 PDF 返回空 items 和 `unsupported_reason=ocr_required`。
- 可抽取文本 PDF 回归不变。
- 前端 capability manifest mapper 可保留可选 OCR 字段。

## 验收命令

后端 focused test：

`python3 -m pytest tests/test_target_http_source_preview.py -q`

结果：

9 passed。

前端 focused test：

`npm run test -- dataServiceClient.test.ts`

结果：

74 passed。

全量 check：

`npm run check`

结果：

PASS。Boundary checks、lint、126 个 Vitest tests、production build 均通过。

## PRD 规格检视

PRD Phase 1 MVP 只要求 P0 PDF / TXT / Markdown，本阶段处理 OCR / 扫描 PDF 是为了明确边界：

- 文本 PDF 仍为受限可用。
- 扫描 PDF 需要 OCR provider，当前不支持。
- OCR 不属于当前 PASS 范围。
- 不把 PDF success 扩大为 scanned PDF ready。

## 风险评估

开发计划漂移风险：LOW。

虚假验收风险：LOW。

原因：报告和 manifest 均明确 OCR disabled，没有声明 OCR ready。

是否存在 HIGH 风险：NO。

## 仍未完成

- OCR provider。
- 扫描 PDF 文本抽取。
- 图片 OCR。
- bbox / page_no / confidence 级 OCR locator。
- OCR EvidenceSpan。

## 下一阶段建议

可以进入 V1.6-D Studio Export / Download。

V1.6-D 必须保留 citation metadata，不得导出 raw path / cache path / artifact physical path。
