# V2.44 Phase 121 Token Budget Optimizer + Context Cache Development Plan

## 1. 阶段目标

Phase 121 为 Agent Context Pack 增加 token budget ledger、context cache、omitted_items reason 和重复阅读减少指标。

## 2. 输入

- V2.42 relationship chains
- V2.43 document semantic claims
- V2.9 / V2.37 context/report artifacts
- task、role、mode、max_tokens

## 3. 输出 Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_44/
  token_budget_ledger.json
  context_cache_index.json
  context_pack_optimized/{pack_id}.json
  context_pack_optimized/{pack_id}.md
```

## 4. 实现计划

1. 新增 token ledger：input sections、estimated_tokens、kept/omitted counts。
2. 新增 context cache：task hash、artifact hash、role/mode/max_tokens。
3. 优化 reading order：优先 capability、entrypoint、evidence、tests、doc constraints。
4. 小 budget 下删除低优先级 recommendation，而不是删除 evidence 后保留 recommendation。
5. 暴露 HTTP/MCP/CLI optimize/read。

## 5. 边界

- token estimate 可近似，但必须稳定。
- cache hit 不代表事实未变化，必须绑定 artifact hash。
- recommendation 必须有 evidence 或 needs_review。
