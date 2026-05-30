# ResearchNotebook V1.4-G Citation Navigation Report

日期：2026-05-26

## 阶段结论

V1.4-G 来源定位与引用高亮产品化确认为 PASS_LIMITED。

已确认：

- Chat answer citation 可打开来源定位。
- Studio artifact citation 可打开 SourcePreviewDrawer。
- citation 携带 source_id + unit_id + evidence_id 时可进入 DocumentUnit / EvidenceSpan。
- 高亮失败不会清空 answer / Studio artifact。
- citation 不使用 sourceRef、slug 或 artifact_ref 伪装 registry source_id。

## 限定范围

- 当前只声明 data_service 支持的 text / markdown / json / 可抽取文本 PDF 路径。
- 不声明扫描版 PDF / OCR / 原版 PDF 页面渲染 ready。
- 不声明 all-source-type precise backjump ready。

## 验证结果

前端 focused test：

```text
npm run test -- src/features/workspaces/WorkspacePage.test.tsx
24 passed
```

覆盖：

- workspace query citation。
- EvidenceSpan drawer navigation。
- Studio artifact citation。
- DocumentUnit selected state。
- EvidenceSpan highlight。

## 风险评估

规格漂移风险：LOW

原因：本阶段是对既有 V1.1-D / V1.4-F citation 能力的产品化确认。

虚假验收风险：MEDIUM

原因：用户可能把受限 source type 的 citation ready 理解为全格式 ready。

收敛措施：所有文档继续保留 all-source-type precise backjump、OCR、扫描版 PDF 为 NOT_READY。

结论：无 HIGH 风险，可以进入 V1.4-H 资料不足补源入口收口。
