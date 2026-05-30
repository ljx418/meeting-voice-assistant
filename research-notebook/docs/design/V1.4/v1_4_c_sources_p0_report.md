# ResearchNotebook V1.4-C Sources P0 Import Audit

日期：2026-05-26

## 阶段结论

V1.4-C Sources P0 导入与解析：PASS_LIMITED。

限定范围：Markdown / TXT / 可抽取文本的 PDF。PDF 已通过浏览器式 base64 文件上传合同完成 smoke。扫描版 PDF、OCR、PPT、音视频和图片仍不声明 ready。

原因：PRD P0 要求 PDF / TXT / Markdown 稳定导入、解析、索引和引用定位。当前 AI 数字人资料包 smoke 已证明 Markdown / TXT / 用户提供的真实 PDF 均可完成导入、build、preview、query citation。PDF preview 已从 `PDF_METADATA_ONLY` 修复为 `PDF_EXTRACTED`。

## 已确认能力

- TXT 文件可由浏览器读取为文本后提交到 source create，并已通过 AI 数字人资料包 smoke。
- Markdown 文件可由浏览器读取为文本后提交到 source create，并已通过 AI 数字人资料包 smoke。
- Source list / get / remove / rename wrapper 已存在。
- Source build / preview / DocumentUnit / EvidenceSpan 继承 V1.1 受限路径。
- PDF 可抽取文本样本已进入 preview / citation 路径。
- UI 已改为通过受控 base64 文件合同提交本地文件内容。

## 剩余缺口

- 多文件批量上传、拖拽上传和上传进度细节仍未产品化。
- 扫描版 PDF / OCR / 加密 PDF 不在本阶段 ready 范围内。
- PDF 原版页面渲染和 canvas 级高亮未实现；当前按抽取文本 + page unit + EvidenceSpan 验收。

## 风险评估

规格漂移风险：MEDIUM。

原因：当前 PDF 成功路径是可抽取文本 PDF，不应被误扩展为扫描版 PDF、OCR、PPT、音视频或图片 ready。

虚假验收风险：MEDIUM。

原因：PDF 已有真实抽取和引用定位证据，但仍可能被误写成 OCR / 原版 PDF 定位 / 全上传体验 ready。

收敛措施：状态使用 `PASS_LIMITED`，并明确限定为 Markdown / TXT / 可抽取文本 PDF。

## 推进决策

按 V1.4 风险门禁，当前没有 HIGH 风险，可以进入下一阶段：

- V1.4-D Notebook Guide。

## 建议下一阶段

V1.4-D Notebook Guide。

目标：

- 生成 Overview / Key Topics / Suggested Questions。
- Guide 必须基于当前 sources。
- Guide 未生成或资料不足时不能伪造内容。

最低验收：

- TXT import smoke：PASS，已用 AI 数字人资料包完成。
- Markdown import smoke：PASS，已用 AI 数字人资料包完成。
- PDF import smoke：PASS。
- PDF browser upload import smoke：PASS。
- PDF preview smoke：PASS，分类 `PDF_EXTRACTED`。
- PDF query citation smoke：PASS。
- 每种 P0 source 均可 list/get/build/preview/query citation。
- response 不泄露本地路径、cache path、artifact physical path。
- fixtures 保存到 `fixtures/real/v1_4/sources-p0/` 并脱敏。
