# ResearchNotebook V1.6-E Research 补源 / 冲突分析 Acceptance

日期：2026-05-28

## 必须执行

```bash
npm run smoke:v1.6-e-research
npm run check
```

## Smoke 路径

1. 创建 workspace。
2. 调用 Research，确认无 sources 时拒答。
3. 导入真实数字人 Markdown 资料。
4. 调用 Research 问数字人相关问题。
5. 验证 structured report。
6. 验证 evidence_refs 可解析 unit 和 EvidenceSpan。
7. 保存脱敏 fixtures。
8. archive workspace。

## PASS_LIMITED_CONTRACT_SMOKE 标准

- `research_available=true`。
- `coverage_status=source_supported`。
- 至少 1 条 supported_conclusions。
- 每条 supported_conclusions 有 evidence_refs。
- 至少 1 个 evidence_ref 含 source_id + unit_id + evidence_id。
- DocumentUnit route PASS。
- EvidenceSpan route PASS。
- no_sources 或 insufficient_evidence 拒答 PASS。
- fixtures 无本地路径。
- npm run check PASS。

## FAIL 标准

- 无 sources 时硬答。
- Research 输出缺 evidence_refs。
- citation 无法解析。
- response 泄漏 raw path / cache path / physical path。
- 使用外部互联网搜索。
- 把 provider 常识当来源。

## 人工验收后移

以下内容进入 V1.6-RC 人工质量验收：

- 结论质量。
- 冲突识别完整性。
- 文字表达。
- 是否满足真实研究报告预期。
