# V1.8-C Agent-Led Guide / QA / Citation Validation Plan

日期：2026-05-30

## 目标

Agent 自动验证 Notebook Guide、source-grounded QA 和 citation resolution。

## 开发内容

1. 获取 Notebook Guide。
2. 检查 Overview / Key Topics / Suggested Questions。
3. 选择 Suggested Question 发起 QA。
4. 检查回答 citation。
5. 验证 source_id / unit_id / evidence_id。
6. 调用 DocumentUnit 与 EvidenceSpan route。
7. 验证资料外问题拒答。
8. 生成 citation validation report。

## 验收标准

- Guide 非空。
- Overview 与资料相关。
- Key Topics 至少 3 个。
- Suggested Questions 至少 3 个。
- QA 回答默认基于 sources。
- 至少一个 citation 可解析到 EvidenceSpan。
- EvidenceSpan offset 合同有效。
- 资料外问题拒答。
- 不使用互联网常识硬答。

## 必跑命令

```bash
npm run check
npm run smoke:v1.5-b-guide
npm run smoke:v1.5-d-qa
npm run smoke:v1.8-agent-guide-qa
```

## 风险

- 规格漂移：MEDIUM。
- 虚假验收：MEDIUM-HIGH。自动检查不能证明内容质量完全达标。

