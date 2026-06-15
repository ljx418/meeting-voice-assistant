# V2.43 Phase 120 drawio / Document Semantics Development Plan

## 1. 阶段目标

Phase 120 增强 drawio 与 Markdown 语义解析，把页面、泳道、分组、边、gate、milestone、acceptance、non-goal、stop condition 转成 document semantic claims / relations。

document claim 不能直接成为 code fact。

## 2. 输入

- docs/**/*.md
- docs/**/*.drawio
- V2.7/V2.37 document registry / claims（若存在）
- V2.42 relationship chains（用于后续报告引用，不用于伪造 code fact）

## 3. 输出 Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_43/
  document_semantic_claims.jsonl
  document_semantic_relations.jsonl
  document_semantic_summary.json
```

## 4. 实现计划

1. 增强 Markdown parser：heading、bullet、table row、acceptance criteria、non-goal、stop condition。
2. 增强 drawio parser：page、lane、group、container、edge、legend、milestone、gate。
3. 每条 claim 记录 `doc_id`、`source_block_type`、`line_range` 或 `drawio_cell_id`。
4. drawio label 必须 escape，Mermaid/HTML 不允许注入。
5. 暴露 HTTP/MCP/CLI build/read。

## 5. 边界

- drawio claim 是 target/document claim。
- 无代码证据时不能变成 supported code fact。
- 图形布局关系不能自动推导 runtime topology。
