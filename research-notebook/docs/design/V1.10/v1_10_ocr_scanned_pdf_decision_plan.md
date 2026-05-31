# ResearchNotebook V1.10 OCR / Scanned PDF Decision Plan

日期：2026-05-31

## 目标

对 OCR / 扫描 PDF 做 V1.x 最终决策。

当前结论：V1.10 不接入 OCR provider，继续保持 OCR / scanned PDF `NOT_READY`，只保留合同发现和 unsupported 状态。

## 当前基线

- 可抽取文本 PDF：`PASS_LIMITED`
- 扫描 PDF / 图片 PDF：`NOT_READY`
- OCR provider：未接入
- OCR page_no / bbox / confidence schema：未冻结

## 默认决策

V1.10 默认不实现 OCR。

原因：

- OCR 需要 provider 和质量评估。
- 扫描 PDF 需要 page text、bbox、confidence、DocumentUnit、EvidenceSpan 的重新定位合同。
- 可抽取文本 PDF 通过不能代表 OCR ready。

## 如果未来实现 OCR

必须新增独立阶段，至少包含：

1. OCR provider contract。
2. OCR health probe。
3. OCR page text schema。
4. bbox / confidence schema。
5. DocumentUnit text basis 决策。
6. EvidenceSpan offset / locator 决策。
7. 扫描 PDF 真实数据 smoke。
8. OCR 质量人工验收。
9. raw path / cache path / artifact physical path 防泄露检查。

## 当前验收标准

V1.10 只验收 OCR boundary：

- 可抽取文本 PDF 不回退。
- 扫描 PDF 不被误报为普通 PDF ready。
- 扫描 PDF 返回 `ocr_required` 或 `unsupported_ocr`。
- UI 显示 OCR 未就绪 / 需要 OCR 合同。
- capability / 文档不声明 OCR ready。
- `npm run check` PASS。

## 风险评估

| 风险项 | 评级 | 收敛措施 |
| --- | --- | --- |
| 规格漂移 | HIGH | OCR 不进入实现，只做决策和边界验收 |
| 虚假验收 | HIGH | 文本 PDF PASS_LIMITED 不得扩展到扫描 PDF |
| 质量风险 | HIGH | 无 OCR provider 和人工质量验收前不声明 ready |
