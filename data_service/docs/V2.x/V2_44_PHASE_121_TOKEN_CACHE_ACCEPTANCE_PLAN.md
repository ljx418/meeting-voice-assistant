# V2.44 Phase 121 Token Budget Optimizer + Context Cache Acceptance Plan

## 1. 验收定义

Phase 121 通过条件：context pack 输出 token/cache/omitted 指标，并在低预算下保持 evidence 完整性。

## 2. 自动化测试

Focused:

```text
backend/tests/test_v2_44_token_budget_context_cache.py
```

必须验证：

- token_budget_ledger 落盘。
- context_cache_index 落盘。
- repeated task 产生 cache hit 或解释无法命中原因。
- low max_tokens 下不保留无 evidence recommendation。
- omitted_items 有 reason。
- JSON/Markdown 来自同一 artifact。
- HTTP/MCP/CLI parity。

## 3. 真实项目 E2E

- data_service：task context 输出 reading order + token metrics。
- HarnessOS：大型项目 task context 有 omitted_items 和 evidence-preserving trim。
- codexPat：非服务型项目不硬失败。

## 4. False-Green Rejection

拒绝：

- 删除 evidence 后保留 recommendation。
- cache hit 未绑定 artifact hash。
- omitted_items 缺 reason。
- token metrics 空但标 accepted。
