# V1.9-A Research Quality Plan

日期：2026-05-30

## 目标

验证 Research 输出严格基于 Notebook sources，能够拒答无来源或资料外问题，并为 supported conclusions 提供可解析 evidence refs。

## 验收

- 无来源时拒答。
- 有来源时返回 structured report。
- `supported_conclusions` 每条有 `evidence_refs`。
- 至少一条 evidence ref 可解析到 DocumentUnit / EvidenceSpan。
- 资料外问题拒答或标记 insufficient evidence。
- `inferences` 如存在，必须有 evidence_refs 和推断提示。
- `missing_evidence` 和 `suggested_source_actions` 字段存在。
- 不自动联网搜索。
- fixtures 不含本地路径或密钥。

## 命令

```bash
npm run check
npm run smoke:v1.9-research-quality
```
