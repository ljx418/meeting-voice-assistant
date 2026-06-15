# V2.26 Phase 92 开发计划：Diagram-to-Claim Parser

## 1. 阶段目标

Phase 92 消费 Phase 91 的 Architecture Source Model，将 drawio/Mermaid/PlantUML/Markdown 中的架构图节点、边和架构性文本块转换为可追踪的 `diagram_claims.jsonl` 与 `diagram_relations.jsonl`。

本阶段只生成 document-side architecture claims，不做 code fact，不做 diagram-to-code accepted match。

## 2. 实现范围

新增模块：

```text
backend/data_service/code_assets/architecture_intent/diagram_claims.py
```

扩展路径：

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/claims/
  diagram_claims.jsonl
  diagram_relations.jsonl
  diagram_claim_summary.json
```

新增测试：

```text
backend/tests/test_v2_26_diagram_to_claim_parser.py
```

## 3. 输入

- Phase 91 `architecture_sources.jsonl`
- Phase 91 `diagram_cells.jsonl`
- Phase 91 `source_blocks.jsonl`

## 4. 输出

Claim 字段：

```text
claim_id
source_id
claim_type
label
normalized_label
source_locator
source_block_type
status_hint
confidence
evidence
needs_review
```

Relation 字段：

```text
relation_id
source_id
source_claim_id
target_claim_id
relation_type
label
source_locator
confidence
evidence
needs_review
```

## 5. 分类策略

Claim 类型：

```text
component
layer
boundary
adapter
provider
runtime
workflow
storage
public_interface
quality_gate
milestone
non_goal
forbidden_claim
unknown
```

Relation 类型：

```text
depends_on
implements
calls_claimed
publishes
consumes
stores
governs
validates
relates_to
```

## 6. 安全边界

- drawio node confidence 默认 <= 0.70。
- drawio edge 无明确 label 时必须 needs_review。
- Mermaid/PlantUML 关系默认是 document_claimed relation，不得写成 runtime call。
- Markdown bullet/table 只产生 document claim，不产生 code fact。
- label 必须 escape/redact 后入库。

## 7. 不做内容

- 不读取代码事实。
- 不做 diagram-to-code match。
- 不做 intent inference。
- 不做人工确认。
